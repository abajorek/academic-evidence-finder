import argparse, os, re, yaml, mailbox, json, time
from pathlib import Path
from datetime import datetime, timezone
from dateutil import parser as dtparse
from icalendar import Calendar
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import Counter

from report import write_csv, write_summary, write_html
from extractors import extract_text

# ---------- helpers ----------

def to_epoch(dstr):
    if not dstr:
        return None
    return datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()

def iso_date_from_epoch(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()

def read_lines_file(path):
    if not path:
        return []
    with open(path, "r") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]

def load_path_list(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [ln.strip() for ln in f if ln.strip()]

def write_progress(outdir, stage, n, total, started_ts):
    os.makedirs(outdir, exist_ok=True)
    now = time.time()
    elapsed = now - started_ts
    remaining = None
    if total and n:
        rate = n / elapsed if elapsed > 0 else 0
        if rate > 0:
            remaining = max(0.0, (total - n) / rate)
    payload = {
        "stage": stage,
        "processed": int(n),
        "total": int(total) if total is not None else None,
        "elapsed_sec": round(elapsed, 2),
        "eta_sec": (round(remaining, 2) if remaining is not None else None),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(os.path.join(outdir, "progress.json"), "w") as f:
        json.dump(payload, f)

# ---------- rules ----------

def load_rules(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    compiled = {}
    for cat, subs in cfg["categories"].items():
        compiled[cat] = {}
        for sub, rule in subs.items():
            pats = [re.compile(p, re.IGNORECASE) for p in rule.get("any", [])]
            compiled[cat][sub] = pats
    scoring = cfg.get("scoring", {})
    per_hit = int(scoring.get("per_hit_points", 1))
    cap = int(scoring.get("cap_per_file", 10))
    cat_w = scoring.get("category_weights", {}) or {}
    bonus = cfg.get("scoring", {}).get("bonus_keywords", {}) or {}
    if isinstance(bonus, list):
        m = {}
        for item in bonus:
            if isinstance(item, str) and ":" in item:
                k, v = item.split(":", 1)
                try:
                    m[k.strip()] = float(v.strip())
                except Exception:
                    pass
        bonus = m
    return cfg, compiled, per_hit, cap, cat_w, bonus

def score_text(text, pats, per_hit, cap):
    if not text:
        return 0, 0
    hits = 0
    for pat in pats:
        hits += len(set(m.span() for m in pat.finditer(text)))
    return min(hits * per_hit, cap), hits

# ---------- walkers ----------

def walk_files(include_dirs, include_exts, exclude_dirs, since_ts=None, until_ts=None, max_bytes=0):
    for root in include_dirs:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            for name in filenames:
                path = os.path.join(dirpath, name)
                ext = os.path.splitext(name.lower())[1]
                if include_exts and ext not in include_exts:
                    continue
                try:
                    st = os.stat(path)
                except Exception:
                    continue
                if max_bytes and st.st_size > max_bytes:
                    continue
                mt = st.st_mtime
                if since_ts and mt < since_ts:
                    continue
                if until_ts and mt > until_ts + 86399:  # inclusive end-of-day
                    continue
                yield path

# ---------- sources ----------

def iter_ics(paths):
    for path in paths:
        try:
            with open(path, "rb") as f:
                cal = Calendar.from_ical(f.read())
            for comp in cal.walk():
                if comp.name != "VEVENT":
                    continue
                subj = comp.get("summary")
                desc = comp.get("description")
                loc = comp.get("location")
                start = comp.get("dtstart")
                txt = "\n".join([str(subj or ""), str(desc or ""), str(loc or "")])
                when = ""
                try:
                    dt = start.dt
                    when = (dt.date().isoformat() if hasattr(dt, "date") else str(dt)[:10])
                except Exception:
                    pass
                meta = " • ".join([str(start.dt) if start else "", str(loc or "")]).strip(" •")
                yield {"display": str(subj or "(no title)"), "text": txt, "when": when, "meta": meta}
        except Exception:
            continue

def iter_mbox(paths):
    for path in paths:
        try:
            mbox = mailbox.mbox(path)
        except Exception:
            continue
        for msg in mbox:
            subj = msg.get("subject", "") or ""
            frm = msg.get("from", "") or ""
            to  = msg.get("to", "") or ""
            date = msg.get("date", "") or ""
            body = ""
            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        ct = (part.get_content_type() or "").lower()
                        if ct == "text/plain":
                            body = part.get_payload(decode=True) or b""
                            body = body.decode(errors="ignore")
                            break
                        elif ct == "text/html" and not body:
                            htmlb = part.get_payload(decode=True) or b""
                            body = BeautifulSoup(htmlb.decode(errors="ignore"), "lxml").get_text(" ", strip=True)
                else:
                    ct = (msg.get_content_type() or "").lower()
                    if ct == "text/plain":
                        body = (msg.get_payload(decode=True) or b"").decode(errors="ignore")
                    elif ct == "text/html":
                        htmlb = msg.get_payload(decode=True) or b""
                        body = BeautifulSoup(htmlb.decode(errors="ignore"), "lxml").get_text(" ", strip=True)
            except Exception:
                pass
            text = "\n".join([subj, frm, to, body])
            when = ""
            try:
                when = dtparse.parse(date).date().isoformat()
            except Exception:
                pass
            meta = " • ".join([date, f"From {frm}", f"To {to}" if to else ""]).strip(" •")
            yield {"display": subj or "(no subject)", "text": text, "when": when, "meta": meta}

# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include", nargs="*", help="Directories to scan")
    ap.add_argument("--include-file", help="File listing directories to scan")
    ap.add_argument("--path-list", help="File with newline-delimited absolute paths (from Spotlight)")
    ap.add_argument("--ics", nargs="*", help="ICS files")
    ap.add_argument("--ics-file", help="File listing ICS paths")
    ap.add_argument("--mbox", nargs="*", help="MBOX files")
    ap.add_argument("--mbox-file", help="File listing MBOX paths")
    ap.add_argument("--rules", default=str(Path(__file__).resolve().parents[1] / "config" / "rules.yml"))
    ap.add_argument("--out", default="out", help="Output directory")
    ap.add_argument("--modified-since", help="YYYY-MM-DD")
    ap.add_argument("--modified-until", help="YYYY-MM-DD")
    ap.add_argument("--max-bytes", type=int, default=0)
    ap.add_argument("--only-ext", help="Comma list to override include_extensions (e.g. .pdf,.docx)")
    args = ap.parse_args()

    start_ts = time.time()

    cfg, compiled, per_hit, cap, cat_w, bonus = load_rules(args.rules)

    include_dirs = set(args.include or []) | set(read_lines_file(args.include_file))
    ics_paths = set(args.ics or []) | set(read_lines_file(args.ics_file))
    mbox_paths = set(args.mbox or []) | set(read_lines_file(args.mbox_file))
    spotlight_paths = set(load_path_list(args.path_list))

    include_exts = set([e.lower() for e in cfg["file_filters"]["include_extensions"]])
    if args.only_ext:
        include_exts = set([e.strip().lower() for e in args.only_ext.split(",") if e.strip()])

    exclude_dirs = set(cfg["file_filters"].get("exclude_dirs", []))

    since_ts = to_epoch(args.modified_since)
    until_ts = to_epoch(args.modified_until)
    max_bytes = max(0, int(args.max_bytes or 0))

    os.makedirs(args.out, exist_ok=True)
    write_progress(args.out, "indexing", 0, 0, start_ts)

    files_to_scan = []
    if spotlight_paths:
        write_progress(args.out, "filtering", 0, len(spotlight_paths), start_ts)
        pbar_filt = tqdm(total=len(spotlight_paths), desc="Filtering file list", unit="file",
                         dynamic_ncols=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        for p in spotlight_paths:
            pbar_filt.update(1)
            try:
                name = os.path.basename(p).lower()
                ext = os.path.splitext(name)[1]
                if include_exts and ext not in include_exts:
                    continue
                st = os.stat(p)
                if max_bytes and st.st_size > max_bytes:
                    continue
                if since_ts and st.st_mtime < since_ts:
                    continue
                if until_ts and st.st_mtime > until_ts + 86399:
                    continue
                files_to_scan.append(p)
            except Exception:
                continue
            finally:
                write_progress(args.out, "filtering", pbar_filt.n, pbar_filt.total, start_ts)
        pbar_filt.close()
    elif include_dirs:
        write_progress(args.out, "walking", 0, 0, start_ts)
        pbar_walk = tqdm(desc="Walking directories", unit="file", dynamic_ncols=True,
                         bar_format="{l_bar}{bar}| {n_fmt} files [{elapsed}, {rate_fmt}]")
        for p in walk_files(include_dirs, include_exts, exclude_dirs, since_ts, until_ts, max_bytes):
            files_to_scan.append(p)
            pbar_walk.update(1)
            write_progress(args.out, "walking", pbar_walk.n, 0, start_ts)
        pbar_walk.close()

    total_files = len(files_to_scan)
    write_progress(args.out, "processing", 0, total_files, start_ts)

    rows = []
    PROPRIETARY_HINTS = {".sib", ".musx", ".mus", ".ftmx", ".ftm", ".3dj", ".3dz", ".3da", ".prod"}
    
    pbar = tqdm(total=total_files, desc="Processing files", unit="file", dynamic_ncols=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    stats = Counter(nonempty=0, empty=0, matched=0)
    
    for path in files_to_scan:
        base = os.path.basename(path)
        if len(base) > 45: base = base[:42] + "..."
        pbar.set_description(f"Processing {base}")

        t0 = time.perf_counter()
        try:
            st = os.stat(path)
        except Exception:
            pbar.update(1)
            write_progress(args.out, "processing", pbar.n, total_files, start_ts)
            continue

ext = os.path.splitext(base.lower())[1]
text = extract_text(path)

# Treat known “proprietary hint” extensions as text = filename when extractor returns empty
if not text and ext in PROPRIETARY_HINTS:
    text = base.lower()

# Track whether we got any text at all
if text and text.strip():
    stats["nonempty"] += 1
else:
    stats["empty"] += 1
    # Still update progress HUD and move on (no text to score)
    dt = time.perf_counter() - t0
    pbar.set_postfix_str(f"{dt:.2f}s txt:{stats['nonempty']}/{pbar.n+1} hit:{stats['matched']}")
    pbar.update(1)
    write_progress(args.out, "processing", pbar.n, total_files, start_ts)
    continue

# Score text against rules
hit_this_file = False
for cat, subs in compiled.items():
    for sub, pats in subs.items():
        score, hits = score_text(text, pats, per_hit, cap)
        if score > 0:
            hit_this_file = True
            wmult = float(cat_w.get(cat, 1.0)) if isinstance(cat_w, dict) else 1.0
            bsum = 0.0
            if isinstance(bonus, dict):
                for k, pts in bonus.items():
                    try:
                        if k and re.search(re.escape(k), text, re.IGNORECASE):
                            bsum += float(pts)
                    except Exception:
                        pass
            adj_score = score * wmult + bsum
            if float(adj_score).is_integer():
                adj_score = int(adj_score)
            rows.append({
                "source": "files",
                "path": path,
                "display": path,
                "category": cat,
                "subcategory": sub,
                "hits": hits,
                "score": adj_score,
                "meta": f"mtime {datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()}",
                "when": iso_date_from_epoch(st.st_mtime),
            })

if hit_this_file:
    stats["matched"] += 1

dt = time.perf_counter() - t0
pbar.set_postfix_str(f"{dt:.2f}s txt:{stats['nonempty']}/{pbar.n+1} hit:{stats['matched']}")
pbar.update(1)
write_progress(args.out, "processing", pbar.n, total_files, start_ts)
    pbar.close()

    if ics_paths:
        w = tqdm(total=len(ics_paths), desc="Parsing ICS", unit="file", dynamic_ncols=True)
        for item_path in ics_paths:
            for item in iter_ics([item_path]):
                text = item["text"]
                for cat, subs in compiled.items():
                    for sub, pats in subs.items():
                        score, hits = score_text(text, pats, per_hit, cap)
                        if score > 0:
                            rows.append({
                                "source": "calendar",
                                "path": "ics",
                                "display": item["display"],
                                "category": cat,
                                "subcategory": sub,
                                "hits": hits,
                                "score": score,
                                "meta": item["meta"],
                                "when": item["when"] or "",
                            })
            w.update(1)
        w.close()

    if mbox_paths:
        w = tqdm(total=len(mbox_paths), desc="Parsing MBOX", unit="file", dynamic_ncols=True)
        for item_path in mbox_paths:
            for item in iter_mbox([item_path]):
                text = item["text"]
                for cat, subs in compiled.items():
                    for sub, pats in subs.items():
                        score, hits = score_text(text, pats, per_hit, cap)
                        if score > 0:
                            rows.append({
                                "source": "email",
                                "path": "mbox",
                                "display": item["display"],
                                "category": cat,
                                "subcategory": sub,
                                "hits": hits,
                                "score": score,
                                "meta": item["meta"],
                                "when": item["when"] or "",
                            })
            w.update(1)
        w.close()

    if not rows:
        write_progress(args.out, "done_no_matches", 0, total_files, start_ts)
        print("No matches. Try widening the date range, extensions, or rules.")
        return

    rows.sort(key=lambda r: (r["source"], -float(r["score"]), r["category"], r["subcategory"], r["display"]))
    evidence_csv = write_csv(rows, args.out, "evidence.csv")
    summary_csv = write_summary(rows, args.out)
    report_html = write_html(rows, args.out)

    write_progress(args.out, "done", total_files, total_files, start_ts)
    print(f"Wrote:\n  {evidence_csv}\n  {summary_csv}\n  {report_html}")

if __name__ == "__main__":
    main()

import argparse, os, re, time, yaml, mailbox, chardet
from pathlib import Path
from tqdm import tqdm
from dateutil import parser as dateparser
from icalendar import Calendar
from extractors import extract_text
from report import write_csv, write_summary, write_html
from datetime import datetime, timezone

def to_epoch(dstr):
    if not dstr: return None
    return datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()


def load_rules(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    compiled = {}
    for cat, subs in cfg["categories"].items():
        compiled[cat] = {}
        for sub, rule in subs.items():
            pats = [re.compile(pat, re.IGNORECASE) for pat in rule.get("any", [])]
            compiled[cat][sub] = pats
    return cfg, compiled

def score_text(text, patterns, per_hit_points, cap):
    hits = 0
    for pat in patterns:
        hits += len(set(m.span() for m in pat.finditer(text)))
    return min(hits * per_hit_points, cap), hits

def load_list_file(path):
    if not path:
        return []
    with open(path, "r") as f:
        return [os.path.expanduser(line.strip()) for line in f if line.strip() and not line.strip().startswith("#")]

# --- replace your walk_files() with this date/size-aware generator ---
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
                if until_ts and mt > until_ts + 86399:  # make 'until' inclusive through end of day
                    continue
                yield path

def safe_decode(b):
    if isinstance(b, str):
        return b
    if not b:
        return ""
    guess = chardet.detect(b).get("encoding") or "utf-8"
    try:
        return b.decode(guess, errors="replace")
    except Exception:
        return b.decode("utf-8", errors="replace")

def ics_events_from_file(path):
    try:
        with open(path, "rb") as f:
            cal = Calendar.from_ical(f.read())
    except Exception:
        return []
    events = []
    for comp in cal.walk():
        if comp.name == "VEVENT":
            summary = safe_decode(comp.get("summary", ""))
            desc = safe_decode(comp.get("description", ""))
            loc = safe_decode(comp.get("location", ""))
            dtstart = comp.get("dtstart")
            when = ""
            if dtstart:
                try:
                    dt = dtstart.dt
                    when = str(dt)
                except Exception:
                    when = ""
            txt = " ".join([summary or "", desc or "", loc or ""]).strip()
            events.append({
                "display": summary or os.path.basename(path),
                "text": f"{summary}\n{desc}\n{loc}",
                "meta": f"{when}{' • ' + loc if loc else ''}",
            })
    return events

def mbox_messages_from_file(path):
    msgs = []
    try:
        mbox = mailbox.mbox(path)
    except Exception:
        return msgs
    for msg in mbox:
        subject = msg.get("subject", "")
        from_ = msg.get("from", "")
        to = msg.get("to", "")
        date = msg.get("date", "")
        # extract body (prefer text/plain)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = (part.get_content_type() or "").lower()
                if ct == "text/plain":
                    try:
                        body = safe_decode(part.get_payload(decode=True))
                        break
                    except Exception:
                        pass
        else:
            try:
                body = safe_decode(msg.get_payload(decode=True))
            except Exception:
                body = str(msg.get_payload())
        text = "\n".join([subject or "", from_ or "", to or "", body or ""])
        meta = []
        if date:
            try:
                meta.append(str(dateparser.parse(date)))
            except Exception:
                meta.append(date)
        if from_:
            meta.append(f"From {from_}")
        if to:
            meta.append(f"To {to}")
        msgs.append({
            "display": subject or os.path.basename(path),
            "text": text,
            "meta": " • ".join(meta),
        })
    return msgs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include", nargs="*", help="Directories to scan for files")
    ap.add_argument("--include-file", help="File listing directories to scan for files")
    ap.add_argument("--ics", nargs="*", help="ICS files")
    ap.add_argument("--ics-file", help="File listing ICS paths")
    ap.add_argument("--mbox", nargs="*", help="MBOX files")
    ap.add_argument("--mbox-file", help="File listing MBOX paths")
    ap.add_argument("--rules", default=str(Path(__file__).resolve().parents[1] / "config" / "rules.yml"))
    ap.add_argument("--out", default="out", help="Output directory")

    # NEW speed knobs
    ap.add_argument("--modified-since", help="YYYY-MM-DD (file mtime lower bound)")
    ap.add_argument("--modified-until", help="YYYY-MM-DD (file mtime upper bound, inclusive)")
    ap.add_argument("--max-bytes", type=int, default=0, help="Skip files larger than this many bytes (0 = no limit)")
    ap.add_argument("--only-ext", help="Comma list to override rules.yml include_extensions (e.g. .pdf,.docx)")
    ap.add_argument("--workers", type=int, default=4, help="Concurrent workers for file reads (4–8 is good)")
    args = ap.parse_args()

    cfg, compiled = load_rules(args.rules)
    include_exts = set(cfg["file_filters"]["include_extensions"])
    exclude_dirs = set(cfg["file_filters"]["exclude_dirs"])
    per_points = int(cfg["scoring"]["per_hit_points"])
    cap = int(cfg["scoring"]["cap_per_file"])

    since_ts = to_epoch(args.modified_since)
    until_ts = to_epoch(args.modified_until)
    include_exts = set(cfg["file_filters"]["include_extensions"])
    if args.only_ext:
    include_exts = set([e.strip().lower() for e in args.only_ext.split(",") if e.strip()])
    max_bytes = max(0, int(args.max_bytes or 0))

    include_dirs = list(filter(None, (args.include or []))) + load_list_file(args.include_file)
    ics_paths = list(filter(None, (args.ics or []))) + load_list_file(args.ics_file)
    mbox_paths = list(filter(None, (args.mbox or []))) + load_list_file(args.mbox_file)

    os.makedirs(args.out, exist_ok=True)
    rows = []

    # --- FILES (pdf/docx/pptx/txt) ---
    file_paths = list(walk_files(include_dirs, include_exts, exclude_dirs, since_ts, until_ts, max_bytes)) if include_dirs else []
    for path in tqdm(file_paths, desc="Scanning files"):
        try:
            text = extract_text(path)
        except Exception:
            text = ""
        if not text:
            continue
        for cat, subs in compiled.items():
            for sub, pats in subs.items():
                score, hits = score_text(text, pats, per_points, cap)
                if score > 0:
                    rows.append({
                        "source": "files",
                        "path": path,
                        "display": os.path.basename(path),
                        "category": cat,
                        "subcategory": sub,
                        "hits": hits,
                        "score": score,
                        "meta": "",
                    })

    # --- CALENDAR (.ics) ---
    for path in tqdm(ics_paths, desc="Scanning calendars"):
        events = ics_events_from_file(path)
        for ev in events:
            text = ev["text"]
            for cat, subs in compiled.items():
                for sub, pats in subs.items():
                    score, hits = score_text(text, pats, per_points, cap)
                    if score > 0:
                        rows.append({
                            "source": "calendar",
                            "path": path,
                            "display": ev["display"],
                            "category": cat,
                            "subcategory": sub,
                            "hits": hits,
                            "score": score,
                            "meta": ev.get("meta",""),
                        })

    # --- EMAIL (.mbox) ---
    for path in tqdm(mbox_paths, desc="Scanning email"):
        msgs = mbox_messages_from_file(path)
        for m in msgs:
            text = m["text"]
            for cat, subs in compiled.items():
                for sub, pats in subs.items():
                    score, hits = score_text(text, pats, per_points, cap)
                    if score > 0:
                        rows.append({
                            "source": "email",
                            "path": path,
                            "display": m["display"],
                            "category": cat,
                            "subcategory": sub,
                            "hits": hits,
                            "score": score,
                            "meta": m.get("meta",""),
                        })

    if not rows:
        print("No matches found. Try expanding config/rules.yml or different sources.")
        return

    rows.sort(key=lambda r: (r["source"], -r["score"], r["category"], r["subcategory"], r["display"]))
    evidence_csv = write_csv(rows, args.out, "evidence.csv")
    summary_csv = write_summary(rows, args.out)
    report_html = write_html(rows, args.out)
    print(f"Wrote:\n  {evidence_csv}\n  {summary_csv}\n  {report_html}")

if __name__ == "__main__":
    main()

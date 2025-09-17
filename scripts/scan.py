import argparse, os, re, time, yaml
from pathlib import Path
from tqdm import tqdm
from extractors import extract_text
from report import write_csv, write_summary, write_html

def load_rules(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    # compile regex
    compiled = {}
    for cat, subs in cfg["categories"].items():
        compiled[cat] = {}
        for sub, rule in subs.items():
            pats = [re.compile(pat, re.IGNORECASE) for pat in rule.get("any", [])]
            compiled[cat][sub] = pats
    return cfg, compiled

def iter_paths(include_dirs, include_exts, exclude_dirs):
    for root in include_dirs:
        for dirpath, dirnames, filenames in os.walk(root):
            # prune excluded dirs
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            for name in filenames:
                ext = os.path.splitext(name.lower())[1]
                if include_exts and ext not in include_exts:
                    continue
                yield os.path.join(dirpath, name)

def score_text(text, patterns, per_hit_points, cap):
    hits = 0
    for pat in patterns:
        # count unique matches per pattern
        hits += len(set(m.span() for m in pat.finditer(text)))
    return min(hits * per_hit_points, cap), hits

def load_include_file(path):
    if not path:
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include", nargs="*", help="Directories to scan")
    ap.add_argument("--include-file", help="File listing directories to scan")
    ap.add_argument("--rules", default=str(Path(__file__).resolve().parents[1] / "config" / "rules.yml"))
    ap.add_argument("--out", default="out", help="Output directory")
    args = ap.parse_args()

    include_dirs = list(filter(None, (args.include or []))) + load_include_file(args.include_file)
    include_dirs = [os.path.expanduser(p) for p in include_dirs]
    if not include_dirs:
        ap.error("Provide --include DIR ... or --include-file examples/include_dirs.txt")

    cfg, compiled = load_rules(args.rules)
    include_exts = set(cfg["file_filters"]["include_extensions"])
    exclude_dirs = set(cfg["file_filters"]["exclude_dirs"])
    per_points = int(cfg["scoring"]["per_hit_points"])
    cap = int(cfg["scoring"]["cap_per_file"])

    os.makedirs(args.out, exist_ok=True)

    rows = []
    paths = list(iter_paths(include_dirs, include_exts, exclude_dirs))
    for path in tqdm(paths, desc="Scanning"):
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
                        "path": path,
                        "category": cat,
                        "subcategory": sub,
                        "hits": hits,
                        "score": score,
                    })

    if not rows:
        print("No matches found. Try adding more terms to config/rules.yml or scanning different folders.")
        return

    rows.sort(key=lambda r: (-r["score"], r["category"], r["subcategory"], r["path"]))
    evidence_csv = write_csv(rows, args.out, "evidence.csv")
    summary_csv = write_summary(rows, args.out)
    report_html = write_html(rows, args.out)

    print(f"Wrote:\n  {evidence_csv}\n  {summary_csv}\n  {report_html}")

if __name__ == "__main__":
    main()

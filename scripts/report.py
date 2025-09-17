import csv
import os
import html
from collections import defaultdict

def write_csv(rows, outdir, name):
    path = os.path.join(outdir, name)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return path

def write_summary(rows, outdir):
    counts = defaultdict(int)
    for r in rows:
        counts[(r["source"], r["category"], r["subcategory"])] += 1
    sum_rows = [
        {"source": s, "category": c, "subcategory": sc, "count": n}
        for (s, c, sc), n in sorted(counts.items())
    ]
    return write_csv(sum_rows, outdir, "summary.csv")

def _esc(x):
    return html.escape(str(x or ""))

def write_html(rows, outdir):
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["source"], r["category"], r["subcategory"])] += [r]

    sections = []
    for (src, cat, sub), items in sorted(grouped.items()):
        items_sorted = sorted(items, key=lambda i: (-i["score"], i["display"]))[:100]
        lis_parts = []
        for i in items_sorted:
            meta = i.get("meta", "")
            meta_html = f'<br><span class="meta">{_esc(meta)}</span>' if meta else ""
            li = (
                "<li>"
                f"<strong>{_esc(os.path.basename(i['display']))}</strong>"
                f" — score {i['score']} "
                f"<br><code title=\"{_esc(i['display'])}\">{_esc(i['path'])}</code>"
                f"{meta_html}"
                "</li>"
            )
            lis_parts.append(li)
        lis_html = "\n".join(lis_parts)
        sections.append(
            f"<h2>{_esc(src)} ▸ { _esc(cat)} ▸ { _esc(sub)} ({len(items)})</h2><ul>{lis_html}</ul>"
        )

    html_doc = (
        "<!doctype html>"
        "<html><head><meta charset='utf-8'><title>Academic Evidence Report</title>"
        "<style>"
        " body{font-family:system-ui,Segoe UI,Arial;margin:24px;}"
        " h1{margin-bottom:8px}"
        " h2{margin-top:24px;border-bottom:1px solid #ddd;padding-bottom:4px}"
        " code{background:#f6f8fa;padding:2px 4px;border-radius:4px}"
        " li{margin:6px 0}"
        " .note{color:#555}"
        " .meta{color:#666;font-size:0.9em}"
        "</style></head><body>"
        "<h1>Academic Evidence Report</h1>"
        "<p class='note'>Generated locally. Grouped by Source ▸ Category ▸ Subcategory (top 100 shown per group).</p>"
        f"{''.join(sections)}"
        "</body></html>"
    )

    path = os.path.join(outdir, "report.html")
    with open(path, "w") as f:
        f.write(html_doc)
    return path

import csv, os, html
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
    sum_rows = [{"source": s, "category": c, "subcategory": sc, "count": n}
                for (s,c,sc), n in sorted(counts.items())]
    return write_csv(sum_rows, outdir, "summary.csv")

def write_html(rows, outdir):
    by_src_cat = defaultdict(list)
    for r in rows:
        by_src_cat[(r["source"], r["category"], r["subcategory"])].append(r)

    def esc(s): return html.escape(str(s or ""))

    groups = []
    for (src, cat, sub), items in sorted(by_src_cat.items()):
        lis = "\n".join(
            f'<li><strong>{esc(os.path.basename(i["display"]))}</strong>'
            f' — score {i["score"]} <br><code title="{esc(i["display"])}">{esc(i["path"])}</code>'
            f'{f"<br><span class=\\"meta\\">{esc(i.get("meta",""))}</span>" if i.get("meta") else ""}'
            f'</li>'
            for i in sorted(items, key=lambda x: -x["score"])[:100]
        )
        groups.append(f"<h2>{esc(src)} ▸ {esc(cat)} ▸ {esc(sub)} ({len(items)})</h2><ul>{lis}</ul>")

    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Academic Evidence Report</title>
<style>
 body{{font-family:system-ui,Segoe UI,Arial;margin:24px;}}
 h1{{margin-bottom:8px}}
 h2{{margin-top:24px;border-bottom:1px solid #ddd;padding-bottom:4px}}
 code{{background:#f6f8fa;padding:2px 4px;border-radius:4px}}
 li{{margin:6px 0}}
 .note{{color:#555}}
 .meta{{color:#666;font-size:0.9em}}
</style></head>
<body>
<h1>Academic Evidence Report</h1>
<p class="note">Generated locally. Grouped by Source ▸ Category ▸ Subcategory (top 100 shown per group).</p>
{''.join(groups)}
</body></html>"""
    path = os.path.join(outdir, "report.html")
    with open(path, "w") as f:
        f.write(html_doc)
    return path

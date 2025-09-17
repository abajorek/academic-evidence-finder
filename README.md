# Academic Evidence Finder

Scan your computer for artifacts that support **Teaching, Service, Scholarship**.

## What it does
- Recursively scans folders you choose.
- Extracts text from PDF, DOCX, PPTX, and TXT.
- Matches against customizable keyword/regex rules in `config/rules.yml`.
- Outputs:
  - `evidence.csv` (one row per file hit)
  - `summary.csv` (counts per category/subcategory)
  - `report.html` (quick visual dashboard with links)

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# edit examples/include_dirs.txt to point at your folders
python scripts/scan.py --include-file examples/include_dirs.txt --out out

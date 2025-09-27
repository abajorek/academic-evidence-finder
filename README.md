# Academic Evidence Finder

Scan your computer for artifacts that support **Teaching, Service, Scholarship**.

## What it does
- Recursively scans folders you choose
- Extracts text from PDF, DOCX, PPTX, TXT, and music notation files
- Matches against customizable keyword/regex rules in `config/rules.yml`
- Supports music files (Finale, Sibelius) and drill design files (Pyware)
- Provides both a modern desktop application and command-line workflows

## Outputs
- `evidence.csv` (one row per file hit)
- `summary.csv` (counts per category/subcategory)
- `report.html` (quick visual dashboard with links)
- `pass1_categorized.json` (metadata-only analysis results)

## Quick Setup

### Desktop application
```bash
./setup_app.sh              # Creates .venv and installs dependencies
python3 scripts/evidence_finder_app.py
```

Want the optional retro sound effects? Re-run setup with the `--with-sound`
flag to install `pygame` and `numpy` from `requirements-optional.txt`:

```bash
./setup_app.sh --with-sound
```

### Command line
```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/scan.py --include ~/Documents --out results
```

## Features

### 🖥️ Desktop application
- **Contemporary interface** with clear typography and accessible controls
- **Year-based filtering** (2021-2025)
- **Multiple scan modes**: Quick metadata, full text extraction, or complete scan
- **Real-time progress log** with timestamps and status updates
- **Start/stop controls** with safe termination of running scans

### ⚡ Optimized Two-Pass Scanner
- **Pass 1**: Lightning-fast metadata-only categorization
- **Pass 2**: Detailed text extraction on selected categories only
- **Smart filtering** to avoid processing irrelevant files
- **Performance gains** of 10-100x for initial categorization

### 🎵 Music & Creative Work Support
- **Finale files** (.mus, .musx, .ftm, .ftmx)
- **Sibelius files** (.sib)
- **Pyware drill design** (.3dj, .3dz, .3da, .prod)
- **MusicXML** (.musicxml, .mxl)
- **Enhanced scoring** for creative scholarship
- **Filename analysis** for proprietary formats

## Usage Examples

### Desktop application
```bash
# Setup and launch the GUI
./setup_app.sh               # or `bash setup_app.sh` on macOS
python3 scripts/evidence_finder_app.py

# Inside the app:
# 1. Select scan mode (Pass 1, Pass 2, or Full)
# 2. Choose target years (2021-2025)
# 3. Add directories to scan
# 4. Start the scan and monitor status updates
```

### Build a macOS App Bundle

Need a self-contained app for macOS that includes the GUI, scan scripts, and configuration? Use the PyInstaller setup that lives in `packaging/macos/`.

```bash
# Run this on macOS – it creates a dedicated build virtualenv
scripts/build_app_macos.sh

# After the build completes
open dist/EvidenceFinder.app   # Launch the bundled GUI
```

The bundle includes all supporting scan scripts, configuration, and assets. When you launch the packaged app, results are written to `~/AcademicEvidenceFinder/results` so reports persist outside the temporary app bundle.

### Two-Pass Command Line
```bash
# Quick metadata-only scan
python3 scripts/scan_optimized.py --pass1-only --include ~/Documents --out results

# Review results, then run detailed analysis on specific categories
python3 scripts/scan_optimized.py --categories scholarship teaching --include ~/Documents --out results

# Or do both passes at once
python3 scripts/scan_optimized.py --include ~/Documents --out results
```

### Traditional Single-Pass Scanner
```bash
# Basic scan
python3 scripts/scan.py --include ~/Documents --out results

# With date filtering
python3 scripts/scan.py --include ~/Documents --modified-since 2024-01-01 --out results
```

### Spotlight Integration (macOS)
```bash
# Use macOS Spotlight to build file list first (much faster)
bash scripts/build_paths.sh  # Creates /tmp/paths.txt on macOS
python3 scripts/scan.py --path-list /tmp/paths.txt --out results
```

## Configuration

### File Types
The scanner recognizes these file types:

**Documents**: PDF, DOCX, PPTX, TXT, DOC, RTF, ODT, Pages, Key, ODP
**Spreadsheets**: XLSX, XLS, CSV, ODS, Numbers
**Music Notation**: MUS, MUSX, SIB, FTM, FTMX, MusicXML, MXL
**Drill Design**: 3DJ, 3DZ, 3DA, PROD (Pyware files)
**Web/Markup**: HTML, HTM, XML, MD, TEX

### Rules Configuration
Edit `config/rules.yml` to customize:
- **Categories** (Teaching, Service, Scholarship)
- **Keyword patterns** (regex supported)
- **File extension weights**
- **Bonus scoring** for important terms
- **Excluded directories**

### Example Rules
```yaml
categories:
  Teaching:
    Syllabi:
      any:
        - "\\bsyllabus\\b"
        - "\\boffice hours\\b"
        - "\\bgrading policy\\b"

  Scholarship:
    Musical_Compositions:
      any:
        - "original composition"
        - "commissioned piece"
        - "world premiere"
```

## Advanced Features

### Effort Analysis
The scanner can estimate time investment in creative files:
- Analyzes file modification patterns
- Detects work sessions and iterations
- Provides effort metrics for portfolios
- Supports tenure/promotion documentation

### Email and Calendar Integration
```bash
# Scan exported email (.mbox files)
python3 scripts/scan.py --mbox ~/Downloads/Inbox.mbox --out results

# Scan calendar exports (.ics files)
python3 scripts/scan.py --ics ~/Downloads/calendar.ics --out results
```

## Output Files

### evidence.csv
Individual file matches with scores and metadata:
```csv
source,path,category,subcategory,hits,score,when
files,/Users/me/Documents/syllabus.pdf,Teaching,Syllabi,3,5,2024-08-15
```

### summary.csv
Aggregate counts by category:
```csv
source,category,subcategory,count
files,Teaching,Syllabi,12
files,Scholarship,Musical_Compositions,8
```

### report.html
Interactive dashboard with:
- Clickable file links
- Organized by category/subcategory
- Score-based ranking
- Metadata display

## Performance Tips

1. **Use two-pass scanning** for large file collections
2. **Filter by date** to focus on recent work
3. **Use Spotlight integration** on macOS for faster file discovery
4. **Exclude unnecessary directories** in rules.yml
5. **Run Pass 1 first** to identify relevant files

## System Requirements

- Python 3.8+ (use the system `python3` on macOS or install the latest from python.org/Homebrew)
- macOS, Linux, or Windows
- For large scans: 4GB+ RAM recommended

## Troubleshooting

### Desktop application will not start
```bash
# Ensure dependencies are installed
./setup_app.sh

# Run from the project root
python3 scripts/evidence_finder_app.py
```

### No files found
- Check directory paths exist
- Verify file extensions in rules.yml
- Try broader date ranges
- Check `exclude_dirs` settings

### Slow performance
- Use `--pass1-only` for a quick survey
- Add `--max-bytes` to skip huge files
- Filter by `--modified-since` date
- Use Spotlight on macOS: `./scripts/build_paths.sh`

---

Ready to find some academic evidence? Launch the desktop app or explore the command-line utilities for batch workflows.

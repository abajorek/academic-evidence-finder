# Academic Evidence Finder

Scan your computer for artifacts that support **Teaching, Service, Scholarship**.

*"It's like a metal detector, but for academic stuff instead of bottle caps."* - The Cheat (probably)

## What it does
- Recursively scans folders you choose
- Extracts text from PDF, DOCX, PPTX, TXT, and music notation files
- Matches against customizable keyword/regex rules in `config/rules.yml`
- Supports music files (Finale, Sibelius) and drill design files (Pyware)
- Features both GUI and command-line interfaces
- Includes Edgar - a retro 80s-style GUI with authentic computer sounds

## Outputs
- `evidence.csv` (one row per file hit)
- `summary.csv` (counts per category/subcategory)
- `report.html` (quick visual dashboard with links)
- `pass1_categorized.json` (metadata-only analysis results)

## Quick Setup

### Edgar GUI (The Fun Way)
```bash
./setup_edgar.sh              # One-command setup (macOS: run with `bash setup_edgar.sh` if needed)
python3 scripts/edgar_gui.py  # Launch the retro GUI with the system Python 3
```

### Command Line (The Serious Way)
```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/scan.py --include ~/Documents --out results
```

## Features

### 🎮 Edgar GUI
- **Retro 80s interface** with green-on-black terminal styling
- **Authentic computer sounds** (because nostalgia)
- **Year-based filtering** (2021-2025)
- **Multiple scan modes**: Quick metadata, full text extraction, or complete scan
- **Real-time progress** with snarky commentary
- **Point-and-click simplicity** for the command-line-averse

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

### Edgar GUI
```bash
# Setup and launch Edgar
./setup_edgar.sh               # or `bash setup_edgar.sh` on macOS
python3 scripts/edgar_gui.py

# Then use the GUI to:
# 1. Select scan mode (Pass 1, Pass 2, or Full)
# 2. Choose target years (2021-2025)
# 3. Add directories to scan
# 4. Hit the big green button
# 5. Enjoy authentic 80s computer sounds
```

### Build a macOS App Bundle

Need a self-contained app for macOS that includes the GUI, scan scripts, and retro sound effects? Use the PyInstaller setup that lives in `packaging/macos/`.

```bash
# Run this on macOS – it creates a dedicated build virtualenv
scripts/build_edgar_macos.sh

# After the build completes
open dist/Edgar.app            # Launch the bundled GUI
```

The bundle includes all of the supporting scan scripts, configuration, and pygame assets. When you launch the packaged app, Edgar writes results to `~/EdgarEvidence/results` so the reports stick around outside the temporary app bundle.

For debugging or scripted runs you can ask the launcher to execute a bundled scanner directly:

```bash
python3 scripts/edgar_gui.py --run-embedded scan.py --help
```

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

# With Edgar mode (for authentic 80s scanning experience)
python3 scripts/scan.py --include ~/Documents --edgar --out results
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

### Edgar Mode
Add `--edgar` to any command-line scan for:
- Animated progress indicators
- Retro terminal styling
- Optional sound effects
- 80s virus scanner aesthetic

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
- For Edgar GUI: pygame for authentic sounds
- For large scans: 4GB+ RAM recommended

## Troubleshooting

### Edgar GUI Won't Start
```bash
# Install pygame for sounds
python3 -m pip install pygame

# Run without sounds if needed
python3 scripts/edgar_gui.py  # Audio will auto-disable if pygame unavailable
```

### No Files Found
- Check directory paths exist
- Verify file extensions in rules.yml
- Try broader date ranges
- Check exclude_dirs settings

### Slow Performance
- Use `--pass1-only` for quick survey
- Add `--max-bytes` to skip huge files
- Filter by `--modified-since` date
- Use Spotlight on macOS: `./scripts/build_paths.sh`

---

*"This tool is like, way more useful than it has any right to be."* - Strong Bad

Ready to find some academic evidence? Choose your weapon:
- 🎮 **Edgar GUI**: `python3 scripts/edgar_gui.py`
- ⚡ **Optimized**: `python3 scripts/scan_optimized.py --help`
- 🖥️ **Classic**: `python3 scripts/scan.py --help`



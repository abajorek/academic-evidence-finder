#!/bin/bash
# Setup script for the Academic Evidence Finder application.

set -euo pipefail

echo "Preparing Academic Evidence Finder..."

if [[ ! -f "requirements.txt" ]]; then
    echo "This script must be run from the project root." >&2
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo "Marking primary scripts as executable..."
chmod +x scripts/evidence_finder_app.py scripts/scan.py scripts/scan_optimized.py

mkdir -p out results

echo "\nSetup complete."
echo "Launch the desktop app with:"
echo "  python3 scripts/evidence_finder_app.py"
echo ""
echo "Command-line scanners remain available:"
echo "  python3 scripts/scan.py --help"
echo "  python3 scripts/scan_optimized.py --help"

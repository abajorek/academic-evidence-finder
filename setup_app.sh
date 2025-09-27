#!/bin/bash
# Setup script for the Academic Evidence Finder application.

set -euo pipefail

install_sound_extras=false

while (( "$#" )); do
    case "$1" in
        --with-sound)
            install_sound_extras=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--with-sound]"
            echo
            echo "  --with-sound   Install optional pygame/numpy dependencies for sound effects"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--with-sound]" >&2
            exit 1
            ;;
    esac
done

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

if [[ "$install_sound_extras" == true ]]; then
    if [[ -f "requirements-optional.txt" ]]; then
        echo "Installing optional sound dependencies..."
        pip install -r requirements-optional.txt
    else
        echo "requirements-optional.txt not found; skipping optional installs." >&2
    fi
else
    echo "Skipping optional pygame/numpy dependencies. Use --with-sound to include them."
fi

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

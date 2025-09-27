#!/usr/bin/env bash
set -euo pipefail

if [[ "${OSTYPE:-}" != darwin* ]]; then
  echo "[app-build] This script must be run on macOS." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.app-build-venv"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip wheel
pip install -r "${PROJECT_ROOT}/requirements.txt" pyinstaller

pyinstaller --clean --noconfirm "${PROJECT_ROOT}/packaging/macos/evidence_finder_app.spec"

echo "\n[app-build] Build complete!"
echo "[app-build] The macOS app is located at: ${PROJECT_ROOT}/dist/EvidenceFinder.app"
echo "[app-build] You can move EvidenceFinder.app into /Applications for easy access."

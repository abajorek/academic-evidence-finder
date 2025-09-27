#!/usr/bin/env bash
set -euo pipefail

if [[ "${OSTYPE:-}" != darwin* ]]; then
  echo "[edgar-build] This script must be run on macOS." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.edgar-build-venv"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[edgar-build] Creating dedicated virtualenv at ${VENV_DIR}" >&2
  python3 -m venv "${VENV_DIR}"
else
  echo "[edgar-build] Reusing existing virtualenv at ${VENV_DIR}" >&2
fi

source "${VENV_DIR}/bin/activate"
trap 'deactivate >/dev/null 2>&1 || true' EXIT

export PIP_NO_INPUT=1
export PIP_PREFER_BINARY=1
export PIP_PROGRESS_BAR=on

python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: "lxml==5.2.2" "pygame==2.6.1" "numpy>=1.21.0"
python -m pip install -r "${PROJECT_ROOT}/requirements.txt"
python -m pip install pyinstaller

echo "[edgar-build] Running PyInstaller..." >&2
pyinstaller --clean --noconfirm "${PROJECT_ROOT}/packaging/macos/edgar_gui.spec"

echo "\n[edgar-build] Build complete!"
echo "[edgar-build] The macOS app is located at: ${PROJECT_ROOT}/dist/Edgar.app"
echo "[edgar-build] You can move Edgar.app into /Applications for easy access."

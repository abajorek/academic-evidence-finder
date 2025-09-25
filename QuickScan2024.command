#!/bin/zsh
set -euo pipefail

# Always run from the repo root (where scripts/ lives)
cd "$(dirname "$0")"

# Ensure venv
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Sanity: pip toolchain
python -m ensurepip || true
python -m pip install --upgrade pip setuptools wheel pyyaml >/dev/null

# Pull extensions from rules.yml (exactly what your tool supports)
EXTS=$(python - <<'PY'
import yaml
cfg = yaml.safe_load(open('config/rules.yml'))
exts = cfg['file_filters']['include_extensions']
print(",".join(sorted(set(exts))))
PY
)

# Build candidate file list with Spotlight
TMP_HOME=/tmp/aef_paths_home.txt
TMP_VOLS=/tmp/aef_paths_vols.txt
OUTLIST=/tmp/aef_paths.txt

if (( $# > 0 )); then
  # User dragged folders/files onto the .command
  : > "$OUTLIST"
  for P in "$@"; do
    if [[ -d "$P" ]]; then
      mdfind -onlyin "$P" 'kMDItemContentTypeTree == "public.data" && kMDItemFSSize <= 50000000' >> "$OUTLIST" || true
    elif [[ -f "$P" ]]; then
      echo "$P" >> "$OUTLIST"
    fi
  done
else
  # Default: scan Home and external volumes (skip obvious system roots)
  mdfind -onlyin "$HOME"  'kMDItemContentTypeTree == "public.data" && kMDItemFSSize <= 50000000' >  "$TMP_HOME" || true
  mdfind -onlyin /Volumes 'kMDItemContentTypeTree == "public.data" && kMDItemFSSize <= 50000000' >  "$TMP_VOLS" || true
  cat "$TMP_HOME" "$TMP_VOLS" | egrep -v '^/System/|^/Applications/|^/Library/|^/private/|^/opt/' | sort -u > "$OUTLIST" || true
fi

# Optional: include any exported MBOXes at ~/MailExports/*.mbox (zsh nullglob)
setopt NULL_GLOB
MBOX_GLOB=($HOME/MailExports/*.mbox)
unsetopt NULL_GLOB
MBOXLIST=/tmp/aef_mboxes.txt
: > "$MBOXLIST"
if (( ${#MBOX_GLOB} )); then
  printf "%s\n" "${MBOX_GLOB[@]}" >> "$MBOXLIST"
fi

# Scan 2024 only
YEAR_START=2024-01-01
YEAR_END=2024-12-31
mkdir -p out
python scripts/scan.py \
  --path-list "$OUTLIST" \
  ${$( [[ -s "$MBOXLIST" ]] && echo --mbox-file "$MBOXLIST" )} \
  --out out \
  --only-ext "$EXTS" \
  --modified-since "$YEAR_START" \
  --modified-until "$YEAR_END" \
  --max-bytes 50000000 \
  --edgar --edgar-interval 0.2

# Open report
if [[ -f out/report.html ]]; then
  open out/report.html
else
  echo "Scan finished, but no report.html found. See out/progress.json"
fi

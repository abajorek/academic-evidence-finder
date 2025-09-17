#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/paths.txt
: > "$OUT"

# Search roots: home + CloudStorage (Drive/OneDrive) + external volumes
ROOTS=(-onlyin /Users)
[ -d "$HOME/Library/CloudStorage" ] && ROOTS+=(-onlyin "$HOME/Library/CloudStorage")
[ -d /Volumes ] && ROOTS+=(-onlyin /Volumes)

# Date window
FROM='2024-01-01T00:00:00Z'
TO='2025-09-15T23:59:59Z'

# Extensions (docs + notation + MusicXML + Pyware)
exts=(pdf docx pptx txt doc rtf odt pages key odp xlsx xls csv ods numbers md tex html htm xml \
      sib musx mus ftmx ftm musicxml mxl 3dj 3dz 3da prod)

for ext in "${exts[@]}"; do
  mdfind "${ROOTS[@]}" \
    'kMDItemFSContentChangeDate >= $time.iso('"$FROM"') &&
     kMDItemFSContentChangeDate <= $time.iso('"$TO"') &&
     kMDItemFSName == "*.'"$ext"'"c' >> "$OUT"
done

sort -u "$OUT" -o "$OUT"
echo "Wrote $(wc -l < "$OUT") paths to $OUT"

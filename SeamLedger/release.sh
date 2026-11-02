#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="接缝不在奇点_量子力学与广义相对论的三十道裂缝"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-seamledger.pdf"
cp "$SRC.html" "$OUT/seamledger.html"
cp "$SRC.md"   "$OUT/seamledger.md"
cp README.md   "$OUT/README.md"
cp seams.csv   "$OUT/seams.csv" 2>/dev/null || true
cp assets/figures/fig*.png "$OUT/" 2>/dev/null || true
cp interactive/seams.html "$OUT/explorer.html" 2>/dev/null || true
{
  echo "接缝不在奇点：量子力学与广义相对论的三十道裂缝 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

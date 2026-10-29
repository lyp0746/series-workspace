#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="同构的强度_对偶与泛性质与不变量与四十条断裂探针"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-isomorphismstrength.pdf"
cp "$SRC.html" "$OUT/isomorphismstrength.html"
cp "$SRC.md"   "$OUT/isomorphismstrength.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp motifs.csv  "$OUT/" 2>/dev/null || true
cp interactive/motifs.html "$OUT/explorer.html" 2>/dev/null || true
{
  echo "同构的强度：对偶、泛性质、不变量与四十条断裂探针 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

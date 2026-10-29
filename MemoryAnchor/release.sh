#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="记忆的锚点_情景唤起与异构重建与日志裁决"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-memoryanchor.pdf"
cp "$SRC.html" "$OUT/memoryanchor.html"
cp "$SRC.md"   "$OUT/memoryanchor.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp schemes.csv "$OUT/" 2>/dev/null || true
cp interactive/schemes.html "$OUT/explorer.html" 2>/dev/null || true
{
  echo "记忆的锚点：情景唤起、异构重建与日志裁决 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

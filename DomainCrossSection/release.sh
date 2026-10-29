#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="领域的剖面_四个问题与二十个领域的审计"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-domaincrosssection.pdf"
cp "$SRC.html" "$OUT/domaincrosssection.html"
cp "$SRC.md"   "$OUT/domaincrosssection.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp domains.csv "$OUT/" 2>/dev/null || true
cp interactive/domains.html "$OUT/explorer.html" 2>/dev/null || true
{
  echo "领域的剖面：四个问题、二十个领域与八十字段的审计 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

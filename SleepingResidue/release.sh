#!/usr/bin/env bash
# 组装 release/：只放读者面文件（PDF/HTML/Markdown/图/交互页/README）。
set -euo pipefail
cd "$(dirname "$0")"
SRC="线外的残余_延迟承认的三种机制"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-sleeping-residue.pdf"
cp "$SRC.html" "$OUT/sleeping-residue.html"
cp "$SRC.md"   "$OUT/sleeping-residue.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp cases.csv   "$OUT/cases.csv" 2>/dev/null || true
{
  echo "线外的残余 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do
    [ -f "$f" ] && printf "%-46s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

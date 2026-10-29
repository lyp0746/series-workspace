#!/usr/bin/env bash
# 组装 release/：扁平、ASCII 文件名（与 Zenodo 记录一致）
set -euo pipefail
cd "$(dirname "$0")"
STEM="明清湘中驿道体系_GEPF三层分析"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$STEM.pdf"  "$OUT/00-hunan-relay-system-paper.pdf"
cp "$STEM.html" "$OUT/hunan-relay-system-paper.html"
cp "$STEM.md"   "$OUT/hunan-relay-system-paper.md"
cp README.md    "$OUT/README.md"
cp stations.csv "$OUT/stations.csv"
cp assets/charts/fig08.png "$OUT/fig08.png"
cp assets/charts/fig09.png "$OUT/fig09.png"
cp interactive/hunan-explorer.html "$OUT/hunan-explorer.html"
cp fig0*.png    "$OUT/" 2>/dev/null || true
{
  echo "明清湘中驿道 GEPF — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-44s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成（$(ls "$OUT" | wc -l) 个文件）"; ls -1 "$OUT"

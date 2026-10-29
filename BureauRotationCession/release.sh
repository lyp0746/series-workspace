#!/usr/bin/env bash
# 组装 release/：扁平结构，文件名 ASCII，便于 Zenodo / DOI 稳定引用
# 参考记录：zenodo.org/records/23480796（湖南驿道）
set -euo pipefail
cd "$(dirname "$0")"

STEM="轮换的让渡_中国官制三千年"
OUT="release"
rm -rf "$OUT"
mkdir -p "$OUT"

cp "$STEM.pdf"  "$OUT/00-bureau-rotation-cession-paper.pdf"
cp "$STEM.html" "$OUT/bureau-rotation-cession-paper.html"
cp "$STEM.md"   "$OUT/bureau-rotation-cession-paper.md"
cp README.md    "$OUT/README.md"
cp cases.csv    "$OUT/cases.csv"
cp data/control_tangsong.csv "$OUT/control_tangsong.csv"
cp data/rupture_events.csv   "$OUT/rupture_events.csv"
cp data/event_leadlag.csv    "$OUT/event_leadlag.csv"
cp interactive/control-explorer.html "$OUT/control-explorer.html"
cp fig??.png    "$OUT/"

{
  echo "轮换的让渡 / The Rotation of Concessions — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do
    [ -f "$f" ] && printf "%-46s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
} > "$OUT/MANIFEST.txt"

echo "release/ 已生成（$(ls "$OUT" | wc -l) 个文件）"
ls -1 "$OUT"

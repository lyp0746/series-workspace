#!/usr/bin/env bash
# 组装 release/：扁平结构，文件名 ASCII，便于 Zenodo / DOI 稳定引用
set -eu
cd "$(dirname "$0")"

SRC="谁在切时间轴_六十部世界史分期与一份自证方案"
OUT="release"

rm -rf "$OUT"
mkdir -p "$OUT"

cp "$SRC.pdf"  "$OUT/00-who-cuts-the-timeline.pdf"
cp "$SRC.html" "$OUT/who-cuts-the-timeline.html"
cp "$SRC.md"   "$OUT/who-cuts-the-timeline.md"
cp README.md   "$OUT/README.md"
cp interactive/periodization-explorer.html "$OUT/periodization-explorer.html"
cp fig??.png   "$OUT/"
cp data/schemes.csv "$OUT/schemes.csv"

{
  echo "门的数目 / The Number of Gates — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do
    [ -f "$f" ] && printf "%-46s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
} > "$OUT/MANIFEST.txt"

echo "release/ 已生成（$(ls "$OUT" | wc -l) 个文件）"
ls -1 "$OUT"

#!/usr/bin/env bash
# 组装 release/：只放读者面文件（PDF/HTML/Markdown/图/交互页/README）。
# 原始数据（csv/py/json）与脚本留在仓库，不进发布包。
set -euo pipefail
cd "$(dirname "$0")"
SRC="术语的账单_从芯片到Agent的八十个计算机概念"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-term-bills-paper.pdf"
cp "$SRC.html" "$OUT/term-bills-paper.html"
cp "$SRC.md"   "$OUT/term-bills-paper.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp data/concepts.csv "$OUT/concepts.csv"
cp interactive/term-explorer.html "$OUT/term-explorer.html" 2>/dev/null || true
{
  echo "术语的账单 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do
    [ -f "$f" ] && printf "%-46s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

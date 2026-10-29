#!/usr/bin/env bash
# 组装 release/：只放读者面文件（PDF/HTML/Markdown/图/交互页/README）。
# 原始数据（csv/py/json）与脚本留在仓库，不进发布包。
set -euo pipefail
cd "$(dirname "$0")"
SRC="被点燃的生态_两个社区与三个标记"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-harness-ecology.pdf"
cp "$SRC.html" "$OUT/harness-ecology.html"
cp "$SRC.md"   "$OUT/harness-ecology.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp interactive/harness-explorer.html "$OUT/harness-explorer.html" 2>/dev/null || true
{
  echo "被点燃的生态 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do
    [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

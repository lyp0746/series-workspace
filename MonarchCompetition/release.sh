#!/usr/bin/env bash
# 组装发布包（只放读者面文件；编码库与原始快照留在仓库）
set -eu
cd "$(dirname "$0")"
SRC="开明君主与两层竞争_执行方向与代价承担者"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-monarchcompetition.pdf"
cp "$SRC.html" "$OUT/monarchcompetition.html"
cp "$SRC.md"   "$OUT/monarchcompetition.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
{
  echo "开明君主与两层竞争：agent 价目表上的执行、方向与代价承担者 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "数据快照: 2026-10-26/27（价目、端点、许可证、平台周报）"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-56s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

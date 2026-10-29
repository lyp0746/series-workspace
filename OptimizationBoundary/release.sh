#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="优化的边界_四前提与越界的二十个案例"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-optimizationboundary.pdf"
cp "$SRC.html" "$OUT/optimizationboundary.html"
cp "$SRC.md"   "$OUT/optimizationboundary.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp ledger.csv cases.csv "$OUT/" 2>/dev/null || true
{
  echo "优化的边界：目标函数、搜索空间与六核心的停止规则 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="容量的三个代理_分期槽位与编码槽位与标签槽位"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-capacityproxies.pdf"
cp "$SRC.html" "$OUT/capacityproxies.html"
cp "$SRC.md"   "$OUT/capacityproxies.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp ledger.csv cases.csv "$OUT/" 2>/dev/null || true
{
  echo "容量的三个代理：分期槽位、编码槽位与标签槽位 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
SRC="六张账单的对账_六核心的可测代理与尺度边界"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-ledgerreconciliation.pdf"
cp "$SRC.html" "$OUT/ledgerreconciliation.html"
cp "$SRC.md"   "$OUT/ledgerreconciliation.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp ledger.csv cases.csv "$OUT/" 2>/dev/null || true
{
  echo "六张账单的对账：六核心的可测代理、失败模式与尺度边界 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="锚点的下限_情景记忆的模拟对照实验"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-anchorfloor.pdf"
cp "$SRC.html" "$OUT/anchorfloor.html"
cp "$SRC.md"   "$OUT/anchorfloor.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp results/summary.csv results/coverage.csv results/thresholds.csv results/drift.csv "$OUT/" 2>/dev/null || true
cp data/experiment.py "$OUT/experiment.py" 2>/dev/null || true
cp interactive/steps.html "$OUT/explorer.html" 2>/dev/null || true
{
  echo "锚点的下限：情景记忆的模拟对照实验 — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

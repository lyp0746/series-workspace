#!/usr/bin/env bash
# 组装 release/：四种格式 + README + MANIFEST（扁平名，ASCII 安全）
set -eu
cd "$(dirname "$0")"
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
OUT="release"
mkdir -p "$OUT"

"$PY" build_collection23.py
"$PY" make_md.py
cp _build-print.html "$OUT/02-合集.html"
cp README.md "$OUT/README.md"
"$PY" - "$OUT" <<'PYZIP'
import os, sys, zipfile
out = sys.argv[1]
with zipfile.ZipFile(os.path.join(out, "04-assets.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for r, _, fs in os.walk(os.path.join(out, "assets")):
        for f in fs:
            p = os.path.join(r, f)
            z.write(p, os.path.relpath(p, out))
PYZIP

{
  echo "有限系统的取舍 — 合集 manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "条目: 九本书 + 十四篇工作论文，附卷首一篇"
  echo
  for f in "$OUT"/*.pdf "$OUT"/*.html "$OUT"/*.md; do
    [ -f "$f" ] && printf "%-36s %8s\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
  echo "assets/$(ls "$OUT/assets" | wc -l) 个子目录"
} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"

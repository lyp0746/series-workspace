# -*- coding: utf-8 -*-
"""为一篇新论文生成标准外围文件（README/CITATION/.zenodo.json/release.sh/versions/清单）。"""
import json, pathlib, sys
repo = pathlib.Path(sys.argv[1]); title = sys.argv[2]; sub = sys.argv[3]; sub_en = sys.argv[4]
pages = sys.argv[5]; main = sys.argv[6]; abstract = sys.argv[7]
series = [("10.5281/zenodo.23286403","错位的时间"),("10.5281/zenodo.23323277","遗忘的边界"),
 ("10.5281/zenodo.23412033","区分的语言"),("10.5281/zenodo.23388628","选择的代价"),
 ("10.5281/zenodo.23416220","诠释的权衡"),("10.5281/zenodo.23447311","涌现的临界"),
 ("10.5281/zenodo.23447341","只能选两样"),("10.5281/zenodo.23526582","热点的账单"),
 ("10.5281/zenodo.23601983","明清湘中驿道"),("10.5281/zenodo.23602311","轮换的让渡"),
 ("10.5281/zenodo.23602360","术语的账单"),("10.5281/zenodo.23602364","谁在切时间轴"),
 ("10.5281/zenodo.23603015","被点燃的生态"),("10.5281/zenodo.23603016","线外的残余")]
R = [(a) for a in [f"| 篇 | 标题 | 页 | DOI |"]]
readme = f"""# {title}

**{sub}**

李毅芃 · 2026-10-24 · 工作论文（{pages} 页，CC BY 4.0）

*{sub_en}*

---

## 一句话

{abstract.splitlines()[0]}

## 摘要

{abstract}

## 文件

| 文件 | 内容 |
|---|---|
| `{main}.pdf` | 排版稿（A4，{pages} 页） |
| `{main}.html` | 单文件网页版 |
| `source/paper.md` | 正文源（含表占位符） |
| `fig01`–`fig08` | 图，由 `analysis/make_figures.py` 生成 |
| `data/` | 数据模块与生成的表 |
| `ledger.csv` / `cases.csv` | 编码库（单一来源） |
| `versions/CHANGELOG.md` | 内部版本记录 |

## 复现

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" analysis/make_figures.py
"$PY" analysis/assemble.py
"$PY" generate_publication_suite.py
bash release.sh
```

## 致谢与关联

本篇与前六篇共用一套记账纪律；`related_identifiers` 指向系列入口与其余各篇。
"""
(repo/"README.md").write_text(readme, encoding="utf-8")

cff = f"""cff-version: 1.2.0
message: "If you cite this paper, please use the DOI below."
title: "{title}"
abstract: >-
  {abstract[:400]}
authors:
  - family-names: "李毅芃"
    given-names: "李毅芃"
date-released: 2026-10-24
license: CC-BY-4.0
type: article
"""
(repo/"CITATION.cff").write_text(cff, encoding="utf-8")

z = {"title": f"{title} / {sub_en}", "description": f"<p><b>中文摘要。</b>{abstract}</p>",
     "creators":[{"name":"李毅芃","affiliation":"独立研究者 / Independent Researcher"}],
     "keywords":["六核心","对账","证据分级","reconciliation","evidence grading"],
     "license":"CC-BY-4.0","upload_type":"publication","publication_type":"preprint",
     "language":"zho","access_right":"open","publication_date":"2026-10-24","version":"2026-10-24",
     "notes":"工作论文/预印本。 系列共 15 件；related_identifiers 已按裸 DOI 归一。",
     "related_identifiers":[{"identifier":"https://github.com/lyp0746/knowledge-tradeoffs","relation":"isPartOf","scheme":"url"}]
       + [{"identifier":d,"relation":"references","scheme":"doi"} for d,_ in series]}
(repo/".zenodo.json").write_text(json.dumps(z, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

(repo/"release.sh").write_text(f"""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SRC="{main}"
OUT="release"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$SRC.pdf"  "$OUT/00-{repo.name.lower()}.pdf"
cp "$SRC.html" "$OUT/{repo.name.lower()}.html"
cp "$SRC.md"   "$OUT/{repo.name.lower()}.md"
cp README.md   "$OUT/README.md"
cp fig*.png    "$OUT/" 2>/dev/null || true
cp ledger.csv cases.csv "$OUT/" 2>/dev/null || true
{{
  echo "{title} — release manifest"
  echo "生成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  for f in "$OUT"/*; do [ -f "$f" ] && printf "%-52s %s\\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"; done
}} > "$OUT/MANIFEST.txt"
echo "release/ 已生成"; ls -1 "$OUT"
""", encoding="utf-8")
(repo/".gitignore").write_text("release/\n_temp/\n__pycache__/\ndata/__pycache__/\nanalysis/__pycache__/\n*.pyc\n", encoding="utf-8")
(repo/"versions").mkdir(exist_ok=True)
(repo/"versions"/"CHANGELOG.md").write_text(f"# CHANGELOG（内部记录，不进发布包）\n\n## 2026-10-24　初稿（{pages} 页）\n\n- {sub}\n", encoding="utf-8")
print("scaffold ok:", repo.name)

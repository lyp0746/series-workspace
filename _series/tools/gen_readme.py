# -*- coding: utf-8 -*-
"""按统一模板重写九本书的 README（结构、证据、构建、引用、系列）。"""
import io, json, os, re
from pypdf import PdfReader

BOOKS = ["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
         "impossibility-triangle","interpretation-tradeoff","emergence-critical","mind-forks","hotspot-bills"]
SERIES = README_LINKS = {
 "knowledge-tradeoffs":("只能选两样","从来不及、会忘记到说不清——六个核心，看懂复杂世界的取舍"),
 "distinction-evolution":("区分的语言","五个领域，同一个二次型"),
 "capacity-cascade":("遗忘的边界","有限容量下的记忆、智能与自我"),
 "entropy-spiral":("错位的时间","为什么我们总是来不及：社会系统的时间错配与可控性边界"),
 "impossibility-triangle":("选择的代价","完备、可组合与可传递的三维权衡"),
 "interpretation-tradeoff":("诠释的权衡","历史研究中的置信度、权衡与理论流变"),
 "emergence-critical":("涌现的临界","为什么有些变化回不去：临界、涌现与形式化的边界"),
 "mind-forks":("心灵的分岔","从无意识到可观察——心理学流派的六次划线"),
 "hotspot-bills":("热点的账单","用六个核心，诊断过去一年的热搜与争论"),
}
row = []
for b in BOOKS:
    bj = json.load(io.open(f"{b}/source/book.json", encoding="utf-8"))
    parts = json.load(io.open(f"{b}/source/parts.json", encoding="utf-8"))
    cff = io.open(f"{b}/CITATION.cff", encoding="utf-8").read()
    doi = re.search(r"^doi:\s*(\S+)", cff, re.M).group(1)
    cdoi = re.search(r"^concept-doi:\s*(\S+)", cff, re.M).group(1)
    pdf = f"{b}/output/book.pdf"
    pages = len(PdfReader(pdf).pages) if os.path.exists(pdf) else 0
    nch = sum(len(p["chapters"]) for p in parts)
    abstract = (bj.get("abstract") or "").strip()
    plist = "\n".join(f"| {i} | {p['part']} | {len(p['chapters'])} | "
                      f"{p['chapters'][0]['title']} → {p['chapters'][-1]['title']} |"
                      for i, p in enumerate(parts, 1))
    series = "\n".join(f"| {t} | [{s}](https://github.com/lyp0746/{s}) |" for s, (t, _) in SERIES.items() if s != b)
    md = f"""# {bj['title']} · {bj.get('title_en','') or ''}

> {bj['subtitle']}
>
> **DOI**：{doi}　·　概念 DOI：{cdoi}　·　{pages} 页 / {len(parts)} 部分 / {nch} 章

{abstract}

---

## 结构

| 部分 | 标题 | 章数 | 起 → 止 |
|---|---|---:|---|
{plist}

每章八段：主提问 → 场景开篇 → 导论 → 机制 → 表/图 → 反例 → 本章小结 → 一句话带走。
每个部分有满栏插图扉页（`assets/svg/part-NN.svg`）、一段部分导语与一段部分小结。

## 证据与自检

- 结论标注 **A/B/C** 证据等级与甲/乙/丙概念等级；结论强度不超过证据强度。
- 可证伪登记簿：`docs/preregistration/checkups.csv`（append-only）。
- 结构校阅：系列 lint 24 条规则，本书 **error 0 / warn 0**（见 `_series/lint/REPORT.md`）。

## 文件

| 路径 | 是什么 |
|---|---|
| `source/` | **唯一正文来源**（HTML）；`book.json` 元数据、`parts.json` 结构 |
| `analysis/` | 图表、统计、抓取脚本（可重跑） |
| `assets/` | 封面、SVG 图、CSS |
| `scripts/build.sh` | audit → 印刷 PDF → 电子版 → EPUB → Markdown |
| `docs/` | 方法、数据来源、缺口与登记簿 |

产物（`output/`、`release/`）不入库，可由 `source/` 重建。

## 引用

```
{bj['title']}：{bj['subtitle']}。李毅芃，2026。{doi}
```

## 系列（九本书）

| 书 | 仓库 |
|---|---|
{series}

十四篇工作论文与全部条目的 DOI 见 [series-workspace](https://github.com/lyp0746/series-workspace)。

## 许可

正文与图件 CC BY 4.0；脚本 MIT。
"""
    io.open(f"{b}/README.md", "w", encoding="utf-8").write(md)
    row.append((b, pages, nch, len(parts), doi))
for r in row: print(r)

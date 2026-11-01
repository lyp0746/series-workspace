# 审阅工作区（2026-11）

取数与审阅报告；本轮修复由 `_series/tools/` 下的脚本执行（可重跑）。

| 文件 | 内容 |
|---|---|
| `REPORT-2026-11.md` | 总报告：全局诊断、四类体裁深审、知识网络、修单、§7/§8 修复与核对记录 |
| `ITEMS.md` | 23 件逐件报告（8 轴评分 + 结构/论证/叙事/视觉/网络/关怀 + 修单） |
| `OUTLINE.md` | 机器总表：结构、章节失衡、骨架缺项、附录、禁词、互引、六核心词频 |
| `data.json` | 同上，机器可读 |
| `audit_series.py` | 取数脚本（可重跑：`python _series/review/audit_series.py`） |
| `CITATION-AUDIT.md` | 文献抽样核对（36/468，OpenAlex/Crossref）：命中 26、版本存疑 5、未命中 5 |
| `evidence/` | 取数中间件与样张：未引用资产、图号、图注长度、论文节号、xref 矩阵、页面渲染 |

工具（均在 `_series/tools/`）：`audit_series.py` 已移到 `_series/review/`；另有
`make_explorers.py`（生成论文交互探索器）、`layout_probe.py`（孤行/题注分页体检）、
`audit_citations.py`（Tier-2 文献核对）、`citation_grounding.py`（引用/延伸分栏）、
`reduce_ruishi.py`（用词密度）。

纲领：`academic-book-pipeline/references/design-review-doctrine.md`（skill v1.8）。

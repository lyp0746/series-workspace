# AGENTS.md — 有限系统的取舍（系列级约定 v2）

> 本文件是**宪法**，不是编年史：只写"任何时候都成立"的规则。
> 版本流水、某轮改了什么，一律写 `_series/versions/CHANGELOG.md`（旧编年史见 `_series/versions/AGENTS-编年史-2026-10-28.md`）。
> 结构规范：`_series/spec/skeleton.md`（v2，已冻结）。**规范与本文冲突时，以规范为准。**
> 校阅账：`_series/lint/REPORT.md`（`python _series/lint/lint.py` 生成）。

---

## 1 这是什么

同一作者的独立研究系列：**九本书 + 十四篇工作论文 + 一部合集**，共用一个母题——
复杂系统如何保持结构、如何变化、如何生成新结构。

| 类 | 件 | 仓库根 |
|---|---|---|
| 书（学术 6 + 通俗 2 + 科普 1） | 9 | `knowledge-tradeoffs/` … `mind-forks/` |
| 论文（实证 6 + 方法 6 + 测试 2） | 14 | `BureauRotationCession/` … `MonarchCompetition/` |
| 合集 | 1 | `合集23/`（构建脚本 + release/） |
| 元数据单一来源 | — | `inventory.tsv`（件数、标题、DOI）、`zenodo_deposits.tsv` |
| 共享层 | — | `_series/`（规范、lint、工具、术语、版本） |

**件数只由 `inventory.tsv` 决定**，任何文档、封面、副标题都不许写死数字。

## 2 三种体裁与两套骨架

- **书**：5–7 部分 × 3–6 章（22–28 章）；每部分有导语（300–500 字）与小结（150–300 字）；
  每章八段（主提问框 → 场景开篇 → 导论 → 机制 → 表/图 → 反例 → 本章小结 → 一句话带走）。
- **论文**：12–16 节，一条结果一节；`实证档`另加"协议（预注册）"与"逐条裁决"两节。
- **附录**：书与论文都是 ≤6 件（A 形式化／B 数据与案例／C 协议与稳健性／D 登记簿／E 工具／F 增补），
  且 ≤正文 12%。**参考文献与术语表不占附录字母。**

范本：结构取 `mind-forks`（《心灵的分岔》）、学术装置取 `distinction-evolution`（《区分的语法》）、
内容密度取 `entropy-spiral`（《错位的时间》）。

## 3 十条纪律（不可违反）

1. `source/` 是唯一正文来源；`output/`、`release/` 是派生产物，**永不手改**。
2. **编号冻结**：已发布的章号、节号、附录字母，只在"重排窗口"内整体改；窗口外不许增量改号。
3. 一个序列一个词：`第N部分`／`第N章`／`N.M 节`／`表N.M`／`图N.M`／`附录A`。禁用"部"指章。
4. **附录准入**：一份材料配进附录，当且仅当**算得出来 / 查得到 / 可被否证**。其余进正文。
5. **可证伪登记簿 append-only**：只追加，不改旧行（`docs/preregistration/checkups.csv`、
   `LedgerReconciliation/ledger.csv`；lint 会比对哈希）。
6. 证据分级封顶结论：**结论强度 ≤ 证据强度**（A 官方可复现／B 稳定公开估计／C 稀疏·构造·思辨）。
7. 系列计数只有一个来源；正文指"写作时的前 N 件"必须写"**其时的 N 件**"。
8. 产物文件名**不带件数**（`00-合集-印刷版.pdf`）；一个产物一个 tag。
9. **已发布的 DOI 与资产名不改名、不覆盖**；修订只能发新版本（概念 DOI 不变，版本 DOI 变）。
10. 禁止词：必然／注定／不可避免／无法消除／死路。张力写清，宿命不写。

## 4 命令

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

"$PY" _series/lint/lint.py            # 全校阅：23 件 → _series/lint/REPORT.md（有 error 退出码 1）
cd <book> && "$PY" build_book.py --pdf   # 书：HTML + A4 PDF（无头 Chrome，不是 weasyprint）
cd <paper> && "$PY" analysis/assemble.py && "$PY" generate_publication_suite.py   # 论文：表注入 → HTML/PDF
bash scripts/build.sh                  # 书的全量：audit → 印刷 → 电子版 → EPUB → Markdown
bash release.sh                        # 组装 release/
```

## 5 目录契约（两套）

**书**：`source/{book.json,parts.json,front_*.html,ch*.html,appendix_*.html,back_*.html}`
`assets/{css,svg,charts}` · `analysis/` · `data/` · `docs/` · `scripts/` · `versions/CHANGELOG.md` · `校对清单.md`

**论文**：`source/paper.md`（唯一来源）· `assets/figures/*.png`（图件只在这里）· `data/*.csv|json` ·
`analysis/{assemble.py,make_figures.py,audit.py}` · 产物 `.md/.html/.pdf` 在仓库根（合集脚本按此路径读）·
`versions/CHANGELOG.md` · `校对清单.md`

## 6 归档（Zenodo 两套 description）

- **论文**（`publication_type: preprint`）：版本行 → 本文做什么 → Abstract（英文）→ Files → 系列。
- **书与合集**（`publication_type: book`）：中文 → 核心主张 → 结构与证据 → 本版修订 → 诚实纪律 → 边界 → 版本 → 系列。
- 标题 `中文题名：副题 / English Title: Subtitle`；`publication_date`/`version` 用真实完成日，不带 v1/2.0。
- 每篇备两份：`_zenodo/desc/<slug>.html`（HTML 视图粘贴）与 `_zenodo/desc_plain/<slug>.txt`（富文本粘贴）。

## 7 校阅与写作

- 五条目的：论证严谨、逻辑清晰、叙事完整、人文关怀、生动有趣。
- **冷峻的验证，温暖的关怀**：数可以硬，话必须软；每个约束章要写"谁在承担代价"与"这条限制使什么成为可能"。
- 改稿顺序固定：**结构 → 论证 → 文字**，不并行；每次改稿以 lint 0 error 为提交条件。
- 分级在装置（表与附录），不在每句；正文一句精确限定即可，不表演式谦逊。

## 8 已知未完成（工作单）

见 `_series/lint/REPORT.md` 的 error 列表，按件排。当前主要三类：
① 章骨架补全（主提问框/场景开篇/本章小结）；② 附录占比 >12% 的六本书；
③ 系列计数统一（"五本/六本/八本/九本"并存）。逐件认领时，先把该件的 error 清零再动文字。

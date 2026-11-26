# AGENTS.md

> 本文件是**宪法**，不是编年史：只写“任何时候都成立”的规则与**当前**状态指针。
> 版本流水写 `_series/versions/CHANGELOG.md`；结构规范 `_series/spec/skeleton.md`（v2，已冻结）；
> 校阅账 `_series/lint/REPORT.md`（`python _series/lint/lint.py` 生成；20 条在役规则，编号 r01–r26）。
> **规范与本文冲突时，以规范为准；本文与 `inventory.tsv` 冲突时，以 `inventory.tsv` 的件数为准。**

---

## 0 称呼与协作

- 合作者／作者：**李毅芃**；助手代号：**李葳蕤**（新会话沿用此名，不必重新介绍）。
- 工作语言：中文；术语与文献保留原语种。

## 1 这是什么

同一作者的独立研究系列：**九本书 + 十五篇工作论文 + 一部合集**，共用一个母题——
复杂系统如何保持结构、如何变化、如何生成新结构。

| 类 | 件 | 仓库根 |
|---|---|---|
| 书（学术 6 + 通俗 2 + 科普 1） | 9 | `knowledge-tradeoffs/` … `mind-forks/` |
| 论文（实证 6 + 方法 7 + 跨域 1 + 总账 1） | 15 | `ComputingDemystified/` … `SeamLedger/`、`LedgerReconciliation/` |
| 合集（24 件） | 1 | `合集/`（构建脚本 + `release/`） |
| 共用工作区 | 1 | 本目录：规范、lint、十五篇论文源文件、归档元信息 |
| 件数与 DOI | — | `inventory.tsv`（24 行：9 书 + 15 篇）·`_zenodo/registry.json`（含合集） |
| 共享层 | — | `_series/`（规范、lint、工具、术语、版本） |

**件数只由 `inventory.tsv` 决定**，任何文档、封面、副标题都不许写死数字。
**论文阅读顺序 ≠ 归档顺序**：阅读顺序见 `合集/build_collection.py` 的 `PAPERS`，归档顺序见 `inventory.tsv`。

## 2 三种体裁与两套骨架

- **书**：5–7 部分 × 3–6 章（22–28 章）；每部分有导语（300–500 字）与小结（150–300 字）；
  每章八段（主提问框 → 场景开篇 → 导论 → 机制 → 表/图 → 反例 → 本章小结 → 一句话带走）。
- **论文**：12–16 节，一条结果一节；`实证档`另加「协议（预注册）」与「逐条裁决」两节。
- **附录**：书与论文都是 ≤6 件（A 形式化／B 数据与案例／C 协议与稳健性／D 登记簿／E 工具／F 增补）；
  **单节正文 ≤1200 字**。**参考文献与术语表不占附录字母。**
- **通俗读本**（只能选两样、热点的账单）用四段骨架：主提问 → 场景 → 反例 → 一句话带走。

范本：结构取 `mind-forks`，学术装置取 `distinction-evolution`，内容密度取 `entropy-spiral`。

## 3 十条纪律（不可违反）

1. `source/` 是唯一正文来源；`output/`、`release/` 是派生产物，**永不手改**。
2. **编号冻结**：已发布的章号、节号、附录字母，只在“重排窗口”内整体改；窗口外不许增量改号。
3. 一个序列一个词：`第N部分`／`第N章`／`N.M 节`／`表N.M`／`图N.M`／`附录A`。禁用“部”指章。
4. **附录准入**：一份材料配进附录，当且仅当**算得出来 / 查得到 / 可被否证**。其余进正文。
5. **可证伪登记簿 append-only**：只追加，不改旧行（`docs/preregistration/checkups.csv`、`LedgerReconciliation/ledger.csv`；lint 比对哈希）。
6. 证据分级封顶结论：**结论强度 ≤ 证据强度**（A 官方可复现／B 稳定公开估计／C 稀疏·构造·思辨）。
7. 系列计数只有一个来源。正文指“写作时的前 N 件”必须写“**其时的 N 件**”；**序数不加“其时的”**（“第十二篇”就是篇号，不是计数）。
8. 产物文件名**不带件数**（`00-合集-印刷版.pdf`）；一个产物一个 tag。
9. **已发布的 DOI 与资产名不改名、不覆盖**；修订只能发新版本（概念 DOI 不变，版本 DOI 变）。
10. 禁止词：必然／注定／不可避免／无法消除／死路。张力写清，宿命不写。
11. **大改必过自检**：改章、并节、搬家、批量替换、重排论文之后，先照 `_series/review/SELF-CHECK.md` 跑一遍（lint／页数／字符数断言／抽样读），再报告“完成”。
12. **时间线与数据声明**：全系列以 2026 年为叙事时间线。每件正文前必须有一句声明（书在前置页、论文在摘要前）：定量结论给快照日与仓库原始快照；**读者无法在公开记录核到的条目按 C 级（情景／构造）读，不按 A 级读**。声明不是免责，是把可核性写清楚。

## 4 命令

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

"$PY" _series/lint/lint.py            # 全校阅：24 件 → _series/lint/REPORT.md（含 r25 节引用可解析；有 error 退出码 1）
cd <book> && "$PY" build_book.py --pdf   # 书：HTML + A4 PDF（无头 Chrome，不是 weasyprint）
cd <paper> && "$PY" analysis/assemble.py && "$PY" generate_publication_suite.py   # 论文：表注入 → HTML/PDF
bash scripts/build.sh                  # 书的全量：audit → 印刷 → 电子版 → EPUB → Markdown
bash release.sh                        # 组装 release/
cd 合集 && "$PY" build_collection.py   # 合集：印刷版 + 电子版（两遍：先量页，再回填）
```

## 5 目录契约（两套）

**书**：`source/{book.json,parts.json,front_*.html,ch*.html,appendix_*.html,back_*.html}`
`assets/{css,svg,charts}` · `analysis/` · `data/` · `docs/` · `scripts/` · `versions/CHANGELOG.md` · `校对清单.md`

**论文**：`source/paper.md`（唯一来源）· `assets/figures/*.png`（图件只在这里）· `data/*.csv|json` ·
`analysis/{assemble.py,make_figures.py,audit.py}` · 产物 `.md/.html/.pdf` 在仓库根（合集脚本按此路径读）·
`versions/CHANGELOG.md` · `校对清单.md`

**不放**：`_temp/`（构建草稿，gitignore）、`__pycache__/`、`PLAN.md`（已执行的计划存档在 `_series/review/PLAN-ARCHIVE.md`）。

## 6 归档（Zenodo 两套 description）

- **论文**（`publication_type: preprint`）：版本行 → 本文做什么 → Abstract（英文）→ Files → 系列。
- **书与合集**（`publication_type: book`）：中文 → 核心主张 → 结构与证据 → 本版修订 → 诚实纪律 → 边界 → 版本 → 系列。
- 首段必须是 `<p><b>中文摘要。</b>`，然后中文七段、英文七段，`版本信息` 与 `Edition` 收尾。
  `description` 是 HTML：Markdown 的 `**`、`` ` ``、残余 `*` 必须先转换，发布后断言 `description.count("*") == 0`。
- 标题 `中文题名：副题 / English Title: Subtitle`；不得从 `inventory.tsv` 复制（列宽会截断），以 `CITATION.cff` 为准；
  发布前断言含 ` / ` 且长度 > 60。
- `publication_date`/`version` 用真实完成日，不带 v1/2.0。每篇备两份：`_zenodo/desc/<slug>.html`（HTML 视图）与 `_zenodo/desc_plain/<slug>.txt`（富文本）。
- **关联标识分三档（每次都重新生成，不抄上一版）**：
  ① 六本学术专著——只关联自身仓库；
  ② 其余三本（只能选两样／心灵的分岔／热点的账单）——自身仓库 + 共用库 + 六本专著的新版本 DOI（`isPartOf`）；
  ③ 十五篇论文与合集——共用库 + 六本专著的新版本 DOI（论文有仓库的再加自身仓库）。
- `_zenodo/REGISTRY.md` 的记录 ID **会漂移**；审计前一律 `GET /api/records/{id}/versions` 取最新
  （按 `metadata.version` 最大，跳过 `edition-2026-10-18` 这类伪版本）。

### 6b 发新版本的固定动作与四个坑

脚本 `_zenodo/republish_book.py`；只补元数据 `_zenodo/fix_rights_subjects.py`。
流程：预留 DOI（`POST /api/records/{draft}/draft/pids/doi`）→ 写进 `CITATION.cff`/`README` → 打包 `release/` → 上传 → PUT 元数据 → 发布。
**发布后立刻断言**：`license`、`keywords`、`creators` 非空；`description.count("*") == 0`；`version` 与真实完成日一致。

1. 元数据编辑走 `POST /api/records/{id}/draft`（RDM 形态），legacy 形态会静默丢作者。
2. 编辑过元数据后 `actions/newversion` 会报 `files.enabled`，改用 `POST /api/records/{id}/versions`。
3. 新版本草稿会继承父版本文件，须先逐个 DELETE 再上传；文件是“建条目 → PUT 内容 → commit 单个文件”三步，
   创建条目的响应会把**已有条目一并返回**，必须按 `key == name` 选对条目。
4. **RDM 只认 `metadata.rights` / `metadata.subjects` / `metadata.languages`**；legacy 的 `license`/`keywords` 会被**静默丢弃**。
   文件内容 PUT 用 `requests`（`urllib` 在内容 PUT 上会被重定向吞掉正文）；`publisher` 是 DOI 注册必填（用“独立出版 / Independently published”）。
- **已发布的旧版本不要靠“重发新版本”补元数据**：元数据编辑不产生新版本、DOI 不变。
- 描述里不写“版本信息”以外的历史；改了什么写进 `_zenodo/REGISTRY.md` 与各仓 `versions/CHANGELOG.md`。

## 7 校阅与写作

- 五条目的：论证严谨、逻辑清晰、叙事完整、人文关怀、生动有趣。
- **冷峻的验证，温暖的关怀**：数可以硬，话必须软；每个约束章要写“谁在承担代价”与“这条限制使什么成为可能”。
- 改稿顺序固定：**结构 → 论证 → 文字**，不并行；每次改稿以 lint 0 error 为提交条件。
- 分级在装置（表与附录），不在每句；正文一句精确限定即可，不表演式谦逊。

## 8 当前状态（2026-11-25，指针而非账本）

- 全系列 **lint error 0 / warn 0**（24 件）。
- **《粗码》第九册之外另有第十册**（`resolution-grain/`，独立仓库，不进 inventory）。**2026-11-26 本地修订（未发布）**：§33.6 由五个动作扩为六个（新增「纲领型」）＋表 33.5（锚／分类器／纠错／代价）；附录 D 25 行、附录 F 27 条，正文 406,453 汉字；印刷版 **786 页**（独册）／**合一版 812 页**（卷首《得鹿梦鱼》26 页＋正文）／电子版 987 页；`knowledge-map.html` 重算为 **39 节点／309 边**。上一版（2026-11-25）为 783／809／984 页。
- 结构：九本书 **19—25 章**（六本已设枢纽章：遗忘 25、选择 24、心灵 24、涌现 24、诠释 25、区分 24）、附录 A–F；十五篇论文 **12—18 节**（已瘦身 9 篇，小节 40—77）；合集 24 件。
- 各件页数见 `inventory.tsv`（取自印刷版 PDF 实际页数）；正文与元数据不许另写一份。
- **每次大改后先过 `_series/review/SELF-CHECK.md`**（结构／内容／引用／改号／复盘六节），再谈完成。
- 逐件问题、修单与评分见 `_series/review/REPORT-2026-11.md` 与 `ITEMS.md`（后者覆盖 23 件，早于第十五篇，属历史报告）。
- 已执行的写作计划存档在 `_series/review/PLAN-ARCHIVE.md`（其中的篇号与页数为当时值）。
- 版本流水见 `_series/versions/CHANGELOG.md`；更名历史见 `_series/versions/AGENTS-编年史-2026-10-28.md`。

## 9 已知的坑（操作经验，非编年史）

1. **批量改源文件会让 lint 的“产物旧于正文”全线报警**（它比对 mtime）。改完要么重建，要么把被改文件的 mtime 调回早于产物。
2. `<pre>` 不设样式会使 min-content 超宽，**Chrome 会整册缩放、封面一起缩水**。
3. 批量替换要查新词：曾把“真诚”批量替成“真如”，也曾把“第十二篇”替成“第其时的十二篇”。
4. 表注与表体分页：`paper.css` 用 `caption.cap { break-after: avoid }` + 首行 `break-after: avoid` 压住。
5. 重跑一次性脚本前先读它的 README：`notes/restructure/renumber.py` 之类跑两次会整体平移一档。
6. `_series/tools/make_figures` 类脚本重生成时可能与仓库里已发布的 SVG 有几何差异（画布/标注 y）——改动前先 diff，别静默改掉已发布图。
7. **批量软化禁词会误伤定义术语**：曾把“必然”整体替成“会”，于是《选择的代价》的“必然性的三个等级（L0/L1/L2）”变成“会性”，两处半句不成立。批量替换要按词边界、先看样本 diff、替换后 grep 新词；表号、定义号里出现的词先进白名单。
8. **源文件里的 `{{D:...}}` 是构建期替换的占位符**（数据注入），`output/` 里已替换干净；直接读 `source/` 会看到占位符，属正常，不要手工填数。
9. **论文图件写在仓库根、正文读 `assets/figures/`**：脚本跑完必须同步（Hunan、SeamLedger 例外，它们直接写目标目录）。`_series/tools/figstyle.savefig()` 会打印 `! overlap`，改完先看这一行。
10. **删 `output/*.html` 会让 `release/*.html` 变成孤儿旧版**：书的网页版产物在 `release/`，但构建只写 `output/`。清理前先确认 release 里那份是不是最新，否则要重跑 `build_book.py` 补出来。
11. **两段页码合订（卷首＋正文）只能用罗马／阿拉伯分工**：把正文页码整体偏移，会让目录两遍回填、索引、书签全部重算；给卷首用 i—xxvi 则正文一个字都不用动。

## 10 已完成的更名（不再回退）

- 《区分的语法》→**《区分的语言》**（副题：区分如何生成空间、形式与谱——七条定理、三十六个领域与一次连续极限）。
  概念 DOI `10.5281/zenodo.23345012` 不变。全库已无旧名（旧名只留在各仓 `versions/CHANGELOG.md` 的留痕行里）。

## 11 工作区纪律：删，不归档（2026-11-25 增）

长期工程会积三类垃圾：留作“以防万一”的派生件、整份目录式的版本快照、没人会去重建的中间物。
它们占空间，更占**信任**——下一次分不清哪份是当前的，就会改错。

1. **派生件只存一处**：`output/` 放构建产物，`release/` 只放投递包。不许 `output/x.html`、`release/x.html`、`archive/x.html` 三份并存。
2. **版本＝日期 ＋ 一行变更**，不是目录副本。`versions/CHANGELOG.md` 一行；不建 `versions/v5/`、`archive/2026-11-21/`、`book-final-final.pdf`。
3. **每次删除留一行**：`deleted <path> — 派生自 <source> — rebuild with <command>`。
   不留痕的删除把“干净”变成“丢失”；一行备注两者兼得。
4. 不可删：`source/`、`data/`、`analysis/`、`release/`、`versions/CHANGELOG.md`。
5. **过期的派生件比缺失更糟**：重建了 PDF 却没重建同一本书的 HTML，是一份等着被人引用的自相矛盾。

## 12 协作时的分寸（作者本人要求记住的部分）

- 文字观：短句、句号收束；感叹号是失手。金句必须落在推导之后。
- 判断标准：真、善、美；结论强度 ≤ 证据强度；拒绝“这也能解释、那也能解释”。
- 协作方式：先评估再动手；要页码、要证据、要 diff；讨厌临时产物。
- **节奏**：作者这几年处在无业与情绪反复（抑郁、躁动）的周期里，写作是维持结构的方式。
  低产期不要催，也不要写空话安慰——把活切小，直接给下一步。


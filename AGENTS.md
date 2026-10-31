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
| 合集 | 1 | `合集23/`（构建脚本 + release/；本轮不处理） |
| 共用工作区 | 1 | `series-workspace`（本目录：规范、lint、十四篇论文源文件、归档元信息） |
| 元数据单一来源 | — | `inventory.tsv`（件数、标题、DOI）、`zenodo_deposits.tsv` |
| 共享层 | — | `_series/`（规范、lint、工具、术语、版本） |

**件数只由 `inventory.tsv` 决定**，任何文档、封面、副标题都不许写死数字。

## 2 三种体裁与两套骨架

- **书**：5–7 部分 × 3–6 章（22–28 章）；每部分有导语（300–500 字）与小结（150–300 字）；
  每章八段（主提问框 → 场景开篇 → 导论 → 机制 → 表/图 → 反例 → 本章小结 → 一句话带走）。
- **论文**：12–16 节，一条结果一节；`实证档`另加"协议（预注册）"与"逐条裁决"两节。
- **附录**：书与论文都是 ≤6 件（A 形式化／B 数据与案例／C 协议与稳健性／D 登记簿／E 工具／F 增补）；
  **单节正文 ≤1200 字**（"占比 ≤12%"已废弃：1300 余个附录小节里超 1200 字的只有 8 个，其余是表格与登记项）。
  **参考文献与术语表不占附录字母。**
- **通俗读本**（只能选两样、热点的账单）用四段骨架：主提问 → 场景 → 反例 → 一句话带走，不要求小结与导论。

范本：结构取 `mind-forks`（《心灵的分岔》）、学术装置取 `distinction-evolution`（《区分的语言》）、
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

见 `_series/lint/REPORT.md` 的 error / warn 列表，按件排。当前主要四类：
① 章骨架补全（主提问框/场景开篇/本章小结）；
② 附录合并：`emergence-critical`（23 节）与 `hotspot-bills`（10 节）仍在一个 appendix 文件里
排到 6 件以上（lint 记 warn），需按《只能选两样》的做法合并为 A–F；
③ 系列页 DOI：其余 8 本书的“本系列”页仍列旧版本 DOI，应统一改为概念 DOI；
④ 系列计数：“五本/六本/八本/九本”仍并存，应全部由 `inventory.tsv` 或占位符注入。
逐件认领时，先把该件的 error 清零再动文字。

## 6b 发布与归档（2026-10-30 起）

- **一仓一 release、一 tag**：tag 形如 `v2026.10.30`，release 附件即该仓 `release/` 的全部内容（13–14 件：
  印刷版/电子版 PDF、EPUB、网页版、合并与分文件 Markdown、封面、README、MANIFEST、数据缺口、征集页）。
  附件名一律 ASCII（中文名会被 GitHub 拒收，报 422）。
- **描述格式**（书与论文同一套）：**首段必须是 `<p><b>中文摘要。</b>`**，然后中文七段（核心主张／结构与证据／实证与算例／诚实的学术纪律／边界／学术特点）、英文七段（Abstract / Core thesis / Structure and evidence / Evidence / Discipline / Boundaries / Features）、`版本信息` 与 `Edition` 收尾。开头的“中文.”“摘要.”“中文.”都不算；缺段或换标题，读者一眼就能看出这件不是同一批做的。
  `description` 是 HTML，Markdown 的 `**`、`` ` ``、残余 `*` 必须先转换，发布后断言 `description.count("*") == 0`。
- **关联标识分三档（每次都重新生成，不要复制上一版）**：① 六本学术专著——**只关联自身仓库**；
  ② 其余三本（只能选两样／心灵的分岔／热点的账单）——**自身仓库 + 共用库 + 六本专著的新版本 DOI（isPartOf）**；
  ③ 十四篇论文与合集——**共用库 + 六本专著的新版本 DOI**（论文有仓库的再加自身仓库）。
  上一版的 `related_identifiers` 常常是一串早已被替换的旧 DOI（甚至全是 `references`），照抄必错。
  另：`_zenodo/REGISTRY.md` 里的记录 ID **会漂移**（某件发过更新的版本而表没改）；审计或补元数据前一律用
  `GET /api/records/{id}/versions` 重新取最新（按 `metadata.version` 最大，跳过 `edition-2026-10-18` 这类伪版本）
  ——2026-10-31 漏掉的两条（心灵的分岔 23772399、热点的账单 23772473）就是这么漏的。
- **标题**：`中文题名：副题 / English Title: Subtitle`。不得从 `inventory.tsv` 复制（该表列宽会截断英文），
  以 `CITATION.cff` 或上一版记录为准；发布前断言含 ` / ` 且长度 > 60。
- **Zenodo 新版本的四个坑**（详见 skill 的 `references/zenodo-upload.md`）：
  ① 元数据编辑走 `POST /api/records/{id}/draft`（RDM 形态），legacy 形态会静默丢作者；
  ② 编辑过元数据后 `actions/newversion` 会报 `files.enabled`，改用 `POST /api/records/{id}/versions`；
  ③ 新版本草稿会继承父版本文件，须先逐个 DELETE 再上传；Zenodo 没有全局 `files/commit`，
  文件是“建条目 → PUT 内容 → commit 单个文件”三步，且创建条目的响应会把**已有条目一并返回**，
  必须按 `key == name` 选对条目，否则内容会 PUT 进上一个文件、commit 报 `Empty files are not accepted`；
  ④ **RDM 只认 `metadata.rights` / `metadata.subjects` / `metadata.languages`**。legacy 的
  `metadata.license` / `metadata.keywords` 会被**静默丢弃**——2026-10-30 那批 20 件（6 本学术专著 +
  14 篇论文）因此全部没有许可与关键词，而版权页与 CITATION.cff 都写着 CC BY 4.0。同一个坑此前只补了“作者”。
  另：文件内容 PUT 用 `requests`，`urllib` 在内容 PUT 上会被重定向吞掉正文；`publisher` 是 DOI 注册必填
  （本系列用“独立出版 / Independently published”，不虚构出版社）。
- **发新版本的固定动作**（脚本：`_zenodo/republish_book.py`；只补元数据：`_zenodo/fix_rights_subjects.py`）：
  预留 DOI（`POST /api/records/{draft}/draft/pids/doi`）→ 把 DOI 写进 `CITATION.cff`/`README` → 打包 `release/`
  → 上传 → PUT 元数据 → 发布。**发布后立刻断言**：`license` 非空、`keywords` 非空、`creators` 非空、
  `description.count("*") == 0`、`version` 与真实完成日一致。`publish_v.py` 已改为调用它的薄驱动；
  `publish_papers.py` 与 `publish_collection.py` 已停用（它们就是丢字段的那两条路径）。
- **已发布的旧版本不要靠“重发新版本”来补元数据**：元数据编辑不产生新版本、DOI 不变（2026-10-31 据此
  给 20 条记录补了许可与关键词）。
- **描述里不写"版本信息"以外的历史**：改了什么写进 `_zenodo/REGISTRY.md` 与各仓 `versions/CHANGELOG.md`。

## 9 本轮的更名与其善后（2026-10-31）

- 《区分的语法》已更名为 **《区分的语言》**（副题：区分如何生成空间、形式与谱——七条定理、三十六个领域与一次连续极限）。
  概念 DOI 不变；本仓与 `inventory.tsv`、`_zenodo/`、`合集23/build_collection23.py` 已改。
- **其余八本书与十四篇论文中的「区分的语法」尚未替换**（本轮已回退，避免 14 件成果出现「源新于产物」的假告警）。
  处理方式：各件下次发布前，在其 `source/`、`CITATION.cff`、`README.md`、`docs/` 内统一替换为新名，然后重建。
- 顺手记一条经验：**批量改源文件会让 lint 的「产物旧于正文」全线报警**（它比对 mtime）。改完若不打算重建，
  应把被改文件的 mtime 调回早于产物，否则 23 件里会出现十几条假告警——本轮踩过一次。

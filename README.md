# series-workspace · 有限系统的取舍（工作区）

**同一作者的独立研究系列：九本书 ＋ 十五篇工作论文 ＋ 一部合集 ＋ 第十册《粗码》。**
A single-author research series: nine books, fifteen working papers, one collection, plus a tenth volume.

> **件数以 `inventory.tsv` 为准；本仓只放规范、lint、十五篇论文源文件与工具。**
> **可视化阅读台**（离线单文件）在 `文集\可视化阅读台\`：`index.html` 是总入口。

## 这是什么 ｜ What this is

| 类 | 件 | 位置 |
|---|---|---|
| 书（学术 6 ＋ 通俗 2 ＋ 科普 1） | 9 | 各自独立仓库（见下表） |
| 工作论文 | 15 | 本仓各目录（`source/paper.md` 为唯一来源） |
| 合集 | 1 | `合集/`（印刷版／电子版／EPUB） |
| 《粗码》 | 1 | `resolution-grain/`（独立仓库，不进 inventory） |
| 规范与工具 | — | `_series/`（spec／lint／tools／review／versions） |

## 十件的离线阅读台 ｜ The ten reading consoles

| 仓库 | 章 | 审问卡 | 阅读页 | 结构地图 |
|---|---|---|---|---|
| `knowledge-tradeoffs/` | 19 | 19 | 522 KB | 149 KB |
| `capacity-cascade/` | 25 | 25 | 943 KB | 206 KB |
| `emergence-critical/` | 24 | 24 | 747 KB | 111 KB |
| `entropy-spiral/` | 25 | 25 | 2737 KB | 299 KB |
| `interpretation-tradeoff/` | 25 | 25 | 772 KB | 185 KB |
| `impossibility-triangle/` | 24 | 24 | 1090 KB | 181 KB |
| `distinction-evolution/` | 24 | 24 | 2239 KB | 1608 KB |
| `mind-forks/` | 24 | 24 | 940 KB | 220 KB |
| `hotspot-bills/` | 21 | 21 | 450 KB | 92 KB |
| `resolution-grain/` | 39 | 39 | 8499 KB | 3523 KB |

每件两个入口：`assets/<repo>-reader.html`（三档阅读＋章末审问卡＋可复制对账指令）与
`assets/<repo>-explorer.html`（3D 章际螺旋／部×部矩阵／附录台账／图件账）。**离线单文件、断网可开、零依赖。**

## 命令 ｜ Commands

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" _series/lint/lint.py                    # 全校阅 24 件
"$PY" _series/tools/make_atlas.py --all       # 结构地图（九本）
"$PY" _series/tools/make_reader.py --all      # 阅读页（九本＋十五篇＋粗码）
"$PY" _series/tools/make_index.py             # 总入口 index.html
"$PY" _series/tools/publish_viz.py            # 一源三投：assets → release → 文集
"$PY" _series/tools/republish_all.py --tag 2026-11-26   # 每仓 1 tag ＋ 1 release
```

## 纪律 ｜ Discipline

结论强度 ≤ 证据强度（A 官方可复现／B 稳定公开估计／C 稀疏·构造·思辨）；禁词：必然、注定、不可避免、无法消除、死路；
可证伪登记簿 append-only；已发布的 DOI 与资产名不改名、不覆盖，修订只发新版本。详见 `AGENTS.md`。

## 许可 ｜ License

正文 CC BY 4.0；脚本 MIT。

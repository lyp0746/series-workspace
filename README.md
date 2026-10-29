# 有限系统的取舍 — 系列工作区

李毅芃 · 独立研究系列 · 2026-10-26

**九本书 + 十三篇工作论文 + 一本二十二件合集。**

---

## 一、目录结构（统一约定）

```
D:\0_Article\
├── AGENTS.md                  # 系列级记忆：约定、命令、状态
├── README.md                  # 本文件：索引
├── notes/                     # 讨论与评估记录（非出版内容）
├── _zenodo/                   # 归档小工具（finish.py / scaffold.py）
│
├── 九本书（书模式：source/*.html 为唯一正文源）
│   ├── knowledge-tradeoffs/      只能选两样
│   ├── distinction-evolution/    区分的语法
│   ├── capacity-cascade/         遗忘的边界
│   ├── entropy-spiral/           错位的时间
│   ├── impossibility-triangle/   选择的代价
│   ├── interpretation-tradeoff/  诠释的权衡
│   ├── emergence-critical/       涌现的临界
│   ├── mind-forks/               心灵的分岔
│   └── hotspot-bills/            热点的账单
│
├── 十三篇工作论文（论文模式：Markdown 为唯一正文源）
│   ├── ComputingDemystified/     论文一 术语的账单
│   ├── WorldPeriodization/       论文二 谁在切时间轴
│   ├── SleepingResidue/          论文三 线外的残余
│   ├── HunanRelaySystem/         论文四 明清湘中驿道
│   ├── BureauRotationCession/    论文五 轮换的让渡
│   ├── HarnessEcology/           论文六 被点燃的生态
│   ├── OptimizationBoundary/     论文七 优化的边界
│   ├── CapacityProxies/          论文八 容量的三个代理
│   ├── DomainCrossSection/       论文十 领域的剖面
│   ├── IsomorphismStrength/      论文十一 同构的强度
│   ├── MemoryAnchor/             论文十二 记忆的锚点
│   ├── MemoryStressTest/         论文十三 锚点的下限
│   └── LedgerReconciliation/     论文九 六张账单的对账
│
└── 合集22/                    # 二十二件合集（当前；三部编排）

> 本地构建目录只保留当前版 `合集22/`；18／20／21 件版仅保留 Zenodo 记录（PDF/HTML/MD/zip 可从记录下载）。
```

**每篇论文的目录结构（十三篇一致）**

```
<论文>/
├── source/paper.md        正文源（含 <!--TABLE_x--> 占位符）
├── analysis/              make_figures.py / assemble.py（+ 取数脚本）
├── data/                  数据模块与生成的表
├── fig01.png …           图（根目录）
├── interactive/           单文件交互页
├── release/               发布包（PDF/HTML/MD/图/CSV/MANIFEST）
├── versions/CHANGELOG.md  内部版本记录
├── README.md  CITATION.cff  .zenodo.json  release.sh
├── 上传前检查清单.md  目录与图表清单.md
└── generate_publication_suite.py
```

## 二、二十二件与 DOI

| 序 | 题名 | 主核 | 页 | 版本 DOI |
|---|---|---|---|---|
| 卷一 | 只能选两样 | 导览 | — | 10.5281/zenodo.23447341 |
| 卷二 | 区分的语法 | 看见 | — | 10.5281/zenodo.23447201 |
| 卷三 | 遗忘的边界 | 记住 | — | 10.5281/zenodo.23447169 |
| 卷四 | 错位的时间 | 跟上 | — | 10.5281/zenodo.23447129 |
| 卷五 | 选择的代价 | 选择 | — | 10.5281/zenodo.23447238 |
| 卷六 | 诠释的权衡 | 讲述 | — | 10.5281/zenodo.23447292 |
| 卷七 | 涌现的临界 | 临界 | — | 10.5281/zenodo.23447311 |
| 卷八 | 心灵的分岔 | 全应用 | 309 | 10.5281/zenodo.23637236 |
| 卷九 | 热点的账单 | 应用 | — | 10.5281/zenodo.23637708 |
| 论文一 | 术语的账单 | 看见 | 50 | 10.5281/zenodo.23602360 |
| 论文二 | 谁在切时间轴 | 看见＋讲述 | 53 | 10.5281/zenodo.23602364 |
| 论文三 | 线外的残余 | 记住 | 51 | 10.5281/zenodo.23603016 |
| 论文四 | 明清湘中驿道 | 跟上 | 50 | 10.5281/zenodo.23601983 |
| 论文五 | 轮换的让渡 | 选择 | 72 | 10.5281/zenodo.23602311 |
| 论文六 | 被点燃的生态 | 临界 | 50 | 10.5281/zenodo.23603015 |
| 论文七 | 优化的边界 | 接口 | 33 | 10.5281/zenodo.23611782 |
| 论文八 | 容量的三个代理 | 记住·代理 | 22 | 10.5281/zenodo.23611799 |
| 论文十 | 领域的剖面 | 看见·操作化 | 51 | 10.5281/zenodo.23664233 |
| 论文十一 | 同构的强度 | 看见＋讲述·跨域 | 50 | 10.5281/zenodo.23663027 |
| 论文九 | 六张账单的对账 | 总账（62 条） | 54 | 10.5281/zenodo.23612202 |
| 论文十二 | 记忆的锚点 | 记住·架构 | 50 | 10.5281/zenodo.23665882 |
| 论文十三 | 锚点的下限 | 记住·测试 | 51 | 10.5281/zenodo.23667929 |
| 合集 | 二十二件合集（第五版，三部编排） | — | 1846 | 10.5281/zenodo.23668413（概念 23613406） |
| 合集 | 历史版本（保留记录） | — | — | 23666079 / 23664446 / 23663577 / 23638342 / 23614675 |
| 合集 | 十八件合集（首版，保留） | — | 1646 | 10.5281/zenodo.23638342 |

## 三、常用命令

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

# 论文（每篇目录内）
"$PY" analysis/make_figures.py
"$PY" analysis/assemble.py
"$PY" generate_publication_suite.py
bash release.sh

# 合集
cd 合集22 && bash release.sh     # build_collection22.py → make_md.py → release/

# 归档
"$PY" _zenodo/finish.py --record <draft> --repo "<仓库绝对路径>" --fresh --publish
```

## 四、纪律（摘要）

1. 结论强度 ≤ 证据强度（A/B/C、甲/乙/丙）。
2. 图表同源：由 `data/` 生成，附录表不手抄。
3. 负面结果进正文，登记簿 append-only。
4. 正文不含版本号；日期只用真实完成日。
5. 每篇必备「六核心 × 六专著」对照表。

详见 `AGENTS.md`。

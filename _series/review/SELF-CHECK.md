# 大改之后的自检清单（SELF-CHECK）

> 每次做大改动（改章、并节、搬家、批量替换、重排论文）之后，**先跑这一页，再谈完成**。
> 依据：`AGENTS.md` 纪律、`voice.md`、`_series/review/` 的历史教训。全部命令可在仓库根直接跑。

## 0 三条铁律

1. **先备份，再动手**；改完删备份。
2. **搬字必须断言**：搬移前后“可见字符数”完全相等才写盘（去掉空白、`#`、`*`、标点后的字数）。
3. **不提交、不重建合集、不动 Zenodo**，除非作者说“收口”。

## 1 结构（5 分钟）

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" _series/lint/lint.py            # 必须 0 error / 0 warn
"$PY" _series/tools/fogcheck.py       # 节/章、中位字/节、短节比
"$PY" _series/tools/density.py        # 数字密度（中文数词计入）
```

- 改过书：`cd <book> && "$PY" build_book.py --pdf`，再核页数。
- 改过论文：`"$PY" analysis/assemble.py`（若有）→ `"$PY" generate_publication_suite.py`；无 assemble 的仓先 `cp source/paper.md <根目录成品>.md`。
- 页数逐件核对（应等于 `inventory.tsv` 第 5 列）：

```bash
"$PY" - <<'EOF'
import io,glob,os
from pypdf import PdfReader
rows=[l.split('\t') for l in io.open('inventory.tsv',encoding='utf-8') if l.strip() and not l.startswith('#')]
bad=[]
for r in rows:
    repo=r[1]; inv=int(r[4])
    c=glob.glob(repo+'/output/book.pdf')+[x for x in glob.glob(repo+'/*.pdf') if 'ereader' not in x and 'print' not in x]
    n=len(PdfReader(max(c,key=os.path.getmtime)).pages)
    if n!=inv: bad.append((repo,inv,n))
print('mismatches',bad or 0)
EOF
```

## 2 内容（逐章）

- 每章有：主提问 → 场景 → 导论 → 机制 → 表/图 → **反例** → 小结 → 一句话带走。
- 每个章级主张有一句「若这条判据错了，会看到什么」（互斥观测，20—40 字）。
- 每节至少一个数／物／例；数字标「实测／示意／外推」。
- 禁词：必然、注定、不可避免、无法消除、死路。
- 元话语 ≤1 处/章（章首路线图允许一次）。
- 术语首现给中文；年份：正文中文日期、表格 ISO。

## 3 引用与编号（改号必做）

- `r25`：所有 `第 N.M 节`／`§N.M` 必须能解析。
- `r26`：论文子节号必须与父节一致（`x.k` 属于 `## x`）。
- 跨书引用：`《书名》第 N 章` 要在**被引书**里核对（lint 不查跨书）。
- 图表号随章平移；`parts.json` 的 `no/file/sections` 同步。
- 合并章的检查：**一个 h2、一个小结、一套本章文献**（多余的要删）。

## 4 改号脚本约定

`_series/tools/renumber_book.py`：章号、节号、锚点、图/表号、`parts.json` 一次改；先 `--dry`。
合并/搬家用手写脚本时：按“块”切分（标题＋正文），搬完做字符数断言；**不要**用跨段落的贪婪正则。

## 5 收口前（只在作者说“收口”时）

1. 每仓 `build_book.py --pdf` → `release.sh`；论文 `generate_publication_suite.py`。
2. 合集两遍重建：`cd 合集 && "$PY" build_collection.py`。
3. 每仓一个 release + 一个 tag；`inventory.tsv` 页数最后核一遍。
4. Zenodo：先 `GET /api/records/{id}/versions` 取最新 ID，再 `_zenodo/republish_book.py`；
   发布后断言 `license`／`keywords`／`creators` 非空、`description.count("*")==0`、`version`＝真实完成日。
5. 提交（各书仓独立；`.gitignore` 不含 `source/`）。

## 6 复盘三问（每次大改后写进 NEXT）

1. 这次改动**可能**弄坏什么？我怎么证明没弄坏？（字符数、页数、lint、抽样读）
2. 有没有把“数量指标”当成“质量”？（密度尺、节数尺的教训）
3. 有没有把缺陷**藏进改号**里？（宁可留 warn，也不要用重排掩盖孤儿块）

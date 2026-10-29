# _zenodo — 归档小工具（2026-10-24）

批量发布时 Zenodo 会持续返回 504/502，官方脚本的"一次跑完"不可靠。这里的三个小脚本按
"建版本 → 记 draft id → 只补缺失文件 → 核文件数 → 发布"的顺序做，可反复重跑。

| 脚本 | 作用 |
|---|---|
| `finish.py` | 补全草稿：`--record <draft> --repo <dir> [--fresh] [--publish]`；每步 150—300s 超时、失败即停 |
| `descriptions.py` / `replace_assets.py` | 历史工具：批量改描述、替换附件 |

**流程（新版本）**

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
# 1) 建新版本，拿 latest_draft 的 id
"$PY" - <<'EOF'
import json,urllib.request,pathlib
TOK=pathlib.Path(r"D:\0_Article\zenodo_token.txt").read_text(encoding="utf-8").strip()
API="https://zenodo.org/api"
r=urllib.request.Request(f"{API}/deposit/depositions/<记录ID>/actions/newversion?size=1",
    headers={"Authorization":"Bearer "+TOK}, method="POST")
d=json.load(urllib.request.urlopen(r,timeout=300))
r2=urllib.request.Request(d["links"]["latest_draft"]+"?size=1",headers={"Authorization":"Bearer "+TOK})
print(json.load(urllib.request.urlopen(r2,timeout=300))["id"])
EOF
# 2) 补文件 + 元数据 + 发布
"$PY" _zenodo/finish.py --record <draft> --repo "D:\0_Article\<仓库>" --fresh --publish
```

**三条纪律**

1. `--fresh` 先删继承文件，避免旧版多出来的文件残留；发布前核 `files` 数与 `release/` 一致。
2. 失败重试会留下 **0 文件的空草稿**，用 `GET /api/deposit/depositions?size=100` 列出来删掉。
3. 发布后把 `doi` 与 `conceptdoi` 写回 `CITATION.cff` 与 `README`；**不要用正则批量改正文里的 DOI**（会误伤引用别篇的行）。

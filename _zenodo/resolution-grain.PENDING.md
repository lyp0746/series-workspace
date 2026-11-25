# resolution-grain（《粗码》）· Zenodo 发布记录

> **已发布（2026-11-21）**：最新版本记录 **24393431**，DOI **10.5281/zenodo.24393431**，概念 DOI **10.5281/zenodo.24339909**（2026-11-20 版 24390257 已被本版取代）。
> 14 个文件（印刷版／阅读版 PDF、EPUB、两个 HTML、Markdown、分章 zip、可视化 zip、封面、README、修订说明、数据缺口、MANIFEST、SHA256SUMS）。
> 关联标识 8 条：自身仓库、共用库、六本学术专著当前版本（`isPartOf`）。
> 标题与描述的全角标点被 Zenodo 归一成半角——与已发布的二十四件一致，不是本次的错。
> 本地备份：`_zenodo/published_resolution-grain.json`。**未进 `inventory.tsv`，未进合集**（作者决定）。
> 记录页：https://zenodo.org/records/24393431

---


> 状态：**元信息已备好，尚未建记录、未注册 DOI。** 本件未进 `inventory.tsv`（系列第十册，在建）。
> 备好的文件：`resolution-grain/.zenodo.json`（完整 payload）、
> `_zenodo/desc/resolution-grain.html`（HTML 视图）、`_zenodo/desc_plain/resolution-grain.txt`（富文本）。
> 发布包：`release/`（含 `MANIFEST.txt`、`SHA256SUMS`）。

---

## 1 发布前必须跑的四条断言

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" - <<'EOF'
import io, json
z = json.load(io.open("resolution-grain/.zenodo.json", encoding="utf-8"))
d = z["description"]
assert d.count("*") == 0, "描述里有 markdown 星号"
assert d.startswith("<p><b>中文摘要。</b>"), "首段不是中文摘要"
assert " / " in z["title"] and len(z["title"]) > 60, "标题须为「中文 / English」且 >60 字"
assert z["license"] == "CC-BY-4.0" and z["keywords"] and z["creators"], "授权/关键词/作者不可空"
assert z["publication_date"] == "2026-11-18" and z["version"] == "2026-11-18"
print("四条断言通过")
EOF
```

另有一条人工项：**六本学术专著的 DOI 每次都要重新取**（`GET /api/records/{id}/versions` 取 `metadata.version`
最大者，跳过 `edition-2026-…` 这类伪版本），不要抄 `.zenodo.json` 里这一份（那是 2026-11-18 的快照）：

| slug | 本快照的版本 DOI |
|---|---|
| entropy-spiral | 10.5281/zenodo.24029909 |
| capacity-cascade | 10.5281/zenodo.24029873 |
| distinction-evolution | 10.5281/zenodo.24029812 |
| impossibility-triangle | 10.5281/zenodo.24030720 |
| interpretation-tradeoff | 10.5281/zenodo.24029980 |
| emergence-critical | 10.5281/zenodo.24030004 |

## 2 关联标识（按根 `AGENTS.md` §6 第②档：通俗理论书）

- 自身仓库 `https://github.com/lyp0746/resolution-grain`（`isSupplementedBy`）
- 共用库 `https://github.com/lyp0746/series-workspace`（`isPartOf`）
- 六本学术专著的新版本 DOI（`isPartOf`，逐个重新取）

## 3 建记录与发布的动作（照根 `AGENTS.md` §6b 的四个坑）

```bash
cd /mnt/d/0_Article
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

# ① 建草稿（RDM 形态），先预留 DOI
"$PY" - <<'EOF'
import api, json, io
z = json.load(io.open("resolution-grain/.zenodo.json", encoding="utf-8"))
meta = {"metadata": {
  "title": z["title"], "description": z["description"],
  "creators": [{"person_or_org": {"type": "personal", "name": "李毅芃",
                                  "given_name": "毅芃", "family_name": "李"},
                "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}],
  "publication_date": z["publication_date"], "version": z["version"],
  "resource_type": {"id": "publication-book"},
  "rights": [{"id": "cc-by-4.0"}],
  "subjects": z["subjects"], "languages": [{"id": "zho"}],
  "keywords": z["keywords"],
  "related_identifiers": z["related_identifiers"],
  "publisher": "独立出版 / Independently published",
  "notes": z["notes"],
}}
d = api.post("/api/records", json=meta)          # 建草稿
rid = d["id"]
api.post("/api/records/%s/draft/pids/doi" % rid)  # 预留 DOI
print(rid)
EOF
```

```bash
# ② 上传 release/ 全量（文件三步走：建条目 → PUT 内容 → commit；键名必须 == 文件名）
#    新版本会继承父版本文件，须先逐个 DELETE
# ③ PUT 元数据（RDM 键名：rights / subjects / languages；legacy 的 license/keywords 会被静默丢弃）
# ④ 发布后立刻断言：license、keywords、creators 非空；description.count("*") == 0；version 与真实完成日一致
```

## 4 发布后要改的三处

1. `_zenodo/registry.json` 增加一条 `works` 记录（字段照既有条目：类／slug／仓库／页／版本 DOI／概念 DOI）；
2. `_zenodo/REGISTRY.md` 记一行（记录 ID 会漂移，审计前 `GET /api/records/{id}/versions` 取最新）；
3. `inventory.tsv` 加第 25 行（本书进件数），同时把根 `AGENTS.md` §1 的「九本书」等计数按新件数改一次
   （**件数只由 inventory.tsv 决定**，任何文档不许写死）。

## 5 一句话提醒

首版没有“上一版”可比，所以 `与本版前稿的差别` 写在 `versions/CHANGELOG.md` 与描述里的「本版修订」一段，
**不要**在 Zenodo 描述里写修订史（描述是 HTML，只有「版本信息」一段允许写版本）。

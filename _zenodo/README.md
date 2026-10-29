# `_zenodo/` — 归档小工具

面向 Zenodo 的一次性脚本都放在这里。**已发布记录的文件不可改**：改元数据用编辑草稿，改文件只能发新版本。

| 脚本 | 用途 |
|---|---|
| `common.py` | 共用常量与工具：六本专著 DOI、共用库地址、`title_of()`、`md2html()`、`related()`、`registry()` |
| `api.py` | Zenodo API 封装（带重试）：`show` / `newversion` / `meta` / `publish` / `files` / `delete` |
| `publish_v.py` | **书**：从 `release/` 发新版本（legacy 元数据），描述取 `descriptions.py` |
| `publish_papers.py` | **论文**：从 `release/` 发新版本，标题中英双语，关联共用库 + 六专著 DOI |
| `scan_fix_desc.py` | 体检/修复：描述里的 Markdown 记号转 HTML、标题补双语（只改元数据） |
| `descriptions.py` / `desc_mindforks.py` / `desc_v3.py` | 八本书与论文的长描述（HTML） |
| `scaffold.py` | 为一篇新论文生成标准外围文件（README / CITATION / 清单 / release.sh） |
| `finish.py` / `push.py` / `replace_assets.py` | 补传文件、大文件续传、替换已发布记录的资源 |
| `registry.json` / `REGISTRY.md` | 23 件的登记（版本 DOI / 概念 DOI / 页数 / 仓库） |

## 三条铁律（都是踩过的坑）

1. **元数据两套形态**：deposit API 用 legacy（`upload_type`/`publication_type`/`creators:[{name}]`），
   record API 用 RDM（`resource_type:{"id":...}`/`creators:[{person_or_org}]`/`relation_type`）。混用会 PUT 成功、
   publish 报缺字段，或**静默丢作者**。
2. **编辑过元数据后 `actions/newversion` 会失败**（`files.enabled`）→ 改用 `POST /api/records/{id}/versions`；
   新版本草稿**继承父版本文件**，须先逐个 DELETE 再上传；Zenodo 没有 `files/commit`。
3. **描述是 HTML、标题不能从 `inventory.tsv` 复制**（该表英文列会截断）。发布后断言：
   `" / " in title`、`len(title) > 60`、`description.count("*") == 0`。

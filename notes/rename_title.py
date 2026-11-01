# -*- coding: utf-8 -*-
import io, json, sys
sys.path.insert(0, r"D:\0_Article\_zenodo")
import api

TITLE = ("区分的语言:区分如何生成空间、形式与谱——七条定理、三十六个领域与一次连续极限 / "
         "The Language of Distinction: How Distinctions Generate Space, Form and Spectrum — "
         "Seven Theorems, Thirty-Six Domains, and One Continuum Limit")
# 1) 本地 .zenodo.json
p = r"D:\0_Article\distinction-evolution\.zenodo.json"
z = json.load(io.open(p, encoding="utf-8"))
z["title"] = TITLE
io.open(p, "w", encoding="utf-8").write(json.dumps(z, ensure_ascii=False, indent=2) + "\n")
print("本地 .zenodo.json 标题已更新")

# 2) 已发布记录：元数据编辑（不产生新版本、DOI 不变）
RID = "23853687"
try:
    api.req("POST", "https://zenodo.org/api/records/%s/draft" % RID, tries=1, timeout=90)
except Exception:
    pass
_, d = api.req("GET", "https://zenodo.org/api/records/%s/draft" % RID, tries=3, timeout=120)
m = d["metadata"]
meta = {
    "title": TITLE,
    "description": m["description"],
    "creators": m.get("creators") or [{"person_or_org": {"type": "personal", "name": "李毅芃",
                                                         "given_name": "毅芃", "family_name": "李"},
                                       "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}],
    "publication_date": m.get("publication_date"),
    "version": m.get("version"),
    "resource_type": {"id": "publication-book"},
    "rights": [{"id": "cc-by-4.0"}],
    "subjects": [{"subject": k} for k in (m.get("keywords") or [])][:24],
    "languages": [{"id": "zho"}],
    "publisher": "独立出版 / Independently published",
    "related_identifiers": [{"identifier": r["identifier"],
                             "scheme": r.get("scheme") or ("doi" if r["identifier"].startswith("10.") else "url"),
                             "relation_type": {"id": ((r.get("relation_type") or {}).get("id")
                                                      or r.get("relation") or "issupplementedby").lower()}}
                            for r in (m.get("related_identifiers") or [])],
}
api.req("PUT", "https://zenodo.org/api/records/%s/draft" % RID, data={"metadata": meta}, tries=2, timeout=300)
_, r = api.req("POST", "https://zenodo.org/api/records/%s/draft/actions/publish" % RID, tries=2, timeout=300)
print("已发布记录标题更新:", (r.get("metadata") or {}).get("title", "")[:60])

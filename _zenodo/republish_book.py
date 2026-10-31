# -*- coding: utf-8 -*-
"""给一本书发新版本（RDM 形态，元数据完整：rights / subjects / languages）。

用法：
    python _zenodo/republish_book.py new  <slug>          # 建新版本草稿，打印草稿 ID 与预留 DOI
    python _zenodo/republish_book.py up   <slug> <draft>   # 清空继承文件 + 上传 release/ 全量
    python _zenodo/republish_book.py meta <slug> <draft>   # PUT 元数据（rights/subjects 用 RDM 键名）
    python _zenodo/republish_book.py go   <slug>           # 上面三步 + 发布

为什麼要有这个脚本：2026-10-30 那一批 20 条记录用了 legacy 键名（metadata.license /
metadata.keywords），经 RDM 草稿接口时被静默丢弃，导致 20 件全部没有 CC BY 4.0。
RDM 只认 metadata.rights / metadata.subjects / metadata.languages。
"""
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = "2026-10-31"
RDM_TYPE = {"book": {"id": "publication-book"},
            "preprint": {"id": "publication-preprint"}}
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}


def reg(slug):
    g = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT, "_zenodo", "registry.json"),
                                                  encoding="utf-8"))["works"]}
    return g[slug]


def zenodo_json(slug):
    p = os.path.join(ROOT, slug, ".zenodo.json")
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else {}


def title_of(slug):
    z = zenodo_json(slug)
    if z.get("title"):
        return z["title"]
    t = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    return re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M).group(1).strip().strip('"')


def description_of(slug, draft):
    """优先用 prepared 文件，其次沿用草稿继承来的 description。"""
    for name in (os.path.join("desc", "%s.html" % slug), "%s_desc_new.html" % slug):
        p = os.path.join(ROOT, "_zenodo", name)
        if os.path.exists(p):
            return io.open(p, encoding="utf-8").read().strip()
    meta = draft.get("metadata") or {}
    return meta.get("description") or ""


REL_MAP = {"issupplementedby": "issupplementedby", "ispartof": "ispartof",
           "isversionof": "isversionof", "references": "references",
           "iscitedby": "iscitedby", "issupplementto": "issupplementto",
           "isderivedfrom": "isderivedfrom", "isidenticalto": "isidenticalto",
           "isnewversionof": "isnewversionof", "ispreviousversionof": "ispreviousversionof",
           "documents": "documents", "isdescribedby": "isdescribedby"}


def _rel(r):
    """legacy {relation: isPartOf} 与 RDM {relation_type:{id:ispartof}} 统一成 RDM 形态。"""
    raw = r.get("relation_type") or r.get("relation") or "issupplementedby"
    rid = raw.get("id") if isinstance(raw, dict) else str(raw)
    rid = REL_MAP.get(rid.lower().replace("_", ""), "issupplementedby")
    return {"identifier": r["identifier"],
            "scheme": r.get("scheme") or ("doi" if r["identifier"].startswith("10.") else "url"),
            "relation_type": {"id": rid}}


def metadata(slug, draft):
    z = zenodo_json(slug)
    kind = "preprint" if (z.get("publication_type") == "preprint") else "book"
    base = draft.get("metadata") or {}
    # 相关标识从“上一版已发布记录”取：草稿可能已被清空
    try:
        _, pub = api.req("GET", "https://zenodo.org/api/records/%s" % reg(slug)["记录ID"],
                         tries=2, timeout=120)
        rel_src = (pub.get("metadata") or {}).get("related_identifiers") or []
    except Exception:
        rel_src = base.get("related_identifiers") or []
    return {"metadata": {
        "title": title_of(slug),
        "description": description_of(slug, draft),
        "creators": [CREATOR],
        "publication_date": DATE,
        "version": DATE,
        "resource_type": RDM_TYPE[kind],
        "rights": [{"id": "cc-by-4.0"}],
        "subjects": [{"subject": k} for k in (z.get("keywords") or [])][:24],
        "languages": [{"id": "zho"}],
        # DOI 注册要求 publisher；本系列为作者独立出版，不虚构出版社
        "publisher": "独立出版 / Independently published",
        "related_identifiers": [_rel(r) for r in rel_src],
    }}


def new(slug):
    rid = reg(slug)["记录ID"]
    try:
        _, d = api.req("POST", "https://zenodo.org/api/records/%s/versions" % rid, tries=2, timeout=120)
    except Exception as e:
        print("  /versions 失败，改用 legacy newversion：", str(e)[:120])
        _, d = api.req("POST", "https://zenodo.org/api/deposit/depositions/%s/actions/newversion" % rid,
                       tries=2, timeout=120)
        _, d = api.req("GET", d["links"]["latest_draft"], tries=2, timeout=120)
    print("DRAFT %s  DOI %s  concept %s" % (d["id"], d.get("doi"), d.get("conceptdoi")))
    print("files inherited:", len(d.get("files", [])))
    return d["id"], d.get("doi")


def up(slug, did):
    """RDM 三步骤：POST 建条目 → PUT 内容 → POST commit。（Zenodo 无全局 files/commit）
    用 requests：urllib 在内容 PUT 上会被重定向吞掉正文，导致 commit 报 Empty files。"""
    import requests
    base = "https://zenodo.org/api/records/%s/draft/files" % did
    H = {"Authorization": "Bearer " + api.TOK}
    r = requests.get(base, headers=H, timeout=120)
    for f in (r.json().get("entries") or []):
        key = f.get("key")
        requests.delete("%s/%s" % (base, urllib.parse.quote(key)), headers=H, timeout=120)
        print("   -", key)
    folder = os.path.join(ROOT, slug, "release")
    names = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    n = 0
    for name in names:
        p = os.path.join(folder, name)
        r = requests.post(base, headers=H, json=[{"key": name}], timeout=180)
        r.raise_for_status()
        ent = next(e for e in (r.json().get("entries") or [r.json()]) if e.get("key") == name)
        data = open(p, "rb").read()
        r2 = requests.put(ent["links"]["content"],
                          headers={**H, "Content-Type": "application/octet-stream"},
                          data=data, timeout=1800)
        r2.raise_for_status()
        r3 = requests.post("%s/%s/commit" % (base, urllib.parse.quote(name)), headers=H, timeout=600)
        r3.raise_for_status()
        n += 1
        print("   + %-40s %5d MB" % (name, len(data) // 1024 // 1024))
    return n


def meta(slug, did):
    _, d = api.req("GET", "https://zenodo.org/api/records/%s/draft" % did, tries=2, timeout=120)
    m = metadata(slug, d)
    _, r = api.req("PUT", "https://zenodo.org/api/records/%s/draft" % did, data=m, tries=3, timeout=300)
    got = r.get("metadata") or {}
    lic = got.get("rights") or got.get("license")
    kw = got.get("subjects") or got.get("keywords") or []
    print("   license:", lic, "| keywords:", len(kw), "| creators:", bool(got.get("creators")),
          "| related:", len(got.get("related_identifiers") or []),
          "| version:", got.get("version"), "| stars:", (got.get("description") or "").count("*"))


def publish(did):
    _, r = api.req("POST", "https://zenodo.org/api/records/%s/draft/actions/publish" % did,
                   tries=2, timeout=600)
    print("PUBLISHED", r.get("doi"), "| concept", r.get("conceptdoi"))


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == "new":
        new(slug)
    elif cmd == "up":
        up(slug, sys.argv[3])
    elif cmd == "meta":
        meta(slug, sys.argv[3])
    elif cmd == "go":
        did, doi = new(slug)
        n = up(slug, did)
        meta(slug, did)
        publish(did)
        print("files:", n, "DOI:", doi)

# -*- coding: utf-8 -*-
"""只改元数据：给没有 CC BY 4.0 的记录补 rights + subjects（不改文件、不发新版本）。

背景（2026-10-31）：10-30 那批新版本用 legacy 键名（metadata.license / metadata.keywords）
调 RDM 草稿接口，这两个键被静默丢弃——20 条记录（6 本学术专著 + 14 篇论文）因此
既没有许可、也没有关键词，而文件与版权页都写着 CC BY 4.0。
RDM 只认 metadata.rights / metadata.subjects / metadata.languages。

用法：
    python _zenodo/fix_rights_subjects.py dry  <slug>...      # 只打印将要写什么
    python _zenodo/fix_rights_subjects.py go   <slug>...
    python _zenodo/fix_rights_subjects.py all                 # 扫全部 24 件里缺许可的
"""
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIC = {"id": "cc-by-4.0"}
PUBLISHER = "独立出版 / Independently published"
REL_MAP = {"issupplementedby", "ispartof", "isversionof", "references", "iscitedby",
           "issupplementto", "isderivedfrom", "isidenticalto", "isnewversionof",
           "ispreviousversionof", "documents", "isdescribedby"}


def works():
    return json.load(io.open(os.path.join(ROOT, "_zenodo", "registry.json"), encoding="utf-8"))["works"]


def keywords_of(slug):
    p = os.path.join(ROOT, slug, ".zenodo.json")
    if os.path.exists(p):
        z = json.load(io.open(p, encoding="utf-8"))
        return z.get("keywords") or []
    return []


def creator_rdm(c):
    """legacy {'name': '李, 毅芃'} → RDM person_or_org。"""
    name = (c or {}).get("name") or "李毅芃"
    if isinstance(c, dict) and c.get("person_or_org"):
        return c
    if "," in name:
        family, given = [x.strip() for x in name.split(",", 1)]
    else:
        family, given = "李", "毅芃"
    return {"person_or_org": {"type": "personal", "name": "%s%s" % (family, given),
                              "given_name": given, "family_name": family},
            "affiliations": [{"name": (c or {}).get("affiliation") or
                              "独立研究者 / Independent Researcher"}]}


def rel_rdm(r):
    raw = r.get("relation_type") or r.get("relation") or "issupplementedby"
    rid = raw.get("id") if isinstance(raw, dict) else str(raw)
    rid = rid.lower().replace("_", "")
    if rid not in REL_MAP:
        rid = "issupplementedby"
    return {"identifier": r["identifier"],
            "scheme": r.get("scheme") or ("doi" if str(r["identifier"]).startswith("10.") else "url"),
            "relation_type": {"id": rid}}


def rtype(m):
    rt = m.get("resource_type") or {}
    if isinstance(rt, str):
        return {"id": rt}
    if rt.get("subtype"):
        return {"id": "publication-%s" % rt["subtype"]}
    return {"id": "publication-preprint"}


def build(slug, rid):
    _, pub = api.req("GET", "https://zenodo.org/api/records/%s" % rid, tries=3, timeout=120)
    m = pub["metadata"]
    kws = keywords_of(slug) or (m.get("keywords") or [])
    meta = {
        "title": m["title"],
        "description": m.get("description") or "",
        "creators": [creator_rdm(c) for c in (m.get("creators") or [])] or
                    [{"person_or_org": {"type": "personal", "name": "李毅芃",
                                        "given_name": "毅芃", "family_name": "李"},
                      "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}],
        "publication_date": m.get("publication_date"),
        "version": m.get("version"),
        "resource_type": rtype(m),
        "rights": [LIC],
        "subjects": [{"subject": k} for k in kws][:24],
        "languages": [{"id": "zho"}],
        "publisher": PUBLISHER,
        "related_identifiers": [rel_rdm(r) for r in (m.get("related_identifiers") or [])],
    }
    return meta


def fix(slug, rid, do=True):
    meta = build(slug, rid)
    print("%-24s %s | kw=%d rel=%d rt=%s ver=%s" %
          (slug, rid, len(meta["subjects"]), len(meta["related_identifiers"]),
           meta["resource_type"]["id"], meta["version"]), flush=True)
    if not do:
        return
    # 1) 建（或取回）元数据草稿
    try:
        api.req("POST", "https://zenodo.org/api/records/%s/draft" % rid, tries=1, timeout=90)
    except Exception:
        pass
    # 2) PUT 元数据
    for i in range(3):
        try:
            api.req("PUT", "https://zenodo.org/api/records/%s/draft" % rid,
                    data={"metadata": meta}, tries=2, timeout=300)
            break
        except Exception as e:
            if i == 2:
                raise
            print("   retry meta PUT:", str(e)[:100], flush=True)
            time.sleep(5)
    # 3) 发布元数据修改（不产生新版本、DOI 不变）
    _, r = api.req("POST", "https://zenodo.org/api/records/%s/draft/actions/publish" % rid,
                   tries=2, timeout=300)
    got = r.get("metadata") or {}
    print("   → license=%s keywords=%d creators=%s" %
          (json.dumps(got.get("license") or got.get("rights"), ensure_ascii=False),
           len(got.get("keywords") or got.get("subjects") or []), bool(got.get("creators"))), flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "go" and len(sys.argv) > 2 and sys.argv[2] == "all":
        cmd = "all"; sys.argv = sys.argv[:2]
    g = {w["slug"]: w for w in works()}
    if cmd == "all":
        todo = [(s, w["记录ID"]) for s, w in g.items()
                if s != "合集23" and not w.get("有许可")]
        # 用线上状态判断，而不是 registry 标记
        todo = []
        for s, w in g.items():
            if s == "合集23":
                continue
            _, d = api.req("GET", "https://zenodo.org/api/records/%s" % w["记录ID"], tries=3, timeout=120)
            if not (d["metadata"].get("license") or d["metadata"].get("rights")):
                todo.append((s, w["记录ID"]))
        print("待补许可：", len(todo), flush=True)
        for s, rid in todo:
            fix(s, rid, do=(cmd == "all" and "--dry" not in sys.argv))
    else:
        do = (cmd == "go")
        for s in sys.argv[2:]:
            fix(s, g[s]["记录ID"], do=do)

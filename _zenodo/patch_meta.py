# -*- coding: utf-8 -*-
"""改已发布记录的元数据（不发新版本、DOI 不变）：描述、关联、许可、关键词。

用法：
    python _zenodo/patch_meta.py <slug> [--desc 文件] [--rel mono|book3|coll] [--dry]

关联规则（AGENTS.md §6b）：
    mono  —— 六本学术专著：只关联自身仓库
    book3 —— 其余三本（只能选两样 / 心灵的分岔 / 热点的账单）：自身仓库 + 共用库 + 六本专著的新版本 DOI
    coll  —— 合集：共用库 + 六本专著的新版本 DOI

注意：RDM 只认 metadata.rights / subjects / languages；写 legacy 的 license / keywords 会被静默丢弃。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api
import fix_rights_subjects as fx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = ["10.5281/zenodo.23771608", "10.5281/zenodo.23771832", "10.5281/zenodo.23771933",
        "10.5281/zenodo.23772040", "10.5281/zenodo.23771397", "10.5281/zenodo.23772106"]
SHARED = "https://github.com/lyp0746/series-workspace"


def relations(slug, rule):
    R = lambda ident, rel: {"identifier": ident,
                            "scheme": "doi" if ident.startswith("10.") else "url",
                            "relation_type": {"id": rel}}
    out = []
    if rule == "mono":
        out.append(R("https://github.com/lyp0746/%s" % slug, "issupplementedby"))
        return out
    if rule == "book3":
        out.append(R("https://github.com/lyp0746/%s" % slug, "issupplementedby"))
    out.append(R(SHARED, "issupplementedby"))
    out += [R(d, "ispartof") for d in MONO]
    return out


def main(argv):
    slug = argv[1]
    desc = rel_rule = None
    dry = "--dry" in argv
    if "--desc" in argv:
        desc = io.open(os.path.join(ROOT, "_zenodo", "desc", argv[argv.index("--desc") + 1]),
                       encoding="utf-8").read().strip()
    if "--rel" in argv:
        rel_rule = argv[argv.index("--rel") + 1]
    rid = fx.works() and {w["slug"]: w for w in fx.works()}[slug]["记录ID"]
    meta = fx.build(slug, rid)
    if desc:
        meta["description"] = desc
    if rel_rule:
        meta["related_identifiers"] = relations(slug, rel_rule)
    print("%-24s %s | desc %d | rel %d (%s) | kw %d" %
          (slug, rid, len(meta["description"]), len(meta["related_identifiers"]),
           rel_rule or "keep", len(meta["subjects"])), flush=True)
    if dry:
        return
    try:
        api.req("POST", "https://zenodo.org/api/records/%s/draft" % rid, tries=1, timeout=90)
    except Exception:
        pass
    api.req("PUT", "https://zenodo.org/api/records/%s/draft" % rid,
            data={"metadata": meta}, tries=2, timeout=300)
    _, r = api.req("POST", "https://zenodo.org/api/records/%s/draft/actions/publish" % rid,
                   tries=2, timeout=300)
    got = r.get("metadata") or {}
    print("   → license=%s kw=%d rel=%d desc[:0]=%d stars=%d" %
          (json.dumps(got.get("license") or got.get("rights"), ensure_ascii=False)[:40],
           len(got.get("keywords") or got.get("subjects") or []),
           len(got.get("related_identifiers") or []),
           len(got.get("description") or ""),
           (got.get("description") or "").count("*")), flush=True)


if __name__ == "__main__":
    main(sys.argv)

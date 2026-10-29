# -*- coding: utf-8 -*-
"""把论文标题补成中英双语（取历史版本里最长的双语标题），并把 creators 改为 RDM 形态。"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}

def versions(concept):
    try:
        _, d = api.req("GET", f"https://zenodo.org/api/records?q=conceptdoi:{concept}&size=25&sort=mostrecent", tries=2, timeout=90)
        return d["hits"]["hits"]
    except Exception:
        return []

def fix(slug, concept, rid):
    best = None
    for v in versions(concept):
        t = v["metadata"]["title"]
        if " / " in t and (best is None or len(t) > len(best)):
            best = t
    if best is None:
        for v in versions(concept):
            t = v["metadata"]["title"]
            if best is None or len(t) > len(best): best = t
    try:
        try: api.req("POST", f"https://zenodo.org/api/records/{rid}/draft", tries=1, timeout=90)
        except Exception: pass
        _, d = api.req("GET", f"https://zenodo.org/api/records/{rid}/draft", tries=2, timeout=90)
        m = d["metadata"]
        meta = {"title": best or m["title"], "description": m["description"],
                "creators": [CREATOR], "publication_date": m.get("publication_date") or "2026-10-30",
                "version": m.get("version") or "2026-10-30",
                "resource_type": m.get("resource_type") if isinstance(m.get("resource_type"), dict) else {"id": "publication-preprint"},
                "license": {"id": "cc-by-4.0"}, "languages": [{"id": "zho"}],
                "related_identifiers": [{"identifier": "https://github.com/lyp0746/series-workspace",
                                          "scheme": "url", "relation_type": {"id": "issupplementedby"}}] +
                     [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}}
                      for v in MONO.values()],
                "publisher": "Zenodo", "keywords": (m.get("keywords") or [])[:20]}
        if isinstance(meta["resource_type"], dict) and "id" not in meta["resource_type"]:
            meta["resource_type"] = {"id": "publication-preprint"}
        api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta}, tries=2, timeout=120)
        api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish", tries=2, timeout=120)
        print(f"{slug:24} OK 双语={' / ' in meta['title']} 长度={len(meta['title'])}", flush=True)
    except Exception as e:
        print(f"{slug:24} 失败 {str(e)[:160]}", flush=True)

if __name__ == "__main__":
    reg = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
    for slug in sys.argv[1:]:
        fix(slug, reg[slug]["概念DOI"], reg[slug]["记录ID"])

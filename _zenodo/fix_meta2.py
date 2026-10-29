# -*- coding: utf-8 -*-
"""用 records 编辑草稿修已发布记录的元数据（不改文件、不产生新版本）。"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
from desc_mindforks import MF
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = "https://github.com/lyp0746/series-workspace"
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}

def title_of(slug, is_paper):
    t = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    zh = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M).group(1).strip().strip('"')
    if " / " in zh: return zh
    en = re.search(r'^title-en:\s*"?(.+?)"?\s*$', t, re.M)
    return f"{zh} / {en.group(1).strip().strip('\"')}" if en else zh

def rel_of(slug, kind):
    R = lambda i, rt: {"identifier": i, "scheme": "doi" if i.startswith("10.") else "url",
                       "relation_type": {"id": rt}}
    if kind == "mono":
        return [R(f"https://github.com/lyp0746/{slug}", "issupplementedby")]
    if kind == "book3":
        return [R(f"https://github.com/lyp0746/{slug}", "issupplementedby")] + \
               [R(d, "ispartof") for d in MONO.values()]
    return [R(SHARED, "issupplementedby")] + [R(d, "ispartof") for d in MONO.values()]

def patch(rid, slug, kind, rtype):
    try:
        api.req("POST", f"https://zenodo.org/api/records/{rid}/draft")
    except Exception:
        pass
    _, d = api.req("GET", f"https://zenodo.org/api/records/{rid}/draft")
    m = d["metadata"]
    meta = {
        "title": title_of(slug, kind == "paper"),
        "description": MF if slug == "mind-forks" else m["description"],
        "creators": [CREATOR],
        "publication_date": "2026-10-30", "version": "2026-10-30",
        "resource_type": {"id": rtype},
        "license": {"id": "cc-by-4.0"},
        "languages": [{"id": "zho"}],
        "related_identifiers": rel_of(slug, kind),
        "publisher": "Zenodo",
        "keywords": m.get("keywords", [])[:20],
    }
    api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta})
    _, pub = api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish")
    return pub.get("doi"), len(meta["related_identifiers"])

ITEMS = [("entropy-spiral",23771608,"mono"),("capacity-cascade",23771832,"mono"),
         ("distinction-evolution",23771933,"mono"),("impossibility-triangle",23772040,"mono"),
         ("interpretation-tradeoff",23771397,"mono"),("emergence-critical",23772106,"mono"),
         ("knowledge-tradeoffs",23772341,"book3"),("mind-forks",23772399,"book3"),
         ("hotspot-bills",23772473,"book3"),
         ("ComputingDemystified",23772792,"paper"),("WorldPeriodization",23772831,"paper"),
         ("SleepingResidue",23773215,"paper")]
if __name__ == "__main__":
    for slug, rid, kind in ITEMS:
        rtype = "publication-book" if kind != "paper" else "publication-preprint"
        try:
            doi, n = patch(rid, slug, kind, rtype)
            print(f"{slug:24} OK  {doi}  关联 {n}", flush=True)
        except Exception as e:
            print(f"{slug:24} 失败 {str(e)[:220]}", flush=True)

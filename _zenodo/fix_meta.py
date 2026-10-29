# -*- coding: utf-8 -*-
"""修已发布记录的元数据（不产生新版本）：标题含英文、描述补全、关联指向共用库/六本专著。"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
from desc_mindforks import MF
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = "https://github.com/lyp0746/series-workspace"
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
BOOKS3 = ["knowledge-tradeoffs","mind-forks","hotspot-bills"]
PAPERS = ["ComputingDemystified","WorldPeriodization","SleepingResidue","HunanRelaySystem",
          "BureauRotationCession","HarnessEcology","OptimizationBoundary","CapacityProxies",
          "DomainCrossSection","IsomorphismStrength","MemoryAnchor","MemoryStressTest",
          "LedgerReconciliation","MonarchCompetition"]

def title_of(slug, is_paper):
    t = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    zh = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M).group(1).strip()
    if not is_paper or " / " in zh:
        return zh
    en = re.search(r'^title-en:\s*"?(.+?)"?\s*$', t, re.M)
    return f"{zh} / {en.group(1).strip()}" if en else zh

def related(slug, kind):
    if kind == "mono":
        return [{"identifier": f"https://github.com/lyp0746/{slug}", "relation": "isSupplementedBy", "scheme": "url"}]
    if kind == "book3":
        rel = [{"identifier": f"https://github.com/lyp0746/{slug}", "relation": "isSupplementedBy", "scheme": "url"}]
        rel += [{"identifier": d, "relation": "isPartOf", "scheme": "doi"} for d in MONO.values()]
        return rel
    rel = [{"identifier": SHARED, "relation": "isSupplementedBy", "scheme": "url"}]
    rel += [{"identifier": d, "relation": "isPartOf", "scheme": "doi"} for d in MONO.values()]
    return rel

def patch(rid, slug, kind):
    st, d = api.req("GET", f"https://zenodo.org/api/deposit/depositions/{rid}")
    m = d["metadata"]
    is_paper = kind == "paper"
    m["title"] = title_of(slug, is_paper)
    if slug == "mind-forks":
        m["description"] = MF
    m["related_identifiers"] = related(slug, kind)
    m["publication_date"] = "2026-10-30"
    m["version"] = "2026-10-30"
    st2, r2 = api.req("PUT", f"https://zenodo.org/api/deposit/depositions/{rid}", data={"metadata": m})
    print(f"{slug:24} {st2}  {m['title'][:40]}  关联 {len(m['related_identifiers'])}")

if __name__ == "__main__":
    items = [("entropy-spiral","mono"),("capacity-cascade","mono"),("distinction-evolution","mono"),
             ("impossibility-triangle","mono"),("interpretation-tradeoff","mono"),("emergence-critical","mono"),
             ("knowledge-tradeoffs","book3"),("mind-forks","book3"),("hotspot-bills","book3"),
             ("ComputingDemystified","paper"),("WorldPeriodization","paper"),("SleepingResidue","paper")]
    for slug, kind in items:
        patch({"entropy-spiral":23771608,"capacity-cascade":23771832,"distinction-evolution":23771933,
               "impossibility-triangle":23772040,"interpretation-tradeoff":23771397,"emergence-critical":23772106,
               "knowledge-tradeoffs":23772341,"mind-forks":23772399,"hotspot-bills":23772473,
               "ComputingDemystified":23772792,"WorldPeriodization":23772831,"SleepingResidue":23773215}[slug], slug, kind)

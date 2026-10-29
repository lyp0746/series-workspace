# -*- coding: utf-8 -*-
"""从旧版记录取回完整中英双语标题，写到新版记录（元数据编辑，不产生新版本）。"""
import io, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
from fix_tc import CREATOR, MONO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fix(slug, old_id, new_id):
    _, old = api.req("GET", f"https://zenodo.org/api/records/{old_id}", tries=2, timeout=90)
    title = old["metadata"]["title"]
    try: api.req("POST", f"https://zenodo.org/api/records/{new_id}/draft", tries=1, timeout=90)
    except Exception: pass
    _, d = api.req("GET", f"https://zenodo.org/api/records/{new_id}/draft", tries=2, timeout=90)
    m = d["metadata"]
    meta = {"title": title, "description": m["description"], "creators": [CREATOR],
            "publication_date": m.get("publication_date"), "version": m.get("version"),
            "resource_type": {"id": "publication-preprint"},
            "license": {"id": "cc-by-4.0"}, "languages": [{"id": "zho"}],
            "related_identifiers": [{"identifier": "https://github.com/lyp0746/series-workspace",
                                     "scheme": "url", "relation_type": {"id": "issupplementedby"}}] +
                [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()],
            "publisher": "Zenodo", "keywords": (m.get("keywords") or [])[:20]}
    api.req("PUT", f"https://zenodo.org/api/records/{new_id}/draft", data={"metadata": meta}, tries=2, timeout=120)
    api.req("POST", f"https://zenodo.org/api/records/{new_id}/draft/actions/publish", tries=2, timeout=120)
    print(f"{slug:24} 双语={' / ' in title}  {title[:50]}", flush=True)

if __name__ == "__main__":
    P = [("ComputingDemystified",23602360),("WorldPeriodization",23602364),("SleepingResidue",23603016),
         ("HunanRelaySystem",23601983),("BureauRotationCession",23602311),("HarnessEcology",23603015),
         ("OptimizationBoundary",23611782),("CapacityProxies",23611799),("DomainCrossSection",23695806),
         ("IsomorphismStrength",23695810),("MemoryAnchor",23665882),("MemoryStressTest",23667929),
         ("LedgerReconciliation",23695813),("MonarchCompetition",23695757)]
    reg = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
    want = sys.argv[1:]
    for slug, old in P:
        if want and slug not in want: continue
        fix(slug, old, reg[slug]["记录ID"])

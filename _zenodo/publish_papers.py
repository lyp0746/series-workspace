# -*- coding: utf-8 -*-
"""发布/重发十四篇论文：文件来自各自 release/；标题含英文；关联共用库 + 六本专著 DOI。"""
import io, json, os, re, sys, glob, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
from common import title_of, MONO, SHARED
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = "2026-10-30"
PAPERS = ["ComputingDemystified","WorldPeriodization","SleepingResidue","HunanRelaySystem",
          "BureauRotationCession","HarnessEcology","OptimizationBoundary","CapacityProxies",
          "DomainCrossSection","IsomorphismStrength","MemoryAnchor","MemoryStressTest",
          "LedgerReconciliation","MonarchCompetition"]

def upload(dep, folder):
    _, d = api.req("GET", f"https://zenodo.org/api/deposit/depositions/{dep}")
    bucket = d["links"]["bucket"]
    for f in d.get("files", []):
        api.req("DELETE", f"https://zenodo.org/api/deposit/depositions/{dep}/files/{f['id']}")
    n = 0
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        if not os.path.isfile(p): continue
        r = urllib.request.Request(f"{bucket}/{urllib.parse.quote(os.path.basename(p))}",
            data=open(p, "rb").read(), method="PUT",
            headers={"Authorization": "Bearer " + api.TOK, "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x:
            x.read(); n += 1
    return n

if __name__ == "__main__":
    reg = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
    for slug in PAPERS:
        rid = reg[slug]["记录ID"]
        _, rec = api.req("GET", f"https://zenodo.org/api/records/{rid}")
        descr = rec["metadata"]["description"]
        try:
            _, d = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{rid}/actions/newversion")
            _, d2 = api.req("GET", d["links"]["latest_draft"]); did = d2["id"]
            n = upload(did, os.path.join(ROOT, slug, "release"))
            meta = {"upload_type": "publication", "publication_type": "preprint",
                    "title": title_of(slug, True), "description": descr,
                    "creators": [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}],
                    "publication_date": DATE, "version": DATE, "access_right": "open",
                    "license": "cc-by-4.0", "language": "zho",
                    "related_identifiers":
                        [{"identifier": SHARED, "relation": "isSupplementedBy", "scheme": "url"}] +
                        [{"identifier": v, "relation": "isPartOf", "scheme": "doi"} for v in MONO.values()]}
            api.req("PUT", f"https://zenodo.org/api/deposit/depositions/{did}", data={"metadata": meta})
            _, pub = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{did}/actions/publish")
            print(f"{slug:24} {pub.get('doi')}  文件 {n}", flush=True)
        except Exception as e:
            print(f"{slug:24} 失败 {str(e)[:180]}", flush=True)

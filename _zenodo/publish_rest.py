# -*- coding: utf-8 -*-
"""发布其余三本书与十四篇论文：related_identifiers = 六本专著 DOI + 各自仓库（书）／系列入口（论文）。"""
import io, json, os, re, sys, glob, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
from publish_v import state, desc, DATE, ROOT

MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
BOOKS3 = ["knowledge-tradeoffs","mind-forks","hotspot-bills"]
PAPERS = ["ComputingDemystified","WorldPeriodization","SleepingResidue","HunanRelaySystem",
          "BureauRotationCession","HarnessEcology","OptimizationBoundary","CapacityProxies",
          "DomainCrossSection","IsomorphismStrength","MemoryAnchor","MemoryStressTest",
          "LedgerReconciliation","MonarchCompetition"]

def series_rel(slug):
    rel=[{"identifier":d,"relation":"isPartOf","scheme":"doi"} for d in MONO.values()]
    rel.append({"identifier":"https://github.com/lyp0746/knowledge-tradeoffs","relation":"isPartOf","scheme":"url"})
    if slug in BOOKS3:
        rel.insert(0,{"identifier":f"https://github.com/lyp0746/{slug}","relation":"isSupplementedBy","scheme":"url"})
    return rel

def upload(dep_id, folder):
    _, d = api.req("GET", "https://zenodo.org/api/deposit/depositions/%s" % dep_id)
    bucket = d["links"]["bucket"]
    for f in d.get("files", []):
        api.req("DELETE", "https://zenodo.org/api/deposit/depositions/%s/files/%s" % (dep_id, f["id"]))
    n = 0
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        if not os.path.isfile(p): continue
        r = urllib.request.Request(f"{bucket}/{urllib.parse.quote(os.path.basename(p))}", data=open(p,'rb').read(),
                                   method="PUT", headers={"Authorization":"Bearer "+api.TOK,
                                   "Content-Type":"application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x: x.read(); n += 1
    return n

if __name__ == "__main__":
    reg={w["slug"]:w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
    for slug in BOOKS3+PAPERS:
        rid=reg[slug]["记录ID"]
        is_book = slug in BOOKS3
        cff=io.open(os.path.join(ROOT,slug,"CITATION.cff"),encoding="utf-8").read()
        title=re.search(r'^title:\s*"(.+?)"\s*$',cff,re.M).group(1)
        if is_book:
            st=state(slug); description=desc(slug,st); folder=os.path.join(ROOT,slug,"release")
            upload_type, pub_type = "publication","book"
        else:
            pub=os.path.join(ROOT,slug,".pub"); os.makedirs(pub,exist_ok=True)
            for f in os.listdir(os.path.join(ROOT,slug)):
                if f.endswith((".pdf",".html",".md")) and not f.startswith("_"):
                    import shutil; shutil.copy(os.path.join(ROOT,slug,f), os.path.join(pub,f))
            folder=pub
            _,rec=api.req("GET",f"https://zenodo.org/api/records/{rid}")
            description=rec["metadata"]["description"]; upload_type, pub_type = "publication","preprint"
        _,d=api.req("POST",f"https://zenodo.org/api/deposit/depositions/{rid}/actions/newversion")
        _,d2=api.req("GET",d["links"]["latest_draft"]); did=d2["id"]
        n=upload(did, folder)
        meta={"upload_type":upload_type,"publication_type":pub_type,"title":title,
              "description":description,"creators":[{"name":"李毅芃","affiliation":"独立研究者 / Independent Researcher"}],
              "publication_date":DATE,"version":DATE,"access_right":"open","license":"cc-by-4.0","language":"zho",
              "related_identifiers":series_rel(slug)}
        api.req("PUT",f"https://zenodo.org/api/deposit/depositions/{did}",data={"metadata":meta})
        _,pub=api.req("POST",f"https://zenodo.org/api/deposit/depositions/{did}/actions/publish")
        print(f"{slug:24} {pub.get('doi')}  文件 {n}", flush=True)

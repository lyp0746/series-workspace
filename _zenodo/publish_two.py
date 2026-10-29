# -*- coding: utf-8 -*-
"""只更新这两篇：容量的三个代理、优化的边界（新版本，文件取自 release/）。"""
import io, json, os, re, sys, glob, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
SHARED = "https://github.com/lyp0746/series-workspace"
TARGETS = {"CapacityProxies": 23774073, "OptimizationBoundary": 23774015}

def descr(slug):
    t = io.open(os.path.join(ROOT, slug, "source", "paper.md"), encoding="utf-8").read()
    zh = re.search(r"(?ms)^## 摘要\s*\n(.*?)^## ", t).group(1).strip()
    en = re.search(r"(?ms)^## Abstract\s*\n(.*?)^## ", t).group(1).strip()
    fix = lambda s: re.sub(r"\n(?=[^\n])", " ", s)
    return f"<p><b>中文摘要。</b>{fix(zh)}</p>\n<p><b>Abstract (English).</b> {fix(en)}</p>"

def title_of(slug):
    for line in io.open(os.path.join(ROOT, "inventory.tsv"), encoding="utf-8"):
        c = line.split("\t")
        if len(c) > 3 and c[1] == slug: return c[3].strip()

def upload(dep, folder):
    _, d = api.req("GET", f"https://zenodo.org/api/deposit/depositions/{dep}", tries=2, timeout=90)
    bucket = d["links"]["bucket"]
    for f in d.get("files", []):
        api.req("DELETE", f"https://zenodo.org/api/deposit/depositions/{dep}/files/{f['id']}", tries=1, timeout=60)
    n = 0
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        if not os.path.isfile(p): continue
        r = urllib.request.Request(f"{bucket}/{urllib.parse.quote(os.path.basename(p))}",
            data=open(p, "rb").read(), method="PUT",
            headers={"Authorization": "Bearer " + api.TOK, "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x:
            x.read(); n += 1
    return n

for slug, rid in TARGETS.items():
    _, d = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{rid}/actions/newversion", tries=2, timeout=120)
    _, d2 = api.req("GET", d["links"]["latest_draft"], tries=2, timeout=120)
    did = d2["id"]
    n = upload(did, os.path.join(ROOT, slug, "release"))
    meta = {"upload_type": "publication", "publication_type": "preprint",
            "title": title_of(slug), "description": descr(slug),
            "creators": [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}],
            "publication_date": "2026-10-30", "version": "2026-10-30",
            "access_right": "open", "license": "cc-by-4.0", "language": "zho",
            "related_identifiers": [{"identifier": SHARED, "relation": "isSupplementedBy", "scheme": "url"}] +
                [{"identifier": v, "relation": "isPartOf", "scheme": "doi"} for v in MONO.values()]}
    api.req("PUT", f"https://zenodo.org/api/deposit/depositions/{did}", data={"metadata": meta}, tries=2, timeout=180)
    _, pub = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{did}/actions/publish", tries=2, timeout=180)
    print(f"{slug:24} {pub.get('doi')}  文件 {n}  描述 {len(meta['description'])}", flush=True)

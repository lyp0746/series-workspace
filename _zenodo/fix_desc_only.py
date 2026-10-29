# -*- coding: utf-8 -*-
"""只改描述（元数据编辑，不发新版本）。"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
SHARED = "https://github.com/lyp0746/series-workspace"
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}

def descr(slug):
    t = io.open(os.path.join(ROOT, slug, "source", "paper.md"), encoding="utf-8").read()
    zh = re.search(r"(?ms)^## 摘要\s*\n(.*?)^## ", t).group(1).strip()
    en = re.search(r"(?ms)^## Abstract\s*\n(.*?)^## ", t).group(1).strip()
    fix = lambda s: re.sub(r"\n(?=[^\n])", " ", s)
    return f"<p><b>中文摘要。</b>{fix(zh)}</p>\n<p><b>Abstract (English).</b> {fix(en)}</p>"

for rid, slug in ((23774073, "CapacityProxies"), (23774015, "OptimizationBoundary")):
    try:
        api.req("POST", f"https://zenodo.org/api/records/{rid}/draft", tries=1, timeout=90)
    except Exception:
        pass
    _, d = api.req("GET", f"https://zenodo.org/api/records/{rid}/draft", tries=2, timeout=90)
    m = d["metadata"]
    meta = {"title": m["title"], "description": descr(slug), "creators": [CREATOR],
            "publication_date": m.get("publication_date"), "version": m.get("version"),
            "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
            "languages": [{"id": "zho"}],
            "related_identifiers": [{"identifier": SHARED, "scheme": "url",
                                     "relation_type": {"id": "issupplementedby"}}] +
                [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()],
            "publisher": "Zenodo", "keywords": (m.get("keywords") or [])[:20]}
    api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta}, tries=2, timeout=120)
    api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish", tries=2, timeout=120)
    print(f"{slug:22} 描述已更新（{len(meta['description'])} 字符）", flush=True)

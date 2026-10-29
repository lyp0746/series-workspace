# -*- coding: utf-8 -*-
"""用 RDM 的 /versions 接口发新版本（文件白名单 + 统一描述）。"""
import io, json, os, re, sys, glob, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
from pypdf import PdfReader
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
SHARED = "https://github.com/lyp0746/series-workspace"
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}

def title_of(slug):
    for line in io.open(os.path.join(ROOT, "inventory.tsv"), encoding="utf-8"):
        c = line.split("\t")
        if len(c) > 3 and c[1] == slug: return c[3].strip()

def descr(slug):
    t = io.open(os.path.join(ROOT, slug, "source", "paper.md"), encoding="utf-8").read()
    zh = re.search(r"(?ms)^## 摘要\s*\n(.*?)^## ", t).group(1).strip()
    en = re.search(r"(?ms)^## Abstract\s*\n(.*?)^## ", t).group(1).strip()
    fix = lambda s: re.sub(r"\n(?=[^\n])", " ", s)
    pdf = [f for f in glob.glob(os.path.join(ROOT, slug, "release", "*.pdf"))][0]
    pages = len(PdfReader(pdf).pages)
    figs = len(glob.glob(os.path.join(ROOT, slug, "release", "*.png")))
    return (f"<p><b>中文摘要。</b>{fix(zh)}</p>\n"
            f"<p><b>Abstract (English).</b> {fix(en)}</p>\n"
            f"<p><b>Files.</b>论文（PDF {pages} 页 / HTML / Markdown / README）；{figs} 幅图；"
            f"<code>MANIFEST.txt</code>。数据表与可复算脚本在仓库中，可逐项重跑。</p>\n"
            f"<p><b>系列 / Series。</b>同一作者的独立研究系列：九本书与十四篇工作论文。"
            f"<b>系列入口与外部登记库：</b>https://github.com/lyp0746/knowledge-tradeoffs；"
            f"工作区、源文件与复现脚本：https://github.com/lyp0746/series-workspace</p>")

def upload_rdm(rec_id, folder):
    for f in sorted(glob.glob(os.path.join(folder, "*"))):
        if not os.path.isfile(f): continue
        key = os.path.basename(f)
        api.req("POST", f"https://zenodo.org/api/records/{rec_id}/draft/files",
                data=[{"key": key}], tries=2, timeout=90)
        r = urllib.request.Request(f"https://zenodo.org/api/records/{rec_id}/draft/files/{urllib.parse.quote(key)}/content",
            data=open(f, "rb").read(), method="PUT",
            headers={"Authorization": "Bearer " + api.TOK, "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x: x.read()
    api.req("POST", f"https://zenodo.org/api/records/{rec_id}/draft/files/commit", tries=2, timeout=180)

if __name__ == "__main__":
    JOBS = [("CapacityProxies", 23774073, 23778062), ("OptimizationBoundary", 23774015, None)]
    for slug, rid, reuse in JOBS:
        if reuse:
            new_id = reuse
        else:
            st, d = api.req("POST", f"https://zenodo.org/api/records/{rid}/versions", tries=2, timeout=120)
            new_id = d.get("id") or d.get("links", {}).get("self", "").rstrip("/").split("/")[-1]
        upload_rdm(new_id, os.path.join(ROOT, slug, "release"))
        meta = {"title": title_of(slug), "description": descr(slug), "creators": [CREATOR],
                "publication_date": "2026-10-30", "version": "2026-10-30",
                "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
                "languages": [{"id": "zho"}], "publisher": "Zenodo",
                "related_identifiers": [{"identifier": SHARED, "scheme": "url",
                                         "relation_type": {"id": "issupplementedby"}}] +
                    [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()]}
        api.req("PUT", f"https://zenodo.org/api/records/{new_id}/draft", data={"metadata": meta}, tries=2, timeout=180)
        _, pub = api.req("POST", f"https://zenodo.org/api/records/{new_id}/draft/actions/publish", tries=2, timeout=180)
        print(f"{slug:22} {pub.get('doi')}  新记录 {new_id}", flush=True)

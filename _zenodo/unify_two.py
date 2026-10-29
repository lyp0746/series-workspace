# -*- coding: utf-8 -*-
"""把两篇的元信息写成与其余论文一致的形式（只改元数据，不发新版本）。"""
import io, json, os, re, sys, glob
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
TARGETS = {"CapacityProxies": 23774073, "OptimizationBoundary": 23774015}

def build_desc(slug):
    t = io.open(os.path.join(ROOT, slug, "source", "paper.md"), encoding="utf-8").read()
    zh = re.search(r"(?ms)^## 摘要\s*\n(.*?)^## ", t).group(1).strip()
    en = re.search(r"(?ms)^## Abstract\s*\n(.*?)^## ", t).group(1).strip()
    fix = lambda s: re.sub(r"\n(?=[^\n])", " ", s)
    pdf = sorted(glob.glob(os.path.join(ROOT, slug, "release", "*.pdf")))[0]
    pages = len(PdfReader(pdf).pages)
    figs = len(glob.glob(os.path.join(ROOT, slug, "release", "*.png")))
    files = (f"<p><b>Files.</b>论文（PDF {pages} 页 / HTML / Markdown / README）；{figs} 幅图；"
             f"<code>MANIFEST.txt</code>。数据表与可复算脚本在仓库中，可逐项重跑。</p>")
    series = ("<p><b>系列 / Series。</b>同一作者的独立研究系列：九本书与十四篇工作论文。"
              "<b>系列入口与外部登记库：</b>https://github.com/lyp0746/knowledge-tradeoffs；"
              "工作区、源文件与复现脚本：https://github.com/lyp0746/series-workspace</p>")
    return (f"<p><b>中文摘要。</b>{fix(zh)}</p>\n"
            f"<p><b>Abstract (English).</b> {fix(en)}</p>\n{files}\n{series}")

for slug, rid in TARGETS.items():
    try: api.req("POST", f"https://zenodo.org/api/records/{rid}/draft", tries=1, timeout=90)
    except Exception: pass
    _, d = api.req("GET", f"https://zenodo.org/api/records/{rid}/draft", tries=2, timeout=90)
    m = d["metadata"]
    meta = {"title": m["title"], "description": build_desc(slug), "creators": [CREATOR],
            "publication_date": "2026-10-30", "version": "2026-10-30",
            "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
            "languages": [{"id": "zho"}],
            "related_identifiers": [{"identifier": SHARED, "scheme": "url",
                                     "relation_type": {"id": "issupplementedby"}}] +
                [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()],
            "publisher": "Zenodo"}
    api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta}, tries=2, timeout=120)
    api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish", tries=2, timeout=120)
    print(f"{slug:22} 完成：描述 {len(meta['description'])} 字符 / 关联 {len(meta['related_identifiers'])}", flush=True)

# -*- coding: utf-8 -*-
"""修这两篇的元数据：完整中英标题 + 描述里把 Markdown 记号转成 HTML（不留 *）。"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
from pypdf import PdfReader
import glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = {"entropy-spiral":"10.5281/zenodo.23771608","capacity-cascade":"10.5281/zenodo.23771832",
        "distinction-evolution":"10.5281/zenodo.23771933","impossibility-triangle":"10.5281/zenodo.23772040",
        "interpretation-tradeoff":"10.5281/zenodo.23771397","emergence-critical":"10.5281/zenodo.23772106"}
SHARED = "https://github.com/lyp0746/series-workspace"
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}

def md2html(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![A-Za-z])_([^_\n]+?)_(?![A-Za-z])", r"<i>\1</i>", s)
    s = s.replace("*", "")
    return s

def descr(slug):
    t = io.open(os.path.join(ROOT, slug, "source", "paper.md"), encoding="utf-8").read()
    zh = re.search(r"(?ms)^## 摘要\s*\n(.*?)^## ", t).group(1).strip()
    en = re.search(r"(?ms)^## Abstract\s*\n(.*?)^## ", t).group(1).strip()
    flat = lambda s: re.sub(r"\n(?=[^\n])", " ", s)
    pdf = glob.glob(os.path.join(ROOT, slug, "release", "*.pdf"))[0]
    pages = len(PdfReader(pdf).pages)
    figs = len(glob.glob(os.path.join(ROOT, slug, "release", "*.png")))
    return (f"<p><b>中文摘要。</b>{md2html(flat(zh))}</p>\n"
            f"<p><b>Abstract (English).</b> {md2html(flat(en))}</p>\n"
            f"<p><b>Files.</b>论文（PDF {pages} 页 / HTML / Markdown / README）；{figs} 幅图；"
            f"<code>MANIFEST.txt</code>。数据表与可复算脚本在仓库中，可逐项重跑。</p>\n"
            f"<p><b>系列 / Series。</b>同一作者的独立研究系列：九本书与十四篇工作论文。"
            f"<b>系列入口与外部登记库：</b>https://github.com/lyp0746/knowledge-tradeoffs；"
            f"工作区、源文件与复现脚本：https://github.com/lyp0746/series-workspace</p>")

JOBS = [("CapacityProxies", "23778062", "23611799"), ("OptimizationBoundary", "23778157", "23611782")]
for slug, rid, old in JOBS:
    _, o = api.req("GET", f"https://zenodo.org/api/records/{old}", tries=2, timeout=90)
    title = o["metadata"]["title"]
    try: api.req("POST", f"https://zenodo.org/api/records/{rid}/draft", tries=1, timeout=90)
    except Exception: pass
    meta = {"title": title, "description": descr(slug), "creators": [CREATOR],
            "publication_date": "2026-10-30", "version": "2026-10-30",
            "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
            "languages": [{"id": "zho"}], "publisher": "Zenodo",
            "related_identifiers": [{"identifier": SHARED, "scheme": "url",
                                     "relation_type": {"id": "issupplementedby"}}] +
                [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()]}
    api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta}, tries=2, timeout=180)
    api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish", tries=2, timeout=180)
    print(f"{slug:22} 标题{len(title)}字 描述{len(meta['description'])}字 星号{meta['description'].count('*')}", flush=True)

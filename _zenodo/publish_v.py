# -*- coding: utf-8 -*-
"""发布新版本（RDM 形态）：薄驱动，实际动作在 republish_book.py。

用法：
    python _zenodo/publish_v.py dry  <slug>...
    python _zenodo/publish_v.py go   <slug>...

为什么改成薄驱动（2026-10-31）
------------------------------
旧版本走 `POST /deposit/depositions/{id}/actions/newversion` 建草稿，再把 **legacy 键名**
（`metadata.license` / `metadata.keywords` / 平铺的 `creators`）PUT 到
`/deposit/depositions/{draft}`。新版本草稿其实是 RDM 形态，这些键被**静默丢弃**：
2026-10-30 那一批 20 件（6 本学术专著 + 14 篇论文）因此全部没有许可、也没有关键词，
而正文版权页与 CITATION.cff 都写着 CC BY 4.0。同一个坑此前只补了"作者"一项，
这一次补齐了许可与关键词，并把发布路径整体换成 RDM：
    POST /api/records/{id}/versions        → 新版本草稿
    POST /api/records/{draft}/draft/pids/doi → 预留 DOI（写进 CITATION.cff）
    PUT  /api/records/{draft}/draft        → metadata.rights / subjects / languages
    POST /api/records/{draft}/draft/files  → 建条目 → PUT 内容 → commit
"""
import glob
import io
import json
import os
import re
import sys

from pypdf import PdfReader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import republish_book as rb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = rb.DATE


def state(slug):
    src = os.path.join(ROOT, slug, "source")
    parts = json.load(io.open(os.path.join(src, "parts.json"), encoding="utf-8"))
    bj = json.load(io.open(os.path.join(src, "book.json"), encoding="utf-8"))
    nch = sum(len(p["chapters"]) for p in parts)
    figs = sum(len(re.findall(r"<img", io.open(f, encoding="utf-8").read()))
               for f in glob.glob(os.path.join(src, "ch*.html")))
    apx = sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix_[a-z]\.html", f))
    letters = "—".join([chr(65), chr(64 + len(apx))]) if apx else "无"
    pdf = os.path.join(ROOT, slug, "output", "book.pdf")
    pages = len(PdfReader(pdf).pages)
    return dict(pages=pages, nch=nch, nparts=len(parts), figs=figs,
                napx=len(apx), letters=letters, title=bj["title"], sub=bj["subtitle"])


if __name__ == "__main__":
    mode, slugs = sys.argv[1], sys.argv[2:]
    for slug in slugs:
        st = state(slug)
        print("%s: %s 页 / %s 章 / 附录文件 %s" % (slug, st["pages"], st["nch"], st["napx"]))
        if mode == "dry":
            continue
        did, doi = rb.new(slug)
        n = rb.up(slug, did)
        rb.meta(slug, did)
        rb.publish(did)
        print("  files %d | DOI %s" % (n, doi))

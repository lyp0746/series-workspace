# -*- coding: utf-8 -*-
"""重建 _pages.json（合集总目录/卷目录的页码回填）。

判据只用两条，简单且不依赖顺序对齐：
  · 卷封面 / 论文封面 / 章首页 —— 该页规范化正文以「卷X」「论文X」「第N章」开头；
  · 附录 —— 按源文件 h2 原文精确前匹配，框在该卷封面与下一卷封面之间。
"""
import json, os, re, sys
sys.path.insert(0, ".")
import pymupdf
import build_collection as B

PDF = sys.argv[1] if len(sys.argv) > 1 else "release/00-合集-印刷版.pdf"
doc = pymupdf.open(PDF)
N = lambda s: re.sub(r"\s+", "", s)
P = [N(doc[i].get_text()) for i in range(doc.page_count)]

CH = re.compile(r"^\u7b2c(\d+)\u7ae0")
vol_pages = [i + 1 for i, s in enumerate(P) if s.startswith("\u5377")]
pap_pages = [i + 1 for i, s in enumerate(P) if s.startswith("\u8bba\u6587")]
ch_pages = [i + 1 for i, s in enumerate(P) if CH.match(s)]

expect_vol = len(B.VOLUMES)
expect_pap = len(B.PAPERS)
expect_ch = 0
for book, *_ in B.VOLUMES:
    pj = json.load(open(f"../{book}/source/parts.json", encoding="utf-8"))
    expect_ch += len([c for part in pj for c in part.get("chapters", [])
                      if c.get("written", True) and c.get("file")])

assert len(vol_pages) == expect_vol, f"卷封面 {len(vol_pages)}≠{expect_vol}"
assert len(pap_pages) == expect_pap, f"论文封面 {len(pap_pages)}≠{expect_pap}"
assert len(ch_pages) == expect_ch, f"章首页 {len(ch_pages)}≠{expect_ch}"

volumes = {f"vol{i}": p for i, p in enumerate(vol_pages, 1)}
papers = {f"paper{i}": p for i, p in enumerate(pap_pages, 1)}

appendices = []
bounds = vol_pages + [10 ** 6]
for vi, (book, *_r) in enumerate(B.VOLUMES):
    lo, hi = bounds[vi], bounds[vi + 1]
    aplist = []
    for f in sorted(x for x in os.listdir(f"../{book}/source") if x.startswith("appendix")):
        t = open(f"../{book}/source/{f}", encoding="utf-8").read()
        m = re.search(r"<h2[^>]*>(.*?)</h2>", t, re.S)
        probe = N(re.sub(r"<[^>]+>", "", m.group(1))).strip()[:18] if m else "\x00"
        aplist.append(next((i + 1 for i in range(lo, min(hi, len(P))) if P[i].startswith(probe)), 0))
    appendices.append(aplist)

json.dump({"chapters": ch_pages, "appendices": appendices,
           "volumes": volumes, "papers": papers},
          open("_pages.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("卷", list(volumes.values()))
print("论文", list(papers.values()))
print("章", len(ch_pages), "附录组", [len(a) for a in appendices],
      "零值", sum(a.count(0) for a in appendices))

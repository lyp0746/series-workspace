# -*- coding: utf-8 -*-
"""版式体检：孤行标题、题注分页、末行孤字（粗判）。只读 PDF。"""
import glob
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def blocks(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        lines = []
        size = 0
        for ln in b["lines"]:
            txt = "".join(sp["text"] for sp in ln["spans"]).strip()
            if not txt:
                continue
            for sp in ln["spans"]:
                size = max(size, sp["size"])
            lines.append(txt)
        if lines:
            out.append((size, " ".join(lines)))
    return out


def check(pdf):
    d = pymupdf.open(pdf)
    orphan_head = []      # 页末是标题（字号 > 正文）
    caption_split = []    # 页首即图注（图在上一页）
    tiny_last = []        # 页末行很少且以句号结尾（孤行粗判）
    body = 12.5
    for i, p in enumerate(d):
        bs = blocks(p)
        if not bs:
            continue
        size, txt = bs[-1]
        if size > body * 1.02 and len(txt) < 60 and i + 1 < len(d):
            orphan_head.append((i + 1, txt[:28]))
        if re.match(r"^图\s*\d", txt) and len(txt) < 160:
            caption_split.append((i + 1, txt[:28]))
        if i + 1 < len(d):
            nxt = blocks(d[i + 1])
            if bs and len(txt) < 18 and not re.match(r"^\d+$", txt):
                tiny_last.append((i + 1, txt[:28]))
    return orphan_head, caption_split, tiny_last


if __name__ == "__main__":
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "*/output/book.pdf"))) + \
            sorted(glob.glob(os.path.join(ROOT, "*", "00-*.pdf"))):
        name = os.path.relpath(f, ROOT)
        oh, cs, tl = check(f)
        rows.append((name, len(oh), len(cs), len(tl), oh[:3]))
    for r in rows:
        print(f"{r[0]:56s} 孤行标题={r[1]:3d} 题注分页={r[2]:3d} 末行过短={r[3]:3d} {r[4]}")

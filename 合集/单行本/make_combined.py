# -*- coding: utf-8 -*-
"""合一版：《得鹿梦鱼》作卷首（罗马页码）＋《粗码》正文（阿拉伯页码）。

用法：
    python make_combined.py

只影响投递包（release/）；Downloads 里仍是两册分开。
体例说明：散文用 i—xxv 罗马页码，粗码保持原阿拉伯页码不动——
这样粗码的目录、索引、§号、表图号、书签全部无需重算。
"""
import io
import os
import re

import pymupdf
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

import common as C
from build_sanwen import build as build_sanwen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
SANWEN_ROMAN = os.path.join(OUT_DIR, "_sanwen_roman.pdf")
COVER = os.path.join(OUT_DIR, "_combined_cover.pdf")
RAW = os.path.join(HERE, "..", "..", "resolution-grain", "output", "book.pdf")
DEST = os.path.join(HERE, "..", "..", "resolution-grain", "release", "resolution-grain-print-combined.pdf")

TITLE = "粗码"
SUB = "为什么越省力分得越粗，而核实为何总是追不上"
LINE = "附卷首《得鹿梦鱼》——五公里的单向时间、粗码与电子幽灵"
BY = "李毅芃"


def make_cover():
    C.register_fonts()
    C.CFG["title"] = TITLE
    C.CFG["author"] = BY
    C.CFG["cover_pages"] = 1
    C.CFG["folio"] = "arabic"
    st = C.build_styles()
    doc = SimpleDocTemplate(COVER, pagesize=(C.PAGE_WIDTH, C.PAGE_HEIGHT),
                            leftMargin=C.MARGIN_L, rightMargin=C.MARGIN_R,
                            topMargin=C.MARGIN_T, bottomMargin=C.MARGIN_B,
                            title=f"{TITLE}：{SUB}", author=BY)
    story = [Spacer(1, 58 * mm),
             Paragraph(C.spaced(TITLE), st["cover_title"]),
             Spacer(1, 6 * mm), C.CoverDivider(), Spacer(1, 6 * mm),
             Paragraph(SUB, st["cover_sub"]),
             Spacer(1, 24 * mm),
             Paragraph(LINE, st["cover_sub"]),
             Spacer(1, 52 * mm),
             C.AuthorWithSeal(BY, "粗码"),  # 两字印
             PageBreak()]
    doc.build(story, canvasmaker=C.BookCanvas)
    print("[封面]", COVER)


def main():
    if not os.path.exists(RAW):
        raise SystemExit(f"缺粗码正文 PDF：{RAW}（先跑 resolution-grain/build_book.py --pdf）")
    build_sanwen(out=SANWEN_ROMAN, with_cover=False, folio="roman")
    make_cover()

    cover = pymupdf.open(COVER)
    front = pymupdf.open(SANWEN_ROMAN)
    body = pymupdf.open(RAW)

    n_cover, n_front = cover.page_count, front.page_count
    drop = 1                                  # 粗码原封面并入总封面后去掉
    offset = n_cover + n_front - drop         # 粗码第 p 页 → 新第 p+offset 页

    out = pymupdf.open()
    out.insert_pdf(cover)
    out.insert_pdf(front)
    out.insert_pdf(body, from_page=drop)

    toc = [[1, "卷首　得鹿梦鱼", n_cover + 1]]
    for lvl, t, p in front.get_toc():
        toc.append([min(lvl + 1, 3), t, p + n_cover])
    toc.append([1, "粗码　为什么越省力分得越粗，而核实为何总是追不上", n_cover + n_front + 1])
    for lvl, t, p in body.get_toc():
        if p <= drop:
            continue
        toc.append([min(lvl + 1, 4), t, p + offset])
    toc.sort(key=lambda x: x[2])
    out.set_toc(toc)

    out.set_metadata({"title": f"{TITLE}：{SUB}（附卷首《得鹿梦鱼》）",
                      "author": BY, "subject": LINE, "keywords": "粗码, 得鹿梦鱼"})
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    out.save(DEST, garbage=3, deflate=True)
    print(f"[合一] {DEST}  {out.page_count} 页  {os.path.getsize(DEST)/1e6:.1f} MB"
          f"（卷首 {n_front} 页 i—{C.roman(n_front)}；粗码偏移 +{offset}；书签 {len(toc)} 条）")


if __name__ == "__main__":
    main()

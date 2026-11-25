# -*- coding: utf-8 -*-
"""《得鹿梦鱼》单行本：md → 宣纸/朱砂 A4 PDF。

用法：
    python build_sanwen.py

源：得鹿梦鱼.md（唯一源；docx 只作存档，不再参与构建）。
    由 convert_sanwen.py 从 docx 一次性转出，此后改文字改 md。
版式与《中道周行集》共用 common.py。
"""
import io
import os
import re

from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                KeepTogether)
from reportlab.lib.units import mm

import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "得鹿梦鱼.md")
OUT = os.path.join(HERE, "out", "得鹿梦鱼：五公里的单向时间、粗码与电子幽灵.pdf")

# 全篇只保留一处感叹号（那段真实的喊话）；其余若有，构建时报出来
EXCLAIM_ALLOWED = "给我抓虫"


def parse(path):
    meta = {"title": "", "sub": "", "by": "李毅芃", "seal": ""}
    sections, cur = [], None
    for raw in io.open(path, encoding="utf-8").read().split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            meta["title"] = line[2:].strip(); continue
        if line.startswith("SUB "):
            meta["sub"] = line[4:].strip(); continue
        if line.startswith("BY "):
            meta["by"] = line[3:].strip(); continue
        if line.startswith("SEAL "):
            meta["seal"] = line[5:].strip(); continue
        if line.startswith("## "):
            cur = {"head": line[3:].strip(), "blocks": []}
            sections.append(cur); continue
        if cur is None:
            continue
        for tag in ("P", "Q", "FIG"):
            if line.startswith(tag + " "):
                body = line[len(tag) + 1:].strip()
                if tag == "FIG":
                    f, _, cap = body.partition("|")
                    cur["blocks"].append(("FIG", (f.strip(), cap.strip())))
                else:
                    cur["blocks"].append((tag, body))
                break
    return meta, sections


def build(out=None, with_cover=True, folio="arabic"):
    C.register_fonts()
    meta, sections = parse(SRC)
    C.CFG["title"] = meta["title"] or "得鹿梦鱼"
    C.CFG["author"] = meta["by"]
    C.CFG["folio"] = folio
    C.CFG["folio_start"] = 1
    C.CFG["cover_pages"] = 1 if with_cover else 0

    styles = C.build_styles()
    styles["ending"] = C.ParagraphStyle(
        "Ending", parent=styles["prose"], alignment=C.TA_LEFT, firstLineIndent=0,
        fontSize=11.4, leading=23, textColor=C.INK_DEEP, spaceBefore=2, spaceAfter=4)

    story = []
    if with_cover:
        story += [Spacer(1, 58 * mm),
                  Paragraph(C.spaced(meta["title"] or "得鹿梦鱼"), styles["cover_title"]),
                  Spacer(1, 6 * mm), C.CoverDivider(), Spacer(1, 6 * mm),
                  Paragraph(meta["sub"], styles["cover_sub"]),
                  Spacer(1, 88 * mm),
                  C.AuthorWithSeal(meta["by"], meta["seal"] or "得鹿梦鱼"),
                  PageBreak()]

    # 收尾三句单独成页：从最后一段正文里取「最后三块」
    flat = [b for s in sections for b in s["blocks"]]
    tail = flat[-3:]

    cites = 0
    first = True
    seen = 0
    for sec in sections:
        if not first:
            story.append(PageBreak())
        first = False
        story.append(Spacer(1, 9 * mm))
        head = sec["head"]
        label, sep, title = head.partition("：")
        block = [Paragraph("　".join(list(label)), styles["section_no"])]
        if title:
            block.append(Paragraph(title, styles["section_title"]))
        story.append(KeepTogether(block))
        story.append(C.SectionRule(head))
        story.append(Spacer(1, 6 * mm))

        for kind, body in sec["blocks"]:
            seen += 1
            if seen > len(flat) - 3:          # 最后三块留给末页
                continue
            if kind == "FIG":
                fname, cap = body
                path = os.path.join(HERE, fname)
                if os.path.exists(path):
                    story.append(C.Plate(path, cap))
                else:
                    print(f"[缺图] {fname}")
            elif kind == "Q":
                story.append(Paragraph(body, styles["quote"]))
                cites += 1
            else:
                if "！" in body and EXCLAIM_ALLOWED not in body:
                    print(f"[感叹号] {body[:40]}…")
                story.append(Paragraph(body, styles["prose"]))

    story.append(PageBreak())
    story.append(Spacer(1, 172 * mm))
    ending = [Paragraph(body, styles["ending"]) for kind, body in tail if isinstance(body, str)]
    ending += [Spacer(1, 3 * mm), C.Ornament(span=22 * mm), Spacer(1, 3 * mm),
               C.SealMark(meta["seal"] or "得鹿梦鱼", 10 * mm)]
    story.append(KeepTogether(ending))

    target = out or OUT
    os.makedirs(os.path.dirname(target), exist_ok=True)
    doc = SimpleDocTemplate(
        target, pagesize=(C.PAGE_WIDTH, C.PAGE_HEIGHT),
        leftMargin=C.MARGIN_L, rightMargin=C.MARGIN_R,
        topMargin=C.MARGIN_T, bottomMargin=C.MARGIN_B,
        title=f"{meta['title']}：{meta['sub']}", author=meta["by"], subject=meta["sub"])
    doc.build(story, canvasmaker=C.BookCanvas)
    print(f"[完成] {target}（引语段 {cites} 处）")
    return target


if __name__ == "__main__":
    import sys
    a = sys.argv[1:]
    build(out=(a[a.index("--out") + 1] if "--out" in a else None),
          with_cover=("--no-cover" not in a),
          folio=("roman" if "--roman" in a else "arabic"))

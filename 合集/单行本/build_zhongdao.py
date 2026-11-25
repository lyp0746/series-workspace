# -*- coding: utf-8 -*-
"""《中道周行集》单行本：Markdown → 宣纸/朱砂 A4 PDF。

用法：
    python build_zhongdao.py

源文件：中道周行集.md（同一目录）。改字只改 md，再跑一次即可。
"""
import os
import re

from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                KeepTogether)
from reportlab.lib.units import mm

import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "中道周行集.md")
OUT = os.path.join(HERE, "out", "中道周行集.pdf")

TITLE = "中道周行集"
SUB = "持满若虚卷　·　六体并序"
AUTHOR = "李毅芃"
SEAL = "中道周行"

PUNCT = "，。；：、？！》」』）·—…"


# ---------------------------------------------------------------- 解析
def parse(path):
    meta = {"title": TITLE, "sub": SUB, "by": AUTHOR, "seal": SEAL}
    sections = []
    cur = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("# "):
                meta["title"] = line[2:].strip()
                continue
            if line.startswith("SUB "):
                meta["sub"] = line[4:].strip()
                continue
            if line.startswith("BY "):
                meta["by"] = line[3:].strip()
                continue
            if line.startswith("SEAL "):
                meta["seal"] = line[5:].strip()
                continue
            if line.startswith("## "):
                cur = {"head": line[3:].strip(), "blocks": [], "nobreak": False}
                sections.append(cur)
                continue
            if cur is None:
                continue
            if line.startswith("P "):
                cur["blocks"].append(("P", line[2:].strip()))
            elif line.startswith("V "):
                cur["blocks"].append(("V", line[2:].strip()))
            elif line.startswith("TI "):
                cur["blocks"].append(("TI", line[3:].strip()))
            elif line.startswith("SIGN "):
                cur["blocks"].append(("SIGN", line[5:].strip()))
            elif line.strip() == "ORN":
                cur["blocks"].append(("ORN", ""))
            elif line.strip() == "FLOW":
                cur["nobreak"] = True
    return meta, sections


NUM_RE = re.compile(r"^([一二三四五六七八九十]+)、\s*(.+)$")


def split_head(head):
    m = NUM_RE.match(head)
    if m:
        return m.group(1), m.group(2)
    return "", head


# ---------------------------------------------------------------- 排版
def spread(text):
    """诗句：字间加全角空格，标点前不加。"""
    out = []
    for i, ch in enumerate(text):
        if i and ch not in PUNCT:
            out.append("　")
        out.append(ch)
    return "".join(out)


def verse_block(lines, styles, spread_it):
    paras = []
    long_lines = any(len(x) > 24 for x in lines)
    style = styles["verse_ci"] if long_lines else styles["verse"]
    for ln in lines:
        txt = spread(ln) if (spread_it and not long_lines) else ln
        paras.append(Paragraph(txt, style))
    return KeepTogether(paras) if len(paras) <= 20 else paras


def build():
    C.register_fonts()
    meta, sections = parse(SRC)

    C.CFG["title"] = meta["title"]
    C.CFG["author"] = meta["by"]

    styles = C.build_styles()
    story = []

    # ---- 封面 ----
    story.append(Spacer(1, 58 * mm))
    story.append(Paragraph(C.spaced(meta["title"]), styles["cover_title"]))
    story.append(Spacer(1, 6 * mm))
    story.append(C.CoverDivider())
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(meta["sub"], styles["cover_sub"]))
    story.append(Spacer(1, 88 * mm))
    story.append(C.AuthorWithSeal(meta["by"], meta["seal"]))
    story.append(PageBreak())

    # ---- 正文 ----
    first = True
    for sec in sections:
        label, title = split_head(sec["head"])
        if not first:
            if sec.get("nobreak"):
                story.append(Spacer(1, 10 * mm))
            else:
                story.append(PageBreak())
        first = False

        story.append(Spacer(1, 9 * mm))

        head_block = []
        if label:
            head_block.append(Paragraph(
                "　".join(["其", label]), styles["section_no"]))
        head_block.append(Paragraph(title, styles["section_title"]))
        story.append(KeepTogether(head_block))

        blocks = sec["blocks"]

        # 题注紧跟标题
        if blocks and blocks[0][0] == "TI":
            story.append(Paragraph(blocks[0][1], styles["note"]))
            blocks = blocks[1:]

        story.append(C.SectionRule(f"{label}、{title}" if label else title))
        story.append(Spacer(1, 6 * mm))

        i = 0
        n = len(blocks)
        while i < n:
            kind, text = blocks[i]
            if kind == "V":
                j = i
                lines = []
                while j < n and blocks[j][0] == "V":
                    lines.append(blocks[j][1])
                    j += 1
                story.append(verse_block(lines, styles, spread_it=True))
                i = j
                continue
            if kind == "P":
                style = styles["quote"] if (len(text) <= 20 and "——" in text) else styles["prose"]
                story.append(Paragraph(text, style))
            elif kind == "TI":
                story.append(Paragraph(text, styles["note"]))
            elif kind == "SIGN":
                story.append(Paragraph(text, styles["sign"]))
            elif kind == "ORN":
                story.append(Spacer(1, 3 * mm))
                story.append(C.Ornament())
                story.append(Spacer(1, 3 * mm))
            i += 1

    # ---- 尾花 ----
    story.append(Spacer(1, 10 * mm))
    story.append(C.Ornament(span=26 * mm))
    story.append(Spacer(1, 5 * mm))
    story.append(C.SealMark(meta["seal"], 12 * mm))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = SimpleDocTemplate(
        OUT, pagesize=(C.PAGE_WIDTH, C.PAGE_HEIGHT),
        leftMargin=C.MARGIN_L, rightMargin=C.MARGIN_R,
        topMargin=C.MARGIN_T, bottomMargin=C.MARGIN_B,
        title=f"{meta['title']}：{meta['sub']}", author=meta["by"],
        subject=meta["sub"],
    )
    doc.build(story, canvasmaker=C.BookCanvas)
    print(f"[完成] {OUT}")
    return OUT




# ---------------------------------------------------------------- 合集卷首（HTML）
def emit_fragment(dest):
    """把同一份 md 排成合集的卷首片段，保证单行本与合集卷首永远同源。"""
    import html as _html

    meta, sections = parse(SRC)
    out = ['<div class="zhongdao">',
           f'<h2 class="front" style="font-size:26pt;letter-spacing:12px;'
           f'text-align:center;margin:18mm 0 2mm">{_html.escape(meta["title"])}</h2>',
           f'<p class="zd-sub">{_html.escape(meta["sub"])}</p>',
           f'<p class="zd-byline">{_html.escape(meta["by"])}</p>', ""]
    first = True
    for sec in sections:
        label, title = split_head(sec["head"])
        if not first:
            out.append("")
        first = False
        out.append(f'<h2 class="front">{_html.escape(sec["head"] if not label else sec["head"])}</h2>')
        for kind, text in sec["blocks"]:
            if kind == "P":
                out.append(f'<p class="prose">{_html.escape(text)}</p>')
            elif kind == "V":
                out.append(f'<p class="verse">{_html.escape(text)}</p>')
            elif kind == "TI":
                out.append(f'<p class="ti">{_html.escape(text)}</p>')
            elif kind == "SIGN":
                cls = "zd-end" if "书于" in text else "byline"
                out.append(f'<p class="{cls}">{_html.escape(text)}</p>')
            elif kind == "ORN":
                out.append('<p class="zd-orn">❖</p>')
    out.append("</div>")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(f"[片段] {dest}")


if __name__ == "__main__":
    build()
    if "--fragment" in __import__("sys").argv:
        emit_fragment(os.path.join(HERE, "..", "_front_daozhou.html"))

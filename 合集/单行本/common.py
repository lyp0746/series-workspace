# -*- coding: utf-8 -*-
"""单行本共同版式：宣纸底 · 朱砂印 · 宋楷双体。

build_zhongdao.py（《中道周行集》）与 build_sanwen.py（《得鹿梦鱼》）共用
这里的字体注册、配色、装饰件与 BookCanvas。改版式只改这一处。
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable
from reportlab.pdfgen import canvas as pdfcanvas

# ---- 中文标点禁则：reportlab 自带的避头集只收了日文半角标点，补上全角
from reportlab.lib import textsplit as _ts
from reportlab.platypus import paragraph as _para

_EXTRA_CANNOT_START = "；，：！？．…～—）（】》〉”’"
if "；" not in _ts.ALL_CANNOT_START:
    _ts.ALL_CANNOT_START = _ts.ALL_CANNOT_START + _EXTRA_CANNOT_START
_para.ALL_CANNOT_START = _ts.ALL_CANNOT_START

PAGE_WIDTH, PAGE_HEIGHT = A4

# =========================
# 1. 字体：正文宋体，诗题落款楷体
# =========================
SERIF = "BookSerif"
KAI = "BookKai"

FONT_CANDIDATES = {
    SERIF: [
        r"C:\Windows\Fonts\SourceHanSerifSC-Regular.otf",
        r"C:\Windows\Fonts\SourceHanSerifCN-Regular.otf",
        r"C:\Windows\Fonts\STSONG.TTF",
        r"C:\Windows\Fonts\simsun.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ],
    KAI: [
        r"C:\Windows\Fonts\simkai.ttf",
        r"C:\Windows\Fonts\STKAITI.TTF",
        r"C:\Windows\Fonts\KaiTi.ttf",
        r"C:\Windows\Fonts\STKaiti.ttf",
    ],
}


def _register(name, candidates):
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            if path.lower().endswith(".ttc"):
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(name, path))
            print(f"[信息] {name} ← {path}")
            return path
        except Exception:
            continue
    raise FileNotFoundError(f"未找到可用字体：{name}；请检查 {candidates}")


def register_fonts():
    for name, cands in FONT_CANDIDATES.items():
        _register(name, cands)


# =========================
# 2. 配色（宣纸与朱墨）
# =========================
BG_PAPER = HexColor("#FAF8F3")
INK_DEEP = HexColor("#1A1917")
INK_BODY = HexColor("#2C2B29")
INK_MUTED = HexColor("#5A5650")
INK_LIGHT = HexColor("#8C867E")
LINE_WARM = HexColor("#C8C0B4")
CINNABAR = HexColor("#9E2A22")

# 版心：比学术书略窄，给诗行留呼吸
MARGIN_L = 30 * mm
MARGIN_R = 30 * mm
MARGIN_T = 27 * mm
MARGIN_B = 26 * mm

# 页眉文字（各脚本在 build 之前填）
CFG = {
    "title": "",
    "author": "李毅芃",
    "hide_header_on_section_start": True,
    "cover_pages": 1,      # 前几页是封面（不印页眉页码、印折角边框）；无封面时置 0
    "folio": "arabic",     # "arabic" | "roman"（卷首用罗马数字，正编不动）
    "folio_start": 1,
}


def roman(n):
    """1—3999 的罗马数字（页码用）。"""
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
            (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
            (5, "v"), (4, "iv"), (1, "i")]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


# =========================
# 3. 装饰件
# =========================
def _diamond(c, x, y, r, color):
    p = c.beginPath()
    p.moveTo(x, y + r)
    p.lineTo(x + r * 0.36, y + r * 0.36)
    p.lineTo(x + r, y)
    p.lineTo(x + r * 0.36, y - r * 0.36)
    p.lineTo(x, y - r)
    p.lineTo(x - r * 0.36, y - r * 0.36)
    p.lineTo(x - r, y)
    p.lineTo(x - r * 0.36, y + r * 0.36)
    p.close()
    c.setFillColor(color)
    c.drawPath(p, stroke=0, fill=1)


class CoverDivider(Flowable):
    """封面主副题之间的星菱装饰线。"""

    def __init__(self, width=76 * mm):
        super().__init__()
        self.width = width
        self.height = 8 * mm

    def wrap(self, availWidth, availHeight):
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        cx = self._doctemplate.width / 2.0
        cy = self.height / 2.0
        half = self.width / 2.0

        c.setStrokeColor(LINE_WARM)
        c.setLineWidth(0.55)
        c.line(cx - half, cy, cx - 5.5 * mm, cy)
        c.line(cx + 5.5 * mm, cy, cx + half, cy)

        c.setFillColor(LINE_WARM)
        c.circle(cx - 3.6 * mm, cy, 0.45 * mm, stroke=0, fill=1)
        c.circle(cx + 3.6 * mm, cy, 0.45 * mm, stroke=0, fill=1)
        _diamond(c, cx, cy, 1.45 * mm, CINNABAR)
        c.restoreState()


def draw_seal(c, sx, sy, s, text, font=None):
    """在画布上画一枚四字阴刻朱砂印。"""
    text = (text or "")[:4]
    font = font or SERIF
    two = (len(text) == 2)
    c.setFillColor(CINNABAR)
    c.roundRect(sx, sy, s, s, radius=0.65 * mm, stroke=0, fill=1)

    c.setStrokeColor(BG_PAPER)
    c.setLineWidth(0.45)
    inset = 0.65 * mm
    inner = s - 2 * inset
    c.rect(sx + inset, sy + inset, inner, inner, stroke=1, fill=0)

    mid_x, mid_y = sx + s / 2.0, sy + s / 2.0
    c.setLineWidth(0.3)
    if two:                       # 两字印：竖排一列，不画十字格
        c.line(sx + inset, mid_y, sx + s - inset, mid_y)
    else:
        c.line(mid_x, sy + inset, mid_x, sy + s - inset)
        c.line(sx + inset, mid_y, sx + s - inset, mid_y)

    # 刀痕飞白
    c.setFillColor(BG_PAPER)
    c.rect(sx + 0.35 * mm, sy + s - 1.5 * mm, 0.7 * mm, 0.45 * mm, stroke=0, fill=1)
    c.rect(sx + s - 1.0 * mm, sy + 1.2 * mm, 0.7 * mm, 0.4 * mm, stroke=0, fill=1)
    c.rect(sx + 1.8 * mm, sy + 0.35 * mm, 0.45 * mm, 0.7 * mm, stroke=0, fill=1)
    c.rect(sx + s - 2.2 * mm, sy + s - 0.9 * mm, 0.5 * mm, 0.5 * mm, stroke=0, fill=1)

    c.setFillColor(BG_PAPER)
    if two:
        c.setFont(font, s * 0.42)
        c.drawCentredString(mid_x, mid_y + inner * 0.22, text[0])
        c.drawCentredString(mid_x, sy + inset + inner * 0.10, text[1])
        return
    c.setFont(font, s * 0.30)  # 字号随印面缩放（8.4mm 印面 → 7.2pt）
    q = inner / 2.0
    cx1 = sx + inset + q / 2.0
    cx2 = mid_x + q / 2.0
    cy1 = sy + inset + q / 2.0 - s * 0.105
    cy2 = mid_y + q / 2.0 - s * 0.105
    for i, (x, y) in enumerate([(cx1, cy2), (cx2, cy2), (cx1, cy1), (cx2, cy1)]):
        if i < len(text):
            c.drawCentredString(x, y, text[i])


class SealMark(Flowable):
    """单独一枚居中的朱砂印（卷末）。"""

    def __init__(self, text, size=11 * mm):
        super().__init__()
        self.text = text
        self.size = size
        self.height = size + 2 * mm

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        draw_seal(c, self.availWidth / 2.0 - self.size / 2.0, 1 * mm, self.size, self.text)
        c.restoreState()


class AuthorWithSeal(Flowable):
    """作者署名 + 四字阴刻朱砂方印。"""

    def __init__(self, author_name, seal_text="", seal_size=8.4 * mm, name_size=12.5):
        super().__init__()
        self.author_name = author_name
        self.seal_text = (seal_text or "")[:4]
        self.seal_size = seal_size
        self.name_size = name_size
        self.height = 16 * mm

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        cx = self.availWidth / 2.0
        cy = self.height / 2.0

        spaced = "  ".join(list(self.author_name)) + "   著"
        c.setFont(SERIF, self.name_size)
        c.setFillColor(INK_MUTED)
        text_w = c.stringWidth(spaced, SERIF, self.name_size)

        has_seal = len(self.seal_text) >= 2
        gap = 3.8 * mm if has_seal else 0
        seal = self.seal_size if has_seal else 0
        total_w = text_w + gap + seal
        start_x = cx - total_w / 2.0

        c.drawString(start_x, cy - 1.6 * mm, spaced)
        if has_seal:
            self._draw_seal(c, start_x + text_w + gap, cy - seal / 2.0 + 0.3 * mm)
        c.restoreState()

    def _draw_seal(self, c, sx, sy):
        draw_seal(c, sx, sy, self.seal_size, self.seal_text)


class SectionRule(Flowable):
    """卷题下方的朱黑短栏线；同时向 BookCanvas 登记“本页是卷首页”。"""

    def __init__(self, label, bookmark=True):
        super().__init__()
        self.label = label
        self.bookmark = bookmark
        self.height = 5 * mm

    def wrap(self, availWidth, availHeight):
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.mark_section_start(self.label, self.bookmark)

        c.saveState()
        y = self.height / 2.0
        c.setStrokeColor(CINNABAR)
        c.setLineWidth(1.3)
        c.line(0, y, 8.5 * mm, y)
        c.setFillColor(CINNABAR)
        c.circle(11 * mm, y, 0.55 * mm, stroke=0, fill=1)
        c.setStrokeColor(LINE_WARM)
        c.setLineWidth(0.55)
        c.line(13.5 * mm, y, 42 * mm, y)
        c.restoreState()


class Ornament(Flowable):
    """段间装饰：三枚菱星（替代字体里没有的 ❖）。"""

    def __init__(self, span=20 * mm):
        super().__init__()
        self.span = span
        self.height = 10 * mm

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        cx = self.availWidth / 2.0
        cy = self.height / 2.0
        c.setStrokeColor(LINE_WARM)
        c.setLineWidth(0.45)
        c.line(cx - self.span, cy, cx - 6 * mm, cy)
        c.line(cx + 6 * mm, cy, cx + self.span, cy)
        for dx, scale, col in ((-3.2 * mm, 0.7, LINE_WARM),
                              (0, 1.15, CINNABAR),
                              (3.2 * mm, 0.7, LINE_WARM)):
            _diamond(c, cx + dx, cy, 1.05 * mm * scale, col)
        c.restoreState()


class Tailpiece(Flowable):
    """书末尾花。"""

    def __init__(self):
        super().__init__()
        self.height = 12 * mm

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        cx = self.availWidth / 2.0
        cy = self.height / 2.0 - 1 * mm
        c.setStrokeColor(LINE_WARM)
        c.setLineWidth(0.45)
        c.line(cx - 22 * mm, cy, cx - 7 * mm, cy)
        c.line(cx + 7 * mm, cy, cx + 22 * mm, cy)
        for dx, scale, col in ((-3.5 * mm, 0.75, LINE_WARM),
                               (0, 1.15, CINNABAR),
                               (3.5 * mm, 0.75, LINE_WARM)):
            _diamond(c, cx + dx, cy, 1.05 * mm * scale, col)
        c.restoreState()


class Plate(Flowable):
    """图版：居中一幅照片，细线框，下接一行楷体图注。"""

    def __init__(self, path, caption="", max_w=108 * mm, max_h=80 * mm,
                 top_gap=5 * mm, bottom_gap=5 * mm):
        super().__init__()
        from reportlab.lib.utils import ImageReader
        self.path = path
        self.caption = caption
        iw, ih = ImageReader(path).getSize()
        k = min(max_w / iw, max_h / ih)
        self.iw, self.ih = iw * k, ih * k
        self.top_gap, self.bottom_gap = top_gap, bottom_gap
        self.cap_h = 6 * mm if caption else 0
        self.height = top_gap + self.ih + self.cap_h + bottom_gap

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        x = (self.availWidth - self.iw) / 2.0
        y = self.bottom_gap + self.cap_h

        c.setStrokeColor(LINE_WARM)
        c.setLineWidth(0.4)
        c.rect(x - 1 * mm, y - 1 * mm, self.iw + 2 * mm, self.ih + 2 * mm, stroke=1, fill=0)
        c.drawImage(self.path, x, y, width=self.iw, height=self.ih,
                    preserveAspectRatio=True, mask=None)

        if self.caption:
            c.setFont(KAI, 9)
            c.setFillColor(INK_LIGHT)
            c.drawCentredString(self.availWidth / 2.0, self.bottom_gap + 1.2 * mm, self.caption)
        c.restoreState()


class ColophonRule(Flowable):
    """卷末朱砂小印（居中）。"""

    def __init__(self, text, size=10 * mm):
        super().__init__()
        self.text = text[:1]
        self.size = size
        self.height = size + 2 * mm

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        c.saveState()
        x = self.availWidth / 2.0 - self.size / 2.0
        y = 1 * mm
        c.setFillColor(CINNABAR)
        c.roundRect(x, y, self.size, self.size, radius=0.6 * mm, stroke=0, fill=1)
        c.setFillColor(BG_PAPER)
        c.setFont(SERIF, self.size * 0.62)
        c.drawCentredString(x + self.size / 2.0, y + self.size * 0.30, self.text)
        c.restoreState()


# =========================
# 4. 页面画布：底色、页眉、页码、书签
# =========================
def draw_chinoiserie_frame(canvas):
    """封面上的中式折角双线边框。"""
    canvas.saveState()
    mx, my = 20 * mm, 20 * mm
    w = PAGE_WIDTH - 2 * mx
    h = PAGE_HEIGHT - 2 * my

    canvas.setStrokeColor(LINE_WARM)
    canvas.setLineWidth(0.8)
    canvas.rect(mx, my, w, h, stroke=1, fill=0)

    ins = 2.4 * mm
    x0, y0 = mx + ins, my + ins
    x1, y1 = mx + w - ins, my + h - ins
    k = 3.8 * mm

    p = canvas.beginPath()
    p.moveTo(x0 + k, y0)
    p.lineTo(x1 - k, y0)
    p.lineTo(x1 - k, y0 + k)
    p.lineTo(x1, y0 + k)
    p.lineTo(x1, y1 - k)
    p.lineTo(x1 - k, y1 - k)
    p.lineTo(x1 - k, y1)
    p.lineTo(x0 + k, y1)
    p.lineTo(x0 + k, y1 - k)
    p.lineTo(x0, y1 - k)
    p.lineTo(x0, y0 + k)
    p.lineTo(x0 + k, y0 + k)
    p.close()
    canvas.setLineWidth(0.4)
    canvas.drawPath(p, stroke=1, fill=0)
    canvas.restoreState()


class BookCanvas(pdfcanvas.Canvas):
    """接管页面生命周期：宣纸底 → 正文 → 页眉页码 → 落版。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_section = ""
        self._this_page_is_section_start = False
        self._bookmark_seq = 0
        self._paint_background()

    def mark_section_start(self, label, bookmark=True):
        self._current_section = label
        self._this_page_is_section_start = True
        if bookmark:
            self._bookmark_seq += 1
            key = f"sec{self._bookmark_seq}"
            self.bookmarkPage(key)
            self.addOutlineEntry(label, key, level=0)

    def _paint_background(self):
        self.saveState()
        self.setFillColor(BG_PAPER)
        self.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
        if self.getPageNumber() <= CFG.get("cover_pages", 1):
            draw_chinoiserie_frame(self)
        self.restoreState()

    def _draw_header_and_footer(self):
        page_no = self.getPageNumber()
        if page_no <= CFG.get("cover_pages", 1):
            return

        body_no = page_no - CFG.get("cover_pages", 1) + CFG.get("folio_start", 1) - 1
        self.saveState()

        hide = CFG["hide_header_on_section_start"] and self._this_page_is_section_start
        if not hide:
            y = PAGE_HEIGHT - 18.0 * mm
            self.setFont(SERIF, 8.5)
            self.setFillColor(INK_LIGHT)
            self.drawString(MARGIN_L, y, f"{CFG['title']}  ·  {CFG['author']}")
            self.drawRightString(PAGE_WIDTH - MARGIN_R, y, self._current_section)
            self.setStrokeColor(LINE_WARM)
            self.setLineWidth(0.35)
            self.line(MARGIN_L, y - 2.6 * mm, PAGE_WIDTH - MARGIN_R, y - 2.6 * mm)

        self.setFont(SERIF, 8.8)
        self.setFillColor(INK_LIGHT)
        label = roman(body_no) if CFG.get("folio") == "roman" else str(body_no)
        self.drawCentredString(PAGE_WIDTH / 2.0, 14.5 * mm, f"—  {label}  —")
        self.restoreState()

    def showPage(self):
        self._draw_header_and_footer()
        super().showPage()
        self._this_page_is_section_start = False
        self._paint_background()

    def save(self):
        # 清掉最后多预涂的一页底色，避免文末多出空白页
        self._code.clear()
        super().save()


# =========================
# 5. 段落样式
# =========================
def build_styles():
    ss = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "CoverTitle", parent=ss["Normal"], fontName=SERIF, fontSize=30, leading=42,
        alignment=TA_CENTER, textColor=INK_DEEP)
    styles["cover_sub"] = ParagraphStyle(
        "CoverSub", parent=ss["Normal"], fontName=KAI, fontSize=12.5, leading=20,
        alignment=TA_CENTER, textColor=INK_MUTED)

    styles["section_no"] = ParagraphStyle(
        "SectionNo", parent=ss["Normal"], fontName=KAI, fontSize=11, leading=16,
        alignment=TA_LEFT, textColor=CINNABAR, spaceAfter=3)
    styles["section_title"] = ParagraphStyle(
        "SectionTitle", parent=ss["Normal"], fontName=SERIF, fontSize=19, leading=28,
        alignment=TA_LEFT, textColor=INK_DEEP, spaceAfter=5)
    styles["note"] = ParagraphStyle(
        "Note", parent=ss["Normal"], fontName=KAI, fontSize=10, leading=17,
        alignment=TA_CENTER, textColor=INK_MUTED, spaceBefore=2, spaceAfter=7)

    styles["prose"] = ParagraphStyle(
        "Prose", parent=ss["Normal"], fontName=SERIF, fontSize=11.2, leading=21.6,
        alignment=TA_JUSTIFY, firstLineIndent=22.4, textColor=INK_BODY,
        spaceAfter=6.5, wordWrap="CJK")
    styles["quote"] = ParagraphStyle(
        "Quote", parent=styles["prose"], fontSize=11.2, leading=21.6,
        firstLineIndent=0, leftIndent=22.4, rightIndent=16,
        textColor=INK_MUTED, spaceBefore=2.5, spaceAfter=8.0)

    styles["verse"] = ParagraphStyle(
        "Verse", parent=ss["Normal"], fontName=KAI, fontSize=12.6, leading=25.5,
        alignment=TA_CENTER, textColor=INK_BODY, wordWrap="CJK", spaceAfter=0)
    styles["verse_ci"] = ParagraphStyle(
        "VerseCi", parent=ss["Normal"], fontName=KAI, fontSize=11.2, leading=23,
        alignment=TA_LEFT, leftIndent=3 * mm, textColor=INK_BODY, wordWrap="CJK",
        spaceBefore=3, spaceAfter=3)
    styles["sign"] = ParagraphStyle(
        "Sign", parent=ss["Normal"], fontName=KAI, fontSize=11, leading=18,
        alignment=TA_RIGHT, textColor=INK_MUTED, spaceBefore=5, spaceAfter=2)
    styles["ending"] = ParagraphStyle(
        "Ending", parent=styles["prose"], alignment=TA_RIGHT, firstLineIndent=0,
        fontSize=11, leading=20, textColor=INK_MUTED)
    return styles


def spaced(text):
    """字间距：中文标题用空格拉开（reportlab 无字距属性，用空格模拟）。"""
    return " ".join(list(text))

# -*- coding: utf-8 -*-
"""build_collection21.py — 九卷合集（套装式）：印刷版 A4 / 电子版 B5 / EPUB 3。

结构（出版社套装惯例）：
  总封面 → 总书名页 → 总版权页 → 总序 → 总目录
  卷一：卷封面 → 卷版权页 → 卷目录 → 卷前言 → 正文 → 附录 → 卷结语
  ……
  后记 → 版本记

规则：
  * 只拼接各书既有内容；不重排、不改写正文。
  * 图片：印刷/电子版内联 SVG；EPUB 独立文件。
  * 目录：锚点 + 内部链接 + 两遍回填页码。
  * 不在 PDF 上做二次加工（pypdf 重写会破坏内部链接）。
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
import zipfile
import markdown as _md

from lxml import html as LH, etree

ROOT = os.path.abspath(os.path.dirname(__file__))
OUT = os.path.join(ROOT, "release")
BASE = os.path.dirname(ROOT)

VOLUMES = [
    ("knowledge-tradeoffs", "卷一", "只能选两样", "从来不及、会忘记到说不清——六个核心，看懂复杂世界的取舍",
     "全书的导览：六个核心是什么，为什么它们其实是同一笔账单。", "front_intro.html"),
    ("distinction-evolution", "卷二", "区分的语法", "五个领域，同一个二次型",
     "一切认识都从划一道线开始。这一卷给出那一道线的语法。", "front_preface.html"),
    ("capacity-cascade", "卷三", "遗忘的边界", "有限容量下的记忆、智能与自我",
     "线划下之后，能装多少？遗忘为什么是学习的前提。", "front_preface.html"),
    ("entropy-spiral", "卷四", "错位的时间", "为什么我们总是来不及：社会系统的时间错配与可控性边界",
     "装不下的东西，还要赶上时间。这一卷把时间变成变量。", "front_preface.html"),
    ("impossibility-triangle", "卷五", "选择的代价", "完备、可组合与可传递的三维权衡——复杂知识系统如何形成、演化与更新",
     "三样不能同时要。这一卷把取舍写成一张价目表。", "front_preface.html"),
    ("interpretation-tradeoff", "卷六", "诠释的权衡", "历史研究中的置信度、权衡与理论流变——从人物还原到范式转移的五个应用",
     "价目表也适用于我们怎么讲过去。这一卷谈置信度。", "front_preface.html"),
    ("emergence-critical", "卷七", "涌现的临界", "为什么有些变化回不去：临界、涌现与形式化的边界",
     "取舍积累到某个点，会换一个东西。这一卷谈那道门槛。", "front_intro.html"),
    ("mind-forks", "卷八", "心灵的分岔", "从无意识到可观察——心理学流派的六次划线",
     "把六核从复杂系统带到心理学史：每个流派都划了一条线，也让出了什么。", "front_intro.html"),
    ("hotspot-bills", "卷九", "热点的账单", "用六个核心，诊断过去一年的热搜与争论",
     "把前八卷的尺子，落在过去一年真实的公共讨论上。", "front_intro.html"),
]

TITLE = "有限系统的取舍"
_CN = "零一二三四五六七八九十"


def _cn(n):
    """1—99 的汉字数字（只用于标题这类需要读顺的地方）。"""
    if n <= 10:
        return _CN[n]
    if n < 20:
        return "十" + _CN[n % 10]
    return _CN[n // 10] + "十" + (_CN[n % 10] if n % 10 else "")


# 副标题按实际条目动态生成：加件/减件时封面不会写错
AUTHOR = "李毅芃"
DATE = "2026-10-28"


PAPERS = [
    ("ComputingDemystified", "论文一", "术语的账单", "从芯片到 Agent 的八十个计算机概念",
     "看见", "实证", "术语的账单_从芯片到Agent的八十个计算机概念.md", "10.5281/zenodo.23602360"),
    ("WorldPeriodization", "论文二", "谁在切时间轴", "六十部世界史分期，附一份自证方案",
     "看见＋讲述", "实证", "谁在切时间轴_六十部世界史分期与一份自证方案.md", "10.5281/zenodo.23602364"),
    ("SleepingResidue", "论文三", "线外的残余", "被埋没的理论为何被重新发现，为何永久沉默",
     "记住", "实证", "线外的残余_延迟承认的三种机制.md", "10.5281/zenodo.23603016"),
    ("HunanRelaySystem", "论文四", "明清湘中驿道体系的 GEPF 三层分析", "家族记忆、商品流向与地名侵蚀",
     "跟上", "实证", "明清湘中驿道体系_GEPF三层分析.md", "10.5281/zenodo.23601983"),
    ("BureauRotationCession", "论文五", "轮换的让渡", "中国官制三千年（西周—2026）",
     "选择", "实证", "轮换的让渡_中国官制三千年.md", "10.5281/zenodo.23602311"),
    ("HarnessEcology", "论文六", "被点燃的生态", "两个社区、五种口径与三个标记",
     "临界", "实证", "被点燃的生态_两个社区与三个标记.md", "10.5281/zenodo.23603015"),
    ("OptimizationBoundary", "论文七", "优化的边界", "目标函数、搜索空间与六核心的停止规则",
     "接口", "方法", "优化的边界_四前提与越界的二十个案例.md", "10.5281/zenodo.23611782"),
    ("CapacityProxies", "论文八", "容量的三个代理", "分期槽位、编码槽位与标签槽位",
     "记住（代理）", "方法", "容量的三个代理_分期槽位与编码槽位与标签槽位.md", "10.5281/zenodo.23611799"),
    ("DomainCrossSection", "论文十", "领域的剖面", "四个问题、二十个领域与八十字段的审计",
     "看见（操作化）", "方法", "领域的剖面_四个问题与二十个领域的审计.md", "10.5281/zenodo.23695806"),
    ("IsomorphismStrength", "论文十一", "同构的强度", "对偶、泛性质、不变量与四十条断裂探针",
     "看见＋讲述（跨域）", "方法", "同构的强度_对偶与泛性质与不变量与四十条断裂探针.md", "10.5281/zenodo.23695810"),
    ("MemoryAnchor", "论文十二", "记忆的锚点", "情景唤起、异构重建与日志裁决",
     "记住（架构）", "方法", "记忆的锚点_情景唤起与异构重建与日志裁决.md", "10.5281/zenodo.23665882"),
    ("MemoryStressTest", "论文十三", "锚点的下限", "情景记忆的模拟对照实验与 0.57 的覆盖率阈值",
     "记住（测试）", "测试", "锚点的下限_情景记忆的模拟对照实验.md", "10.5281/zenodo.23667929"),
    ("LedgerReconciliation", "论文九", "六张账单的对账", "六核心的可测代理、失败模式与尺度边界",
     "阶段总账（覆盖一—十四）", "阶段总账", "六张账单的对账_六核心的可测代理与尺度边界.md", "10.5281/zenodo.23695813"),
    ("MonarchCompetition", "论文十四", "开明君主与两层竞争", "agent 价目表上的执行、方向与代价承担者",
     "选择＋讲述（价格）", "方法", "开明君主与两层竞争_执行方向与代价承担者.md", "10.5281/zenodo.23695757"),
]

# 分部：九卷 / 实证论文（一—六）/ 方法论文（七、八、十—十三）/ 阶段总账（九）
# 副标题按实际条目动态生成（放在 PAPERS 之后，避免过期）
SUBTITLE = "%s本书 + %s篇工作论文，附卷首一篇" % (_cn(len(VOLUMES)), _cn(len(PAPERS)))

PART_OF = {"论文一": 2, "论文二": 2, "论文三": 2, "论文四": 2, "论文五": 2, "论文六": 2,
           "论文七": 3, "论文八": 3, "论文十": 3, "论文十一": 3, "论文十二": 3, "论文十三": 3,
           "论文九": 4, "论文十四": 3}
PARTS = {2: ("第二部", "实证论文（一—六）", "六篇各自落在一个真实材料上：官制、驿道、术语、分期、生态、残余。"),
         3: ("第三部", "方法论文（七、八、十—十三）", "不新增经验对象，只把六核心的用法钉死：划界、代理、操作化、跨域、架构、测试。"),
         4: ("阶段总账", "六张账单的对账（覆盖一—八）", "它审计的是前 14 件的 62 条命题，覆盖范围见其题名页；十—十三 的登记命题待下一版并账。")}


# ---------------------------------------------------------------- 论文
def papcover_html(pi, pno, title, sub, core, doi, cls="论文", note=""):
    note_html = f'<div class="s" style="font-size:12pt;color:#b3261e;margin-top:4mm">{note}</div>' if note else ""
    return f"""<div class="volcover">
<div class="n">{pno}</div>
<h1 class="t" id="paper{pi}">{title}</h1>
<div class="s">{sub}</div>
<div class="b">类：{cls}　·　主核：{core}</div>{note_html}
<div class="a">{AUTHOR}</div>
<div class="p">工作论文　·　DOI {doi}　·　{DATE}</div>
</div>"""


def paper_html(repo, mdname, mode, assets, pi):
    """论文原样拼接：Markdown → HTML，图片内联。"""
    path = os.path.join(BASE, repo, mdname)
    text = open(path, encoding="utf-8").read()
    html = _md.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    # 图片：相对 repo 根目录
    def rep(m):
        whole, pre, src, post = m.group(0), m.group(1), m.group(2), m.group(3)
        if src.startswith("data:") or src.startswith("http"):
            return whole
        cand = src if os.path.isabs(src) else os.path.join(BASE, repo, src)
        if not os.path.exists(cand):
            return whole
        ext = os.path.splitext(cand)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "svg": "image/svg+xml"}.get(ext, "application/octet-stream")
        data = open(cand, "rb").read()
        if mode == "epub":
            key = hashlib.md5(data).hexdigest()[:12] + "." + ext
            assets[key] = data
            return f'<img src="assets/img/{key}" alt="figure"/>'
        return f'{pre}src="data:{mime};base64,{base64.b64encode(data).decode()}"{post}'
    html = re.sub(r'(<img[^>]*?)src="([^"]+)"([^>]*)>', rep, html)
    # 论文内的 h1/h2 分页
    html = html.replace("<h1>", '<h1 class="paper-t">')
    return f'<div class="paper" id="p{pi}">{html}</div>'


# ---------------------------------------------------------------- CSS
def build_css(mode):
    css = open(os.path.join(BASE, "entropy-spiral/assets/css/paper.css"), encoding="utf-8").read()
    css += "\n" + open(os.path.join(BASE, "entropy-spiral/assets/css/book.css"), encoding="utf-8").read()
    seen = {css}
    for b, *_ in VOLUMES:
        txt = open(os.path.join(BASE, b, "assets/css/book.css"), encoding="utf-8").read()
        if txt not in seen:
            css += "\n" + txt
            seen.add(txt)
    if mode == "ereader":
        css += "\n" + open(os.path.join(BASE, "entropy-spiral/assets/css/ereader.css"), encoding="utf-8").read()

    print_ = (mode == "print")
    extra = """
@page { size: %(page)s; margin: %(margin)s; }
@page :first { margin: 0; }
html, body { margin: 0; padding: 0; max-width: none; }
body { font-family: "Times New Roman", "SimSun", "Songti SC", "STSong", serif;
       font-size: %(fs)s; line-height: %(lh)s; color: #111; max-width: none; margin: 0; }
p { margin: 0 0 0.55em 0; text-align: justify; }
h1.volume, h1.volcover-title { page-break-before: always; text-align: center; }
h2.front { page-break-before: always; text-align: center; font-size: 20pt; margin: 40mm 0 8mm 0; }
h2.chapter { page-break-before: always; }

/* 总封面：满版（负边距抵消 @page 版心） */
.cover { width: %(cw)s; height: %(ch)s; margin: %(cmg)s; padding: 0;
         page-break-after: always;
         background: linear-gradient(165deg, #0a0d13 0%%, #141a25 48%%, #07090d 100%%);
         color: #ece9e1; -webkit-print-color-adjust: exact; print-color-adjust: exact;
         position: relative; box-sizing: border-box; }
.cover .rule-top { position:absolute; top:0; left:0; right:0; height:7mm; background:#b8862f; }
.cover .rule-bottom { position:absolute; bottom:0; left:0; right:0; height:7mm; background:#b8862f; }
.cover .en { position:absolute; top:26mm; left:0; right:0; text-align:center; font-size:10pt;
             letter-spacing:5px; color:#8d949c; }
.cover .t { position:absolute; top:105mm; left:0; right:0; text-align:center; font-size:46pt;
            letter-spacing:10px; font-weight:bold; }
.cover .vol { position:absolute; top:137mm; left:0; right:0; text-align:center; font-size:18pt;
              letter-spacing:14px; color:#d8b25a; }
.cover .cores { position:absolute; top:160mm; left:0; right:0; text-align:center; font-size:11pt;
                letter-spacing:3px; color:#b9c0c8; }
.cover .sub { position:absolute; top:171mm; left:0; right:0; text-align:center; font-size:9.5pt;
              letter-spacing:2px; color:#8d949c; }
.cover .au { position:absolute; bottom:34mm; left:0; right:0; text-align:center; font-size:16pt;
             letter-spacing:6px; }
.cover .yr { position:absolute; bottom:24mm; left:0; right:0; text-align:center; font-size:10pt;
             color:#8d949c; }

/* 卷封面（页内、带框） */
.volcover { page-break-before: always; text-align: center; border: 1.2pt solid #b8862f;
            padding: 30mm 16mm; margin: 14mm 0 0 0; box-sizing: border-box; min-height: 210mm; }
.volcover .n { font-size: 14pt; letter-spacing: 10px; color: #b8862f; }
.volcover h1.t { font-size: 34pt; margin: 26mm 0 6mm 0; page-break-before: auto; letter-spacing: 6px; font-weight: bold; margin: 26mm 0 6mm 0; }
.volcover .s { font-size: 12.5pt; color: #333; margin-bottom: 12mm; }
.volcover .b { font-size: 10.5pt; color: #555; line-height: 1.8; margin: 0 auto; max-width: 105mm; }
.volcover .a { margin-top: 34mm; font-size: 12pt; letter-spacing: 4px; }
.volcover .p { margin-top: 6mm; font-size: 9.5pt; color: #777; }

/* 目录 */
.toc { page-break-before: always; page-break-after: always; }
.toc h2 { page-break-before: auto; text-align:center; font-size: 18pt; margin: 6mm 0 8mm 0; }
.toc .v { font-weight: bold; margin: 4.5mm 0 1mm 0; font-size: 11.5pt; display:flex; }
.toc .c { font-size: 10pt; margin: 1.1mm 0 1.1mm 6mm; display:flex; align-items:baseline; }
.toc .tt { white-space: nowrap; }
.toc .dots { flex: 1 1 auto; border-bottom: 0.6pt dotted #999; margin: 0 4px 3px 6px; }
.toc .pg { white-space: nowrap; color:#555; }
.toc a { color: inherit; text-decoration: none; }

.titlepage { page-break-after: always; text-align: center; margin-top: 55mm; }
.titlepage .t { font-size: 32pt; letter-spacing: 8px; font-weight: bold; }
.titlepage .s { font-size: 14pt; color:#333; margin-top: 8mm; }
.titlepage .a { font-size: 12pt; color:#666; margin-top: 34mm; }
.colophon { page-break-before: always; font-size: 9.6pt; color:#333; }
.paper { page-break-before: always; }
.paper h1.paper-t { font-size: 20pt; text-align:center; margin: 6mm 0 4mm 0; page-break-after: avoid; }
.paper h2 { page-break-before: always; }
.figbox { text-align:center; margin: 10pt 0 4pt 0; page-break-inside: avoid; }
.figbox svg { max-width: 100%%; height: auto; }
img { max-width: 100%%; height: auto; }
table.nat td.s, table.nat th.s { text-align:center; }
""" % dict(
        page="A4" if print_ else "B5",
        margin="25mm 28mm 25mm 28mm" if print_ else "17mm 15mm 17mm 15mm",
        fs="10.6pt" if print_ else "11.6pt",
        lh="1.72" if print_ else "1.85",
        cw="210mm" if print_ else "176mm",
        ch="297mm" if print_ else "250mm",
        cmg="-25mm -28mm 0 -28mm" if print_ else "-17mm -15mm 0 -15mm",
    )
    return css + extra


# ---------------------------------------------------------------- 图片
def svg_inline(raw, assets, mode):
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw)
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw).strip()
    if mode == "epub":
        key = hashlib.md5(raw.encode()).hexdigest()[:12] + ".svg"
        assets[key] = raw
        return f'<img src="assets/img/{key}" alt="figure"/>'
    raw = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r"\1", raw, count=1)
    raw = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r"\1", raw, count=1)
    raw = raw.replace("<svg ", '<svg preserveAspectRatio="xMidYMid meet" ', 1)
    return f'<div class="figbox">{raw}</div>'


def process_images(html, book, mode, assets):
    def rep(m):
        whole, pre, src, post = m.group(0), m.group(1), m.group(2), m.group(3)
        if src.startswith("data:") or src.startswith("http"):
            return whole
        p = os.path.join(BASE, book, src)
        if not os.path.exists(p):
            return whole
        if p.lower().endswith(".svg"):
            return svg_inline(open(p, encoding="utf-8").read(), assets, mode)
        ext = os.path.splitext(p)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "application/octet-stream")
        data = open(p, "rb").read()
        if mode == "epub":
            key = hashlib.md5(data).hexdigest()[:12] + "." + ext
            assets[key] = data
            return f'<img src="assets/img/{key}" alt="figure"/>'
        return f'{pre}src="data:{mime};base64,{base64.b64encode(data).decode()}"{post}'
    return re.sub(r'(<img[^>]*?)src="([^"]+)"([^>]*)>', rep, html)


# ---------------------------------------------------------------- 结构
def clean_front(html):
    """去掉单卷自带的封面式大标题重复，仅保留内容。"""
    return html


def read_source(book, fname, mode, assets):
    p = os.path.join(BASE, book, "source", fname)
    if not os.path.exists(p):
        return ""
    html = open(p, encoding="utf-8").read().replace("{{BOOK_DATE}}", DATE)
    html = process_images(html, book, mode, assets)
    html = re.sub(r"<(https?://[^>\s]+)>", r'<a href="\1">\1</a>', html)
    return html


def chapters_of(book):
    parts = json.load(open(os.path.join(BASE, book, "source/parts.json"), encoding="utf-8"))
    return [c for part in parts for c in part["chapters"]]


def appendices_of(book):
    src = open(os.path.join(BASE, book, "build_book.py"), encoding="utf-8").read()
    m = re.search(r"BACK\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        return []
    skip = ("back_epilogue", "back_popular_guide", "back_series", "back_postscript")
    out = []
    for title, f in re.findall(r'\("([^"]*)",\s*"([^"]*)"', m.group(1)):
        if any(k in f for k in skip):
            continue
        if os.path.exists(os.path.join(BASE, book, "source", f)):
            out.append((title, f))
    return out


def backmatter_file(book):
    for f in ("back_epilogue.html", "back_postscript.html"):
        if os.path.exists(os.path.join(BASE, book, "source", f)):
            return f
    return None


def part_html(kicker, title, desc):
    return f"""<div class="volcover">
<div class="n">{kicker}</div>
<h1 class="t">{title}</h1>
<div class="s" style="max-width:112mm;line-height:1.95;font-size:12pt;color:#333">{desc}</div>
</div>"""


def cover_html():
    return f"""<div class="cover">
<div class="rule-top"></div><div class="rule-bottom"></div>
<div class="en">THE TRADEOFFS OF FINITE SYSTEMS</div>
<div class="t">{TITLE}</div>
<div class="vol">二 十 二 件 合 集</div>
<div class="cores">看见 · 记住 · 跟上 · 选择 · 讲述 · 临界</div>
<div class="sub">九本书 + 十四篇工作论文</div>
<div class="au">{AUTHOR}</div><div class="yr">2026</div>
</div>"""


def volcover_html(vi, vol, title, sub, blurb):
    return f"""<div class="volcover">
<div class="n">{vol}</div>
<h1 class="t" id="vol{vi}">{title}</h1>
<div class="s">{sub}</div>
<div class="b">{blurb}</div>
<div class="a">{AUTHOR}</div>
<div class="p">《{TITLE}》系列合集　·　{DATE}</div>
</div>"""


def assemble(mode="print", toc_pages=None, vol_pages=None, skip_cover=False):
    """toc_pages: 全局章页码列表（按卷顺序）；vol_pages: 各卷附录页码列表。"""
    assets = {}
    body = [] if skip_cover else [cover_html()]
    body += [
        f'<div class="titlepage"><div class="t">{TITLE}</div><div class="s">{SUBTITLE}</div>'
        f'<div class="a">{AUTHOR}　·　{DATE}</div></div>']

    # ---------------- 总版权页
    body.append('<div class="colophon" style="page-break-before:always"><h3 style="text-align:center">版权与说明</h3>'
                f'<p><b>书名：</b>{TITLE}——{SUBTITLE}</p><p><b>作者：</b>{AUTHOR}（独立研究者）</p>'
                f'<p><b>日期：</b>{DATE}　<b>许可：</b>内容 CC BY 4.0；代码 MIT</p>'
                '<p>本合集收录同一系列的九本书（六本学术专著＋两本通俗读本＋一本科普专著）与十四篇工作论文，'
                '分三部编排：第一部 九卷；第二部 实证（一—六）；第三部 方法（七、八、十、十一、十二、十三、十四）；末为阶段总账（九，覆盖一—十四）。卷首另收《中道周行集》一篇，为作者的方法论自述，非学术正文。'
                '每卷保留其单行本的卷首、版权页、目录、前言与结语；每篇论文保留其标题页、作者行、图表与附录，正文一字未改。'
                '全文的章节编号、图表与证据分级均未改动。</p>'
                '<p>书中所用材料与数据截至 2026 年 10 月。凡标注“当代／目前／当前／最近”，均指该时点。</p>'
                '<p><b>卷首《中道周行集》。</b>它以诗、词、散、骈、赋、铭六体写成，是作者的方法自述，与本合集的方法论互为镜像：'
                '“读观行验”对观察—抽象—建模—应用—反馈的闭环；“执两用中”对三样至多取二；“慎终如始、持满若虚”对不作宿命判断、'
                '把每条结论都写成可被推翻的样子。它是精神自述，不承担论证，不参与分级，也不进入任何引用计数。</p>'
                '<p>系列入口与外部登记库：github.com/lyp0746/knowledge-tradeoffs；各卷的 DOI、附录与可证伪登记簿以单行本为准。</p>'
                '<p>版式：正文宋体 + Times New Roman；目录页码由排版后回填。</p></div>')

    # ---------------- 卷首：中道周行集（方法自述，不参与分级）
    body.append(open(os.path.join(ROOT, "_front_daozhou.html"), encoding="utf-8").read())

    # ---------------- 总序
    body.append('<h2 class="front">总序　九本书，一个问题</h2>'
                '<p>这九本书只问一件事：<b>一个有限的东西，怎样一边保持自己的样子，一边还能改变？</b></p>'
                '<p>这个问题有一个比它更靠下的前提：<b>现实中没有无限。</b>没有无限的容量、无限的时间、无限的分辨率、无限的注意力。'
                '无限只作为极限出现在模型里，从不出现在系统的实际状态里。因此，任何以“资源无限、精度无限、时间无限”为前提的方案，'
                '都不是对现实系统的解，而是对理想化模型的解。</p>'
                '<p>有限性本身只说明“有上界”。它要变成“必须让出一样”，还需要三个条件同时成立：需求随规模增长；描述、组合、传递共享同一个承载者；'
                '同时维持两种活动比分别维持更贵（交互惩罚 ψ&gt;0）。<b>有限性是必要条件，不是充分条件</b>——这也是本系列把三角标为框架（C／丙）而不是定理的原因。</p>'
                '<p>记忆要一边记住、一边更新；社会要一边稳定、一边调整；知识要一边传承、一边革命；一个人要一边做自己、一边长大。'
                '每一卷都在同一个形状上做文章，只是对象不同。</p>'
                '<p>这个形状可以压成一句话：<b>有限的承载者背后，都有一张看不见的账单；账单上只有三个价格——看得准、拼得上、传得下去，最多付得起两个。</b>'
                '让出的那一个，就是每一卷要指认的东西。</p>'
                '<p>九卷的次序不是随意的：先给一份导览（卷一），再从“怎么划线”开始（卷二），接着问“能装多少”（卷三）、“来不来得及”（卷四）、'
                '“三样怎么舍”（卷五）、“怎么讲过去”（卷六）、“何时换了一个东西”（卷七），然后把六核整体搬到心理学史（卷八），'
                '最后把尺子落在一年的公共讨论上（卷九）。</p>'
                '<p>每一卷都保留了自己的边界：哪些是定理，哪些是坐标，哪些只是假说；哪些失败了，为什么失败。合集不抹平这些差异——'
                '<b>差异本身，就是这套东西的可信之处。</b></p>'
                '<p>九本书之后，另有十四篇工作论文，分成三部。第二部是实证（一—六）：把六个核心各放到一种真实材料上试一次（术语、分期、残余、驿道、官制、生态）。'
                '第三部是方法（七、八、十、十一、十二、十三、十四）：不新增对象，只把做法钉死——给优化划界（七）、给容量找三个可数代理（八）、'
                '把四问操作化（十）、给跨域类比定价（十一）、把「记住」落成架构（十二）、再把那套架构压测到边界（十三）、'
                '最后把「执行／方向」压成可算的价格比（十四）。'
                '<p>《六张账单的对账》标为<b>阶段总账</b>：它本版已把十—十四 的 48 条并账，因此覆盖一—十四（18 件、<b>110 条命题</b>）。'
                '它排在第三部之后、十四之前，是因为编号不能重排；其题名页已注明覆盖范围。</p>'
                '<p>十四篇论文的共同点是不假装：<b>能做出来的做出来，做不出来的写明做不到。</b>'
                '全书最后一句留给读者自己判断：这套东西现在最硬的成果，是它的方法，不是它的对象。</p>'
                f'<p style="text-align:right;color:#666">{AUTHOR}　2026 年 10 月</p>')

    # ---------------- 总目录（分部）
    toc = ['<div class="toc"><h2>总目录</h2>']
    toc.append('<div class="v" style="margin-top:4mm;font-weight:700;color:#b3261e">第一部　九卷（专著）</div>')
    for vi, (book, vol, title, sub, blurb, _) in enumerate(VOLUMES, 1):
        toc.append(f'<div class="v"><span class="tt"><a href="#vol{vi}">{vol}　{title}</a></span>'
                   f'<span class="dots"></span><span class="pg">{""}</span></div>')
    for pi, (repo, pno, ptitle, psub, core, cls, md, doi) in enumerate(PAPERS, 1):
        if pno == "论文一":
            toc.append('<div class="v" style="margin-top:6mm;font-weight:700;color:#b3261e">第二部　实证论文（一—六）</div>')
        if pno == "论文七":
            toc.append('<div class="v" style="margin-top:6mm;font-weight:700;color:#b3261e">第三部　方法论文（七、八、十—十三）</div>')
        if pno == "论文九":
            toc.append('<div class="v" style="margin-top:6mm;font-weight:700;color:#b3261e">阶段总账（九）</div>')
        if pno == "论文十四":
            toc.append('<div class="v" style="margin-top:6mm;font-weight:700;color:#b3261e">随总账之后（十四）</div>')
        toc.append(f'<div class="v"><span class="tt"><a href="#paper{pi}">{pno}　{ptitle}</a></span>'
                   f'<span class="dots"></span><span class="pg">{""}</span></div>')
    toc.append('</div>')
    body.append("\n".join(toc))

    # ---------------- 编者说明
    body.append('<h2 class="front">编者说明　怎样读这本合集</h2>'
      '<p><b>一、这本合集是什么。</b>它不是一本新书，而是同一系列作品的合订：九本书（六本学术专著＋两本通俗读本＋一本科普专著）'
      '与十四篇工作论文。每件都保留自己的题名、作者行、版权页、图表、附录与登记簿，正文一字未改。</p>'
      '<p><b>二、顺序为什么是这样。</b>九本书按六核心的依赖排：导览（只能选两样）→ 看见（区分的语法）→ 记住（遗忘的边界）→ '
      '跟上（错位的时间）→ 选择（选择的代价）→ 讲述（诠释的权衡）→ 临界（涌现的临界）→ 全应用（心灵的分岔）→ 应用（热点的账单）。'
      '十四篇论文分三部：实证（一—六）→ 方法（七、八、十—十四）→ 阶段总账（九）。阶段总账排在第三部之末，因为它审计的是前面各篇的登记命题；本版并账后覆盖一—十四、共 110 条。</p>'
      '<p><b>三、编号为什么不连续。</b>论文编号按写作与归档先后给出（一—十四），编排则按「部」。九 与 十四 之所以排在最后，'
      '是因为九是总账、十四是它并账之后才写成的第一篇；两者都<b>不在原来的覆盖范围里</b>，故其题名页各自标注覆盖范围。'
      '不重编号，是为了不破坏已发布的 DOI 与引用位置。</p>'
      '<p><b>四、三种读法。</b>第一种，读九本书，跳过论文——那是一套完整的坐标。第二种，读实证六篇（一—六），看坐标落在真材料上是什么样。'
      '第三种，只读方法部（七、八、十—十四）与阶段总账（九），看这套东西自己怎么被检验、哪里失效、哪里被自己的数据打掉。</p>'
      '<p><b>五、一件事先说清。</b>这套东西不追求“补完”。它追求“可维护”：能做到的做出来，做不到的写明做不到。'
      '合集里多处出现“未测”“开放”“反例”——那不是疏漏，是账本的一部分。</p>')

    # ---------------- 一览表
    rows = []
    for vi, (book, vol, title, sub, blurb, _) in enumerate(VOLUMES, 1):
        rows.append((vol, title, sub, "书"))
    for pi, (repo, pno, ptitle, psub, core, cls, md, doi) in enumerate(PAPERS, 1):
        rows.append((pno, ptitle, f"{psub}（主核：{core}）", cls))
    tbl = ['<h2 class="front">合集一览</h2>',
           '<table class="nat" style="width:100%;font-size:9pt"><thead><tr><th>序</th><th>题名</th><th>副题／主核</th><th>类</th></tr></thead><tbody>']
    for a1, a2, a3, a4 in rows:
        tbl.append(f'<tr><td class="s">{a1}</td><td>{a2}</td><td>{a3}</td><td class="s">{a4}</td></tr>')
    tbl.append('</tbody></table>'
               '<p style="font-size:9pt;color:#555">注：九本书的 DOI 见各卷版权页；十四篇论文的 DOI 见各篇题名页与各篇末的参考文献。卷首《中道周行集》为方法自述，无 DOI。</p>')
    body.append("\n".join(tbl))

    # ---------------- 六核心速查
    body.append('<h2 class="front">六核心速查</h2>'
      '<table class="nat" style="width:100%;font-size:9pt"><thead><tr><th>核心</th><th>一句话</th><th>它在哪几件里被做深</th></tr></thead><tbody>'
      '<tr><td class="s">看见</td><td>认识从划一道线开始，划线有成本</td><td>《区分的语法》；论文一、论文二</td></tr>'
      '<tr><td class="s">记住</td><td>遗忘不是失败，是学习的前提</td><td>《遗忘的边界》；论文三、论文八</td></tr>'
      '<tr><td class="s">跟上</td><td>不是不知道，是来不及</td><td>《错位的时间》；论文四</td></tr>'
      '<tr><td class="s">选择</td><td>完备、可组合、可传递，至多取二</td><td>《选择的代价》；论文五</td></tr>'
      '<tr><td class="s">讲述</td><td>诠释就是给竞争命题分配置信度</td><td>《诠释的权衡》；论文二</td></tr>'
      '<tr><td class="s">临界</td><td>量变到质变，是一个可以被看见的时刻</td><td>《涌现的临界》；论文六</td></tr>'
      '<tr><td class="s">看见（操作化）</td><td>四个问题：瓶颈、置换、可写性、承担者</td><td>论文十《领域的剖面》</td></tr>'
      '<tr><td class="s">看见＋讲述（跨域）</td><td>同构有四个价位：严格、伴随、函子、比喻</td><td>论文十一《同构的强度》</td></tr>'
      '<tr><td class="s">记住（架构）</td><td>记忆＝残余＋多线索＋重建；裁决只认日志</td><td>论文十二《记忆的锚点》</td></tr>'
      '<tr><td class="s">记住（测试）</td><td>覆盖率低于约 0.57 时，三层架构不如一张摘要</td><td>论文十三《锚点的下限》</td></tr>'
      '<tr><td class="s">选择（价格）</td><td>重放便宜、判断贵：一次新判断约为一次重放的 34.5 倍；竞争在商品层，收租在旗舰层</td><td>论文十四《开明君主与两层竞争》</td></tr>'
      '</tbody></table>'
      '<p style="font-size:9pt;color:#555">依赖顺序：看见 → 记住／跟上 → 选择 → 讲述 → 临界。'
      '论文七（优化）横切其中四个，论文十（剖面）把四问操作化，论文十一（强度）把它们跨域，'
      '论文十二（锚点）把「记住」落成架构，论文十三（下限）把它压测到边界，论文十四（两层）把「执行／方向」压成价格比，'
      '论文九（阶段总账）审计一—十四、110 条。</p>'
      '<p style="font-size:9pt;color:#555">《心灵的分岔》把六核整体应用到心理学史，是第一次“全应用”；《热点的账单》把同一套尺子落到公共讨论上。</p>')

    # ---------------- 第一部：九卷
    body.append(part_html("第一部", "九卷（专著）",
                          "导览—语言—容量—时间—取舍—诠释—临界—全应用—应用。九本书按六核心的依赖排；各卷保留卷封面、版权、目录、前言、正文与结语。"))
    gi = 0
    for vi, (book, vol, title, sub, blurb, ffront) in enumerate(VOLUMES, 1):
        body.append(volcover_html(vi, vol, title, sub, blurb))
        cp = read_source(book, "front_copyright.html", mode, assets)
        if cp:
            body.append(f'<div class="colophon">{cp}</div>')
        chs = chapters_of(book)
        aps = appendices_of(book)
        vt = ['<div class="toc"><h2>本卷目录</h2>']
        for ci, c in enumerate(chs, 1):
            pg = ""
            if toc_pages and gi < len(toc_pages):
                pg = toc_pages[gi] or ""
            gi += 1
            vt.append(f'<div class="c"><span class="tt"><a href="#v{vi}c{ci}">第{c["no"]}章　{c["title"]}</a></span>'
                      f'<span class="dots"></span><span class="pg">{pg}</span></div>')
        for ai, (at, af) in enumerate(aps, 1):
            pg = ""
            if vol_pages and vi - 1 < len(vol_pages) and ai - 1 < len(vol_pages[vi - 1]):
                pg = vol_pages[vi - 1][ai - 1] or ""
            vt.append(f'<div class="c"><span class="tt"><a href="#v{vi}a{ai}">{at}</a></span>'
                      f'<span class="dots"></span><span class="pg">{pg}</span></div>')
        vt.append('</div>')
        body.append("\n".join(vt))
        pre = read_source(book, ffront, mode, assets)
        if pre:
            body.append(pre)
        for ci, c in enumerate(chs, 1):
            html = read_source(book, c["file"], mode, assets)
            html = re.sub(r'(<h2[^>]*>)', rf'<a id="v{vi}c{ci}"></a>\1', html, count=1)
            body.append(html)
        for ai, (at, af) in enumerate(aps, 1):
            html = read_source(book, af, mode, assets)
            html = re.sub(r'(<h2[^>]*>)', rf'<a id="v{vi}a{ai}"></a>\1', html, count=1)
            body.append(html)
        bf = backmatter_file(book)
        if bf:
            body.append(read_source(book, bf, mode, assets))

    # ---------------- 论文（三部）
    for pi, (repo, pno, ptitle, psub, core, cls, md, doi) in enumerate(PAPERS, 1):
        if pi == 1:
            body.append(part_html(PARTS[2][0], PARTS[2][1], PARTS[2][2]))
        if pno == "论文七":
            body.append(part_html(PARTS[3][0], PARTS[3][1], PARTS[3][2]))
        if pno == "论文九":
            body.append(part_html(PARTS[4][0], PARTS[4][1], PARTS[4][2]))
        note = ("阶段总账：覆盖一—八（14 件、62 条命题）；十—十三 的登记命题不在其中，待下一版并账。"
                if pno == "论文九" else "")
        body.append(papcover_html(pi, pno, ptitle, psub, core, doi, cls, note))
        body.append(paper_html(repo, md, mode, assets, pi))

    # ---------------- 后记
    body.append('<h2 class="front">后记　把这一桌东西摆在一起</h2>'
                '<p>把九本书并成一册，最直接的好处是：那些在单行本里分处不同卷的句子，终于可以互相看见。</p>'
                '<p>《区分的语法》说“先划线”，《遗忘的边界》说“线划下之后要丢东西”，《错位的时间》说“丢完之后还得赶上时间”，'
                '《选择的代价》说“赶时间就要让出一样”，《诠释的权衡》说“连讲述也是分配”，《涌现的临界》说“让出的东西积累到某个点就会变天”。'
                '<b>《心灵的分岔》把这六句话搬进心理学史</b>：每个流派都划了一条线，也让出了什么。</p>'
                '<p>十四篇论文把这六句话放到六种真实材料上各试一次，然后回过头来对账：哪些命题被自己的数据打掉了（<b>16／110，14.5%</b>），'
                '哪些核心至今没有测量（个体层 0 条、Ψ 未测、容量三代理三方向），哪些概念在不同篇里其实是两个东西（<b>七处同名不同物</b>）。</p>'
                '<p>第十四篇还带回一件不太舒服的事：它检验自己最想要的那个解释（溢价来自不可传递性），结果被自己的数据打掉了。'
                '<b>一个框架的性格不在它的结论里，在它的括注里。</b>这一句在这本合集里出现了不止一次，而每次出现都更像真的。</p>'
                '<p>这套东西不追求“补完”，它追求“可维护”：每加一篇只登记、只标边界、只做对账；做不到的测量写成“开放”，不写成“欠债”。'
                '一本越记越长的账，比一本永远差三页的账更接近真实。</p>'
                f'<p style="text-align:right;color:#666">{AUTHOR}　2026 年 10 月</p>')

    # ---------------- 版本记
    body.append('<div class="colophon"><h3>版本记</h3>'
                f'<p>{DATE}：第六版。在二十二件版基础上新增第十四篇《开明君主与两层竞争：agent 价目表上的执行、方向与代价承担者》，'
                '并收录<b>卷首《中道周行集》</b>（诗、词、散、骈、赋、铭六体＋总论＋跋），作为方法论自述与精神追求；'
                '收录九本书（六本专著＋两本通俗读本＋一本科普专著）与十四篇工作论文，另附卷首一篇。'
                '同版本更新：第十篇（附录 M，52 页）、第十一篇（附录 P，51 页）、第九篇（总账 62→110 条、七处同名不同物，54 页）均以本日新版入集，'
                '阶段总账的覆盖范围随之扩到一—十四。各件均以同日单行本为准，章节、图表、证据分级、附录与登记簿与单行本一致，<b>正文一字未改</b>。'
                '合集另加总封面、书名页、版权与说明、卷首、总序、编者说明、合集一览、六核心速查、总目录、后记与版本记。</p>'
                '<p><b>历版。</b>第一版（二十件，10.5281/zenodo.23663577）、第二版（二十件，23664446）、第三版（二十一件，23666079）、'
                '第四版、第五版依次为 23668413 与 23666079 之后的两次重排。本版为第六版，概念 DOI 10.5281/zenodo.23613406 不变。</p>'
                '<p>本合集为阅读便利而编，引用时请以各件单行本为准（含其 DOI、附录与可证伪登记）。'
                '十四篇论文的 DOI 见各篇论文封面页；九本书的 DOI 见各卷版权页。</p></div>')

    html = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<title>{TITLE}——{SUBTITLE}</title><style>' + build_css(mode) + '</style></head><body>'
            + "\n".join(body) + '</body></html>')
    path = os.path.join(ROOT, f"_build-{mode}.html")
    open(path, "w", encoding="utf-8").write(html)
    return path, assets


# ---------------------------------------------------------------- PDF
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]


def cover_only_html(mode="print"):
    """只含封面的 HTML：零页边距、满版；子元素定位规则逐条搬运，避免规则嵌套。"""
    cw, ch = ("210mm", "297mm") if mode == "print" else ("176mm", "250mm")
    page = "A4" if mode == "print" else "B5"
    base = build_css(mode)
    children = re.findall(r"\.cover \.[a-z-]+ \{[^}]*\}", base)
    css = (f"@page {{ size: {page}; margin: 0; }}\n"
           f"html, body {{ margin: 0; padding: 0; width: {cw}; height: {ch}; }}\n"
           f".cover {{ position: relative; width: {cw}; height: {ch}; margin: 0; padding: 0; overflow: hidden;\n"
           f"         background: linear-gradient(165deg,#0a0d13 0%,#141a25 48%,#07090d 100%);\n"
           f"         color: #ece9e1; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}\n"
           + "\n".join(children))
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<title>封面</title><style>{css}</style></head><body>' + cover_html() + '</body></html>')


def print_pdf(html_path, pdf_path):
    """Playwright/Chromium 打印：A4、背景、尊重 CSS @page。"""
    from playwright.sync_api import sync_playwright
    uri = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(uri, wait_until="load")
        pg.wait_for_timeout(800)
        pg.pdf(path=pdf_path, format="A4", print_background=True,
               prefer_css_page_size=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    print("wrote", pdf_path, os.path.getsize(pdf_path)//1024, "KB")


# ---------------------------------------------------------------- EPUB
def build_epub(out_path):
    assets = {}
    docs = []   # (id, nav_title, parent_vol, html)
    docs.append(("master-cover", "封面", None, "<h1>有限系统的取舍</h1><p>九卷合集</p>"))
    docs.append(("master-colophon", "版权与说明", None,
                 "<h1>版权与说明</h1><p>李毅芃 · 2026-10-26 · CC BY 4.0</p>"))
    docs.append(("master-preface", "总序", None,
                 "<h1>总序　九本书，一个问题</h1><p>一个有限的东西，怎样一边保持自己的样子，一边还能改变？</p>"))
    for vi, (book, vol, title, sub, blurb, ffront) in enumerate(VOLUMES, 1):
        parent = f"{vol}　{title}"
        docs.append((f"vol{vi}", parent, None, f"<h1>{parent}</h1><p>{sub}</p><p>{blurb}</p>"))
        cp = read_source(book, "front_copyright.html", "epub", assets)
        if cp:
            docs.append((f"v{vi}cp", "版权与说明", parent, cp))
        for ci, c in enumerate(chapters_of(book), 1):
            html = read_source(book, c["file"], "epub", assets)
            html = re.sub(r'(<h2[^>]*>)', rf'<a id="v{vi}c{ci}"></a>\1', html, count=1)
            docs.append((f"v{vi}c{ci}", f"第{c['no']}章　{c['title']}", parent, html))
        for ai, (at, af) in enumerate(appendices_of(book), 1):
            docs.append((f"v{vi}a{ai}", at, parent, read_source(book, af, "epub", assets)))
        bf = backmatter_file(book)
        if bf:
            docs.append((f"v{vi}end", "结语", parent, read_source(book, bf, "epub", assets)))
    docs.append(("master-afterword", "后记", None, "<h1>后记</h1><p>把九本书放在一张桌子上。</p>"))

    def sanitize(fragment):
        fragment = re.sub(r"<(https?://[^>\s]+)>", r'<a href="\1">\1</a>', fragment)
        try:
            node = LH.fragment_fromstring(fragment, create_parent="div")
            return etree.tostring(node, method="xml", encoding="unicode")
        except Exception:
            return "<div>" + fragment.replace("&", "&amp;").replace("<", "&lt;") + "</div>"

    files = []
    for did, title, parent, html in docs:
        files.append((did, title, parent, f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN"><head><meta charset="utf-8"/>
<title>{title}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><section id="{did}">{sanitize(html)}</section></body></html>"""))

    nav = ['<?xml version="1.0" encoding="utf-8"?>',
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN">',
           '<head><meta charset="utf-8"/><title>目录</title></head><body><nav epub:type="toc" id="toc"><h1>总目录</h1><ol>']
    for did, title, parent, _ in docs:
        if parent is None:
            nav.append(f'<li><a href="{did}.xhtml">{title}</a></li>')
    nav.append('<li><a href="vol1.xhtml">各卷</a><ol>')
    for vi, (book, vol, title, sub, blurb, ffront) in enumerate(VOLUMES, 1):
        nav.append(f'<li><a href="vol{vi}.xhtml">{vol}　{title}</a><ol>')
        for ci, c in enumerate(chapters_of(book), 1):
            nav.append(f'<li><a href="v{vi}c{ci}.xhtml">第{c["no"]}章　{c["title"]}</a></li>')
        nav.append('</ol></li>')
    nav.append('</ol></li></ol></nav></body></html>')

    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
    spine = []
    for did, title, parent, _ in files:
        manifest.append(f'<item id="{did.replace("-", "_")}" href="{did}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{did.replace("-", "_")}"/>')
    for name in assets:
        mt = "image/svg+xml" if name.endswith(".svg") else "image/png"
        manifest.append(f'<item id="i_{name.replace(".", "_")}" href="assets/img/{name}" media-type="{mt}"/>')

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="zh-CN">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">urn:uuid:finite-systems-collection-2026</dc:identifier>
<dc:title>{TITLE}——{SUBTITLE}</dc:title><dc:creator>{AUTHOR}</dc:creator>
<dc:language>zh-CN</dc:language><dc:date>{DATE}</dc:date>
<dc:publisher>独立出版</dc:publisher><dc:rights>CC BY 4.0</dc:rights>
<dc:description>九卷合集：六本学术专著、两本通俗读本、一本科普专著与十四篇工作论文。</dc:description>
<meta property="dcterms:modified">2026-10-18T00:00:00Z</meta>
</metadata>
<manifest>
{chr(10).join(manifest)}
</manifest>
<spine toc="ncx">
{chr(10).join(spine)}
</spine>
</package>"""

    ncx_items = []
    for i, (did, title, parent, _) in enumerate(files, 1):
        ncx_items.append(f'<navPoint id="n{i}" playOrder="{i}"><navLabel><text>{title}</text></navLabel><content src="{did}.xhtml"/></navPoint>')
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="urn:uuid:finite-systems-collection-2026"/></head>
<docTitle><text>{TITLE}</text></docTitle><navMap>{''.join(ncx_items)}</navMap></ncx>"""

    css = re.sub(r"@page[^}]*}", "", build_css("print"))
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="utf-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>""")
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/nav.xhtml", "\n".join(nav))
        z.writestr("OEBPS/toc.ncx", ncx)
        z.writestr("OEBPS/style.css", css)
        for did, _, _, doc in files:
            z.writestr(f"OEBPS/{did}.xhtml", doc)
        for name, data in assets.items():
            z.writestr(f"OEBPS/assets/img/{name}", data.encode() if isinstance(data, str) else data)
    print("wrote", out_path, os.path.getsize(out_path)//1024, "KB", "| docs", len(files), "| images", len(assets))


if __name__ == "__main__":
    import pymupdf
    os.makedirs(OUT, exist_ok=True)
    for mode, name in (("print", "00-合集-印刷版.pdf"), ("ereader", "01-合集-电子版.pdf")):
        # 封面
        ch = os.path.join(ROOT, f"_cover-{mode}.html")
        open(ch, "w", encoding="utf-8").write(cover_only_html(mode))
        cp = os.path.join(ROOT, f"_cover-{mode}.pdf")
        print_pdf(ch, cp)
        # 正文（无封面）
        bh, _ = assemble(mode, skip_cover=True)
        bp = os.path.join(ROOT, f"_body-{mode}.pdf")
        print_pdf(bh, bp)
        # 合并
        out = os.path.join(OUT, name)
        doc = pymupdf.open(cp)
        doc.insert_pdf(pymupdf.open(bp))
        doc.save(out, garbage=3, deflate=True)
        doc.close()
        print("merged ->", out, round(os.path.getsize(out)/1e6, 1), "MB")

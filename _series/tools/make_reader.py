# -*- coding: utf-8 -*-
"""make_reader.py —— 把一本书 / 一篇论文的 HTML 变成「单件单页」交互阅读页。

四种模式（一个脚本，一条命令）：
  book   九本专著：三档（骨架/阅读/全展）＋ 每章审问卡 ＋ 互跳结构地图
  paper  十五篇论文：三档 ＋ **一篇**审问卡（打脸条件读 LedgerReconciliation/ledger.csv 的 126 条总账）
                  ＋ 页内台账（iframe 懒加载）
  grain  《粗码》：三档 ＋ 39 张审问卡（打脸条件优先读附录 F 的表 F.1，其次附录 D，再其次正文）
                  ＋ 两个真沙盘（§3.2 驻点式／§27.7.4 退潮半衰期）
  coll   合集：只做导航（无正文），交给 make_atlas.py

铁律：
  · 不动 source/、不动印刷版；只在这个派生文件上加壳；
  · 四样（带走／打脸条件／封顶／动手）全部原文或原表摘录，一个字不写；
  · 三档只切 body 的一个 class；全展开用 content-visibility 保帧率；
  · 每页页脚印：数据源 / 生成脚本 / 快照日 / 三条「不能主张什么」。

用法：
  "$PY" _series/tools/make_reader.py knowledge-tradeoffs
  "$PY" _series/tools/make_reader.py --all
  "$PY" _series/tools/make_reader.py resolution-grain
"""
from __future__ import annotations

import csv
import glob
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAG = re.compile(r"<[^>]+>")
SNAP = "2026-11-26"

BOOKS = ["knowledge-tradeoffs", "capacity-cascade", "emergence-critical", "entropy-spiral",
         "interpretation-tradeoff", "impossibility-triangle", "distinction-evolution",
         "mind-forks", "hotspot-bills"]

PAPERS = ["ComputingDemystified", "WorldPeriodization", "SleepingResidue", "HunanRelaySystem",
          "BureauRotationCession", "HarnessEcology", "OptimizationBoundary", "CapacityProxies",
          "DomainCrossSection", "IsomorphismStrength", "MemoryAnchor", "MemoryStressTest",
          "MonarchCompetition", "SeamLedger", "LedgerReconciliation"]

# 论文 → 论文十五总账里的「篇」字段
REPO2PAPER = {
    "ComputingDemystified": "术语", "WorldPeriodization": "分期", "SleepingResidue": "残余",
    "HunanRelaySystem": "驿道", "BureauRotationCession": "官制", "HarnessEcology": "生态",
    "OptimizationBoundary": "优化", "CapacityProxies": "容量", "DomainCrossSection": "领域",
    "IsomorphismStrength": "同构", "MemoryAnchor": "锚点", "MemoryStressTest": "下限",
    "MonarchCompetition": "两层", "SeamLedger": "接缝", "LedgerReconciliation": "对账",
}
STATUS_ORDER = ["成立", "支持", "部分", "待检验", "开放", "证伪", "撤回"]


# ---------------------------------------------------------------- 小工具
def plain(s: str) -> str:
    s = TAG.sub("", s)
    s = (s.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
          .replace("&nbsp;", " ").replace("&#12288;", " ").replace("　", " "))
    return re.sub(r"\s+", " ", s).strip()


def squish(x: str, css: bool = False) -> str:
    x = re.sub(r"/\*.*?\*/", "", x, flags=re.S)
    x = re.sub(r"\n\s+", "\n", x)
    x = re.sub(r"\n{2,}", "\n", x)
    if css:
        x = (x.replace(": ", ":").replace(", ", ",").replace(" {", "{")
              .replace("; ", ";").replace(" }", "}").replace("\n", ""))
    return x.strip()


# ---------------------------------------------------------------- ① 折叠证据块
def wrap_evidence(t: str, caption_after: bool = False):
    """表格 / 来源块包进 <details>；summary 写清是哪张表（不编表号）。"""
    n = 0
    last = {"v": ""}
    pat = re.compile(r'<table\b[^>]*>.*?</table>|<div class="datasrc">.*?</div>', re.S)
    out, pos = [], 0

    def after_caption(i: int) -> str:
        if not caption_after:
            return ""
        m = re.match(r'\s*<p[^>]*>\s*(表\s?[A-Z]?[0-9]+[^<]{0,60})</p>', t[i:])
        return plain(m.group(1)) if m else ""

    def before_number(block_start: int) -> str:
        s = plain(t[max(0, block_start - 320):block_start])[-220:]
        hit = None
        for hit in re.finditer(r"表\s?([A-Z]?[0-9]+(?:\.[0-9]+)?)\s*[　 ]?([^\s。；，]{0,26})", s):
            pass
        if not hit:
            return ""
        num, title = hit.group(1), hit.group(2).strip("　 ")
        return f"表{num}：{title}" if title else f"表{num}"

    def cols(block: str) -> str:
        m = re.search(r"<thead>.*?</thead>", block, re.S) or re.search(r"<tr>.*?</tr>", block, re.S)
        if not m:
            return ""
        cells = [plain(x) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", m.group(0), re.S)]
        cells = [c for c in cells if c][:4]
        return ("列：" + " / ".join(cells)) if cells else ""

    for m in pat.finditer(t):
        out.append(t[pos:m.start()])
        block, skip = m.group(0), m.end()
        if block.startswith("<table"):
            c = ""
            cap = re.search(r"<caption[^>]*>(.*?)</caption>", block, re.S)
            if cap:
                c = plain(cap.group(1))
                c = re.sub(r"^表\s*", "表", c)
                c = re.sub(r"^(表[A-Z]?[\d.]+)\s*", r"\1：", c)
            if not c:
                ac = after_caption(m.end())
                if ac:
                    c = re.sub(r"^(表[A-Z]?[0-9]+)\s*", r"\1：", ac)
                    mm = re.match(r'\s*<p[^>]*>\s*(?:表\s?[A-Z]?[0-9]+[^<]{0,60})</p>', t[m.end():])
                    if mm:
                        skip = m.end() + mm.end()
                        tail = t[m.end():skip]
            if not c:
                c = before_number(m.start())
            last["v"] = c
            d = cols(block)
            label = ("证据 · " + c) if c else (("证据 · 表（" + d + "）") if d else "证据 · 表")
            inner = '<div class="tw">' + block + '</div>'
            if skip > m.end():
                inner += t[m.end():skip].strip()
            out.append('<details data-ev><summary>' + label + "</summary>" + inner + "</details>")
        else:
            c = last["v"] or before_number(m.start())
            label = ("来源与等级 · " + c) if c else "来源与等级 · 本表"
            out.append('<details data-ev><summary>' + label + "</summary>" + block + "</details>")
        n += 1
        pos = skip
    out.append(t[pos:])
    return "".join(out), n


# ---------------------------------------------------------------- ② 摘录器
def _grades(ch: str):
    found = []

    def add(x):
        if x and x not in found:
            found.append(x)

    for m in re.finditer(r"([ABC])\s*／\s*([甲乙丙])", ch):
        add(m.group(1) + "／" + m.group(2))
    for m in re.finditer(r"[⊗⊕○◐●◆]\s*[^（(]{0,10}[（(]\s*([ABC])\s*[)）]", ch):
        add(m.group(1))
    for m in re.finditer(r"［[^］]{0,20}?([ABC])\s*(?:／\s*([甲乙丙]))?］", ch):
        add(m.group(1) + ("／" + m.group(2) if m.group(2) else ""))
    for m in re.finditer(r"(?<![A-Za-z])([ABC])\s*级", ch):
        add(m.group(1))
    base = [g for g in found if "／" in g]
    bare = [g for g in found if "／" not in g and not any(b.startswith(g + "／") for b in base)]
    return (base + bare)[:4]


def _takeaway(ch: str) -> str:
    """章末『一句话带走』优先；否则本章小结末条末句。"""
    val = ""
    for m in re.finditer(r'<div class="box box-takeaway">(.*?)</div>', ch, re.S):
        s = plain(m.group(1))
        if "一句话带走" in s:
            val = s
    if not val:
        m = re.search(r'一句话带走[^<]*</h3>\s*<div class="box[^"]*">(.*?)</div>', ch, re.S)
        if m:
            val = plain(m.group(1))
    val = re.sub(r"^\s*(<b>)?\s*一句话带走[：:]?\s*(</b>)?\s*", "", val)
    val = re.sub(r"^本章主张[。：:]?\s*", "", val)
    if not val:
        m0 = re.search(r'<div class="chapter-opener">(.*?)</div>', ch, re.S)
        if m0:
            ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', m0.group(1), re.S)]
            ps = [x for x in ps if len(x) > 30]
            if not val and ps:
                val = ps[0]
        items, _ = _summary_items(ch)
        if not val and items:
            last = items[-1]
            parts = re.split(r"[。！？]", last)
            val = (parts[-2] if len(parts) > 1 and parts[-2] else parts[0]) + "。"
    if not val:                          # 最后一层：本章最长的一段正文（仍是原文）
        ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', ch, re.S)]
        ps = [x for x in ps if len(x) > 40]
        if ps:
            val = max(ps, key=len)
    return val[:120] + ("……" if len(val) > 120 else "")


def _summary_items(ch: str):
    pats = [r'本章(?:小结|结论(?:与边界)?|总结)[^<]*</h3>\s*(?:<p[^>]*>.*?</p>\s*)?<(ol|ul)[^>]*>(.*?)</\1>',
            r'class="box box-summary"[^>]*>\s*<span class="bt">本章(?:小结|结论)</span>\s*<(ol|ul)[^>]*>(.*?)</\1>']
    for pat in pats:
        m = re.search(pat, ch, re.S)
        if m:
            li = [plain(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', m.group(2), re.S)]
            return [x for x in li if x], m.end()
    m = re.search(r'本章小结[^<]*</h3>\s*<p[^>]*>(.*?)</p>', ch, re.S)
    if m:
        return [plain(m.group(1))], m.end()
    m = re.search(r'<div class="box[^"]*">(?:(?!</div>).){0,80}本章(?:小结|结论)(.*?)</div>', ch, re.S)
    if m:
        li = [plain(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.S)]
        if li:
            return li, m.end()
        ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', m.group(1), re.S)]
        if ps:
            return ps[-1:], m.end()
    return [], -1


def _falsify_from_text(ch: str) -> str:
    marks = ("若这条判据错了", "这条要是错了", "可反驳条件", "若这些条目")
    for pat in (r'<div class="note">(.*?)</div>', r'<div class="box[^"]*">(.*?)</div>',
                r'<p[^>]*>(.*?)</p>'):
        for m in re.finditer(pat, ch, re.S):
            s = plain(m.group(1))
            for mk in marks:
                i = s.find(mk)
                if i < 0:
                    continue
                rest = s[i + len(mk):]
                rest = re.sub(r"^[，,、]?\s*(你)?\s*会看到什么[：:]?\s*】?\s*", "", rest)
                rest = re.sub(r"^[】】：:，,、]\s*", "", rest)
                if rest:
                    return rest
    return ""


# ---------------------------------------------------------------- ③ 论文的总账
def ledger_exp(repo: str) -> str:
    """15 篇论文的打脸条件：唯一权威源＝论文十五的 126 条总账。"""
    prefix = REPO2PAPER.get(repo, "")
    path = os.path.join(ROOT, "LedgerReconciliation", "ledger.csv")
    if not prefix or not os.path.exists(path):
        return ""
    rows = [r for r in csv.DictReader(io.open(path, encoding="utf-8")) if r["paper"] == prefix]
    if not rows:
        return ""
    by = {}
    for r in rows:
        by.setdefault(r["status"], []).append(r)
    bits = [f"{k} {len(by[k])}（{'、'.join(r['pid'] for r in by[k])}）"
            for k in STATUS_ORDER if k in by]
    exp = f"论文十五总账登记 {len(rows)} 条：" + "；".join(bits) + "。"
    picks = []
    for k in ("证伪", "撤回", "部分", "待检验"):
        for r in by.get(k, []):
            s = plain(r["stmt"])
            picks.append(f"{r['pid']}（{s[:42] + ('…' if len(s) > 42 else '')}）")
            break
    if picks:
        exp += "战损项 —— " + "；".join(picks[:3]) + "。"
    return exp


# ---------------------------------------------------------------- ④ 章末边界
BACK_PAT = (r'<div class="chapter-opener">', r'<h2 class="chapter"', r'<h1 class="part-title"',
            r'<h2[^>]*>(?!第\d+章)[^<]{0,12}(附录|结语|后记|参考文献|术语表|通俗导读|导读)',
            r'<div id="rfoot">', r'<div class="back-matter"', r'</body>')


def chapter_end(ch: str) -> int:
    own = ch.find('<h2 class="chapter"')
    frm = own + 12 if own >= 0 else 0
    end = len(ch)
    for pat in BACK_PAT:
        m = re.search(pat, ch[frm:])
        if m:
            end = min(end, frm + m.start())
    return end


def _chapter_cards(t: str, extra=None):
    """逐章插卡。extra(no, ch) 可覆盖『打脸条件』（《粗码》读附录 F）。"""
    chunks = re.split(r'(?=<div id="ch\d+">)', t)
    out, made, missing = [], 0, []
    for ch in chunks:
        m = re.match(r'<div id="ch(\d+)">', ch)
        if not m:
            out.append(ch)
            continue
        no = m.group(1)
        end = chapter_end(ch)
        take = _takeaway(ch[:end])
        exp = _falsify_from_text(ch[:end])
        if extra:
            ex = extra(no, ch[:end])
            if ex:
                exp = ex
        do = re.search(r'<div class="box box-do">(.*?)</div>', ch[:end], re.S)
        do_txt = re.sub(r"^【[^】]*】\s*", "", plain(do.group(1))) if do else ""
        do_txt = do_txt[:80] + ("……" if len(do_txt) > 80 else "")
        if len(exp) > 300:
            exp = exp[:300] + "……"
        grades = _grades(ch[:end])
        if not (take or exp):
            missing.append(no)
            out.append(ch)
            continue
        made += 1
        rows = [("带走", take)] if take else []
        rows += [("打脸条件", exp)] if exp else []
        rows += [("封顶", "、".join(grades))] if grades else []
        rows += [("动手", do_txt)] if do_txt else []
        card = ['<details class="audit" data-ch="' + no + '">',
                '<summary>审问第' + no + '章：带走什么 · 怎么推翻</summary><div class="abody">']
        card += ['<div class="ar"><b>' + k + '</b><p>' + v + "</p></div>" for k, v in rows]
        card.append('<button class="acopy" data-ch="' + no + '">复制这一章的对账指令</button>')
        card.append("</div></details>")
        card = "".join(card)
        # 插在章内最后一个标题级『本章文献』之前；否则章末边界
        pos = end
        for mk in re.finditer(r'<h[2-4][^>]*>[^<]{0,8}本章文献', ch[:end]):
            pos = mk.start()
        ch = ch[:pos] + card + ch[pos:]
        out.append(ch)
    return "".join(out), made, missing


# ---------------------------------------------------------------- ⑤ 外壳
CSS = r"""
html,body{max-width:100%;overflow-x:hidden}
pre,code{overflow-wrap:anywhere;word-break:break-word}
pre{overflow-x:auto;max-width:100%}
figure,svg,img,canvas,table{max-width:100%!important;height:auto}
.tw,details[data-ev]{max-width:100%;overflow-x:auto}
#sandbox,#sandbox2,#sandbox3,.sgrid,.sl{max-width:100%;min-width:0;box-sizing:border-box}
:root{--ink:#1f3b57;--alt:#b5651d;--line:#e2dccd;--wash:#faf8f3;--paper:#fbfaf7;--faint:#6b6255}
body{background:var(--paper);color:#1c1c1c;font-family:"Noto Sans SC","Microsoft YaHei",-apple-system,sans-serif}
body.reader{max-width:47em;margin:0 auto;padding:0 20px 90px;font-size:17px;line-height:1.9}
body.reader p{margin:0 0 .85em}
body.reader svg,body.reader img{max-width:100%;height:auto}
body.reader figure{max-width:100%;overflow-x:auto}
body.reader h2.chapter{margin:1.6em 0 .5em;font-size:26px;line-height:1.35}
body.reader h3{margin:1.4em 0 .4em;font-size:19px}
body.reader h4{margin:1.1em 0 .3em;font-size:17px}
body.reader table.nat{width:100%;font-size:14.5px;border-collapse:collapse}
body.reader table.nat th,body.reader table.nat td{padding:7px 9px;border-bottom:1px solid #eee}
body.reader .cover-page{width:auto!important;max-width:100%;height:auto}
body.reader .part-page{height:auto;min-height:60vh;border:1px solid var(--line)}
body.reader .datasrc{font-size:12.5px;color:var(--faint);background:var(--wash);
  border-left:3px solid var(--line);padding:8px 11px;margin:.4em 0}
body.reader .mblock{background:#f7f6f2;border:1px solid #ece8de;border-radius:8px;padding:10px 12px;overflow-x:auto}
body.reader code{overflow-wrap:anywhere}
body.reader pre{overflow-x:auto;max-width:100%}
body.reader #ledger,body.reader #ledger iframe{max-width:100%}
body.reader #ledger{overflow-x:auto}
.tw{overflow-x:auto}
.tw table{min-width:100%}
details[data-ev]{margin:.5em 0 1.1em;border:1px solid #ece7da;border-radius:10px;background:#fff;padding:0 12px}
details[data-ev]>summary{cursor:pointer;list-style:none;padding:8px 0;font-size:13px;color:var(--alt);line-height:1.5}
details[data-ev]>summary::-webkit-details-marker{display:none}
details[data-ev]>summary:before{content:"▸ ";color:var(--alt)}
details[data-ev][open]>summary:before{content:"▾ "}
details.audit{margin:1.6em 0 2em;border:1px solid #dfd7c4;border-radius:12px;background:#fffdf7;padding:0 14px}
details.audit>summary{cursor:pointer;list-style:none;padding:11px 0;font-size:13.5px;color:var(--ink);font-weight:600}
details.audit>summary::-webkit-details-marker{display:none}
details.audit>summary:before{content:"⌗ ";color:var(--alt)}
details.audit .ar{margin:2px 0 9px;display:grid;grid-template-columns:74px 1fr;gap:8px}
details.audit .ar b{font-size:11.5px;color:var(--alt);font-weight:600;padding-top:2px}
details.audit .ar p{margin:0;font-size:13.5px;line-height:1.8;color:#3d3a34}
.acopy{margin:4px 0 12px;font:12px/1 inherit;padding:7px 12px;border:1px solid var(--line);
  background:#fff;border-radius:999px;cursor:pointer;color:#4a463d}
.acopy.ok{background:var(--ink);color:#fff;border-color:var(--ink)}
body.mode-bone p,body.mode-bone ul,body.mode-bone ol,body.mode-bone li{display:none}
body.mode-bone h2+p,body.mode-bone h2+p+ul{display:block}
body.mode-bone .box p,body.mode-bone .part-intro p,body.mode-bone p.lead,
body.mode-bone .epigraph p,body.mode-bone p.epigraph{display:block}
body.mode-bone .box ul,body.mode-bone .box ol{display:block}
body.mode-bone .box li{display:list-item}
body.mode-bone details[data-ev],body.mode-bone table,body.mode-bone .audit{display:none}
body.mode-full details[data-ev]{display:block}
body.mode-full details[data-ev]:not([open])>.tw,body.mode-full details[data-ev]:not([open])>.datasrc{
  content-visibility:auto;contain-intrinsic-size:auto 520px}
#rbar{position:fixed;right:16px;top:14px;z-index:60;display:flex;gap:6px;align-items:center;
  background:rgba(255,255,255,.95);border:1px solid var(--line);border-radius:999px;padding:5px 8px;
  box-shadow:0 6px 22px rgba(31,59,87,.10)}
#rbar button{font:12.5px/1 inherit;padding:7px 12px;border:1px solid transparent;background:none;
  color:#4a463d;border-radius:999px;cursor:pointer}
#rbar button.on{background:var(--ink);color:#fff}
#rbar .sep{width:1px;height:16px;background:var(--line);margin:0 2px}
#rbar .jump{font:12.5px/1 inherit;padding:7px 12px;color:#fff;background:var(--alt);
  border-radius:999px;text-decoration:none;white-space:nowrap}
#rfoot{margin:46px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--wash);
  padding:14px 18px;font-size:12.8px;color:#4a463d;line-height:1.85}
#rfoot .lb{display:block;font-size:11px;letter-spacing:.1em;color:#8c8c8c;margin:10px 0 2px}
#rfoot code{background:#fff;border:1px solid var(--line);border-radius:4px;padding:0 4px}
#sandbox,#sandbox2{scroll-margin-top:70px;margin:32px 0 10px;border:1px solid var(--line);
  border-radius:14px;background:#fff;padding:18px 20px 14px}
#sandbox h2,#sandbox2 h2{font-size:19px;margin:0 0 4px;color:var(--ink)}
.lede{font-size:13px;color:var(--faint);margin:0 0 14px}
.sgrid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:18px}
.sl{margin:0 0 10px}
.sl{display:grid;grid-template-columns:minmax(0,1fr);gap:4px}
.sl label{display:flex;justify-content:space-between;gap:8px;font-size:12.5px;color:#4a463d;min-width:0}
.sl input[type=range]{width:100%;min-width:0;accent-color:#1f3b57}
canvas{max-width:100%;height:auto;display:block}
.srow{display:flex;justify-content:space-between;font-size:13px;padding:5px 8px;border-radius:7px;background:var(--wash);margin:5px 0}
.srow b{color:var(--ink);font-variant-numeric:tabular-nums}
.badge{margin-top:8px;padding:8px 10px;border-radius:8px;font-size:12.5px}
.badge.t{background:#eef4fb;color:#1f3b57;border:1px solid #cdd9e4}
.badge.f{background:#fdf6ec;color:#8a4f14;border:1px solid #e8d4b4}
#cv-vstar,#cv-half{width:100%;height:230px;display:block;background:#fff;border:1px solid var(--line);border-radius:12px}
@media (max-width:820px){.sgrid{grid-template-columns:1fr}}
@media (max-width:640px){
  body.reader{padding:0 12px 80px;font-size:16px;line-height:1.85}
  body.reader #sandbox,body.reader #sandbox2{padding:14px 12px 10px}
  body.reader #cv-vstar,body.reader #cv-half{height:200px}
  details.audit .ar{grid-template-columns:1fr;gap:2px}
  #rbar{right:8px;top:8px;padding:4px 5px}
  #rbar button{padding:6px 8px;font-size:11.5px}
}
"""

JS = r"""
(function(){
  var bar=document.getElementById('rbar');
  var de=document.querySelectorAll('details[data-ev]');
  var au=document.querySelectorAll('details.audit');
  function set(m){
    document.body.classList.remove('mode-bone','mode-full');
    if(m==='bone') document.body.classList.add('mode-bone');
    if(m==='full') document.body.classList.add('mode-full');
    var open=(m==='full');
    [].forEach.call(de,function(d){d.open=open;});
    [].forEach.call(au,function(d){d.open=false;});
    [].forEach.call(bar.querySelectorAll('[data-m]'),function(b){
      b.classList.toggle('on', b.getAttribute('data-m')===m);
    });
    try{localStorage.setItem('reader-mode',m);}catch(e){}
  }
  bar.addEventListener('click',function(e){
    var b=e.target.closest('[data-m]'); if(!b) return;
    var m=b.getAttribute('data-m');
    if(m==='sandbox'||m==='sb1'||m==='sb2'){
      var id=m==='sb2'?'sandbox2':(m==='sb3'?'sandbox3':'sandbox');
      var s=document.getElementById(id); if(s) s.scrollIntoView({behavior:'smooth',block:'start'});
      return;
    }
    if(m==='ledger'){var l=document.getElementById('ledger');
      if(l) l.scrollIntoView({behavior:'smooth',block:'start'}); return;}
    set(m);
  });
  var saved='read'; try{saved=localStorage.getItem('reader-mode')||'read';}catch(e){}
  set(saved);
  var lb=document.getElementById('ledbox');
  if(lb) lb.addEventListener('toggle',function(){
    if(!lb.open) return;
    var f=lb.querySelector('iframe');
    if(f && !f.src && f.dataset.src) f.src=f.dataset.src;
  });
  document.addEventListener('click',function(e){
    var b=e.target.closest('.acopy'); if(!b) return;
    var card=b.closest('details.audit'), txt=
      '你正在读一本方法论上很硬的书。请严格按作者的三条纪律与我讨论：'+
      '① 结论强度不得超过证据强度；② C 级（稀疏·构造·思辨）的命题一律写成条件句；'+
      '③ 不许顺从讨好，先帮我找出我例子里的隐藏代价与成本转移，再谈结论。'+
      '下面是我刚读完的这段的“对账四行”，材料全部摘自原文：\n\n';
    card.querySelectorAll('.ar').forEach(function(r){
      txt += '【'+r.querySelector('b').textContent+'】'+r.querySelector('p').textContent+'\n';
    });
    txt += '\n请先用“这个词/这个结论凭什么”反问我一次，再回答。';
    function done(){ b.textContent='已复制'; b.classList.add('ok');
      setTimeout(function(){ b.textContent=b.dataset.t||'复制对账指令'; b.classList.remove('ok'); },1600); }
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(done,fallback);
    } else fallback();
    function fallback(){
      var ta=document.createElement('textarea'); ta.value=txt; document.body.appendChild(ta);
      ta.select(); try{document.execCommand('copy'); done();}catch(err){}
      document.body.removeChild(ta);
    }
  });
})();
"""

JS_SB = r"""
(function(){
  function sl(box,label,key,mn,mx,step,val,fmt){
    var d=document.createElement('div'); d.className='sl';
    d.innerHTML='<label>'+label+'<b id="lbl-'+key+'">'+fmt(val)+'</b></label>'+
      '<input type="range" id="sl-'+key+'" min="'+mn+'" max="'+mx+'" step="'+step+'" value="'+val+'">';
    box.appendChild(d);
  }
  var V={T:8,lam:2,w:1,s0:6}, vb=document.getElementById('vsliders');
  if(vb){
    sl(vb,'T 时间压力','T',0.5,20,0.5,8,function(v){return v.toFixed(1)});
    sl(vb,'λ 精力影子价格','lam',0,10,0.5,2,function(v){return v.toFixed(1)});
    sl(vb,'w 错的代价','w',0.2,5,0.1,1,function(v){return v.toFixed(1)});
    sl(vb,'σ₀ 外生环境宽度','s0',0.5,20,0.5,6,function(v){return v.toFixed(1)});
    vb.addEventListener('input',function(e){
      var k=e.target.id.replace('sl-',''); V[k]=parseFloat(e.target.value);
      document.getElementById('lbl-'+k).textContent=e.target.value; drawV();
    });
    function drawV(){
      var v=(V.T+V.lam)/(2*V.w), tunnel=V.s0>v;
      document.getElementById('vout').innerHTML=
        '<div class="srow"><span>v* 驻点</span><b>'+v.toFixed(2)+'</b></div>'+
        '<div class="srow"><span>σ₀ ／ v*</span><b>'+(V.s0/v).toFixed(2)+'</b></div>'+
        '<div class="badge '+(tunnel?'t':'f')+'">'+
        (tunnel?'隧道：σ₀ > v* → 切中心、把格缩窄':'模糊：σ₀ ≤ v* → 保中心、把格压粗')+'</div>';
      var c=document.getElementById('cv-vstar'),g=c.getContext('2d');
      var r=c.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);
      c.width=r.width*dpr;c.height=r.height*dpr;g.setTransform(dpr,0,0,dpr,0,0);
      var W=r.width,H=r.height;g.clearRect(0,0,W,H);
      var mx=Math.max(v,V.s0)*1.3;
      [['v*',v,'#b5651d'],['σ₀',V.s0,'#1f3b57']].forEach(function(it,i){
        var y=H*0.30+i*H*0.34, w=it[1]/mx*(W-130);
        g.fillStyle=it[2];g.globalAlpha=.85;g.fillRect(56,y,w,24);g.globalAlpha=1;
        g.fillStyle='#3d3a34';g.font='12px sans-serif';g.fillText(it[0],12,y+17);
        g.fillText(it[1].toFixed(2),60+w+8,y+17);
      });
      g.fillStyle='#8c8c8c';g.font='11px sans-serif';
      g.fillText('条长＝数值；谁更长，决定落进哪一相（只判方向与量级）',12,H-8);
    }
    drawV();
  }
  var H2={C:3,lam:0.8,g0:0.12}, hb=document.getElementById('hsliders');
  if(hb){
    sl(hb,'C 专用性转换成本','C',0,8,0.5,3,function(v){return v.toFixed(1)});
    sl(hb,'λ 精力约束','lam',0,3,0.1,0.8,function(v){return v.toFixed(2)});
    sl(hb,'γ₀ 退场基础速率／年','g0',0.02,0.6,0.01,0.12,function(v){return v.toFixed(2)});
    hb.addEventListener('input',function(e){
      var k=e.target.id.replace('sl-',''); H2[k]=parseFloat(e.target.value);
      document.getElementById('lbl-'+k).textContent=e.target.value; drawH();
    });
    function th(C,lam,g0){ return Math.log(2)/g0*Math.exp(lam*C); }
    function drawH(){
      var t2=th(H2.C,H2.lam,H2.g0);
      document.getElementById('hout').innerHTML=
        '<div class="srow"><span>半衰期 t½</span><b>'+(t2<1?(t2*12).toFixed(1)+' 个月':t2.toFixed(1)+' 年')+'</b></div>'+
        '<div class="srow"><span>退潮 10 年后存量</span><b>'+(100*Math.exp(-Math.log(2)*10/t2)).toFixed(1)+'%</b></div>'+
        '<div class="badge f">C＝'+H2.C.toFixed(1)+' 时，半衰期是 C＝0 的 '+Math.exp(H2.lam*H2.C).toFixed(1)+' 倍</div>';
      var c=document.getElementById('cv-half'),g=c.getContext('2d');
      var r=c.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);
      c.width=r.width*dpr;c.height=r.height*dpr;g.setTransform(dpr,0,0,dpr,0,0);
      var W=r.width,Hh=r.height,P={l:44,r:14,t:14,b:26};g.clearRect(0,0,W,Hh);
      var TY=10;
      function X(y){return P.l+y/TY*(W-P.l-P.r)}
      function Y(f){return Hh-P.b-f*(Hh-P.t-P.b)}
      g.strokeStyle='#e2dccd';g.beginPath();g.moveTo(P.l,P.t);g.lineTo(P.l,Hh-P.b);g.lineTo(W-P.r,Hh-P.b);g.stroke();
      [[H2.C,'#b5651d'],[0,'#8fa8bd'],[Math.min(8,H2.C+2),'#1f3b57']].forEach(function(cv){
        var tt=th(cv[0],H2.lam,H2.g0);
        g.beginPath();
        for(var y=0;y<=TY+1e-9;y+=0.1){
          var f=Math.exp(-Math.log(2)*y/tt), x=X(y), yy=Y(f);
          y?g.lineTo(x,yy):g.moveTo(x,yy);
        }
        g.strokeStyle=cv[1];g.lineWidth=2;g.stroke();
      });
      g.fillStyle='#8c8c8c';g.font='11px sans-serif';
      g.fillText('年',W-P.r-8,Hh-8); g.fillText('存量',4,P.t+9);
      var t2x=X(Math.min(TY,t2));
      g.strokeStyle='rgba(181,101,29,.55)';g.setLineDash([4,4]);
      g.beginPath();g.moveTo(t2x,P.t);g.lineTo(t2x,Hh-P.b);g.stroke();g.setLineDash([]);
    }
    drawH();
  }
})();
"""

TRI_SB = """
<section id="sandbox3">
  <h2>动手：12 站背包客（正文那个模型）</h2>
  <p class="lede">12 个单元排成一条尺度线，每站三选一：不描述 0／粗捆绑 1／精确描述 2，预算 Σr≤15。
  C＝精确单元数÷12，A＝1−档位断点÷11，T＝相邻两单元都被覆盖的比例÷11——三个式子照抄正文。</p>
  <div class="sgrid"><div><div id="sts"></div><div id="tout"></div>
  <button id="trun" style="margin-top:8px;font:12.5px/1 inherit;padding:7px 12px;border:1px solid #e2dccd;border-radius:999px;background:#fff;cursor:pointer">穷举校验（3¹² 全算）</button>
  </div><div><canvas id="cv-tri2"></canvas></div></div>
</section>
"""

JS_TRI = r"""
(function(){
  var box=document.getElementById('sts'); if(!box) return;
  var N=12,K=15, lv=new Array(N).fill(0); lv[0]=1; lv[1]=2; lv[2]=1;
  for(var i=0;i<N;i++){(function(i){
    var d=document.createElement('div');
    d.style.cssText='display:inline-block;width:calc(8.33% - 4px);margin:2px;height:30px;line-height:30px;'+
      'text-align:center;font-size:11px;border:1px solid #e2dccd;border-radius:6px;cursor:pointer;background:#fbfaf7';
    d.textContent=i+1; d.onclick=function(){lv[i]=(lv[i]+1)%3;render();}; box.appendChild(d);
  })(i);}
  function calc(v){var cost=0,n2=0,brk=0,both=0;
    for(var i=0;i<N;i++){cost+=v[i];if(v[i]===2)n2++;}
    for(var i=1;i<N;i++){if(v[i]!==v[i-1])brk++;if(v[i]>=1&&v[i-1]>=1)both++;}
    var C=n2/N,A=1-brk/(N-1),T=both/(N-1);return {cost:cost,C:C,A:A,T:T,sum:C+A+T};}
  function render(){
    var c=calc(lv);
    [].forEach.call(box.children,function(d,i){
      d.style.background=lv[i]===2?'#1f3b57':(lv[i]===1?'#e8eef4':'#fbfaf7');
      d.style.color=lv[i]===2?'#fff':'#6b6255';
    });
    document.getElementById('tout').innerHTML=
      '<div class="srow"><span>预算</span><b>'+c.cost+' / '+K+'</b></div>'+
      '<div class="srow"><span>C 完备 ／ A 可组合</span><b>'+c.C.toFixed(2)+' ／ '+c.A.toFixed(2)+'</b></div>'+
      '<div class="srow"><span>T 传递 ／ 三者和</span><b>'+c.T.toFixed(2)+' ／ '+c.sum.toFixed(2)+'</b></div>'+
      '<div class="badge '+(c.cost>K?'f':'t')+'">'+(c.cost>K?'超支：不在模型允许的集合里':'余 '+(K-c.cost)+' 单位')+'</div>';
  }
  document.getElementById('trun').onclick=function(){
    var t0=performance.now(),best={C:0,A:0,T:0,sum:0},n=0,v=new Array(N),tot=Math.pow(3,N);
    for(var t=0;t<tot;t++){var x=t,cost=0;
      for(var i=0;i<N;i++){v[i]=x%3;x=(x-v[i])/3;cost+=v[i];}
      if(cost>K)continue;n++;var c=calc(v);
      best.C=Math.max(best.C,c.C);best.A=Math.max(best.A,c.A);
      best.T=Math.max(best.T,c.T);best.sum=Math.max(best.sum,c.sum);}
    document.getElementById('tout').innerHTML=
      '<div class="srow"><span>预算内分配</span><b>'+n.toLocaleString()+'</b></div>'+
      '<div class="srow"><span>max C / A / T</span><b>'+best.C.toFixed(2)+' / '+best.A.toFixed(2)+' / '+best.T.toFixed(2)+'</b></div>'+
      '<div class="srow"><span>三者和上界</span><b>'+best.sum.toFixed(2)+'</b></div>'+
      '<div class="badge f">'+(Math.round(performance.now()-t0))+' ms；书上印的是 473,721 / 0.58 / 1.00 / 1.00 / 2.16——对得上</div>';
  };
  render();
})();
"""

SB_VSTAR = """
<section id="sandbox">
  <h2>动手：驻点式 v* = (T + λ) / 2w（第 3 章 §3.2）</h2>
  <p class="lede">T＝时间压力，λ＝精力影子价格，w＝错一次的代价权重；<b>v* 是"该切多细"的驻点</b>。
  再拿它与外生环境宽度 σ₀ 比：<b>σ₀ 比 v* 宽</b>就切中心、把格缩窄（隧道）；<b>σ₀ 不比 v* 宽</b>就保中心、把格压粗（模糊）。
  滑块上没有一个是编的系数。</p>
  <div class="sgrid"><div><div id="vsliders"></div><div id="vout"></div></div>
  <div><canvas id="cv-vstar"></canvas></div></div>
</section>
"""

SB_HALF = """
<section id="sandbox2">
  <h2>动手：退潮半衰期 t½ = (ln2 / γ₀) · e^{λC}（第 27 章 §27.7.4）</h2>
  <p class="lede">退潮期新进项归零，存量按 n(t) = n₀·exp(−γ₀·e^{−λC}·t) 冻结衰减（式 27.4）；半衰期式 27.5。
  <b>C 是专用性转换成本</b>：C 每加一档，半衰期乘 e^{λ·ΔC}——<b>进场攒局快，退场出清慢</b>。</p>
  <div class="sgrid"><div><div id="hsliders"></div><div id="hout"></div></div>
  <div><canvas id="cv-half"></canvas></div></div>
</section>
"""


def shell(t: str, bar: str, foot: list, body_class="reader") -> str:
    t = re.sub(r"<body[^>]*>", '<body class="' + body_class + '">' + bar, t, count=1)
    t = t.replace("</body>", "".join(foot) + "</body>", 1)
    t = t.replace("</head>", "<style>" + squish(CSS, css=True) + "</style></head>", 1)
    return t


def foot_block(repo, src_note, script_note, bounds):
    f = ['<div id="rfoot"><b>读法与边界</b>',
         '<span class="lb">数据源</span><div>' + src_note + '</div>',
         '<span class="lb">生成脚本</span><div>' + script_note + '</div>',
         '<span class="lb">快照</span><div>' + SNAP + ' 的仓库状态；改稿后重跑本脚本，数字会跟着变。</div>',
         '<span class="lb">不能主张什么</span>']
    f += ['<div>· ' + b + '</div>' for b in bounds]
    f.append('</div>')
    return f


BOUNDS_BOOK = [
    "本页只是**阅读层**：正文、表格、公式一个字未改；折叠条与审问卡都是原文摘录。",
    "每一处 A／B／C 等级是作者标的，**本页不重算、不改写**；摘要不等于全章。",
    "骨架档藏起来的是证据与推导，不是删掉——按「全展」可随时看见被收起的每一张表。",
]


# ---------------------------------------------------------------- ⑥ 四种构建
def out_path(repo, name=None):
    d = os.path.join(ROOT, repo, "assets")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name or f"{repo}-reader.html")


TRI_ANCHOR = {"knowledge-tradeoffs": '<h3 id="sec4-4"', "impossibility-triangle": '<h3 id="sec2-9">'}


def build_book(repo: str) -> dict:
    src = os.path.join(ROOT, repo, "output", "book-ereader.html")
    t = io.open(src, encoding="utf-8").read()
    base = os.path.getsize(src) / 1024
    t, n_ev = wrap_evidence(t)
    t, n_card, miss = _chapter_cards(t)
    has_tri = repo in TRI_ANCHOR and TRI_ANCHOR[repo] in t
    if has_tri:
        t = t.replace(TRI_ANCHOR[repo], TRI_SB + TRI_ANCHOR[repo], 1)
    bar = ('<div id="rbar"><button data-m="bone">骨架</button>'
           '<button data-m="read" class="on">阅读</button><button data-m="full">全展</button>'
           + ('<span class="sep"></span><button data-m="sb3">沙盘</button>' if has_tri else '')
           + '<span class="sep"></span><a class="jump" href="' + repo + '-explorer.html">结构地图 →</a></div>')
    foot = foot_block(repo,
                      "正文与表格：<code>" + repo + "/source/</code>；本页由 <code>output/book-ereader.html</code> 派生。",
                      "<code>_series/tools/make_reader.py</code>（book 模式）。", BOUNDS_BOOK)
    t = shell(t, bar, foot)
    t = t.replace("</body>", "<script>" + squish(JS) + (squish(JS_TRI) if has_tri else "") + "</script></body>", 1)
    out = out_path(repo)
    io.open(out, "w", encoding="utf-8", newline="\n").write(t)
    return {"out": out, "base": base, "kb": os.path.getsize(out) / 1024,
            "ev": n_ev, "cards": n_card, "missing": miss}


def build_paper(repo: str) -> dict:
    cands = [x for x in glob.glob(os.path.join(ROOT, repo, "*.html"))
             if "explorer" not in os.path.basename(x) and "reader" not in os.path.basename(x)]
    src = max(cands, key=os.path.getsize)
    t = io.open(src, encoding="utf-8").read()
    base = os.path.getsize(src) / 1024
    t, n_ev = wrap_evidence(t, caption_after=True)

    # 带走：结论/小结首段 → 摘要首段
    take = ""
    for pat in (r'<h2[^>]*>[^<]{0,10}(结论|小结)</h2>(.*?)(?:<h2|$)',
                r'<h2[^>]*>[^<]{0,6}摘要</h2>(.*?)(?:<h2|$)'):
        m = re.search(pat, t, re.S)
        if m:
            ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', m.group(m.lastindex), re.S)]
            ps = [x for x in ps if len(x) > 30]
            if ps:
                take = ps[0][:130] + ("……" if len(ps[0]) > 130 else "")
                break
    # 打脸条件：论文十五总账 → 正文
    exp = ledger_exp(repo) or _falsify_from_text(t)
    if len(exp) > 300:
        exp = exp[:300] + "……"
    grades = _grades(t)
    rows = [("带走", take or "见结论节"), ("打脸条件", exp or "见附录的可证伪登记")]
    if grades:
        rows.append(("封顶", "、".join(grades)))
    card = ['<details class="audit" data-ch="0">'
            '<summary>审问本篇：核心主张 · 证据封顶 · 怎么推翻</summary><div class="abody">']
    card += ['<div class="ar"><b>' + k + '</b><p>' + v + "</p></div>" for k, v in rows]
    card.append('<button class="acopy" data-ch="0">复制这一篇的对账指令</button></div></details>')
    card = "".join(card)
    mk = re.search(r'<h2[^>]*>[^<]{0,4}附录\s?A', t)
    t = (t[:mk.start()] + card + t[mk.start():]) if mk else t.replace("</body>", card + "</body>", 1)

    # 台账：同目录 <repo>-explorer.html，iframe 懒加载
    # 只认「轻量数据台账」：排除 reader 与任何 >400 KB 的整篇正文（否则会把阅读页误当台账）
    exps = [x for x in sorted(glob.glob(os.path.join(ROOT, repo, "interactive", "*.html")))
            + sorted(glob.glob(os.path.join(ROOT, repo, "assets", "*.html")))
            if "reader" not in os.path.basename(x)
            and os.path.basename(x) != f"{repo}-explorer.html"
            and os.path.getsize(x) < 400 * 1024]
    ledger_url = ""
    if exps:
        dst = os.path.join(ROOT, repo, "assets", f"{repo}-explorer.html")
        if os.path.abspath(exps[0]) != os.path.abspath(dst):
            shutil.copy2(exps[0], dst)
        ledger_url = f"{repo}-explorer.html"
    if ledger_url:
        led = ('<section id="ledger" style="margin:28px 0 8px">'
               '<h2 style="font-size:20px;color:#1f3b57">交互台账</h2>'
               '<p class="lede">下面的筛选器与详情卡就是这篇文章的数据底账（同一份 <code>data/</code>）。'
               '它在需要时才加载，不拖慢正文。</p><details id="ledbox">'
               '<summary style="cursor:pointer;color:#b5651d;font-size:13px">打开交互台账（' + ledger_url + '）</summary>'
               '<iframe data-src="' + ledger_url + '" style="width:100%;height:80vh;border:1px solid #e2dccd;'
               'border-radius:12px;margin-top:10px;background:#fff"></iframe></details></section>')
        t = t.replace("</body>", led + "</body>", 1)

    bar = ('<div id="rbar"><button data-m="bone">骨架</button>'
           '<button data-m="read" class="on">阅读</button><button data-m="full">全展</button>'
           '<span class="sep"></span><button data-m="ledger">台账</button></div>')
    foot = foot_block(repo, "正文：<code>" + repo + "/" + os.path.basename(src) + "</code>；台账：<code>interactive/" +
                      (ledger_url or "—") + "</code>；本页只加外壳。",
                      "<code>_series/tools/make_reader.py</code>（paper 模式）；打脸条件读 <code>LedgerReconciliation/ledger.csv</code>。",
                      ["审问卡四行是**原文摘录**，摘要不等于全文。",
                       "打脸条件来自论文十五的 126 条总账，**不是本页重新判定的**。",
                       "骨架档藏起来的是表格与推导，不是删掉——「全展」可随时看见。"])
    t = shell(t, bar, foot)
    t = t.replace("</body>", "<script>" + squish(JS) + "</script></body>", 1)
    out = out_path(repo)
    io.open(out, "w", encoding="utf-8", newline="\n").write(t)
    return {"out": out, "base": base, "kb": os.path.getsize(out) / 1024, "ev": n_ev, "cards": 1, "missing": []}


def _f_table(t: str):
    """附录 F 表 F.1：章号 → (被检, 作废成什么)。"""
    m = re.search(r'<h[23][^>]*>[^<]{0,10}附录\s?F(.*?)(?:<h2|<div id="rfoot">|$)', t, re.S)
    if not m:
        return {}
    seg = m.group(1)
    out = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
        cs = [plain(x) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        if len(cs) >= 3 and re.match(r"^\d+$", cs[0]):
            out[cs[0]] = (cs[-2], cs[-1])
    return out


def build_grain() -> dict:
    repo = "resolution-grain"
    src = os.path.join(ROOT, repo, "output", "book-ereader.html")
    t = io.open(src, encoding="utf-8").read()
    base = os.path.getsize(src) / 1024
    ftab = _f_table(t)
    t, n_ev = wrap_evidence(t)

    def extra(no, ch):
        if no in ftab:
            a, b = ftab[no]
            return f"表 F.1 登记 —— 被检/观察：{a} ⇒ 若看到：{b}"
        m = re.search(r'<h3[^>]*>[^<]{0,30}(反例与边界|反例与失败|反例：|可测边界)[^<]{0,20}</h3>(.*?)(?=<h3|$)', ch, re.S)
        if m:
            ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', m.group(2), re.S)]
            ps = [x for x in ps if len(x) > 20]
            pick = next((x for x in ps if x.startswith("第一，")), ps[0] if ps else "")
            if pick:
                return "本章反例与边界 —— " + pick[:220]
        m = re.search(r'<h3[^>]*>[^<]{0,40}(越界|不要带走|可测边界|边界)[^<]{0,30}</h3>(.*?)(?=<h3|$)', ch, re.S)
        if m:
            ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', m.group(2), re.S)]
            ps = [x for x in ps if len(x) > 20]
            if ps:
                return "本章边界节 —— " + ps[0][:220]
        return "本章未单列否证线：全书否证线见表 F.1（27 条）与附录 D（25 行登记）"

    t, n_card, miss = _chapter_cards(t, extra=extra)
    for anchor, blk in (('<h3 id="sec3-3"', SB_VSTAR), ('<h3 id="sec27-8"', SB_HALF)):
        if anchor in t:
            t = t.replace(anchor, blk + anchor, 1)
        else:
            print("  ! 沙盘锚点缺失", anchor)
    bar = ('<div id="rbar"><button data-m="bone">骨架</button>'
           '<button data-m="read" class="on">阅读</button><button data-m="full">全展</button>'
           '<span class="sep"></span><button data-m="sb1">驻点式</button>'
           '<button data-m="sb2">半衰期</button>'
           '<span class="sep"></span><a class="jump" href="knowledge-map.html">结构地图 →</a></div>')
    foot = foot_block(repo,
                      "正文：<code>resolution-grain/source/</code>；由 <code>output/book-ereader.html</code> 派生。",
                      "<code>make_reader.py</code>（grain 模式）；沙盘 1 照抄 §3.2 驻点式，沙盘 2 照抄式 (27.4)(27.5)。",
                      ["两个沙盘是**说明性装置（C 级）**：演示式子怎么动，不预测任何具体行业。",
                       "半衰期是模型里的时间常数，不是\"某行业会撑几年\"的预言；C 的量法变了，数就变。",
                       "骨架档藏起来的是证据与推导，不是删掉——「全展」可随时看见。"])
    t = shell(t, bar, foot)
    t = t.replace("</body>", "<script>" + squish(JS) + squish(JS_SB) + "</script></body>", 1)
    out = out_path(repo)
    io.open(out, "w", encoding="utf-8", newline="\n").write(t)
    return {"out": out, "base": base, "kb": os.path.getsize(out) / 1024,
            "ev": n_ev, "cards": n_card, "missing": miss}


def report(tag: str, r: dict):
    miss = ("；无卡章：" + "、".join(r["missing"])) if r.get("missing") else ""
    print(f"  [{tag}] {os.path.basename(r['out'])}  {r['kb']:.0f} KB"
          f"（基准 {r['base']:.0f}，+{(r['kb'] / r['base'] - 1) * 100:.1f}%）"
          f"  折叠 {r['ev']}  卡 {r['cards']}{miss}")


def main(argv):
    targets = argv or ["knowledge-tradeoffs"]
    if targets == ["--all"]:
        targets = BOOKS + PAPERS + ["resolution-grain"]
    for r in targets:
        if r == "resolution-grain":
            report("grain", build_grain())
        elif r in BOOKS:
            report("book", build_book(r))
        else:
            report("paper", build_paper(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""系列校阅器：一次跑完九本书 + 十四篇论文，按 spec/skeleton.md v2 出账。

用法：
    python _series/lint/lint.py            # 全跑，写 REPORT.md / REPORT.json
    python _series/lint/lint.py --item mind-forks
    python _series/lint/lint.py --rules 1,2,4

规则编号与 spec 对应（见 README）。退出码：有 error → 1，仅 warning → 0。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "_series", "lint")
CJK = re.compile(r"[\u4e00-\u9fff]")

# ---------------------------------------------------------------- 基础工具


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_html(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return h


def cn(s):
    return len(CJK.findall(s))


def norm(s):
    return re.sub(r"\s+", "", s)


# ---------------------------------------------------------------- 结构模型

class Item:
    """一件（一本书或一篇论文）"""

    def __init__(self, kind, repo, title):
        self.kind, self.repo, self.title = kind, repo, title
        self.path = os.path.join(ROOT, repo)
        self.files = {}      # name -> text  （章节类文件）
        self.order = []      # 章节顺序
        self.body_cn = 0
        self.appendix_cn = 0
        self.parts = []      # [(title, desc, [chapter dumps])]
        self.meta = {}

    # ---- 书
    @classmethod
    def book(cls, repo, title):
        it = cls("book", repo, title)
        src = os.path.join(it.path, "source")
        if not os.path.isdir(src):
            return it
        for f in sorted(os.listdir(src)):
            if f.endswith(".html"):
                it.files[f] = read(os.path.join(src, f))
        it.order = sorted(f for f in it.files if re.fullmatch(r"ch\d+\.html", f))
        it.body_cn = sum(cn(strip_html(it.files[f])) for f in it.order)
        it.appendix_files = sorted(f for f in it.files if f.startswith("appendix"))
        it.appendix_cn = sum(cn(strip_html(it.files[f])) for f in it.appendix_files)
        it.front_files = sorted(f for f in it.files if f.startswith("front_"))
        it.back_files = sorted(f for f in it.files if f.startswith("back_"))
        pj = os.path.join(src, "parts.json")
        if os.path.exists(pj):
            try:
                data = json.loads(read(pj))
            except Exception:
                data = []
            for p in data:
                chs = [c for c in p.get("chapters", []) if c.get("written", True) and c.get("file")]
                it.parts.append({"title": p.get("part", ""), "desc": p.get("desc", ""), "ch": chs})
        bj = os.path.join(src, "book.json")
        if os.path.exists(bj):
            try:
                it.meta = json.loads(read(bj))
            except Exception:
                it.meta = {}
        return it

    # ---- 论文
    @classmethod
    def paper(cls, repo, title):
        it = cls("paper", repo, title)
        cand = [os.path.join(it.path, "source", "paper.md")]
        cand += [os.path.join(it.path, f) for f in sorted(os.listdir(it.path))
                 if f.endswith(".md")] if os.path.isdir(it.path) else []
        skip = {"README.md", "PLAN.md", "english-note.md", "stats_out.md",
                "上传前检查清单.md", "目录与图表清单.md"}
        it.src = None
        for c in cand:
            if os.path.exists(c) and os.path.basename(c) not in skip:
                it.src = c
                break
        if not it.src:
            return it
        it.files["paper.md"] = read(it.src)
        t = it.files["paper.md"]
        m = re.search(r"^##\s*附\s*录", t, re.M)
        it.body_cn = cn(t[:m.start()] if m else t)
        it.appendix_cn = cn(t[m.start():]) if m else 0
        # 章节
        it.h2 = [(mm.start(), mm.group(1).strip()) for mm in re.finditer(r"^##\s+(.+)$", t, re.M)]
        return it


# ---------------------------------------------------------------- 规则

class Finding:
    __slots__ = ("item", "rule", "severity", "msg", "where")

    def __init__(self, item, rule, severity, msg, where=""):
        self.item, self.rule, self.severity, self.msg, self.where = item, rule, severity, msg, where


def r01_section_numbers(it):
    """节号唯一且连续"""
    if it.kind != "paper" or "paper.md" not in it.files:
        return []
    nums = [h for _, h in it.h2 if re.match(r"^\d+[\s　．.]", h)]
    seq = [int(re.match(r"^(\d+)", h).group(1)) for h in nums]
    out = []
    dup = [n for n, c in Counter(seq).items() if c > 1]
    if dup:
        out.append(Finding(it.repo, 1, "error",
                           f"节号重复：{sorted(dup)}（共 {len(nums)} 个节标题、{len(set(seq))} 个不同号）"))
    if seq and seq != sorted(seq):
        out.append(Finding(it.repo, 1, "warn", f"节序非升序：{seq}"))
    expect = 1
    for n in sorted(set(seq)):
        if n != expect:
            out.append(Finding(it.repo, 1, "warn", f"节号跳号：缺 {expect}（现 {sorted(set(seq))}）", ))
            break
        expect += 1
    return out


APPX = re.compile(r"^附\s*录\s*([A-Z](?:\d)?)(?=[\s　]|$)")
# 同一 appendix 文件内以 <h3>附录 X</h3> 分节的情形（多节合并在一个文件里）。
# 2026-10-31 补：此前只按文件取字母，一本书把所有附录塞进 appendix_a.html 时
# r02/r03/r04 全部放行，《只能选两样》因此出现过两套 D/E/F 而校阅为零。
APPX_H3 = re.compile(r"<h3[^>]*>\s*附\s*录\s*([A-Z])(?=[\s　]|$)")


def _appendix_letters(it):
    if it.kind == "book":
        out = []
        for f in it.appendix_files:
            txt = it.files.get(f, "")
            got = False
            h2 = re.search(r'<h2 class="chapter">([^<]*)</h2>', txt)
            if h2:
                m = re.match(r"^附\s*录\s*([A-Z])", h2.group(1))
                if m:                       # 只有带字母的才算附录
                    out.append((f, m.group(1)))
                    got = True
            for m in APPX_H3.finditer(txt):  # 同文件内的分节字母一并计入
                out.append((f, m.group(1)))
                got = True
            if got:
                continue
            m = re.match(r"appendix_([a-zA-Z0-9]+)", f)
            out.append((f, (m.group(1) if m else "?").upper()))
        return out
    out = []
    for _, h in it.h2:
        m = APPX.match(h)
        if m:
            out.append((h, m.group(1)))
    return out


def r02_appendix_order(it):
    """附录字母连续、无 A0/D2/J2/AA；同文件内不得出现两套同号附录"""
    out = []
    letters = _appendix_letters(it)
    if not letters:
        return out
    tags = [l for _, l in letters]
    for t in tags:
        if re.search(r"\d$", t):
            out.append(Finding(it.repo, 2, "error", f"附录编号打补丁：{t}（禁 A0/D2/J2 形态）"))
    # 重复 / 乱序：按“同一附录文件内的号序”判（跨文件按 build 顺序，号可以分属不同文件）
    per_file = {}
    for f, l in letters:
        per_file.setdefault(f, []).append(l)
    for f, seq in per_file.items():
        s = [t for t in seq if len(t) == 1]
        dup = sorted({t for t in s if s.count(t) > 1})
        if dup:
            out.append(Finding(it.repo, 2, "error",
                               f"附录字母重复：{' '.join(dup)}（{f} 内，读者无法按号引用）"))
        if s != sorted(s):
            out.append(Finding(it.repo, 2, "error", f"附录字母乱序：{f} 内的 {' '.join(seq)}"))
    # 缺号（全书按出现顺序）
    simple = [t for t in tags if len(t) == 1]
    if simple:
        want = [chr(ord(simple[0]) + i) for i in range(len(simple))]
        if simple != want:
            out.append(Finding(it.repo, 2, "warn", f"附录字母不连续：{' '.join(simple)}（期望 {' '.join(want)}）"))
    return out


def r03_refs_in_appendix(it):
    """参考文献 / 术语表 不得编进附录序列"""
    out = []
    if it.kind == "book":
        for f in it.appendix_files:
            txt = it.files.get(f, "")
            h = strip_html(txt)
            first = h.strip().split("\n")[0][:40]
            if re.search(r"参考文献|术语表", first):
                out.append(Finding(it.repo, 3, "error", f"{f} 实为「{first}」，应移出附录序列"))
            # 分节标题里带字母的术语表 / 参考文献同样不合格
            for m in re.finditer(r"<h([23])[^>]*>([^<]*)</h\1>", txt):
                head = m.group(2)
                if re.match(r"^附\s*录\s*[A-Z]", head) and re.search(r"参考文献|术语表", head):
                    out.append(Finding(it.repo, 3, "error", f"附录条目实为「{head[:24]}」，应去字母"))
    else:
        for _, h in it.h2:
            if not APPX.match(h):
                continue
            if re.search(r"参考文献|术语表", h):
                out.append(Finding(it.repo, 3, "error", f"附录条目实为「{h}」"))
    return out


def r04_appendix_count(it):
    letters = _appendix_letters(it)
    n = len(letters)
    if n <= 6:
        return []
    files = len({f for f, _ in letters})
    if files > 6:                     # 真的用了 7 个以上附录文件
        return [Finding(it.repo, 4, "error", f"附录 {files} 个文件 > 6")]
    # 一个文件里塞了 7 节以上：按文件数是 1，按读者可引用的号数是 n。
    # 规范判据写的是数文件，所以这里给 warn（不阻断），但把真实件数写进账。
    return [Finding(it.repo, 4, "warn",
                    f"附录 {n} 节 > 6（同文件分节；skeleton §4 要求 ≤6 件，建议合并）")]


def prose_cn(s):
    """只数正文段落：去掉表格、列表、代码行"""
    s = re.sub(r"<table.*?</table>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<ul.*?</ul>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<pre.*?</pre>", " ", s, flags=re.S | re.I)
    return cn(strip_html(s))


APPX_SEC_MAX = 1200      # 附录单节正文上限（字）


def r05_appendix_ratio(it):
    """附录判据（v3）：件数 ≤6，且**单节正文 ≤1200 字**——附录是证据与工具，不是论述。

    为什么不用"附录占正文 ≤12%"：全系列 1300 余个附录小节里，超过 1200 字的只有 8 个，
    绝大多数是登记项、空白表与清单。按字数占比判，会把表格误判成"第二正文"。
    """
    out = []
    # 件数判据统一由 r04 负责（按文件 error、按分节 warn），此处只管单节长度。
    # 逐节测长
    if it.kind == "book":
        for f in it.appendix_files:
            t = it.files[f]
            for blk in re.split(r"(?m)(?=<h3)", t):
                m = re.match(r"<h3[^>]*>([^<]*)</h3>", blk)
                if not m:
                    continue
                p = prose_cn(blk)
                if p > APPX_SEC_MAX:
                    out.append(Finding(it.repo, 5, "error",
                                       f"附录小节过长：{f}「{m.group(1)[:16]}」{p} 字 > {APPX_SEC_MAX}"))
    else:
        t = it.files.get("paper.md", "")
        m0 = re.search(r"(?m)^## 附\s*录", t)
        if m0:
            for blk in re.split(r"(?m)^## ", t[m0.start():])[1:]:
                head = blk.partition("\n")[0][:20]
                for sub in re.split(r"(?m)^### ", blk)[1:]:
                    p = cn(sub)
                    if p > APPX_SEC_MAX:
                        out.append(Finding(it.repo, 5, "error",
                                           f"附录小节过长：{head}「{sub.partition(chr(10))[0][:16]}」{p} 字"))
    return out


SKEL = {
    "主提问框": (r"box-takeaway", "box-takeaway"),
    "场景开篇": (r'class="lead"', "lead"),
    "导论": (r"导论|主提问|本章追问|class=\"lead\"", "导论"),
    "本章小结": (r"本章小结|^小结|小结$", "小结"),
    "一句话带走": (r"一句话带走", "带走"),
    "反例": (r"反例|失败|不成立|失效", "反例"),
    "表": (r"<table", "表"),
    "图": (r"<img", "图"),
}


POPULAR = {"knowledge-tradeoffs", "hotspot-bills"}


def r06_chapter_skeleton(it):
    """书：章骨架。学术本八段，通俗本四段（spec v2 §2b）"""
    if it.kind != "book" or not it.order:
        return []
    popular = it.repo in POPULAR
    need = ("主提问框", "场景开篇", "一句话带走") if popular else tuple(SKEL) + ("表或图",)
    hard = ("主提问框", "场景开篇", "一句话带走", "反例") if popular else ("本章小结", "一句话带走", "反例", "场景开篇")
    out = []
    missing = defaultdict(list)
    for f in it.order:
        t = it.files[f]
        if not re.search(r"<table|<img|<div class=\"box", t):
            missing["表或图"].append(f.replace("ch", "").replace(".html", ""))
        for name, (pat, _) in SKEL.items():
            if name in ("表", "图"):
                continue
            if not re.search(pat, t, re.M):
                missing[name].append(f.replace("ch", "").replace(".html", ""))
    for name, chs in missing.items():
        if not chs or name not in need:
            continue
        sev = "error" if name in hard else "warn"
        out.append(Finding(it.repo, 6, sev,
                           f"缺「{name}」：{len(chs)}/{len(it.order)} 章（ch {','.join(chs[:10])}{'…' if len(chs) > 10 else ''}）"))
    return out


def r07_part_intro(it):
    """部分导语必须被渲染"""
    if it.kind != "book" or not it.parts:
        return []
    out = []
    no_desc = [p["title"][:16] for p in it.parts if not p["desc"]]
    if no_desc:
        out.append(Finding(it.repo, 7, "warn", f"parts.json 缺 desc：{no_desc}"))
    bf = os.path.join(it.path, "build_book.py")
    if os.path.exists(bf) and "part-intro" not in read(bf):
        out.append(Finding(it.repo, 7, "error", "build_book.py 未渲染 part-intro（部分导语不出现）"))
    return out


def r08_part_size(it):
    if it.kind == "book" or not it.parts:
        pass
    if not getattr(it, "parts", None):
        return []
    out = []
    for p in it.parts:
        n = len(p["ch"])
        if n < 3:
            out.append(Finding(it.repo, 8, "error", f"部分「{p['title'][:20]}」只有 {n} 章（规范 ≥3）"))
        elif n > 7:
            out.append(Finding(it.repo, 8, "warn", f"部分「{p['title'][:20]}」有 {n} 章（规范 ≤7）"))
    if len(it.parts) < 2:
        out.append(Finding(it.repo, 8, "error", f"全书仅 {len(it.parts)} 部分（规范 5–7）"))
    return out


def r09_unit_words(it):
    """部/章/篇/卷用词不串"""
    if it.kind != "book":
        return []
    out = []
    for f in it.order:
        m = re.search(r'<h2 class="chapter">([^<]*)</h2>', it.files[f])
        if m and re.search(r"第\s*[0-9一二三四五六七八九十]+\s*[部篇卷]", m.group(1)):
            out.append(Finding(it.repo, 9, "error", f"{f} 章标题用「部/篇/卷」：{m.group(1)[:24]}"))
    return out


def r10_dup_paragraph(it):
    """跨文件重复段落（≥80 字）"""
    seen = {}
    for name, t in it.files.items():
        for p in re.split(r"\n\s*\n|<p[^>]*>", strip_html(t)):
            p = p.strip()
            if cn(p) < 80:
                continue
            seen.setdefault(norm(p), set()).add(name)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    if not dups:
        return []
    files = set()
    for v in dups.values():
        files |= v
    sample = list(dups)[0][:40]
    return [Finding(it.repo, 10, "error",
                    f"重复段落 {len(dups)} 处，涉及 {len(files)} 个文件（例：{sample}…）")]


def r11_dup_h3(it):
    """跨章同名小节标题"""
    if it.kind != "book":
        return []
    c = Counter()
    where = defaultdict(list)
    for f in it.order:
        for m in re.finditer(r"<h3[^>]*>([^<]*)</h3>", it.files[f]):
            t = re.sub(r"^[\d.]+[　 ]*", "", m.group(1).strip())
            if len(t) < 4:
                continue
            c[t] += 1
            where[t].append(f)
    STD = ("一句话带走", "本章小结", "本章参考文献", "本章的边界", "参考文献")
    out = []
    for t, n in c.items():
        if t in STD:
            continue
        chs = sorted(where[t])
        idxs = [int(re.findall(r"\d+", c)[0]) for c in chs]
        contiguous = all(b - a <= 1 for a, b in zip(idxs, idxs[1:]))
        if n >= 5 and not contiguous:
            out.append(Finding(it.repo, 11, "warn", f"同名小节「{t[:20]}」出现 {n} 次（{','.join(sorted(set(where[t]))[:4])}）"))
    return sorted(out, key=lambda x: x.msg)[:6]


SERIES_CNT = re.compile(r"([一二三四五六七八九十\d]+)\s*(本书|本专著|篇论文|篇工作论文)")
CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
            "八": 8, "九": 9, "十": 10}


def cn2int(s):
    """「九」「十八」「20」→ int；无法解析返回 None。"""
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十") and len(s) == 2:
        return 10 + CN_DIGIT.get(s[1], 0)
    if len(s) == 2 and s[1] == "十" and s[0] in CN_DIGIT:
        return CN_DIGIT[s[0]] * 10
    if len(s) == 1:
        return CN_DIGIT.get(s)
    return None


def r12_series_count(it, n_books, n_papers):
    """系列计数与 inventory 一致；历史处须带「其时」"""
    out = []
    files = it.files
    hits = Counter()
    for name, t in files.items():
        txt = strip_html(t) if it.kind == "book" else t
        for m in SERIES_CNT.finditer(txt):
            ctx = txt[max(0, m.start() - 12):m.end() + 4]
            if "其时" in ctx or "写作时" in ctx or "此前" in ctx:
                continue
            if txt[:m.start()].rstrip().endswith("第"):
                continue
            if not re.search(r"(系列|现有|本书系|共|总计)", ctx):
                continue
            hits[(m.group(1), m.group(2))] += 1
    SMALL = {"一", "二", "三", "四", "五", "六", "七", "1", "2", "3", "4", "5", "6", "7"}
    for (n, unit), c in hits.items():
        if n in SMALL:          # 「一本书」「三本书」多指某几本具体著作，不是系列总数
            continue
        # 与 inventory 一致的总数不算错（2026-10-31：此前一律 warn，导致“系列共九本书”这类
        # 正确陈述也被记一笔；真正要挡的是过期计数与不带「其时」的历史叙述）
        k = cn2int(n)
        if (unit in ("本书", "本专著") and k == n_books) or (unit in ("篇论文", "篇工作论文") and k == n_papers):
            continue
        out.append(Finding(it.repo, 12, "warn", f"系列计数「{n}{unit}」×{c}（今为 {n_books} 书 / {n_papers} 篇；历史处须写「其时的…」）"))
    return out


def r13_narrative(it):
    """叙事性：每章 ≥1 年份/世纪线索（通俗本不适用）"""
    if it.kind != "book" or it.repo in POPULAR:
        return []
    bad = [f for f in it.order if not re.search(r"(1[5-9]\d\d|20\d\d|世纪|公元)", it.files[f])]
    if len(bad) > len(it.order) * 0.8:
        return [Finding(it.repo, 13, "warn", f"{len(bad)}/{len(it.order)} 章无具体年份线索")]
    return []


BAN = ["必然失败", "必然崩溃", "注定失败", "注定崩溃", "不可避免", "无法消除", "死路", "无可挽回"]


def r16_banwords(it):
    out = []
    for name, t in it.files.items():
        txt = strip_html(t) if it.kind == "book" else t
        for w in BAN:
            n = txt.count(w)
            if n:
                out.append(Finding(it.repo, 16, "warn", f"禁词「{w}」×{n}（{name}）"))
    return out


def r17_reverse_power(it):
    """「这条限制使……成为可能」类反向力量句"""
    pat = r"使[^，。]{0,30}成为可能|让[^，。]{0,20}成为可能|恰恰是[^，。]{0,20}的可能"
    n = sum(len(re.findall(pat, strip_html(t) if it.kind == "book" else t)) for t in it.files.values())
    need = 1
    if n < need:
        return [Finding(it.repo, 17, "warn", f"反向力量句仅 {n} 处（建议 ≥{need}）")]
    return []


def r21_ledger(it):
    """登记簿 append-only"""
    for cand in ("LedgerReconciliation/ledger.csv", "docs/preregistration/checkups.csv"):
        p = os.path.join(it.path, cand)
        if not os.path.exists(p):
            continue
        h = hashlib.sha256(read(p).encode()).hexdigest()[:16]
        d = os.path.join(OUT, "ledgers")
        os.makedirs(d, exist_ok=True)
        stamp = os.path.join(d, f"{it.repo}.sha256")
        if not os.path.exists(stamp):
            with open(stamp, "w", encoding="utf-8") as f:
                f.write(h + "\n")
            return [Finding(it.repo, 21, "info", f"登记簿基线已记录 {cand} {h}")]
        old = read(stamp).strip().split("\n")
        if old[0] != h:
            rows_now = read(p).count("\n")
            return [Finding(it.repo, 21, "warn", f"登记簿内容变化 {cand}（{old[0]} → {h}，当前 {rows_now} 行）；仅允许追加")]
    return []


def r22_appendix_patch(it):
    """附录里不得写「本文附录曾…」式打补丁叙述"""
    pat = r"本文附录曾|附录中已经|本版新增附录|前版附录"
    for name, t in it.files.items():
        txt = strip_html(t) if it.kind == "book" else t
        if re.search(pat, txt):
            return [Finding(it.repo, 22, "warn", f"{name} 出现附录打补丁式叙述（应改写进正文）")]
    return []


def r24_word_limits(it):
    out = []
    if it.kind == "paper" and "paper.md" in it.files:
        t = it.files["paper.md"]
        m = re.search(r"^##\s*摘要\s*$(.*?)^##", t, re.M | re.S)
        if m and cn(m.group(1)) > 900:
            out.append(Finding(it.repo, 24, "warn", f"中文摘要 {cn(m.group(1))} 字（规范 ≤600，硬上限 900）"))
    if it.kind == "book":
        for f in ("front_preface.html",):
            if f in it.files and cn(strip_html(it.files[f])) > 5000:
                out.append(Finding(it.repo, 24, "warn", f"{f} {cn(strip_html(it.files[f]))} 字（规范 ≤4000）"))
    return out


# ---------------------------------------------------------------- 全局规则


def global_rules(items):
    out = []
    # 23 构建脚本壳
    books = [it for it in items if it.kind == "book"]
    sig = defaultdict(list)
    for it in books:
        for name in ("build_book.py", "build_epub.py", "build_markdown.py"):
            p = os.path.join(it.path, name)
            if os.path.exists(p):
                src = read(p).split("FRONT = [")[0]
                sig[name].append(hashlib.md5(src.encode()).hexdigest()[:8])
    for name, hs in sig.items():
        if len(set(hs)) > 1:
            out.append(Finding("_series", 23, "warn",
                               f"{name}：{len(hs)} 份副本 / {len(set(hs))} 个版本（应收敛为 1）"))
    # 20 论文产物同源
    for it in items:
        if it.kind != "paper":
            continue
        md = it.src
        if not md:
            continue
        mt = os.path.getmtime(md)
        for f in os.listdir(it.path):
            if f.endswith((".pdf", ".html")):
                p = os.path.join(it.path, f)
                if os.path.getmtime(p) < mt - 2:
                    out.append(Finding(it.repo, 20, "warn", f"{f} 旧于正文（需重新构建）"))
    # 24 位：台账 vs 事实
    return out


# ---------------------------------------------------------------- 主流程


def load_items():
    inv = os.path.join(ROOT, "inventory.tsv")
    items = []
    if os.path.exists(inv):
        for line in read(inv).splitlines():
            cols = line.split("\t")
            if len(cols) < 3 or cols[0] not in ("BOOK", "PAPER"):
                continue
            kind, repo, title = cols[0], cols[1], cols[2]
            if not os.path.isdir(os.path.join(ROOT, repo)):
                continue
            items.append(Item.book(repo, title) if kind == "BOOK" else Item.paper(repo, title))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item")
    ap.add_argument("--rules")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    items = load_items()
    if a.item:
        items = [it for it in items if it.repo == a.item]
    only = {int(x) for x in a.rules.split(",")} if a.rules else None
    n_books = sum(1 for it in items if it.kind == "book")
    n_papers = sum(1 for it in items if it.kind == "paper")

    findings = []
    for it in items:
        for fn in (r01_section_numbers, r02_appendix_order, r03_refs_in_appendix,
                   r04_appendix_count, r05_appendix_ratio, r06_chapter_skeleton,
                   r07_part_intro, r08_part_size, r09_unit_words, r10_dup_paragraph,
                   r11_dup_h3):
            findings += fn(it)
        findings += r12_series_count(it, n_books, n_papers)
        findings += r13_narrative(it) + r16_banwords(it) + r17_reverse_power(it)
        findings += r21_ledger(it) + r22_appendix_patch(it) + r24_word_limits(it)
        if not it.files:
            findings.append(Finding(it.repo, 0, "error", "找不到正文来源（source/ 缺失）"))
    findings += global_rules(items)
    if only:
        findings = [f for f in findings if f.rule in only]

    # ---- 输出
    errs = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]
    by_item = defaultdict(list)
    for f in findings:
        by_item[f.item].append(f)

    lines = ["# 校阅账（lint v2）", "",
             f"规则：`_series/spec/skeleton.md` v2　｜　对象：{len(items)} 件"
             f"（{n_books} 书 / {n_papers} 篇）",
             f"**error {len(errs)}　warn {len(warns)}**", ""]
    lines.append("| 件 | 等级 | 字数(正文/附录) | 附录 | 主要问题 |")
    lines.append("|---|---|---:|---:|---|")
    for it in sorted(items, key=lambda x: (x.kind, -len([f for f in by_item[x.repo] if f.severity == 'error']))):
        fs = [f for f in by_item[it.repo] if f.severity != "info"]
        e = sum(1 for f in fs if f.severity == "error")
        w = sum(1 for f in fs if f.severity == "warn")
        n_ap = len(_appendix_letters(it))
        lines.append(f"| {it.repo} | {'error ' + str(e) if e else 'ok'}{' / warn ' + str(w) if w else ''} "
                     f"| {it.body_cn:,} / {it.appendix_cn:,} | {n_ap} | "
                     f"{'; '.join(f.msg.split('（')[0][:40] for f in fs[:3])} |")
    lines.append("")
    for item in sorted(by_item):
        fs = [f for f in by_item[item] if f.severity != "info"]
        if not fs:
            continue
        lines.append(f"## {item}")
        for f in sorted(fs, key=lambda x: (x.rule, x.severity)):
            mark = "**E**" if f.severity == "error" else "w"
            lines.append(f"- `{f.rule:02d}` {mark} {f.msg}")
        lines.append("")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "REPORT.json"), "w", encoding="utf-8") as f:
        json.dump([{"item": x.item, "rule": x.rule, "sev": x.severity, "msg": x.msg} for x in findings],
                  f, ensure_ascii=False, indent=1)
    if not a.quiet:
        print(f"error {len(errs)} / warn {len(warns)} → _series/lint/REPORT.md")
        for f in errs[:40]:
            print(f"  E{f.rule:02d} {f.item}: {f.msg}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

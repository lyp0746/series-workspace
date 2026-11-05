#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""连贯性审计：编号、悬空引用、拼接痕迹、图表号、公式框、防御性写作。

用法：
    python _series/tools/coherence_audit.py                 # 全部
    python _series/tools/coherence_audit.py distinction-evolution
输出：_series/review/COHERENCE.md（人读）+ _series/review/coherence.json（机读）
"""
from __future__ import annotations
import json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "_series", "review", "COHERENCE.md")
CJK = re.compile(r"[\u4e00-\u9fff]")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_html(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", "\n", h)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&mdash;", "—")):
        h = h.replace(a, b)
    return h


def cn(s):
    return len(CJK.findall(s))


# ---------------------------------------------------------------- 书目

def items():
    out = []
    for line in read(os.path.join(ROOT, "inventory.tsv")).splitlines():
        f = line.split("\t")
        if len(f) > 3:
            out.append({"kind": f[0].lower(), "repo": f[1], "title": f[3]})
    return out


# ---------------------------------------------------------------- 书

def audit_book(it):
    d = os.path.join(ROOT, it["repo"], "source")
    r = {"repo": it["repo"], "kind": "book", "title": it["title"], "f": defaultdict(list)}
    if not os.path.isdir(d):
        r["f"]["missing"].append("source/ 不存在")
        return r
    files = sorted(f for f in os.listdir(d) if f.endswith(".html"))
    chapters = sorted(f for f in files if re.fullmatch(r"ch\d+\.html", f))
    r["chapters"] = len(chapters)
    alltext = {}
    for f in files:
        alltext[f] = read(os.path.join(d, f))
    r["front"] = sorted(f for f in files if f.startswith("front_"))
    r["back"] = sorted(f for f in files if f.startswith("back_"))
    r["appendix"] = sorted(f for f in files if f.startswith("appendix"))

    # 章号连续
    nums = [int(re.search(r"\d+", f).group()) for f in chapters]
    if nums and nums != list(range(1, len(nums) + 1)):
        r["f"]["chapter_seq"].append(f"章文件号不连续：{nums}")

    # 节号：h3 中 N.M 形式
    secs = []           # (num tuple, title, file, order_idx)
    dup_titles = defaultdict(list)
    for f in chapters:
        txt = alltext[f]
        for m in re.finditer(r"<h3[^>]*>(.*?)</h3>", txt, re.S):
            h = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            dup_titles[re.sub(r"[\s　]+", "", h)].append(f)
            mm = re.match(r"^(\d+)[.．](\d+)([a-z]?)(?:[.．](\d+))?[　\s]", h)
            if mm:
                secs.append(((int(mm.group(1)), int(mm.group(2)), mm.group(3)),
                             h, f, m.start()))
    sec_nums = [s[0] for s in secs]
    # b 补丁号
    bpatch = [s for s in secs if s[0][2]]
    if bpatch:
        r["f"]["b_suffix"].append("字母补丁号：" + "、".join(s[1][:22] for s in bpatch))
    # 重复
    c = Counter(sec_nums)
    dups = [(k, v) for k, v in c.items() if v > 1]
    if dups:
        r["f"]["sec_dup"].append("节号重复：" + "、".join(f"{k[0]}.{k[1]}" for k, _ in dups))
    # 每章内部顺序
    by_ch = defaultdict(list)
    for s in secs:
        by_ch[s[0][0]].append(s[0][1])
    for ch, seq in by_ch.items():
        if seq != sorted(seq):
            r["f"]["sec_order"].append(f"第{ch}章节序非升序：{seq}")
        exp = 1
        for n in sorted(set(seq)):
            if n != exp:
                r["f"]["sec_gap"].append(f"第{ch}章缺 {ch}.{exp}（现有 {ch}.{sorted(set(seq))[0]}–{ch}.{max(seq)}）")
                break
            exp += 1
    # 标题重复
    dt = [(k, v) for k, v in dup_titles.items() if len(v) > 1 and cn(k) > 3]
    if dt:
        r["f"]["title_dup"].append("重复节标题：" + "；".join(f"{k[:20]}({','.join(v)})" for k, v in dt[:8]))

    # 小节号 N.M.K（h4）与引用
    h4 = set()
    for f in chapters + r["appendix"]:
        for m in re.finditer(r"<h4[^>]*>(.*?)</h4>", alltext.get(f, ""), re.S):
            h = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            mm = re.match(r"^(\d+)[.．](\d+)[.．](\d+)", h)
            if mm:
                h4.add((int(mm.group(1)), int(mm.group(2)), int(mm.group(3))))

    body = "\n".join(strip_html(alltext[f]) for f in chapters)
    front = "\n".join(strip_html(alltext[f]) for f in r["front"] + r["back"])
    appx = "\n".join(strip_html(alltext[f]) for f in r["appendix"])

    # 章引用越界
    chap_refs = [int(m.group(1)) for m in re.finditer(r"第\s*(\d+)\s*章", body + front + appx)]
    over = sorted(set(n for n in chap_refs if n > r["chapters"]))
    if over:
        r["f"]["ref_chapter"].append(f"引用不存在的章：第{over}章（共 {r['chapters']} 章）")

    # 节引用悬空
    existing = set(sec_nums)
    refs = set()
    ctx = r"(?:第|见|如|参|按|据|在|与|和|见第|参见)\s*"
    for m in re.finditer(ctx + r"(\d{1,2})[.．](\d{1,2})(?:[.．](\d{1,2}))?(?![\d.])", body + front + appx):
        a, b, cc = int(m.group(1)), int(m.group(2)), m.group(3)
        if a > r["chapters"] or a == 0:
            continue
        if cc is not None:
            refs.add((a, b, int(cc)))
        else:
            refs.add((a, b, 0))
    dangling = []
    for a, b, cc in sorted(refs):
        if (a, b, "") not in existing and (a, b, None) not in existing:
            dangling.append(f"{a}.{b}")
        elif cc and (a, b, cc) not in h4:
            dangling.append(f"{a}.{b}.{cc}")
    if dangling:
        r["f"]["dangling"].append("引用了不存在的节/小节：" + "、".join(sorted(set(dangling))[:20]))

    # 拼接与版本痕迹
    patch_words = ["补全", "补遗", "再补", "续补", "本版", "上一版", "旧版", "旧稿", "原文误", "勘误",
                   "新增节", "新增了", "本版新增", "本次修订", "前一版", "此前版本", "原书", "改版"]
    hits = [(w, body.count(w) + front.count(w) + appx.count(w)) for w in patch_words]
    hits = [(w, n) for w, n in hits if n]
    if hits:
        r["f"]["patch"].append("版本/拼接痕迹：" + "、".join(f"{w}×{n}" for w, n in hits))

    # 防御性写作
    hedge = ["需要指出的是", "值得一提的是", "必须强调", "值得注意的是", "不难发现", "某种意义上",
             "或许", "也许", "某种程度上", "在某种意义上", "本书并不", "本文并不", "本章并不",
             "限于篇幅", "众所周知", "显而易见", "诚实地", "诚实的", "坦白说"]
    hh = [(w, (body + front + appx).count(w)) for w in hedge]
    hh = [(w, n) for w, n in hh if n]
    if hh:
        r["f"]["hedge"].append("防御性/空话：" + "、".join(f"{w}×{n}" for w, n in hh))

    # 公式：<p class="eq"> 与编号
    raw = "\n".join(alltext[f] for f in chapters)
    eq = re.findall(r'<(?:p|div)[^>]*class="[^"]*\beq\b[^"]*"[^>]*>(.*?)</(?:p|div)>', raw, re.S)
    eqnum = re.findall(r"式\s*[（(]\s*(\d+)[.．](\d+)\s*[)）]", body + front + appx)
    if eq and not eqnum:
        r["f"]["eq"].append(f"有 {len(eq)} 个公式框，但正文无“式(N.M)”编号引用")
    if eqnum and not eq:
        r["f"]["eq"].append(f"正文引用 {len(eqnum)} 处“式(N.M)”，但没有 .eq 公式框")

    # 图号
    figs = []
    for f in chapters:
        t = alltext[f]
        for m in re.finditer(r'<img[^>]*class="[^"]*fig[^"]*"[^>]*>', t):
            figs.append((f, m.group(0)))
        for m in re.finditer(r'<div class="cap"><b>图\s*(\d+)[.．](\d+)', t):
            figs.append((f, "cap:" + m.group(1) + "." + m.group(2)))
    fignums = [x[1][4:] for x in figs if x[1].startswith("cap:")]
    fc = Counter(fignums)
    fd = [k for k, v in fc.items() if v > 1]
    img_no_cap = len([x for x in figs if not x[1].startswith("cap:")]) - len(fignums)
    if fd:
        r["f"]["fig_dup"].append("图号重复：" + "、".join(fd))
    if img_no_cap > 0:
        r["f"]["fig_cap"].append(f"{img_no_cap} 个图无编号图注")
    # 图引用
    figref = set(re.findall(r"图\s*(\d+)[.．](\d+)", body))
    figdef = set(tuple(x.split(".")) for x in fignums)
    undef = sorted(figref - figdef)
    if undef:
        r["f"]["fig_ref"].append("引用未定义的图：" + "、".join(f"{a}.{b}" for a, b in undef[:12]))

    # 表号
    tabs = set(re.findall(r"<caption[^>]*>.*?<b>表\s*(\d+)[.．](\d+)", raw, re.S))
    tabs |= set(re.findall(r'<div class="cap"><b>表\s*(\d+)[.．](\d+)', raw))
    tabref = set(re.findall(r"表\s*(\d+)[.．](\d+)", body))
    undef_t = sorted(tabref - tabs)
    if undef_t:
        r["f"]["tab_ref"].append("引用未定义的表：" + "、".join(f"{a}.{b}" for a, b in undef_t[:12]))
    tdup = [k for k, v in Counter(tabs).items() if v > 1]
    if tdup:
        r["f"]["tab_dup"].append("表号重复：" + "、".join(f"{a}.{b}" for a, b in tdup))

    # 本章小结位置
    for f in chapters:
        hs = [(m.start(), re.sub(r"<[^>]+>", "", m.group(1))) for m in
              re.finditer(r"<h3[^>]*>(.*?)</h3>", alltext[f], re.S)]
        idx = [i for i, (_, h) in enumerate(hs) if "本章小结" in h]
        if idx and idx[0] < len(hs) - 2:
            r["f"]["summary_pos"].append(f"{f} 本章小结在第 {idx[0]+1}/{len(hs)} 节")

    # 开头禁语
    for f in chapters:
        m = re.search(r'<p class="lead"[^>]*>(.*?)</p>', alltext[f], re.S)
        if m and re.match(r"^\s*(本章将|本节|这一章将|本章讨论)", strip_html(m.group(1)).strip()):
            r["f"]["lead"].append(f"{f} 场景开篇以“本章将/本节”开头")

    # 元数据与前置里的章号
    bj = os.path.join(d, "book.json")
    if os.path.exists(bj):
        meta = read(bj)
        bad = sorted(set(n for n in (int(x.group(1)) for x in re.finditer(r"第\s*(\d+)\s*章", meta)) if n > r["chapters"]))
        if bad:
            r["f"]["meta_ref"].append(f"book.json 引用不存在的章：第{bad}章")
        if re.search(r"\d{1,2}[.．]\d{1,2}[.．]\d{1,2}", meta):
            r["f"]["meta_ref"].append("book.json 含三级小节号（易随重排失效）")

    # 字数
    r["cn_body"] = sum(cn(strip_html(alltext[f])) for f in chapters)
    r["cn_appx"] = sum(cn(strip_html(alltext[f])) for f in r["appendix"])
    return r


# ---------------------------------------------------------------- 论文

def audit_paper(it):
    d = os.path.join(ROOT, it["repo"])
    r = {"repo": it["repo"], "kind": "paper", "title": it["title"], "f": defaultdict(list)}
    src = os.path.join(d, "source", "paper.md")
    if not os.path.exists(src):
        cand = [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md") and f not in
                ("README.md", "PLAN.md", "english-note.md", "stats_out.md",
                 "上传前检查清单.md", "目录与图表清单.md")]
        cand = [c for c in cand if os.path.getsize(c) > 40000]
        src = max(cand, key=os.path.getsize) if cand else None
    if not src or not os.path.exists(src):
        r["f"]["missing"].append("找不到正文 markdown")
        return r
    t = read(src)
    h2 = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^##\s+(.+)$", t, re.M)]
    h3 = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^###\s+(.+)$", t, re.M)]
    r["h2"] = [h for _, h in h2]
    # 节号
    sn = [(int(m.group(1)), h) for _, h in h2 for m in [re.match(r"^(\d+)[.．\s]", h)] if m]
    seq = [n for n, _ in sn]
    if seq != sorted(seq):
        r["f"]["sec_order"].append(f"节序非升序：{seq}")
    if len(set(seq)) != len(seq):
        r["f"]["sec_dup"].append("节号重复")
    # 悬空小节引用
    n = len(seq)
    refs = [int(m.group(1)) for m in re.finditer(r"第\s*(\d+)\s*节", t)]
    over = sorted(set(x for x in refs if x > max(seq or [0])))
    if over:
        r["f"]["ref_section"].append(f"引用不存在的节：第{over}节（共 {n} 节）")
    # 拼接痕迹
    for w in ["补全", "补遗", "本版", "上一版", "旧版", "旧稿", "勘误", "原文误", "本次修订", "前一版"]:
        c = t.count(w)
        if c:
            r["f"]["patch"].append(f"版本/拼接痕迹：{w}×{c}")
    hedge = ["需要指出的是", "值得一提的是", "必须强调", "值得注意的是", "不难发现", "某种意义上", "或许", "也许", "限于篇幅", "众所周知"]
    hh = [(w, t.count(w)) for w in hedge if t.count(w)]
    if hh:
        r["f"]["hedge"].append("防御性/空话：" + "、".join(f"{w}×{n}" for w, n in hh))
    # 图表
    figs = re.findall(r"!\[([^\]]*)\]", t)
    fignums = [re.match(r"图\s*(\d+)", x.strip()) for x in figs]
    if any(not m for m in fignums) and figs:
        r["f"]["fig_cap"].append("有图注未以“图 N”开头")
    fc = Counter(m.group(1) for m in fignums if m)
    if any(v > 1 for v in fc.values()):
        r["f"]["fig_dup"].append("图号重复：" + "、".join(k for k, v in fc.items() if v > 1))
    # 公式块
    eqblocks = re.findall(r"^\s*\$\$", t, re.M)
    r["eq_blocks"] = len(eqblocks) // 2
    if r["eq_blocks"] and not re.search(r"式\s*[（(]\s*\d+", t):
        r["f"]["eq"].append(f"{r['eq_blocks']} 个公式块，无“式(N)”编号引用")
    if re.search(r"式\s*[（(]\s*\d+", t) and not r["eq_blocks"]:
        r["f"]["eq"].append("引用“式(N)”但无公式块")
    r["cn_body"] = cn(t)
    return r


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    for it in items():
        if only and it["repo"] != only:
            continue
        r = audit_book(it) if it["kind"] == "book" else audit_paper(it)
        rows.append(r)
    # 输出
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = ["# 连贯性审计（coherence audit）", "",
             "对象：24 件。检查：编号连续、悬空引用、拼接痕迹、图表号、公式框、防御性写作、小结位置。", ""]
    total = 0
    for r in rows:
        f = {k: v for k, v in r["f"].items() if v}
        total += sum(len(v) for v in f.values())
        lines.append(f"## {r['repo']}　{r['title']}")
        lines.append("")
        lines.append(f"- 字数：正文 {r.get('cn_body', 0):,} / 附录 {r.get('cn_appx', 0):,}")
        if r["kind"] == "book":
            lines.append(f"- 章数：{r['chapters']}")
        if not f:
            lines.append("- 未发现问题")
        for k, v in f.items():
            for x in v:
                lines.append(f"- **{k}**：{x}")
        lines.append("")
    lines.insert(3, f"**发现 {total} 条**\n")
    with open(OUT, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
    with open(OUT.replace(".md", ".json"), "w", encoding="utf-8") as fp:
        json.dump([{**r, "f": dict(r["f"])} for r in rows], fp, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}; findings={total}")


if __name__ == "__main__":
    main()

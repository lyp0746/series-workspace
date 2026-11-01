#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""系列审阅取数器（只读）：结构、骨架、编号、图表、附录、跨著互引。

用法：
    python _series/review/audit_series.py
产出：
    _series/review/data.json     机器可读
    _series/review/OUTLINE.md    人读总表（结构 / 缺项 / 编号冲突 / 图表账）
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "_series", "review")
CJK = re.compile(r"[\u4e00-\u9fff]")

BOOKS = [
    "knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
    "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
    "emergence-critical", "mind-forks", "hotspot-bills",
]
PAPERS = [
    "ComputingDemystified", "WorldPeriodization", "SleepingResidue", "HunanRelaySystem",
    "BureauRotationCession", "HarnessEcology", "OptimizationBoundary", "CapacityProxies",
    "DomainCrossSection", "IsomorphismStrength", "MemoryAnchor", "MemoryStressTest",
    "LedgerReconciliation", "MonarchCompetition",
]

CORES = {
    "时间错配": ["时间错配", "来不及", "错位的时间", "时滞"],
    "容量": ["容量", "遗忘", "带宽", "槽位"],
    "区分": ["区分", "不可通约", "说不清", "维数"],
    "三元": ["完备", "可组合", "可传递", "弃权"],
    "置信度": ["置信度", "诠释", "证据等级"],
    "临界": ["临界", "涌现", "相变"],
}
BANNED = ["必然", "注定", "不可避免", "无法消除", "死路"]
HEDGE = ["本书不宣称", "必须强调", "需要指出的是", "仅仅是示意", "在某种意义上"]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_html(h):
    h = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", "", h)
    return (h.replace("&nbsp;", " ").replace("&amp;", "&")
             .replace("&lt;", "<").replace("&gt;", ">"))


def cn(s):
    return len(CJK.findall(s))


def heads(text):
    out = []
    for m in re.finditer(r"<h([1-4])[^>]*>(.*?)</h\1>", text, flags=re.S):
        out.append((int(m.group(1)), strip_html(m.group(2)).strip()))
    return out


def sec_num(title):
    m = re.match(r"^(\d+)\.(\d+)([a-z]?)", title)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), m.group(3) or "")


def book(repo):
    src = os.path.join(ROOT, repo, "source")
    files = {f: read(os.path.join(src, f)) for f in sorted(os.listdir(src)) if f.endswith(".html")}
    chs = sorted([f for f in files if re.fullmatch(r"ch\d+\.html", f)])
    pj = os.path.join(src, "parts.json")
    parts = json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else []

    seg = []
    chap = []
    tables = figs = figcap = 0
    for f in chs:
        t = files[f]
        s = strip_html(t)
        hs = heads(t)
        nums = [sec_num(x[1]) for x in hs if x[0] == 3]
        nums = [n for n in nums if n]
        # 编号是否单调、是否有重复
        order_bad = []
        for a, b in zip(nums, nums[1:]):
            if (b[0], b[1]) < (a[0], a[1]):
                order_bad.append(f"{a[0]}.{a[1]}{a[2]}→{b[0]}.{b[1]}{b[2]}")
        dup = [k for k, v in Counter(nums).items() if v > 1]
        chap_inside = [x[1] for x in hs if x[0] == 3 and re.search(r"第\s*\d+\s*章", x[1])]
        has = {
            "主提问框": ("box-takeaway" in t) or ("主提问" in s[:500]),
            "场景开篇": 'class="lead"' in t,
            "导论": any(("导论" in x[1]) or ("主提问" in x[1]) for x in hs),
            "反例": "反例" in s,
            "本章小结": "本章小结" in s,
            "一句话带走": "一句话带走" in s,
        }
        chap.append({"file": f, "n_h3": len([x for x in hs if x[0] == 3]),
                     "order_bad": order_bad, "dup": [f"{d[0]}.{d[1]}" for d in dup],
                     "chapter_inside": chap_inside,
                     "n_takeaway": s.count("一句话带走"), "n_exercise": s.count("练习"),
                     "n_summary": s.count("本章小结"), "has": has,
                     "cn": cn(s)})
        miss = [k for k, v in has.items() if not v]
        if miss:
            seg.append((f, miss))
        tables += len(re.findall(r'<table[^>]*class="nat"', t))
        figs += len(re.findall(r'<img[^>]*class="fig"', t)) + len(re.findall(r'<svg[^>]*class="fig', t))
        figcap += len(re.findall(r'<div class="cap"><b>图', t))

    ap = sorted(f for f in files if f.startswith("appendix"))
    letters = []
    longest = (0, "")
    for f in ap:
        t = files[f]
        for m in re.finditer(r"<h2[^>]*>\s*附录\s*([A-F])", t):
            letters.append((f, m.group(1)))
        inner = re.findall(r"<h[34][^>]*>\s*附录\s*([A-F])", t)
        if inner:
            letters.append((f, "内嵌:" + "".join(inner)))
        # 逐节测长
        blocks = re.split(r"<h[2-4][^>]*>", t)
        for b in blocks[1:]:
            title = strip_html(b.split("</h")[0])[:40]
            n = cn(strip_html(b))
            if n > longest[0]:
                longest = (n, f + " :: " + title)

    front = sorted(f for f in files if f.startswith("front"))
    back = sorted(f for f in files if f.startswith("back"))
    alltext = "\n".join(strip_html(v) for v in files.values())
    svgdir = os.path.join(ROOT, repo, "assets", "svg")
    nsvg = len([f for f in os.listdir(svgdir) if f.endswith(".svg")]) if os.path.isdir(svgdir) else 0
    chartdir = os.path.join(ROOT, repo, "assets", "charts")
    nchart = len([f for f in os.listdir(chartdir) if f.endswith(".png")]) if os.path.isdir(chartdir) else 0
    return {
        "kind": "book", "repo": repo,
        "parts": [{"title": p.get("part"), "n": len(p.get("chapters", [])),
                   "chapters": [c.get("title") for c in p.get("chapters", [])]} for p in parts],
        "n_chapters": len(chs),
        "front": front, "back": back, "appendix": ap, "appendix_letters": letters,
        "appendix_longest": longest,
        "cn_body": sum(cn(strip_html(files[f])) for f in chs),
        "cn_appendix": sum(cn(strip_html(files[f])) for f in ap),
        "tables": tables, "figures": figs, "figure_captions": figcap,
        "nsvg": nsvg, "nchart": nchart,
        "skeleton_missing": seg, "chapters": chap,
        "cores": {k: sum(alltext.count(w) for w in v) for k, v in CORES.items()},
        "banned": {w: alltext.count(w) for w in BANNED},
        "hedge": {w: alltext.count(w) for w in HEDGE},
        "text": alltext,
    }


def paper(repo):
    base = os.path.join(ROOT, repo)
    cand = [os.path.join(base, "source", "paper.md")]
    cand += [os.path.join(base, f) for f in os.listdir(base) if f.endswith(".md")]
    p, best = None, -1
    for c in cand:
        if os.path.exists(c):
            n = cn(read(c))
            if n > best:
                p, best = c, n
    t = read(p)
    secs = [l[3:].strip() for l in t.splitlines() if re.match(r"^##\s+\d", l)]
    subs = [l for l in t.splitlines() if re.match(r"^###\s+\d", l)]
    nums = [sec_num(s) for s in secs]
    order_bad = [f"{a}->{b}" for a, b in zip(nums, nums[1:])
                 if a and b and b[:2] < a[:2]]
    return {
        "kind": "paper", "repo": repo, "file": os.path.relpath(p, ROOT),
        "n_sections": len(secs), "n_subsections": len(subs), "sections": secs,
        "order_bad": order_bad,
        "cn": cn(t), "figures": len(re.findall(r"!\[", t)),
        "table_blocks": len(re.findall(r"^\|[-: ]+\|", t, flags=re.M)),
        "cores": {k: sum(t.count(w) for w in v) for k, v in CORES.items()},
        "banned": {w: t.count(w) for w in BANNED},
        "hedge": {w: t.count(w) for w in HEDGE},
        "text": t,
    }


TITLES = {
    "knowledge-tradeoffs": ["只能选两样"],
    "distinction-evolution": ["区分的语言", "区分的语法"],
    "capacity-cascade": ["遗忘的边界"],
    "entropy-spiral": ["错位的时间"],
    "impossibility-triangle": ["选择的代价"],
    "interpretation-tradeoff": ["诠释的权衡"],
    "emergence-critical": ["涌现的临界"],
    "mind-forks": ["心灵的分岔"],
    "hotspot-bills": ["热点的账单"],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {"books": {b: book(b) for b in BOOKS},
            "papers": {p: paper(p) for p in PAPERS}}
    xref = {}
    for name, item in list(data["books"].items()) + list(data["papers"].items()):
        row = {}
        for other, keys in TITLES.items():
            if other != name:
                n = sum(item["text"].count(k) for k in keys)
                if n:
                    row[other] = n
        xref[name] = row
    data["xref"] = xref

    slim = {k: ({kk: {k2: v2 for k2, v2 in vv.items() if k2 != "text"}
                 for kk, vv in v.items()} if isinstance(v, dict) else v)
            for k, v in data.items()}
    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)

    L = ["# 结构总表（审阅取数）", ""]
    L.append("| 件 | 类 | 部分 | 章 | 正面字 | 附录字 | 图 | 图注 | 表 | SVG | PNG图 | 附录字序列 |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for name, it in data["books"].items():
        L.append(f"| {name} | 书 | {len(it['parts'])} | {it['n_chapters']} | {it['cn_body']:,} | "
                 f"{it['cn_appendix']:,} | {it['figures']} | {it['figure_captions']} | {it['tables']} | "
                 f"{it['nsvg']} | {it['nchart']} | "
                 f"{'/'.join(sorted({a[1] for a in it['appendix_letters']}))} |")
    for name, it in data["papers"].items():
        L.append(f"| {name} | 论文 | – | – | {it['cn']:,} | – | {it['figures']} | – | "
                 f"{it['table_blocks']} | – | – | {it['n_sections']} 节 |")
    L.append("")
    L.append("## 分部分章")
    for name, it in data["books"].items():
        L.append(f"### {name}")
        for p in it["parts"]:
            chs = "；".join(f"{i+1}.{t}" for i, t in enumerate(p["chapters"]))
            L.append(f"- {p['title']}（{p['n']} 章）：{chs}")
    L.append("")
    L.append("## 章节失衡（h3 ≥ 14 或 一节带走 >1 或 章内嵌章）")
    for name, it in data["books"].items():
        for c in it["chapters"]:
            flag = []
            if c["n_h3"] >= 14:
                flag.append(f"h3={c['n_h3']}")
            if c["n_takeaway"] > 1:
                flag.append(f"带走×{c['n_takeaway']}")
            if c["n_summary"] > 1:
                flag.append(f"小结×{c['n_summary']}")
            if c["chapter_inside"]:
                flag.append("章内嵌章: " + "、".join(c["chapter_inside"])[:60])
            if c["order_bad"]:
                flag.append("编号倒序: " + "、".join(c["order_bad"][:4]))
            if c["dup"]:
                flag.append("重号: " + "、".join(c["dup"]))
            if flag:
                L.append(f"- {name}/{c['file']}: " + "；".join(flag))
    L.append("")
    L.append("## 章骨架缺项（按体裁读：通俗读本只要求 主提问/场景/反例/带走）")
    for name, it in data["books"].items():
        for f, miss in it["skeleton_missing"]:
            L.append(f"- {name}/{f}: {'、'.join(miss)}")
    L.append("")
    L.append("## 附录")
    for name, it in data["books"].items():
        L.append(f"- {name}: " + ", ".join(f"{f}→{a}" for f, a in it["appendix_letters"]) +
                 f" ｜最长节 {it['appendix_longest'][0]} 字（{it['appendix_longest'][1]}）")
    L.append("")
    L.append("## 前置/后置件")
    for name, it in data["books"].items():
        L.append(f"- {name}: front={it['front']} back={it['back']}")
    L.append("")
    L.append("## 禁词 / 对冲词")
    L.append("| 件 | " + " | ".join(BANNED) + " | " + " | ".join(HEDGE) + " |")
    L.append("|---|" + "---|" * (len(BANNED) + len(HEDGE)))
    for name, it in list(data["books"].items()) + list(data["papers"].items()):
        L.append(f"| {name} | " + " | ".join(str(it["banned"][w]) for w in BANNED) + " | " +
                 " | ".join(str(it["hedge"][w]) for w in HEDGE) + " |")
    L.append("")
    L.append("## 跨著互引")
    for name, row in xref.items():
        L.append(f"- **{name}**: " + ("、".join(f"{k}×{v}" for k, v in
                                                sorted(row.items(), key=lambda x: -x[1])) or "（无）"))
    L.append("")
    L.append("## 六核心词频（粗）")
    L.append("| 件 | " + " | ".join(CORES) + " |")
    L.append("|---|" + "---|" * len(CORES))
    for name, it in list(data["books"].items()) + list(data["papers"].items()):
        L.append(f"| {name} | " + " | ".join(str(it["cores"][k]) for k in CORES) + " |")
    with open(os.path.join(OUT, "OUTLINE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("ok")


if __name__ == "__main__":
    main()

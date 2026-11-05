#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""定义/定理编号归一：按章内出现顺序重排“定义 N.M / 定理 N.M”，并同步引用。

用法：python _series/tools/renumber_labels.py <repo> [--write]
"""
from __future__ import annotations
import os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TYPES = ["定义", "定理", "命题", "引理", "推论"]
# 定义点：define 框内的 bt 标签，或段首 <p><b>定理 …</b>
DEF = re.compile(r'(<span class="bt">|<p><b>)(定义|定理|命题|引理|推论)\s*(\d+)[.．](\d+)([a-z]?)(?=[　\s（(])')


def main():
    repo = sys.argv[1]
    do = "--write" in sys.argv
    src = os.path.join(ROOT, repo, "source")
    files = sorted(f for f in os.listdir(src) if re.fullmatch(r"ch\d+\.html", f))
    plans = {}
    mapping = {}
    for f in files:
        ch = int(re.search(r"\d+", f).group())
        t = open(os.path.join(src, f), encoding="utf-8").read()
        counters = Counter()
        plan = []
        for m in DEF.finditer(t):
            typ = m.group(2)
            counters[typ] += 1
            old = f"{m.group(3)}.{m.group(4)}{m.group(5)}"
            new = f"{ch}.{counters[typ]}"
            plan.append((m, ch, typ, old, new))
            mapping.setdefault((typ, old), new)
        plans[f] = (t, plan)
        if plan:
            print(f, len(plan), "definitions")
    if not do:
        return
    # 先改定义点（从后往前），再改正文引用（跳过已改的定义点）
    for f, (t, plan) in plans.items():
        for m, ch, typ, old, new in sorted(plan, key=lambda x: -x[0].start()):
            whole = m.group(0)
            head = whole[:whole.index(typ) + len(typ)]
            rest = whole[whole.index(typ) + len(typ):]
            rest2 = rest.replace(old, new, 1)
            t = t[:m.start()] + head + rest2 + t[m.end():]
        open(os.path.join(src, f), "w", encoding="utf-8").write(t)
    # 引用：逐类型、旧号唯一才改
    pats = {typ: re.compile(typ + r"\s*(\d+)[.．](\d+)([a-z]?)(?![.．]\d)") for typ in TYPES}
    for f in sorted(os.listdir(src)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(src, f)
        t = open(p, encoding="utf-8").read()
        parts = re.split(r'(<h[1-6][^>]*>.*?</h[1-6]>|<span class="bt">[^<]*</span>|<p><b>(?:定义|定理|命题|引理|推论)[^<]*</b>)', t, flags=re.S)
        for i, part in enumerate(parts):
            if part.startswith("<h") or 'class="bt"' in part or part.startswith("<p><b>"):
                continue
            for typ, pat in pats.items():
                def rep(m):
                    old = f"{m.group(1)}.{m.group(2)}{m.group(3)}"
                    new = mapping.get((typ, old))
                    if not new:
                        return m.group(0)
                    return typ + m.group(0)[len(typ):].replace(old, new, 1)
                part = pat.sub(rep, part)
            parts[i] = part
        t2 = "".join(parts)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
    print("written", repo, "mapped", len(mapping))


if __name__ == "__main__":
    main()

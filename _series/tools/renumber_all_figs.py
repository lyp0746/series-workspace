#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全书图/表号归一：章按章号，附录按宿主字母，前置按 0，后置按 G/R/S。

用法：python _series/tools/renumber_all_figs.py <repo> [--write]
"""
from __future__ import annotations
import os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEF = re.compile(r"<b>([图表])\s*([A-Z0-9]+)[.．](\d+)([a-z]?)")


def prefix_of(fname, text):
    m = re.fullmatch(r"ch(\d+)\.html", fname)
    if m:
        return str(int(m.group(1)))
    if fname.startswith("appendix"):
        h = re.search(r'<h2[^>]*>.*?附\s*录\s*([A-Z])', text, re.S)
        return h.group(1) if h else "X"
    if fname == "back_glossary.html":
        return "G"
    if fname == "back_references.html":
        return "R"
    if fname in ("back_popular_guide.html", "back_series.html"):
        return "S"
    if fname.startswith("front_"):
        return "0"
    return None


def main():
    repo = sys.argv[1]
    do = "--write" in sys.argv
    src = os.path.join(ROOT, repo, "source")
    files = sorted(os.listdir(src))
    order = ([f for f in files if f.startswith("front_")] +
             [f for f in files if re.fullmatch(r"ch\d+\.html", f)] +
             [f for f in files if f.startswith("appendix")] +
             [f for f in files if f.startswith("back_")])
    plans = {}
    mapping = {}
    for f in order:
        if not f.endswith(".html"):
            continue
        t = open(os.path.join(src, f), encoding="utf-8").read()
        pref = prefix_of(f, t)
        if pref is None:
            continue
        cnt = Counter()
        plan = []
        for m in DEF.finditer(t):
            kind = m.group(1)
            cnt[kind] += 1
            old = f"{kind}{m.group(2)}.{m.group(3)}{m.group(4)}"
            new = f"{kind} {pref}.{cnt[kind]}"
            plan.append((m, old, new))
            mapping.setdefault(old, new)
        plans[f] = (t, plan)
        dup = [k for k, v in Counter(x[1] for x in plan).items() if v > 1]
        if dup:
            print(f, "dup-in-file", dup)
    if not do:
        return
    # definitions first (positional), then refs
    for f, (t, plan) in plans.items():
        for m, old, new in sorted(plan, key=lambda x: -x[0].start()):
            t = t[:m.start()] + f"<b>{new}" + t[m.end():]
        open(os.path.join(src, f), "w", encoding="utf-8").write(t)
    ref = re.compile(r"(?<!<b>)([图表])\s*([A-Z0-9]+)[.．](\d+)([a-z]?)(?![0-9a-z.])")
    for f in files:
        if not f.endswith(".html"):
            continue
        p = os.path.join(src, f)
        t = open(p, encoding="utf-8").read()
        def rep(m):
            old = f"{m.group(1)}{m.group(2)}.{m.group(3)}{m.group(4)}"
            return mapping.get(old, m.group(0))
        t2 = ref.sub(rep, t)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
    print("written", repo, len(mapping))


if __name__ == "__main__":
    main()

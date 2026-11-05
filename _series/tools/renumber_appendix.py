#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""附录小节号归一：把附录文件内的 h3「X.N」改为宿主字母下的连续编号。

用法：python _series/tools/renumber_appendix.py <repo> [--write]
"""
from __future__ import annotations
import os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3 = re.compile(r'<h3([^>]*)>(.*?)</h3>', re.S)
SEC = re.compile(r'^([A-Z])[.．](\d+)([a-z]?)[　\s]')


def read(p):
    return open(p, encoding="utf-8").read()


def plain(h):
    return re.sub(r"<[^>]+>", "", h).strip()


def main():
    repo = sys.argv[1]
    do = "--write" in sys.argv
    src = os.path.join(ROOT, repo, "source")
    apps = sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix.*\.html", f))
    plans, host = {}, {}
    all_labels = Counter()
    for f in apps:
        t = read(os.path.join(src, f))
        m = re.search(r'<h2[^>]*>.*?附\s*录\s*([A-Z])', t, re.S)
        if not m:
            continue
        host[f] = m.group(1)
        plan = []
        for h in H3.finditer(t):
            txt = plain(h.group(2))
            sm = SEC.match(txt)
            if sm:
                plan.append((h, txt, f"{sm.group(1)}.{sm.group(2)}{sm.group(3)}"))
                all_labels[f"{sm.group(1)}.{sm.group(2)}{sm.group(3)}"] += 1
        plans[f] = (t, plan)
        print(f, "host", host[f], "sections", len(plan))
    uniq = {k for k, v in all_labels.items() if v == 1}
    mapping = {}
    if not do:
        return
    ref0 = re.compile(r'([A-Z])[.．](\d+)([a-z]?)(?![0-9a-z.])')
    for f, (t, plan) in plans.items():
        L = host[f]
        for i, (h, txt, old) in enumerate(plan, 1):
            if old in uniq:
                mapping[old] = f"{L}.{i}"
        # 先改标题之外的引用，再改标题，避免把新号二次映射
        parts = re.split(r'(<h3[^>]*>.*?</h3>)', t, flags=re.S)
        for j, part in enumerate(parts):
            if part.startswith('<h3'):
                continue
            parts[j] = ref0.sub(lambda m: mapping.get(f"{m.group(1)}.{m.group(2)}{m.group(3)}", m.group(0)), part)
        t = "".join(parts)
        for i, (h, txt, old) in enumerate(plan, 1):
            attr = h.group(1)
            attr2 = re.sub(r'id="[^"]*"', f'id="sec{L}-{i}"', attr)
            head2 = SEC.sub(f"{L}.{i}　", h.group(2), count=1)
            t = t.replace(h.group(0), f"<h3{attr2}>{head2}</h3>", 1)
        open(os.path.join(src, f), "w", encoding="utf-8").write(t)
    # 引用：只改全局唯一的旧号
    ref = re.compile(r'([A-Z])[.．](\d+)([a-z]?)(?![0-9a-z.])')
    for f in sorted(os.listdir(src)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(src, f)
        t = read(p)
        def rep(m):
            old = f"{m.group(1)}.{m.group(2)}{m.group(3)}"
            return mapping.get(old, m.group(0))
        t2 = ref.sub(rep, t)
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
    print("mapped", len(mapping), "ambiguous", len(all_labels) - len(uniq))


if __name__ == "__main__":
    main()

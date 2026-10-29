#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""通俗本：把已有的"这一部回答"框标成主提问框，把第一个故事段标成场景开篇。

只加标记，不改一个字——这两本书本来就写了场景与提问，只是没穿制服。
"""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for book in ("knowledge-tradeoffs", "hotspot-bills"):
    src = os.path.join(ROOT, book, "source")
    n1 = n2 = 0
    for f in sorted(os.listdir(src)):
        if not re.fullmatch(r"ch\d+\.html", f):
            continue
        p = os.path.join(src, f)
        t = io.open(p, encoding="utf-8").read()
        o = t
        if "box-takeaway" not in t:
            t = t.replace('<div class="box">', '<div class="box box-takeaway">', 1)
            if t != o:
                n1 += 1
        if 'class="lead"' not in t:
            m = re.search(r'(<h3[^>]*>.*?</h3>\s*\n)(<p>)(.*?)(</p>)', t, re.S)
            if m:
                t = t[:m.start()] + m.group(1) + '<p class="lead">' + m.group(3) + m.group(4) + t[m.end():]
                n2 += 1
        if t != o:
            io.open(p, "w", encoding="utf-8").write(t)
    print(f"{book}: 主提问框 {n1} 章 / 场景开篇 {n2} 章")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从文件系统重建 BACK 列表（在 build_book.py 被误改后恢复用）。

顺序：结语 → 通俗导读/后记 → 系列 → 参考文献 → 术语表 → 附录 A..F
"""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
         "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]
GIT = "/mnt/d/Git/cmd/git.exe"
HD = re.compile(r'<h[12]\s+class="chapter">([^<]*)</h[12]>')
ORDER = ["back_epilogue.html", "back_popular_guide.html", "back_afterword.html", "back_postscript.html",
         "back_data.html", "back_series.html", "back_references.html", "back_glossary.html"]

for b in BOOKS:
    d = os.path.join(ROOT, b); src = os.path.join(d, "source"); bp = os.path.join(d, "build_book.py")
    files = sorted(os.listdir(src))
    apx = [f for f in files if re.fullmatch(r"appendix_[a-z]\.html", f)]
    def letter(f):
        h = open(os.path.join(src, f), encoding="utf-8").read()
        m = HD.search(h)
        mm = re.match(r"^附\s*录\s*([A-Z])", m.group(1).strip()) if m else None
        return mm.group(1) if mm else "Z"
    apx.sort(key=letter)
    seq = [f for f in ORDER if f in files] + apx
    items = []
    for f in seq:
        h = open(os.path.join(src, f), encoding="utf-8").read()
        m = HD.search(h)
        title = m.group(1).strip() if m else f
        items.append((title, f, "apx" + (letter(f) if f.startswith("appendix") else f[5])))
    body = "BACK = [\n" + "".join(f'        ("{a}", "{b}", "{c}"),\n' for a, b, c in items)
    t = open(bp, encoding="utf-8").read()
    t2, n = re.subn(r"BACK = \[[^\[\]]*\]", body.rstrip("\n") + "]", t, count=1)
    assert n == 1, b
    open(bp, "w", encoding="utf-8").write(t2)
    print(f"{b:24} BACK {len(items)}: " + " ".join(x[1] for x in items))

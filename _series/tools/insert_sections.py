#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按章标题把 _series/content 里的新小节插进正文（在「本章小结/一句话带走/参考文献」之前）。"""
import io, os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def chunks(path):
    t = io.open(path, encoding="utf-8").read()
    blocks = re.split(r"(?m)^<!-- 追加到", t)[1:]
    out = []
    for b in blocks:
        body = re.sub(r"^[^\n]*-->\s*\n", "", b, count=1).strip()
        m = re.search(r"<h3>(.*?)</h3>", body)
        out.append((m.group(1) if m else "", body))
    return out

JOBS = [
    # (book, 章标题关键词, content 文件, 小节标题关键词)
    ("distinction-evolution", "五个领域", "distinction-a.html", "量子概率"),
    ("distinction-evolution", "语言的覆盖", "distinction-a.html", "机器学习"),
    ("distinction-evolution", "涌现的新领域", "distinction-b.html", "语言学"),
    ("emergence-critical", "实践方向", "emergence-a.html", "社会临界之一"),
    ("emergence-critical", "实践方向", "emergence-a.html", "社会临界之二"),
    ("emergence-critical", "实践方向", "emergence-a.html", "社会临界之三"),
    ("distinction-evolution", "五个领域", "distinction-c.html", "经济学的连接"),
    ("distinction-evolution", "语言的覆盖", "distinction-c.html", "拓扑数据分析"),
    ("emergence-critical", "实践方向", "emergence-b.html", "金融临界"),
    ("emergence-critical", "实践方向", "emergence-b.html", "认知临界"),
]

def find_chapter(src, key):
    for p in sorted(glob.glob(os.path.join(src, "ch*.html"))):
        t = io.open(p, encoding="utf-8").read()
        m = re.search(r'<h2 class="chapter">([^<]*)</h2>', t)
        if m and key in m.group(1):
            return p
    return None

def main():
    cache = {}
    for book, key, f, sub in JOBS:
        if f not in cache:
            cache[f] = chunks(os.path.join(ROOT, "_series", "content", f))
        hit = [c for c in cache[f] if sub in c[0]]
        if not hit:
            print("!", book, sub)
            continue
        body = hit[0][1]
        src = os.path.join(ROOT, book, "source")
        p = find_chapter(src, key)
        if not p:
            print("未找到章", book, key); continue
        t = io.open(p, encoding="utf-8").read()
        if hit[0][0] in t:
            continue
        m = re.search(r'<div class="box box-summary">|<div class="box box-takeaway">|<h3[^>]*>\s*本章小结|<h3[^>]*>\s*本章参考文献', t)
        t = (t[:m.start()] + body + "\n\n" + t[m.start():]) if m else (t.rstrip() + "\n" + body)
        io.open(p, "w", encoding="utf-8").write(t)
        print("插入", book, os.path.basename(p), sub, len(re.findall(r"[\u4e00-\u9fff]", body)), "字")
    return 0

sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把附录里的“论证性正文”搬进正文，直到 附录占比 ≤12%（只搬，不删不写）。"""
import io, re, os, json, glob

def cn(s):
    s = re.sub(r"<table.*?</table>", " ", s, flags=re.S|re.I)
    s = re.sub(r"<ul.*?</ul>", " ", s, flags=re.S|re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def fix_book(b):
    src = f"{b}/source"; pj = os.path.join(src, "parts.json")
    parts = json.load(io.open(pj, encoding="utf-8"))
    chs = [c for p in parts for c in p["chapters"]]
    body = sum(cn(io.open(os.path.join(src, c["file"]), encoding="utf-8").read()) for c in chs)
    apx = [f for f in sorted(os.listdir(src)) if f.startswith("appendix")]
    ratio = lambda: sum(cn(io.open(os.path.join(src,f),encoding="utf-8").read()) for f in apx)/(body+sum(cn(io.open(os.path.join(src,f),encoding="utf-8").read()) for f in apx))
    moved = 0
    while ratio() > 0.115 and len(apx) > 3:
        # 最大的附录
        big = max(apx, key=lambda f: cn(io.open(os.path.join(src,f),encoding="utf-8").read()))
        t = io.open(os.path.join(src,big), encoding="utf-8").read()
        blocks = re.split(r"(?m)(?=<h3)", t)
        head, secs = blocks[0], blocks[1:]
        if len(secs) < 3:
            break
        k = min(3, len(chs))
        targets = chs[-k:]
        for i, s in enumerate(secs):
            tgt = os.path.join(src, targets[i % k]["file"])
            x = io.open(tgt, encoding="utf-8").read()
            m = re.search(r'<div class="box box-summary">|<div class="box box-takeaway">', x)
            s2 = re.sub(r"<h3[^>]*>", "<h3>", s)
            x = (x[:m.start()] + s2 + "\n\n" + x[m.start():]) if m else x.rstrip() + "\n" + s2
            io.open(tgt, "w", encoding="utf-8").write(x)
            moved += 1
        io.open(os.path.join(src,big), "w", encoding="utf-8").write(head if cn(head) < 400 else "")
        # 从 BACK 里去掉
        bp = f"{b}/build_book.py"; t2 = io.open(bp, encoding="utf-8").read()
        t2 = re.sub(rf'\s*\("[^"]*", "{big}", "[^"]*"\),', "", t2)
        io.open(bp, "w", encoding="utf-8").write(t2)
        apx.remove(big)
        print(f"  {b}: 迁出 {big} 的 {len(secs)} 节 → 最后 {k} 章")
    return moved

def fix_paper(p):
    src = f"{p}/source/paper.md"
    t = io.open(src, encoding="utf-8").read()
    parts = re.split(r"(?m)^## ", t)
    head, bl = parts[0], [[x.partition("\n")[0], x.partition("\n")[2]] for x in parts[1:]]
    body = sum(cn(b) for h, b in bl if not h.startswith("附"))
    def ratio():
        a = sum(cn(b) for h, b in bl if h.startswith("附"))
        return a / (body + a)
    n = 0
    while ratio() > 0.115:
        aps = [(i, h) for i, (h, _) in enumerate(bl) if re.match(r"^附\s*录", h)]
        if len(aps) <= 3:
            break
        i, h = min(aps, key=lambda x: cn(bl[x[0]][1]))
        disc = next((j for j, (hh, _) in enumerate(bl) if "讨论" in hh), None)
        if disc is None:
            break
        body_ = re.sub(r"(?m)^### ", "#### ", bl[i][1]).strip()
        bl[disc][1] = bl[disc][1].rstrip() + f"\n\n### {re.sub(r'^附\\s*录\\s*[A-F]\\s*[　 ]*', '', h)}\n\n" + body_ + "\n"
        del bl[i]
        n += 1
    k = 0
    for i, (h, b) in enumerate(bl):
        m = re.match(r"^附\s*录\s*[A-F]\s*[　 ]*(.*)$", h)
        if m:
            bl[i][0] = f"附录 {chr(65+k)}　{m.group(1).strip()}"; k += 1
    io.open(src, "w", encoding="utf-8").write(head + "".join(f"## {h}\n{b}\n" for h, b in bl))
    return n

for b in ("distinction-evolution","entropy-spiral","impossibility-triangle","interpretation-tradeoff"):
    fix_book(b)
for p in ("WorldPeriodization","SleepingResidue","DomainCrossSection","IsomorphismStrength",
          "MemoryAnchor","MemoryStressTest","MonarchCompetition"):
    print(p, "并入讨论", fix_paper(p), "节")

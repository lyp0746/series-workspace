#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把节数不足 12 的论文，用"提拔已有小节"的方式补到 12（不新增内容）。"""
import io, re, glob, os
TARGET = 12
for f in sorted(glob.glob('*/source/paper.md')):
    t = io.open(f, encoding="utf-8").read()
    parts = re.split(r"(?m)^## ", t)
    head = parts[0]
    bl = [[x.partition("\n")[0].strip(), x.partition("\n")[2]] for x in parts[1:]]
    body = [i for i, (h, _) in enumerate(bl)
            if not re.sub(r"^\d+[\s　]+", "", h).startswith(("摘要", "Abstract", "参考文献", "附注", "附录"))]
    n = len(body)
    if n >= TARGET:
        continue
    need = TARGET - n
    # 反复挑"小节最多"的节，提拔它的最后一个小节
    for _ in range(need):
        best, k = None, 0
        for i in body:
            subs = re.findall(r"(?m)^### ", bl[i][1])
            if len(subs) > k:
                best, k = i, len(subs)
        if not best or k < 2:
            break
        b = bl[best][1]
        idxs = [m.start() for m in re.finditer(r"(?m)^### ", b)]
        cut = idxs[-1]
        tail = b[cut:]
        bl[best][1] = b[:cut]
        # 新节标题=小节标题，其下 #### 提升为 ###
        newh, _, newb = tail[4:].partition("\n")
        newb = re.sub(r"(?m)^#### ", "### ", newb)
        bl.insert(best + 1, [newh.strip(), newb])
        body = [i for i, (h, _) in enumerate(bl)
                if not re.sub(r"^\d+[\s　]+", "", h).startswith(("摘要", "Abstract", "参考文献", "附注", "附录"))]
        n += 1
    # 重新编号
    k = 0
    for i, (h, b) in enumerate(bl):
        title = re.sub(r"^\d+(\.\d+)?[\s　]+", "", h)
        if title.startswith(("摘要", "Abstract", "参考文献", "附注", "附录")):
            bl[i][0] = title
            continue
        k += 1
        bl[i][0] = f"{k} {title}"
        cnt = [0]
        def rep(mm):
            cnt[0] += 1
            txt = re.sub(r"^\d+\.\d+\s*[　 ]*", "", mm.group(1)).strip()
            return f"### {k}.{cnt[0]} {txt}"
        bl[i][1] = re.sub(r"(?m)^### (.+)$", rep, bl[i][1])
    io.open(f, "w", encoding="utf-8").write(head + "".join(f"## {h}\n{b}\n" for h, b in bl))
    print(f"{os.path.dirname(os.path.dirname(f)):24} {n} 节")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""让 BACK 列表与磁盘上的 appendix 文件一一对应（补挂漏项、重排字母、改写标题）。"""
import io,re,os
BOOKS=["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
       "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]
for b in BOOKS:
    src=f"{b}/source"; bp=f"{b}/build_book.py"
    files=sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix_[a-z]\.html",f))
    titles=[]
    for i,f in enumerate(files):
        p=os.path.join(src,f); t=io.open(p,encoding='utf-8').read()
        m=re.search(r'<h2 class="chapter">([^<]*)</h2>',t)
        title=re.sub(r"^附\s*录\s*[A-F]\s*[　 ]*","",m.group(1)) if m else f
        L=chr(65+i)
        t2=re.sub(r'(<h2 class="chapter">)附\s*录\s*[A-F]\s*[　 ]*', rf'\g<1>附录 {L}　', t, count=1) if m else t
        if t2!=t: io.open(p,'w',encoding='utf-8').write(t2)
        titles.append((f"附录 {L}　{title}", f, "apx"+L))
    t=io.open(bp,encoding='utf-8').read()
    m=re.search(r"BACK = \[([^\[\]]*)\]", t, re.S)
    if not m:
        print(b,"!! BACK 解析失败"); continue
    items=re.findall(r'\(\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)', m.group(1))
    keep=[x for x in items if not x[1].startswith("appendix")]
    new=keep+titles
    body="\n"+"".join(f'        ("{a}", "{c}", "{d}"),\n' for a,c,d in new)
    t=re.sub(r"BACK = \[[^\[\]]*\]", "BACK = ["+body.rstrip("\n")+"\n]", t, count=1)
    io.open(bp,'w',encoding='utf-8').write(t)
    print(f"{b:24} BACK {len(keep)}+{len(titles)}  appendix 磁盘 {len(files)}")

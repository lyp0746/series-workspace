# -*- coding: utf-8 -*-
"""给论文 PDF 加书签：按 paper.md 的 ## 节标题，找到它在 PDF 里首次出现的页，写入 outline。"""
import io, re, os, glob, sys
from pypdf import PdfReader, PdfWriter

PAPERS=[p for p in glob.glob("*/source/paper.md")]
for src in sorted(PAPERS):
    b=os.path.dirname(os.path.dirname(src))
    pdfs=[f for f in glob.glob(os.path.join(b,"*.pdf")) if not os.path.basename(f).startswith("_")]
    if not pdfs: continue
    pdf=sorted(pdfs)[0]
    md=io.open(src,encoding="utf-8").read()
    heads=[re.sub(r"\s+"," ",h).strip() for h in re.findall(r"(?m)^## (.+)$", md)]
    r=PdfReader(pdf)
    pages=[re.sub(r"\s+","",(p.extract_text() or "")) for p in r.pages]
    w=PdfWriter(clone_from=pdf)
    added=0
    for h in heads:
        key=re.sub(r"\s+","",h)[:14]
        if not key: continue
        idx=next((i for i,t in enumerate(pages) if key in t), None)
        if idx is None: continue
        w.add_outline_item(h, idx); added+=1
    if added:
        w.write(pdf)
    print(f"{b:24} 书签 {added}/{len(heads)}")

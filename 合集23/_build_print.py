# -*- coding: utf-8 -*-
"""只做印刷版：封面 + 正文 → 合并。"""
import os, pymupdf, build_collection23 as B
os.makedirs(B.OUT, exist_ok=True)
ch = os.path.join(B.ROOT, "_cover-print.html")
open(ch, "w", encoding="utf-8").write(B.cover_only_html("print"))
cp = os.path.join(B.ROOT, "_cover-print.pdf")
B.print_pdf(ch, cp); print("封面完成", flush=True)
bh, _ = B.assemble("print", skip_cover=True)
bp = os.path.join(B.ROOT, "_body-print.pdf")
B.print_pdf(bh, bp); print("正文完成", flush=True)
out = os.path.join(B.OUT, "00-合集-印刷版.pdf")
d = pymupdf.open(cp); d.insert_pdf(pymupdf.open(bp))
d.save(out, garbage=3, deflate=True); d.close()
print("merged", out, round(os.path.getsize(out)/1e6,1), "MB", len(pymupdf.open(out)), "页", flush=True)

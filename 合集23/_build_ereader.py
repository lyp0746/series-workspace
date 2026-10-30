# -*- coding: utf-8 -*-
"""电子版（B5）+ EPUB 3。"""
import os, pymupdf, build_collection23 as B
os.makedirs(B.OUT, exist_ok=True)
ch = os.path.join(B.ROOT, "_cover-ereader.html")
open(ch, "w", encoding="utf-8").write(B.cover_only_html("ereader"))
cp = os.path.join(B.ROOT, "_cover-ereader.pdf")
B.print_pdf(ch, cp)
bh, _ = B.assemble("ereader", skip_cover=True)
bp = os.path.join(B.ROOT, "_body-ereader.pdf")
B.print_pdf(bh, bp)
out = os.path.join(B.OUT, "01-合集-电子版.pdf")
d = pymupdf.open(cp); d.insert_pdf(pymupdf.open(bp))
d.save(out, garbage=3, deflate=True); d.close()
print("merged", out, round(os.path.getsize(out)/1e6,1), "MB", len(pymupdf.open(out)), "页", flush=True)
B.build_epub(os.path.join(B.OUT, "合集.epub"))

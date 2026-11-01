# -*- coding: utf-8 -*-
"""从已生成的合集 PDF 里量出总目录与各卷目录的页码，写 _pages.json 供二次构建回填。"""
import json
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COL = os.path.join(ROOT, "合集23")
sys.path.insert(0, COL)
import build_collection23 as B  # noqa: E402


def page_texts(doc):
    return [p.get_text() for p in doc]


def find(texts, needle, start=0, nth=1):
    """返回第 nth 次出现的页码（1 起）。"""
    n = 0
    for i in range(start, len(texts)):
        if needle in texts[i]:
            n += 1
            if n == nth:
                return i + 1
    return None


def main():
    pdf = os.path.join(COL, "release", "00-合集-印刷版.pdf")
    d = pymupdf.open(pdf)
    T = page_texts(d)
    out = {"chapters": [], "appendices": [], "volumes": {}, "papers": {}}
    # 先定各卷起页
    cursor = 0
    starts = []
    for vi, (book, vol, title, sub, blurb, _ff) in enumerate(B.VOLUMES, 1):
        vstart = find(T, blurb[:24], cursor, 1) or find(T, title, cursor, 1) or cursor
        starts.append(vstart)
        out["volumes"][f"vol{vi}"] = vstart
        cursor = vstart + 1

    def find_in(needle, lo, hi):
        """区间内最后一次出现（附录/章标题在区间末尾，正文提及在前）。"""
        hit = None
        for i in range(lo - 1, min(hi - 1, len(T))):
            if needle in T[i]:
                hit = i + 1
        return hit

    for vi, (book, vol, title, sub, blurb, _ff) in enumerate(B.VOLUMES, 1):
        lo = starts[vi - 1]
        hi = starts[vi] if vi < len(starts) else None
        if hi is None:
            hi = len(T)
        toc_pg = None
        for i in range(lo - 1, hi - 1):
            if "本卷目录" in T[i]:
                toc_pg = i + 1
                break
        base = (toc_pg or lo) + 1
        cur_ch = base
        for c in B.chapters_of(book):
            pg = None
            for i in range(cur_ch - 1, hi - 1):
                if c["title"][:14] in T[i]:
                    pg = i + 1
                    break
            if not pg:
                for i in range(cur_ch - 1, hi - 1):
                    if f'第{c["no"]}章' in T[i]:
                        pg = i + 1
                        break
            if pg:
                cur_ch = pg + 1
            out["chapters"].append(pg)
        vac = []
        for at, af in B.appendices_of(book):
            key = re.sub(r"^附录\s*[A-Z]\s*", "", at)[:12]
            vac.append(find_in(key, lo, hi) or find_in(at[:10], lo, hi))
        out["appendices"].append(vac)

    # 论文：从卷九之后按顺序找，游标只前进
    cur = starts[-1]
    for pi, (repo, pno, ptitle, psub, core, cls, md, doi) in enumerate(B.PAPERS, 1):
        pg = None
        for needle in (ptitle[:18], ptitle[:12]):
            for i in range(cur - 1, len(T)):
                if needle in T[i]:
                    pg = i + 1
                    break
            if pg:
                break
        out["papers"][f"paper{pi}"] = pg
        cur = (pg or cur) + 1
    json.dump(out, open(os.path.join(COL, "_pages.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    miss = [i for i, x in enumerate(out["chapters"]) if not x]
    print("chapters", len(out["chapters"]), "missing", len(miss), "papers", len(out["papers"]))


if __name__ == "__main__":
    main()

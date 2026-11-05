# -*- coding: utf-8 -*-
"""按已生成 PDF 的实际页码重建 _pages.json（合集目录两遍回填用）。"""
import json, re, sys
import pymupdf

sys.path.insert(0, ".")
import build_collection23 as B


def main(pdf="release/00-合集-印刷版.pdf"):
    doc = pymupdf.open(pdf)
    texts = [doc[i].get_text() for i in range(len(doc))]

    def find(probe, start=0, skip_toc=False):
        p = re.sub(r"\s+", "", probe)[:26]
        for i in range(start, len(texts)):
            if any(k in texts[i] for k in ("本卷目录", "总目录", "合集一览", "六核心速查")):
                continue
            if p and p in re.sub(r"\s+", "", texts[i]):
                return i + 1
        return 0

    volumes, chapters, appendices, papers = {}, [], [], {}
    cursor = max(0, find("第一部　九卷（专著）") - 1)
    gi = 0
    for vi, (book, vol, title, sub, blurb, _) in enumerate(B.VOLUMES, 1):
        pg = find(f"{vol}　{title}", cursor)
        volumes[f"vol{vi}"] = pg
        cursor = max(cursor, pg - 1)
        pj = json.load(open(f"../{book}/source/parts.json", encoding="utf-8"))
        ach = []
        for part in pj:
            for c in part.get("chapters", []):
                if not c.get("written", True) or not c.get("file"):
                    continue
                label = f"第{c['no']}章"
                pg2 = find(f"{label}　{c['title']}", cursor, True)
                if not pg2:
                    pg2 = find(label, cursor, True)
                chapters.append(pg2)
                cursor = max(cursor, pg2 - 1)
        # appendices
        aplist = []
        for f in sorted(x for x in __import__("os").listdir(f"../{book}/source") if x.startswith("appendix")):
            raw = open(f"../{book}/source/{f}", encoding="utf-8").read()
            m = re.search(r"<h2[^>]*>(.*?)</h2>", raw, re.S)
            if not m:
                continue
            at = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            pg3 = find(at[:30], cursor, True)
            aplist.append(pg3)
            cursor = max(cursor, pg3 - 1)
        appendices.append(aplist)
    for pi, (repo, pno, ptitle, *_) in enumerate(B.PAPERS, 1):
        pg = find(f"{pno}　{ptitle}", cursor)
        papers[f"paper{pi}"] = pg
        cursor = max(cursor, pg - 1)
    out = {"chapters": chapters, "appendices": appendices, "volumes": volumes, "papers": papers}
    json.dump(out, open("_pages.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("volumes", volumes)
    print("chapters", len(chapters), "appendices", len(appendices), "papers", papers)
    print("last chapter page", chapters[-1] if chapters else None)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "release/00-合集-印刷版.pdf")

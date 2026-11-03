# -*- coding: utf-8 -*-
"""fix_collection_nav.py — 给合集 PDF 补“能跳的目录”与书签。

问题：合集由 Playwright 打印、再用 PyMuPDF 合并，合并后**既没有书签，也没有链接**
（书名/卷名在目录页上是纯文本）。于是读者点目录没有任何反应。

做法（不重建、不改内容）：
1. 从 build_collection23.VOLUMES 取九卷的卷号与书名；
2. 在成品 PDF 里找每卷的**卷封面页**（首 300 字里同时出现卷号与书名）；
3. 在目录页上找包含书名的行，按行矩形加 GOTO 链接到该卷封面；
4. 用 `set_toc` 写入分卷书签（前置页 + 九卷 + 后置页）。

用法：python scripts/fix_collection_nav.py release/00-合集-印刷版.pdf
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def volumes():
    sys.path.insert(0, HERE)
    import build_collection23 as B
    out = []
    for v in B.VOLUMES:
        repo, vol, name, sub = v[0], v[1], v[2], v[3]
        out.append((vol, name))
    return out


def norm(s):
    return re.sub(r"\s+", "", s)


def find_cover(doc, vol, name, skip):
    """找卷封面页：前 400 字里同时有卷号与书名，且不是目录页。"""
    nv, nn = norm(vol), norm(name)
    for i in range(doc.page_count):
        if i in skip:
            continue
        t = norm(doc[i].get_text()[:400])
        if nv in t and nn in t:
            return i
    for i in range(doc.page_count):
        if nn in norm(doc[i].get_text()[:200]):
            return i
    return None


def main(path):
    try:
        import pymupdf
    except Exception:
        import fitz as pymupdf
    doc = pymupdf.open(path)
    vols = volumes()
    names_all = [norm(n) for _, n in vols]
    toc_guess = set()
    for i in range(min(80, doc.page_count)):
        head = doc[i].get_text()[:1200]
        if re.search(r"目\s*录", head[:120]):
            toc_guess.add(i); continue
        cnt = sum(1 for n in names_all if n in norm(head))
        if cnt >= 3:                      # 一页里出现三本以上的书名 → 是目录页
            toc_guess.add(i)
    targets = []
    for vol, name in vols:
        p = find_cover(doc, vol, name, toc_guess)
        targets.append((vol, name, p))
        print(f"  {vol} {name} -> page {None if p is None else p + 1}")

    # 目录页：含“目　录”或“总目录”，且后面若干页也有大量“点线 + 数字”
    toc_pages = [i for i in range(min(60, doc.page_count))
                 if re.search(r"目\s*录", doc[i].get_text()[:120])]
    print("  TOC pages:", [p + 1 for p in toc_pages])

    added = 0
    for pi in toc_pages:
        page = doc[pi]
        for L0 in page.get_links():
            try:
                page.delete_link(L0)
            except Exception:
                pass
        d = page.get_text("dict")
        for blk in d.get("blocks", []):
            for line in blk.get("lines", []):
                txt = "".join(s.get("text", "") for s in line.get("spans", []))
                if not txt.strip():
                    continue
                flat = norm(txt)
                for vol, name, tp in targets:
                    if tp is None:
                        continue
                    if norm(name) in flat or (norm(vol) in flat and len(flat) < 60):
                        rect = pymupdf.Rect(line["bbox"])
                        # 只给“卷行”本身加链接，避免误伤正文行
                        if re.match(r"^" + vol, flat) or norm(name) in flat:
                            page.insert_link({"kind": pymupdf.LINK_GOTO, "from": rect,
                                              "page": tp, "to": pymupdf.Point(0, 0), "zoom": 0})
                            added += 1
                        break

    # 书签：前置 + 九卷
    toc = [[1, "总封面", 1]]
    for vol, name, tp in targets:
        if tp is not None:
            toc.append([1, f"{vol}　{name}", tp + 1])
    try:
        doc.set_toc(toc)
    except Exception as e:
        print("  set_toc 失败：", e)

    tmp = path + ".nav"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, path)
    d2 = pymupdf.open(path)
    print(f"  已加链接 {added} 条；书签 {len(d2.get_toc())} 条；总页数 {d2.page_count}")
    d2.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])

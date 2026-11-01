# -*- coding: utf-8 -*-
"""给九本 build_book.py 加两件事：目录页码（两遍构建）+ 页脚页码（PyMuPDF 盖章）。

幂等：重复运行不会重复注入（有 GUARD 标记）。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
         "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
         "emergence-critical", "mind-forks", "hotspot-bills"]

GUARD = "# --- folio support (injected) ---"

HELPERS = GUARD + '''
_PM_PATH = os.path.join(OUTPUT, ".pagemap.json")
_CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
           "七": 7, "八": 8, "九": 9, "十": 10}


def load_pagemap():
    return load_json(_PM_PATH, {}) or {}


def _toc_key(text):
    t = re.sub(r"<[^>]+>", "", text or "").strip()
    m = re.search(r"第\\s*(\\d+)\\s*章", t)
    if m:
        return "ch:" + m.group(1)
    m = re.match(r"^(\\d+\\.\\d+[a-z]?)", t)
    if m:
        return "sec:" + m.group(1)
    m = re.search(r"第\\s*([一二三四五六七八九十]+)\\s*部分", t)
    if m:
        return "part:" + str(_CN_NUM.get(m.group(1), 0))
    return "txt:" + re.sub(r"\\s+", "", t)[:10]


def _with_folios(html, pagemap):
    """给目录行右侧补页码。pagemap: {key: page}"""
    if not pagemap:
        return html

    def rep(m):
        head, inner = m.group(1), m.group(2)
        page = pagemap.get(_toc_key(inner))
        if not page:
            return m.group(0)
        return f'{head}{inner}<span class="folio">{page}</span></div>'

    return re.sub(r'(<div class="l[1-4][^"]*">)(.*?)</div>', rep, html, flags=re.S)


def read_toc_map(pdf_path):
    """从 PDF 书签读出 {key: 页码}。页码为物理页（封面=1）。"""
    try:
        import pymupdf
    except Exception:
        try:
            import fitz as pymupdf
        except Exception:
            return {}
    out = {}
    try:
        doc = pymupdf.open(pdf_path)
        for _lvl, title, page in doc.get_toc(simple=True):
            k = _toc_key(title)
            if page and k not in out:
                out[k] = page
        doc.close()
    except Exception as e:
        print("  [folio] 读取书签失败：", e)
    return out


def stamp_folios(pdf_path):
    """在每页页脚居中盖页码（封面除外）。"""
    try:
        import pymupdf
    except Exception:
        try:
            import fitz as pymupdf
        except Exception:
            print("  [folio] 无 PyMuPDF，跳过页码")
            return
    try:
        doc = pymupdf.open(pdf_path)
        n = len(doc)
        for i in range(1, n):                      # 第 1 页是封面，不盖
            page = doc[i]
            w, h = page.rect.width, page.rect.height
            cx = w / 2.0
            y = h - 26
            page.draw_line(pymupdf.Point(cx - 16, y - 11),
                           pymupdf.Point(cx + 16, y - 11),
                           color=(0.72, 0.72, 0.72), width=0.4)
            page.insert_text((cx - 3.2 * len(str(i + 1)), y), str(i + 1),
                             fontsize=8.5, fontname="helv",
                             color=(0.32, 0.32, 0.32))
        doc.saveIncr()
        doc.close()
        print(f"  [folio] 已给 {n - 1} 页盖页码")
    except Exception as e:
        print("  [folio] 盖章失败：", e)
'''


def patch(path):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if GUARD in s:
        print("skip (already patched):", path)
        return
    # 1) 注入助手函数（放在 build_toc 之前）
    s = s.replace("def build_toc(parts):", HELPERS + "\n\ndef build_toc(parts, pagemap=None):", 1)
    # 2) build_toc 返回时套页码
    s = s.replace('    rows.append(\'<div class="pb"></div>\')\n    return "\\n".join(rows)',
                  '    rows.append(\'<div class="pb"></div>\')\n    return _with_folios("\\n".join(rows), pagemap)', 1)
    # 3) build 增加 pagemap 参数并传给 build_toc
    s = s.replace("def build(book, parts, ereader=False):\n    blocks = [build_cover(), build_title_page(book), build_copyright(book), build_toc(parts)]",
                  "def build(book, parts, ereader=False, pagemap=None):\n    blocks = [build_cover(), build_title_page(book), build_copyright(book), build_toc(parts, pagemap)]", 1)
    # 4) main：两遍构建
    old_main = '''    out = build(book, parts, ereader=ereader)
    if "--pdf" in sys.argv:
        print_pdf(out)'''
    new_main = '''    pm = {} if ereader else load_pagemap()
    out = build(book, parts, ereader=ereader, pagemap=pm)
    if "--pdf" in sys.argv:
        print_pdf(out)
        if not ereader:
            pdf = os.path.join(OUTPUT, "book.pdf")
            newpm = read_toc_map(pdf)
            if newpm and newpm != pm:
                with open(_PM_PATH, "w", encoding="utf-8") as fh:
                    json.dump(newpm, fh, ensure_ascii=False, indent=0)
                print(f"  [folio] 目录页码：{len(newpm)} 项，重建一遍")
                out = build(book, parts, ereader=ereader, pagemap=newpm)
                print_pdf(out)
            stamp_folios(pdf)'''
    if old_main not in s:
        raise SystemExit("main pattern not found: " + path)
    s = s.replace(old_main, new_main, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    print("patched:", path)


if __name__ == "__main__":
    for b in BOOKS:
        patch(os.path.join(ROOT, b, "build_book.py"))

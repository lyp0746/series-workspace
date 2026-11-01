# -*- coding: utf-8 -*-
"""扉页瘦身 + 摘要独立成页（去掉扉页溢出造成的空白页）。幂等。"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
         "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
         "emergence-critical", "mind-forks", "hotspot-bills"]
MARK = "# --- abstract page (injected) ---"

OLD_TITLE = '''    return f"""<div class="title-page">
<div class="book-title">{book.get('title','')}</div>
<div class="book-subtitle">{book.get('subtitle','')}</div>
<div class="author">{book.get('author','')}</div>
<div class="aff">{book.get('email','')}　·　学术专著　·　{today}</div>
{ab_html}
</div>
<div class="pb"></div>
"""'''

NEW_TITLE = '''    return f"""<div class="title-page">
<div class="book-title">{book.get('title','')}</div>
<div class="book-subtitle">{book.get('subtitle','')}</div>
<div class="author">{book.get('author','')}</div>
<div class="aff">{book.get('email','')}　·　学术专著　·　{today}</div>
</div>
<div class="pb"></div>
""" + build_abstract_page(book)


def build_abstract_page(book):
    """内容提要与关键词独立成页（扉页只留书名，避免溢出产生空白页）。"""
    ab = book.get("abstract", "")
    if not ab:
        return ""
    kw = (f'<div class="kw"><b>关键词：</b>{book["keywords"]}</div>'
          if book.get("keywords") else "")
    return f'<div class="abstract-page"><div class="abstract"><span class="abt">内容提要</span>　{ab}{kw}</div></div>'
'''

for b in BOOKS:
    p = os.path.join(ROOT, b, "build_book.py")
    s = open(p, encoding="utf-8").read()
    if MARK in s:
        print("skip", b)
        continue
    if OLD_TITLE not in s:
        print("!! title pattern not found", b)
        continue
    s = s.replace(OLD_TITLE, NEW_TITLE, 1)
    s = s.replace("def build_title_page(book):", MARK + "\ndef build_title_page(book):", 1)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", b)

# -*- coding: utf-8 -*-
"""全系列文本归一：旧书名、系列计数、占位符残留、emoji 标记。只改 source/ 与 CITATION/README。"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
         "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
         "emergence-critical", "mind-forks", "hotspot-bills"]

REPL = [
    ("《区分的语法——五个领域，同一个二次型》", "《区分的语言——区分如何生成空间、形式与谱》"),
    ("《区分的语法》", "《区分的语言》"),
    ("区分的语法", "区分的语言"),
    ("系列共<b>本系列专著</b>（另有两本通俗读本）",
     "系列共<b>九本书</b>：六本学术专著、两本通俗读本、一本科普专著"),
    ("系列共<b>本系列</b>：六本学术专著 + 两本通俗读本 + 一本科普专著",
     "系列共<b>九本书</b>：六本学术专著、两本通俗读本、一本科普专著"),
    ("系列共<b>本系列</b>", "系列共<b>九本书</b>"),
    ("本系列（六本专著 + 两本通俗读本 + 一本科普专著）", "本系列（九本书）"),
    ("本系列（六本专著 + 两本通俗读本）", "本系列（九本书）"),
    ("第本系列十四篇", "第十四篇"),
    ("⚙️ 完整路径", "〔技术〕完整路径"),
    ("⚙️", "〔技术〕"),
]


def fix_text(p):
    s = open(p, encoding="utf-8").read()
    o = s
    for a, b in REPL:
        s = s.replace(a, b)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        return True
    return False


n = 0
for b in BOOKS:
    for f in glob.glob(os.path.join(ROOT, b, "source", "*.html")):
        n += fix_text(f)
    n += fix_text(os.path.join(ROOT, b, "build_book.py"))
    for f in ["CITATION.cff", "README.md"]:
        p = os.path.join(ROOT, b, f)
        if os.path.exists(p):
            n += fix_text(p)
for d in glob.glob(os.path.join(ROOT, "*")):
    if not os.path.isdir(d):
        continue
    for f in glob.glob(os.path.join(d, "*.md")) + glob.glob(os.path.join(d, "source", "paper.md")):
        if os.path.basename(f) in ("README.md", "PLAN.md", "AGENTS.md"):
            continue
        n += fix_text(f)
print("files changed:", n)

# -*- coding: utf-8 -*-
"""引用落地：
1) 章末文献表分成「本章引用」（正文点名并标 ★）与「延伸阅读」；
2) 给四本有文献的书补一段体例说明（含计数）；
3) 给 entropy-spiral 生成合并去重的书末参考文献。
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["distinction-evolution", "capacity-cascade", "entropy-spiral", "impossibility-triangle"]


def strip(h):
    return re.sub("<[^>]+>", "", h)


def surname(e):
    m = re.match(r"([^.，,（(]{1,20})[.，,]", e)
    return (m.group(1).strip() if m else e[:8])


def year_of(e):
    m = re.search(r"\((19\d{2}|20\d{2})\)", e) or re.search(r"(19\d{2}|20\d{2})", e)
    return m.group(1) if m else None


def cited_in(body, name, year):
    if not year:
        return False
    return bool(re.search(re.escape(name[:6]) + r".{0,30}" + year, body) or
                re.search(year + r".{0,20}" + re.escape(name[:4]), body))


def process_chapter(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'<div class="refs">(.*?)</div>', s, flags=re.S)
    if not m:
        return 0, 0
    body = strip(s[:m.start()])
    ents = [re.sub("<[^>]+>", "", p).strip() for p in
            re.findall(r"<p>(.*?)</p>", m.group(1), flags=re.S)]
    ents = [e for e in ents if e]
    cited, rest = [], []
    for e in ents:
        (cited if cited_in(body, surname(e), year_of(e)) else rest).append(e)
    if not cited:
        block = ('<div class="refs">\n<p class="refh">延伸阅读</p>\n'
                 + "".join(f"<p>{e}</p>\n" for e in rest) + "</div>")
    else:
        block = ('<div class="refs">\n<p class="refh">本章引用</p>\n'
                 + "".join(f"<p>★ {e}</p>\n" for e in cited)
                 + ('<p class="refh">延伸阅读</p>\n' if rest else "")
                 + "".join(f"<p>{e}</p>\n" for e in rest) + "</div>")
    s = s[:m.start()] + block + s[m.end():]
    open(path, "w", encoding="utf-8").write(s)
    return len(cited), len(rest)


LEDE = """<p class="lead">本表分两栏：<b>本章引用</b>是正文点名过的文献（标 ★）；<b>延伸阅读</b>是本章用到的背景读物，未在正文逐条标出。数据类来源另见各表下的“数据来源”栏。{extra}</p>"""


def main():
    for b in BOOKS:
        C = R = 0
        for f in sorted(glob.glob(os.path.join(ROOT, b, "source", "ch*.html"))):
            c, r = process_chapter(f)
            C += c
            R += r
        print(f"{b:24s} 引用 {C:3d} / 延伸 {R:3d}")
        # 书末体例说明
        p = os.path.join(ROOT, b, "source", "back_references.html")
        if os.path.exists(p):
            s = open(p, encoding="utf-8").read()
            if "本表分两栏" not in s:
                s = re.sub(r"(<h2[^>]*>[^<]*</h2>)", r"\1\n" +
                           LEDE.format(extra=f"全书正文点名 {C} 条，余为延伸阅读。"), s, count=1)
                open(p, "w", encoding="utf-8").write(s)
                print("  lede ->", p)


if __name__ == "__main__":
    main()

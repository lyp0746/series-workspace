# -*- coding: utf-8 -*-
"""用 _series/registry/series.json 重建每本书的「本系列」页表格（单一来源）。
保留各书原有的导语，只替换表格与占位符。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reg = json.load(open(os.path.join(ROOT, "_series", "registry", "series.json"), encoding="utf-8"))
books = reg["books"]

FILES = {
    "knowledge-tradeoffs": "back_series.html",
    "distinction-evolution": "back_popular_guide.html",
    "capacity-cascade": "back_popular_guide.html",
    "entropy-spiral": "back_popular_guide.html",
    "impossibility-triangle": "back_popular_guide.html",
    "interpretation-tradeoff": "back_popular_guide.html",
    "emergence-critical": "back_series.html",
    "mind-forks": "back_series.html",
    "hotspot-bills": "back_series.html",
}


def table(cur_repo):
    rows = ['<table class="nat">',
            '<caption class="cap"><b>表 S.1　本系列九本书：定位、一句话与入口</b></caption>',
            '<thead><tr><th class="l">书名</th><th class="l">副标题</th><th class="l">定位</th>'
            '<th class="l">一句话</th><th class="l">入口</th></tr></thead>', '<tbody>']
    for b in books:
        mark = "（本书）" if b["repo"] == cur_repo else ""
        rows.append(
            f'<tr><td class="l">《{b["title"]}》{mark}</td><td class="l">{b["subtitle"]}</td>'
            f'<td class="l">{b["genre"]}</td><td class="l">{b["one_line"]}</td>'
            f'<td class="l"><a href="{b["entry"]}">DOI</a></td></tr>')
    rows += ['</tbody></table>',
             '<div class="datasrc"><b>入口一律用概念 DOI</b>（指向最新版本），不是某一版的版本 DOI。'
             '六本学术专著按「先读哪一本」排序，不是按出版顺序。</div>']
    return "\n".join(rows)


for repo, fname in FILES.items():
    p = os.path.join(ROOT, repo, "source", fname)
    if not os.path.exists(p):
        print("missing", p)
        continue
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'<table class="nat">.*?</table>', table(repo), s, count=1, flags=re.S)
    s = s.replace("第本系列专著", "系列中的一本").replace("（第本系列专著）", "")
    s = re.sub(r"系列共<b>九本书</b>[^。]*。", reg["series_line"] + "。", s)
    s = re.sub(r"系列共九本书[^。]*。", reg["series_line"] + "。", s)
    if "本书是系列中的一本" in s:
        pass
    open(p, "w", encoding="utf-8").write(s)
    print("rebuilt", repo, fname)

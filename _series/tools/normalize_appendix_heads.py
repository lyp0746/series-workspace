# -*- coding: utf-8 -*-
"""把附录里所有 h3/h4 的编号按组重排（A.1 / A.1.1 …），并修 h3→h4 的闭合标签。
只改标题行，不动正文。"""
import os
import re

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "emergence-critical", "source")

A_TITLES = [
    "推导与解析（一）：朗道理论、临界指数与标度关系",
    "推导与解析（二）：图拉普拉斯、渗流与复杂网络",
    "推导与解析（三）：有限尺度标度与临界指数的估计",
    '边界（一）：为什么决定性质的是"边"，不是"里面"',
    "边界（二）：约束、可行域与 KKT",
]

# --- 先把附录 A 的五段按语义排序（边界 → 边界二）
p = os.path.join(BASE, "appendix_a.html")
s = open(p, encoding="utf-8").read()
head, rest = s.split('<h3 id="secA-1">', 1)
blocks = re.split(r'(?=<h3 id="secA-\d">)', '<h3 id="secA-1">' + rest)
blocks = [b for b in blocks if b.strip()]
assert len(blocks) == 5, len(blocks)
order = [0, 1, 2, 4, 3]
blocks = [blocks[i] for i in order]
for i, b in enumerate(blocks, 1):
    b = re.sub(r'<h3 id="secA-\d">.*?</h3>',
               f'<h3 id="secA-{i}">{A_TITLES[i-1]}</h3>', b, count=1, flags=re.S)
    blocks[i - 1] = b
open(p, "w", encoding="utf-8").write(head + "".join(blocks))

# --- 统一重编号
for L in "abcdef":
    p = os.path.join(BASE, f"appendix_{L}.html")
    lines = open(p, encoding="utf-8").read().splitlines()
    sub = subsub = 0
    out = []
    for ln in lines:
        m = re.match(r"<h([34])([^>]*)>(.*?)</h[34]>\s*$", ln)
        if m and 'class="chapter"' not in m.group(2):
            lvl = int(m.group(1))
            txt = m.group(3)
            # 去掉旧编号：A.1　/ X.1　/ R.1 / 附录 P　/ 25.3　/ U.0.9　
            txt = re.sub(r"^(附录\s*[A-Z]|[A-Z]\.\d+(\.\d+)?|X\.\d+|\d+\.\d+)\s*[　 ]*", "", txt).strip()
            txt = re.sub(r"^第[一二三四五六七八九十百]+章\s*", "", txt).strip()
            if lvl == 3:
                sub += 1
                subsub = 0
                label = f"{L.upper()}.{sub}"
                out.append(f'<h3>{label}　{txt}</h3>')
            else:
                if sub == 0:
                    sub = 1
                subsub += 1
                out.append(f'<h4>{L.upper()}.{sub}.{subsub}　{txt}</h4>')
        else:
            out.append(ln)
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(L, "ok")

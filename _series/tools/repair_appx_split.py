#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把两本被“杂物抽屉化”的附录 E 按原附录字母重新拆成两件，删掉空附录，补回六章小结。"""
import io, re, os
ROOT='.'

PLAN = {
 "impossibility-triangle": {
   "e": ("附录 E　失败记录、案例与探针", "BFPKYQ"),
   "f": ("附录 F　上游、前沿与对话", "JMNORSTUV"),
   "drop": ["appendix_b.html"],
 },
 "interpretation-tradeoff": {
   "e": ("附录 E　案例、对话与借用边界", "AHIJM"),
   "f": ("附录 F　理论、对照与工具", "NOP"),
   "drop": ["appendix_b.html"],
 },
}

def split_sections(t):
    parts = re.split(r"(?m)(?=<h3)", t)
    head, secs = parts[0], parts[1:]
    return head, secs

for b, cfg in PLAN.items():
    src = f"{b}/source"
    e = io.open(os.path.join(src,"appendix_e.html"), encoding="utf-8").read()
    head, secs = split_sections(e)
    groups = {"e": [], "f": []}
    for s in secs:
        m = re.match(r"<h3[^>]*>\s*([A-Z])\.", s)
        key = m.group(1) if m else None
        if key and key in cfg["e"][1]:
            groups["e"].append(s)
        elif key and key in cfg["f"][1]:
            groups["f"].append(s)
        else:
            groups["e"].append(s)      # 无前缀者归“e”
    for k in ("e","f"):
        title = cfg[k][0]
        body = "\n\n".join(x.strip() for x in groups[k])
        txt = f'<h2 class="chapter">{title}</h2>\n<div class="box"><p>本附录汇集原附录 {cfg[k][1]} 各字母项下的条目；它们是证据与工具，不是论述。</p></div>\n\n' + body
        io.open(os.path.join(src, f"appendix_{k}.html"), "w", encoding="utf-8").write(txt)
    for d in cfg.get("drop", []):
        p = os.path.join(src, d)
        if os.path.exists(p):
            os.remove(p)
    # 更新 BACK
    bp = f"{b}/build_book.py"; t = io.open(bp, encoding="utf-8").read()
    t = re.sub(r'\s*\("[^"]*", "appendix_b\.html", "[^"]*"\),', "", t)
    items = re.findall(r'\("([^"]*)", "(appendix_[a-z])\.html", "([^"]*)"\)', t)
    order = "abcdef"
    for i, (old, letter, anchor) in enumerate(sorted(items, key=lambda x: x[1])):
        pass
    # 重排并重命名：按 a..f 顺序给标题字母
    def relabel(match):
        nonlocal_counter[0] += 1
        n = nonlocal_counter[0]
        title = match.group(1)
        title = re.sub(r"^附\s*录\s*[A-F]\s*[　 ]*", "", title)
        return f'("附录 {chr(64+n)}　{title}", "appendix_{chr(96+n)}.html", "{match.group(3)}")'
    nonlocal_counter = [0]
    t = re.sub(r'\("(附录[^"]*)", "(appendix_[a-f])\.html", "([^"]*)"\)', relabel, t)
    io.open(bp, "w", encoding="utf-8").write(t)
    # 同步改文件内标题字母
    for i, letter in enumerate("abcdef", 1):
        p = os.path.join(src, f"appendix_{letter}.html")
        if not os.path.exists(p): continue
        x = io.open(p, encoding="utf-8").read()
        x = re.sub(r'(<h2 class="chapter">)附\s*录\s*[A-F]\s*[−　 ]*', rf'\g<1>附录 {chr(64+i)}　', x, count=1)
        io.open(p, "w", encoding="utf-8").write(x)
    print(b, "→", [f"appendix_{c}.html" for c in "abcdef" if os.path.exists(os.path.join(src,f"appendix_{c}.html"))])

# -*- coding: utf-8 -*-
"""把 distinction-evolution 各章的 h3 按出现顺序重编为 N.1…N.k
（消除 b 后缀、倒序与重号），并同步：正文「第 X.Y 节」引用、锚点、parts.json 的 sections。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "distinction-evolution", "source")
files = sorted(f for f in os.listdir(SRC) if re.fullmatch(r"ch\d+\.html", f))

maps = {}          # (ch, old_suffix) -> new_suffix
new_titles = {}    # ch -> [section titles]
for f in files:
    ch = int(re.search(r"ch(\d+)", f).group(1))
    s = open(os.path.join(SRC, f), encoding="utf-8").read()
    heads = list(re.finditer(r'<h3([^>]*)>(.*?)</h3>', s, flags=re.S))
    k = 0
    titles = []
    out = []
    last = 0
    for m in heads:
        txt = re.sub("<[^>]+>", "", m.group(2)).strip()
        old = re.match(r"^\s*(\d+)\.(\d+)([a-z]?)", txt)
        k += 1
        if old:
            suf = f"{old.group(2)}{old.group(3)}"
            maps.setdefault(ch, {})[suf] = str(k)
            rest = txt[old.end():].lstrip("　 ").strip()
        else:
            rest = txt
        newtitle = f"{ch}.{k}　{rest}"
        titles.append(newtitle)
        out.append(s[last:m.start()] + f'<h3 id="sec{ch}-{k}">{newtitle}</h3>')
        last = m.end()
    out.append(s[last:])
    s = "".join(out)
    # 正文引用：第 X.Y[b] 节
    def rep(m):
        n, suf = int(m.group(1)), m.group(2)
        mp = maps.get(n, {})
        return f"第 {n}.{mp.get(suf, suf)} 节"
    s = re.sub(r"第\s*(\d+)\.(\d+[a-z]?)\s*节", rep, s)
    open(os.path.join(SRC, f), "w", encoding="utf-8").write(s)
    new_titles[ch] = titles

# parts.json：用新标题重建每章 sections
p = os.path.join(SRC, "parts.json")
d = json.load(open(p, encoding="utf-8"))
for part in d:
    for ch in part.get("chapters", []):
        no = int(ch["no"])
        if no in new_titles:
            ch["sections"] = new_titles[no]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("renumbered", len(files), "chapters")

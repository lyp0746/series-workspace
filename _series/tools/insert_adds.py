# -*- coding: utf-8 -*-
"""把 _series/content/*_adds.json 的补写小节插入对应章，编号接在最后一个编号节之后，
位置放在「本章小结」之前（没有则放在「本章参考文献」之前，再没有则追加）。"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS = ["capacity_adds.json", "interpretation_adds.json", "topup_adds.json", "topup2_adds.json", "topup3_adds.json"]


def insert(repo, fname, title, body):
    p = os.path.join(ROOT, repo, "source", fname)
    s = open(p, encoding="utf-8").read()
    if title in re.sub("<[^>]+>", "", s):
        print(f"skip (exists) {repo}/{fname}: {title}")
        return
    ch = int(re.search(r"ch(\d+)", fname).group(1))
    nums = [int(m.group(1)) for m in re.finditer(r'<h3[^>]*>\s*' + str(ch) + r'\.(\d+)', s)]
    k = (max(nums) + 1) if nums else 1
    head = f'<h3 id="sec{ch}-{k}">{ch}.{k}　{title}</h3>\n'
    block = head + body.strip() + "\n\n"
    # 插入点：本章小结 > 本章参考文献 > 末尾
    cand = None
    for pat in [rf'<h3[^>]*>\s*{ch}\.\d+[a-z]?\s*　[^<]*本章小结', r'<h3[^>]*>[^<]*本章小结',
                rf'<h3[^>]*>\s*{ch}\s*　本章参考文献', r'<h3[^>]*>[^<]*本章参考文献']:
        m = re.search(pat, s)
        if m:
            cand = m.start()
            break
    if cand is None:
        s = s.rstrip() + "\n\n" + block
    else:
        s = s[:cand] + block + s[cand:]
    open(p, "w", encoding="utf-8").write(s)
    print(f"{repo}/{fname}: inserted {ch}.{k} {title}")


for job in JOBS:
    data = json.load(open(os.path.join(ROOT, "_series", "content", job), encoding="utf-8"))
    for sec in data["sections"]:
        insert(sec["book"], sec["file"], sec["title"], sec["body"])

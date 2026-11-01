# -*- coding: utf-8 -*-
"""章末排序：把「本章小结」「一句话带走」移到章末（参考文献之前），并按顺序重编 h3。
只动编号与位置，不改文字。可重复运行。"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade",
         "entropy-spiral", "impossibility-triangle", "interpretation-tradeoff",
         "emergence-critical", "mind-forks", "hotspot-bills"]


def split_sections(s, ch):
    """切成 [prefix, (title, block), ..., refs] 结构。"""
    ref = re.search(rf'<h3[^>]*>\s*{ch}\s*　本章参考文献\s*</h3>', s)
    tail = ""
    if ref:
        tail = s[ref.start():]
        s = s[:ref.start()]
    heads = list(re.finditer(r'<h3([^>]*)>(.*?)</h3>', s, flags=re.S))
    if not heads:
        return s, [], tail
    prefix = s[:heads[0].start()]
    blocks = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(s)
        title = re.sub("<[^>]+>", "", m.group(2)).strip()
        blocks.append((title, s[m.start():end]))
    return prefix, blocks, tail


def renumber(title, ch, k):
    t = re.sub(rf'^\s*{ch}\.\d+[a-z]?\s*　', "", title).strip()
    t = re.sub(rf'^\s*{ch}\s*　', "", t).strip()
    return f"{ch}.{k}　{t}"


for b in BOOKS:
    changed = 0
    for f in sorted(glob.glob(os.path.join(ROOT, b, "source", "ch*.html"))):
        ch = int(re.search(r"ch(\d+)", f).group(1))
        s = open(f, encoding="utf-8").read()
        prefix, blocks, tail = split_sections(s, ch)
        if not blocks:
            continue
        # 章末装置：本章小结 / 一句话带走（保持顺序：小结 → 带走）
        end = [x for x in blocks if re.search(r"本章小结|一句话带走", x[0])]
        mid = [x for x in blocks if not re.search(r"本章小结|一句话带走", x[0])]
        if not end:
            continue
        end.sort(key=lambda x: 0 if "本章小结" in x[0] else 1)
        blocks = mid + end
        out = [prefix]
        k = 0
        for title, block in blocks:
            if re.match(rf'^\s*{ch}\.\d+[a-z]?\s*　', title) or re.match(rf'^\s*{ch}\s*　', title):
                k += 1
                new = renumber(title, ch, k)
                block = re.sub(r'<h3[^>]*>.*?</h3>',
                               f'<h3 id="sec{ch}-{k}">{new}</h3>', block, count=1, flags=re.S)
            out.append(block)
        s2 = "".join(out) + tail
        if s2 != s:
            open(f, "w", encoding="utf-8").write(s2)
            changed += 1
    # parts.json 同步
    pj = os.path.join(ROOT, b, "source", "parts.json")
    if os.path.exists(pj):
        d = json.load(open(pj, encoding="utf-8"))
        for part in d:
            for chd in part.get("chapters", []):
                f = os.path.join(ROOT, b, "source", chd["file"])
                ch = int(chd["no"])
                s = open(f, encoding="utf-8").read()
                secs = [re.sub("<[^>]+>", "", m).strip()
                        for m in re.findall(r"<h3[^>]*>(.*?)</h3>", s, flags=re.S)]
                keep = [x for x in secs if re.match(rf"^{ch}\.\d+[a-z]?　", x)]
                if any("本章参考文献" in x for x in secs):
                    keep.append(f"{ch}　本章参考文献")
                chd["sections"] = keep
        json.dump(d, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(b, "chapters reordered:", changed)

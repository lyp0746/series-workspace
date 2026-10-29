#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""终检修复：三处结构性错误 + 未编号小节。

1. entropy-spiral：parts.json 第六部分五条全指向 ch25（别名 bug）→ 4 章从书里消失；
2. emergence-critical：合并后残留 5 个旧文件，parts.json 有一条章号与文件不符；
3. hotspot-bills：第二部分重复挂了第 4、5 章（全书出现两次）；
4. 各书插入的关联领域小节没有 N.M 编号 → 统一补号，并重生成 parts.json 的 sections。
"""
import io, json, os, re, glob, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
         "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]

def h2(t):
    m = re.search(r'<h2 class="chapter">([^<]*)</h2>', t)
    return m.group(1) if m else ""

def h3s(t):
    return [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<h3[^>]*>([^<]*)</h3>", t)]

# ---------- 1. entropy
src = os.path.join(ROOT, "entropy-spiral", "source")
pj = os.path.join(src, "parts.json")
parts = json.load(io.open(pj, encoding="utf-8"))
new6 = []
for n in range(21, 26):
    f = f"ch{n:02d}.html"
    t = io.open(os.path.join(src, f), encoding="utf-8").read()
    new6.append({"no": str(n), "title": re.sub(r"^第\d+章　", "", h2(t)),
                 "file": f, "written": True, "sections": h3s(t)})
parts[5]["chapters"] = new6
json.dump(parts, io.open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("entropy: 第六部分修好", [c["no"] for c in parts[5]["chapters"]])

# ---------- 2. emergence：按内容重排 25 章
src = os.path.join(ROOT, "emergence-critical", "source")
files = {}
for f in glob.glob(os.path.join(src, "ch*.html")):
    n = int(re.findall(r"\d+", os.path.basename(f))[0])
    files[n] = io.open(f, encoding="utf-8").read()

MERGE = [(1, 2), (11, 12), (19, 20), (23, 24)]      # (25,26) 已并过
for i, j in MERGE:
    if i not in files or j not in files:
        continue
    tj = files[j]
    m = re.search(r'<h2 class="chapter">([^<]*)</h2>', tj)
    body = tj[m.end():]
    n_i = len(re.findall(r"<h3", files[i]))
    files[i] = files[i].rstrip() + f'\n\n<h3>{re.sub(r"^第\\d+章　","",m.group(1))}</h3>\n' + body
del files[26]                                        # 内容已在 ch25 里
ORDER = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 27, 28, 29, 30]
assert len(ORDER) == 25 and all(k in files for k in ORDER), [k for k in ORDER if k not in files]
# 清空旧文件
for f in glob.glob(os.path.join(src, "ch*.html")):
    os.remove(f)
NEW = {}
for idx, old in enumerate(ORDER, 1):
    t = files[old]
    t = re.sub(r'<h2 class="chapter">第\d+章', f'<h2 class="chapter">第{idx}章', t, count=1)
    # 节号 N.k → idx.k
    state = {"cnt": 0}
    def rep(mm):
        state["cnt"] += 1
        n = state["cnt"]
        txt = re.sub(r"^\s*\d+\.\d+\s*[　 ]*", "", mm.group(2)).strip()
        return f'<h3 id="sec{idx}-{n}">{idx}.{n}　{txt}</h3>'
    t = re.sub(r'<h3([^>]*)>([^<]*)</h3>', rep, t)
    NEW[idx] = t
    io.open(os.path.join(src, f"ch{idx:02d}.html"), "w", encoding="utf-8").write(t)
SPLIT = [4, 5, 5, 5, 3, 3]
TITLES = ["第一部分　问题、工具与做法", "第二部分　五个出口与形式化的地平线",
          "第三部分　立论：可验证单元与三条方向", "第四部分　方向、案例与反驳",
          "第五部分　推导：朗道、伊辛与网络", "第六部分　边界与可行域"]
parts, k = [], 0
for title, size in zip(TITLES, SPLIT):
    chs = []
    for idx in range(k + 1, k + size + 1):
        chs.append({"no": str(idx), "title": re.sub(r"^第\d+章　", "", h2(NEW[idx])),
                    "file": f"ch{idx:02d}.html", "written": True, "sections": h3s(NEW[idx])})
    parts.append({"part": title, "desc": "", "chapters": chs})
    k += size
json.dump(parts, io.open(os.path.join(src, "parts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("emergence: 30 文件 → 25 章", SPLIT)

# ---------- 3. hotspot 去重
src = os.path.join(ROOT, "hotspot-bills", "source")
pj = os.path.join(src, "parts.json")
parts = json.load(io.open(pj, encoding="utf-8"))
seen, total = set(), 0
for p in parts:
    keep = []
    for c in p["chapters"]:
        if c["file"] in seen:
            continue
        seen.add(c["file"]); keep.append(c); total += 1
    p["chapters"] = keep
json.dump(parts, io.open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("hotspot: 去重后", [len(p["chapters"]) for p in parts], "共", total)

# ---------- 4. 未编号 h3 补号 + 重生成 sections
for b in BOOKS:
    src = os.path.join(ROOT, b, "source")
    pj = os.path.join(src, "parts.json")
    parts = json.load(io.open(pj, encoding="utf-8"))
    fixed = 0
    for p in parts:
        for c in p["chapters"]:
            f = os.path.join(src, c["file"])
            if not os.path.exists(f):
                continue
            t = io.open(f, encoding="utf-8").read()
            heads = list(re.finditer(r'<h3([^>]*)>([^<]*)</h3>', t))
            nums = [int(re.match(r"^\s*(\d+)\.(\d+)", re.sub(r"<[^>]+>", "", m.group(2))).group(2))
                    for m in heads if re.match(r"^\s*\d+\.\d+", re.sub(r"<[^>]+>", "", m.group(2)))]
            nxt = max(nums) + 1 if nums else 1
            for m in reversed(heads):
                txt = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                if not txt or re.match(r"^\d+\.\d+", txt) or txt in ("本章小结", "本章参考文献"):
                    continue
                t = t[:m.start()] + f'<h3 id="sec{c["no"]}-{nxt}">{c["no"]}.{nxt}　{txt}</h3>' + t[m.end():]
                nxt += 1; fixed += 1
            if fixed:
                io.open(f, "w", encoding="utf-8").write(t)
            c["sections"] = h3s(io.open(f, encoding="utf-8").read())
    json.dump(parts, io.open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{b:24} 补号 {fixed} 处")

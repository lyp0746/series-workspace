#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""合并章节并整体重编号（保持 25 章）。

- 被并章（J）并入前一章（I）：正文接在后面，J 的原章标题降为 h3，它的各节再降一级编号；
- 全书按新顺序重编号 1..N，节号随之改为 k.1..k.m；
- 正文里的「第 N 章」「N.M 节」按映射回写；
- parts.json 重写（部分与章表一并更新）。

用法： python merge_chapters.py --book distinction-evolution [--apply]
"""
import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PLANS = {
    # 书 → [(i, j), ...]：第 j 章并入第 i 章
    "distinction-evolution": [(7, 8), (19, 20), (26, 27)],
    "emergence-critical": [(1, 2), (11, 12), (19, 20), (23, 24), (25, 26)],
}

# 合并后的部分划分（按合并前的章号；None 表示该号已被并入，跳过）
PARTS = {
    "distinction-evolution": [
        ("第一部分　问题与方法：统一值不值", [1, 2, 3]),
        ("第二部分　统一的等高线：四个现代样本", [4, 5, 6]),
        ("第三部分　生成：从区分到空间与结构", [7, 9, 10]),
        ("第四部分　结构：语言、形式与对称双线性", [11, 12, 13, 14]),
        ("第五部分　兑现：一个样本，全部证明", [15, 16, 17, 18]),
        ("第六部分　归并与边界", [19, 21, 22, 23, 24]),
        ("第七部分　作为语言规范：完整陈述与可信度", [25, 26, 28]),
    ],
    "emergence-critical": [
        ("第一部分　问题、工具与做法", [1, 3, 4, 5, 6]),
        ("第二部分　五个出口与形式化的地平线", [7, 8, 9, 10, 11]),
        ("第三部分　立论：可验证单元与三条方向", [13, 14, 15, 16, 17]),
        ("第四部分　对照、案例与反驳", [18, 21, 22, 19, 23]),
        ("第五部分　推导、边界与可行域", [25, 27, 28, 29, 30]),
    ],
}


def h2(t):
    return re.search(r'<h2 class="chapter">([^<]*)</h2>', t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    book = a.book
    src = os.path.join(ROOT, book, "source")
    plan = PLANS[book]
    merged_into = {j: i for i, j in plan}

    texts = {}
    for f in sorted(os.listdir(src)):
        if re.fullmatch(r"ch\d+\.html", f):
            texts[int(re.findall(r"\d+", f)[0])] = io.open(os.path.join(src, f), encoding="utf-8").read()

    # 1) 合并
    for i, j in plan:
        ti, tj = texts[i], texts[j]
        mt = h2(tj)
        title_j = mt.group(1) if mt else f"第{j}章"
        body_j = tj[mt.end():] if mt else tj
        # J 的 h3 → 先降为 h4 深度（保留文字），再在 I 的末尾加一个 h3 作为小节标题
        n_i = len(re.findall(r"<h3", ti))
        # 把 J 的 h3 编号清掉，改为纯标题文本，统一在下面重编
        body_j = re.sub(r'(<h3[^>]*>)\s*\d+\.\d+(?:\.\d+)?\s*[　 ]*', r"\1", body_j)
        ti = ti.rstrip() + f'\n\n<h3>{title_j.split("　", 1)[-1]}</h3>\n' + body_j
        texts[i] = ti
        del texts[j]

    # 2) 新顺序
    order = []
    for p in PARTS[book]:
        for no in p[1]:
            if no in texts:
                order.append(no)
    if len(order) != len(texts):
        print("顺序表漏章：", sorted(set(texts) - set(order)))

    # 3) 重编号：章号、节号、id、正文引用
    newno = {old: k + 1 for k, old in enumerate(order)}
    for j, i in merged_into.items():
        newno[j] = newno.get(i)
    out = {}
    for old_no in order:
        n = newno[old_no]
        t = texts[old_no]
        mt = h2(t)
        title = re.sub(r"^第\s*\d+\s*[章]?\s*[　 ]*", "", mt.group(1)) if mt else ""
        t = t[:mt.start()] + f'<h2 class="chapter">第{n}章　{title}</h2>' + t[mt.end():]
        # 节号
        subs = list(re.finditer(r"<h3([^>]*)>([^<]*)</h3>", t))
        cnt = 0
        secmap = {}
        for m in subs:
            cnt += 1
            old_sec = re.match(r"^\s*(\d+)\.(\d+)(?:\.(\d+))?", m.group(2))
            txt = re.sub(r"^\s*\d+\.\d+(?:\.\d+)?\s*[　 ]*", "", m.group(2)).strip()
            if old_sec:
                secmap.setdefault(old_sec.group(0).strip(), f"{n}.{cnt}")
            attrs = re.sub(r'id="[^"]*"', f'id="sec{n}-{cnt}"', m.group(1))
            t = t.replace(m.group(0), f"<h3{attrs}>{n}.{cnt}　{txt}</h3>", 1)
        # 正文里的旧节号引用
        for old_sec, new_sec in secmap.items():
            t = re.sub(rf"(?<![\d.]){re.escape(old_sec)}(?=\s*[节表图])", new_sec, t)
        out[n] = t

    # 4) 正文里的章引用：按内容映射
    for n, t in out.items():
        for old_no, new in newno.items():
            t = re.sub(rf"第\s*{old_no}\s*章", f"第{new}章", t)
        out[n] = t

    # 5) 落盘
    if not a.apply:
        print(f"{book}: 章 {len(texts)} → {len(out)}", [newno[o] for o in order])
        return 0
    for f in os.listdir(src):
        if re.fullmatch(r"ch\d+\.html", f):
            os.remove(os.path.join(src, f))
    for n, t in out.items():
        io.open(os.path.join(src, f"ch{n:02d}.html"), "w", encoding="utf-8").write(t)

    # 6) parts.json
    parts = []
    for title, nos in PARTS[book]:
        chs = []
        for no in nos:
            n = newno.get(no)
            if not n:
                continue
            t = out[n]
            mt = h2(t)
            secs = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<h3[^>]*>[^<]*</h3>", t)]
            chs.append({"no": str(n), "title": re.sub(r"^第\d+章　", "", mt.group(1)),
                        "file": f"ch{n:02d}.html", "written": True, "sections": secs})
        if chs:
            parts.append({"part": title, "desc": "", "chapters": chs})
    json.dump(parts, io.open(os.path.join(src, "parts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"{book}: 合并完成 → {len(out)} 章 / {len(parts)} 部分 "
          f"{[len(p['chapters']) for p in parts]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

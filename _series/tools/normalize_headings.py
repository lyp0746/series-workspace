#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统一章标题：`第N章　标题`（阿拉伯数字，无空格）。

现状有三种写法：`第 5 章`、`第5章`、`第二十章`，甚至 `第八部`（用"部"指章）。
TOC 生成器输出的是 `第5章`，正文必须与之一致。

只改第一章标题（`<h2 class="chapter">`），不动正文内的引用。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade", "entropy-spiral",
         "impossibility-triangle", "interpretation-tradeoff", "emergence-critical",
         "hotspot-bills", "mind-forks"]

CN = {c: i + 1 for i, c in enumerate("一二三四五六七八九")}
CN["十"] = 10


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    total = 0
    for ch in s:
        total = total * 10 + CN.get(ch, 0)
    return total


PAT = re.compile(r"^第\s*([0-9]+|[一二三四五六七八九十百]+)\s*[章部篇卷]\s*[　 \.]*(.*)$")


def main():
    changed = 0
    for b in BOOKS:
        src = os.path.join(ROOT, b, "source")
        if not os.path.isdir(src):
            continue
        for f in sorted(os.listdir(src)):
            m = re.fullmatch(r"ch(\d+)\.html", f)
            if not m:
                continue
            p = os.path.join(src, f)
            t = open(p, encoding="utf-8", newline="").read()
            crlf = "\r\n" in t
            t2 = t.replace("\r\n", "\n")
            mm = re.search(r'<h2 class="chapter">([^<]*)</h2>', t2)
            if not mm:
                print(f"  ! {b}/{f} 无 h2.chapter")
                continue
            raw = mm.group(1).strip()
            pm = PAT.match(raw)
            if not pm:
                print(f"  ? {b}/{f} 无法解析：{raw[:30]}")
                continue
            n = cn2int(pm.group(1))
            title = pm.group(2).strip("　 .")
            want = f"第{n}章　{title}"
            if raw == want:
                continue
            if n != int(m.group(1)):
                print(f"  ! {b}/{f} 标题号 {n} ≠ 文件名 {m.group(1)}，跳过")
                continue
            t2 = t2.replace(mm.group(0), f'<h2 class="chapter">{want}</h2>', 1)
            if crlf:
                t2 = t2.replace("\n", "\r\n")
            open(p, "w", encoding="utf-8", newline="").write(t2)
            changed += 1
            print(f"  {b}/{f}: 「{raw[:22]}」→「{want[:22]}」")
    print(f"共改 {changed} 章标题")
    return 0


if __name__ == "__main__":
    sys.exit(main())

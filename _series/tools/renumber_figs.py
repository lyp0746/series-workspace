#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""图/表号归一：按章内出现顺序重排“图 N.M / 表 N.M”，去掉字母补丁与重号。

用法：python _series/tools/renumber_figs.py <repo> [--write]
"""
from __future__ import annotations
import os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEF = re.compile(r"<b>(表|图)\s*([0-9A-Z]+)[.．]([0-9]+)([a-z]?)")


def read(p):
    return open(p, encoding="utf-8").read()


def main():
    repo = sys.argv[1]
    do = "--write" in sys.argv
    src = os.path.join(ROOT, repo, "source")
    chs = sorted(f for f in os.listdir(src) if re.fullmatch(r"ch\d+\.html", f))
    allmap = {}   # (kind, old) -> new
    plans = {}
    for f in chs:
        ch = int(re.search(r"\d+", f).group())
        t = read(os.path.join(src, f))
        defs = list(DEF.finditer(t))
        cnt = {"表": 0, "图": 0}
        plan = []
        local = {}
        for m in defs:
            kind = m.group(1)
            cnt[kind] += 1
            new = f"{ch}.{cnt[kind]}"
            old = f"{m.group(2)}.{m.group(3)}{m.group(4)}"
            plan.append((m, kind, old, new))
            local.setdefault((kind, old), new)
        allmap.update(local)
        plans[f] = (t, plan)
        # 报告重复/补丁号
        dup = [f"{k}{o}" for (k, o), n in Counter((k, o) for _, k, o, _ in plan).items() if n > 1]
        patch = [f"{k}{o}" for _, k, o, _ in plan if o[-1].isalpha()]
        if dup or patch:
            print(f"{f}: dup={sorted(set(dup))} patch={sorted(set(patch))}")
    if not do:
        return
    for f, (t, plan) in plans.items():
        for m, kind, old, new in sorted(plan, key=lambda x: -x[0].start()):
            t = t[:m.start()] + f"<b>{kind} {new}" + t[m.end():]
        # 引用替换（定义已是新号，剩下的旧号都在正文）
        def rep(m):
            kind, a, b, suf = m.group(1), m.group(2), m.group(3), m.group(4)
            old = f"{a}.{b}{suf}"
            return f"{kind} {allmap[(kind, old)]}" if (kind, old) in allmap else m.group(0)
        t = re.sub(r"(?<!<b>)(表|图)\s*([0-9A-Z]+)[.．]([0-9]+)([a-z]?)(?![0-9a-z.])", rep, t)
        open(os.path.join(src, f), "w", encoding="utf-8").write(t)
    print("written", repo)


if __name__ == "__main__":
    main()

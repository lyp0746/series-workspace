# -*- coding: utf-8 -*-
"""雾感自检（2026-11-14 第二版）：按《错位的时间》的六项指标量九本书。

指标与判据
----------
1. 节／章：范本 9.0；>12 视为"碎"。
2. 中位字／节：范本 594；<400 视为"词条化"。
3. <300 字的节占比：范本 19%；>40% 视为"碎"。
4. 数字／千字：见 `_series/tools/density.py`（阿拉伯 + 中文数词）。
5. 元话语／章："本章要/本章会/本章的路线/本节要/这一章我们要"。
6. 判据覆盖：含"若这条判据错了/这条要是错了/若这条判据/可反驳条件"的章数。

用法
----
    "$PY" _series/tools/fogcheck.py            # 九本书
    "$PY" _series/tools/fogcheck.py <repo>     # 单本，逐章列出最碎的 10 章
"""
import re
import sys
import html
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BOOKS = ["entropy-spiral", "capacity-cascade", "distinction-evolution", "impossibility-triangle",
         "interpretation-tradeoff", "emergence-critical", "knowledge-tradeoffs", "mind-forks", "hotspot-bills"]
TAG = re.compile(r"<[^>]+>")
META = re.compile(r"本章要|本章会|本章的路线|本节要|这一章我们要|本章将")
JUDGE = re.compile(r"若这条判据错了|这条要是错了|若这条判据|可反驳条件")


def plain(t):
    return html.unescape(TAG.sub(" ", t))


def chars(s):
    return len(re.sub(r"\s+", "", s))


def sections(t):
    parts = re.split(r"(<h3[^>]*>.*?</h3>)", t, flags=re.S)
    return [parts[i] + (parts[i + 1] if i + 1 < len(parts) else "") for i in range(1, len(parts), 2)]


def book(repo, detail=False):
    secs = []
    chaps = sorted((ROOT / repo / "source").glob("ch*.html"))
    meta = judge = 0
    all_text = []
    per = []
    for f in chaps:
        t = f.read_text(encoding="utf-8")
        ss = sections(t)
        secs += [chars(plain(s)) for s in ss]
        per.append((f.name, len(ss), int(statistics.median([chars(plain(s)) for s in ss]) if ss else 0)))
        if META.search(plain(t)):
            meta += 1
        if JUDGE.search(t):
            judge += 1
        all_text.append(plain(t))
    text = "".join(all_text)
    n = len(secs)
    row = dict(repo=repo, ch=len(chaps), sec=n, per_ch=n / max(1, len(chaps)),
               med=statistics.median(secs) if secs else 0,
               short=sum(1 for x in secs if x < 300) / max(1, n) * 100,
               chars=chars(text), meta=meta, judge=judge)
    if detail:
        for name, k, med in sorted(per, key=lambda x: (-x[1], x[2]))[:10]:
            print(f"  {name}  节 {k}  中位 {med}")
        return row
    return row


def main():
    if len(sys.argv) > 1:
        print(book(sys.argv[1], detail=True))
        return
    print(f"{'书':24s} {'章':>3} {'节':>4} {'节/章':>5} {'中位字/节':>8} {'<300%':>6} {'元话语章':>7} {'判据章':>6}")
    for b in BOOKS:
        r = book(b)
        print(f"{r['repo']:24s} {r['ch']:3d} {r['sec']:4d} {r['per_ch']:5.1f} {r['med']:8.0f} {r['short']:5.0f}% "
              f"{r['meta']:7d} {r['judge']:6d}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""数字密度尺子（2026-11-14 第五版）：同时计阿拉伯数字与中文数词。

为什么要有这一版
----------------
前四版只认阿拉伯数字（`\\d+`）。通俗读本大量使用「六个核心」「三十年」「三成」，
于是"数字密度"被人为压低——《只能选两样》因此被误判为 18.7／千字，
而它实际写满了量词与数词。第五版把中文数词计入，并把「数 + 量词」
（十年、五倍、三成）单独统计，避免把「一一」「第一」这类序数噪声算进去。

用法
----
    PY=".../python.exe"
    "$PY" _series/tools/density.py            # 24 件汇总
    "$PY" _series/tools/density.py <repo>     # 单件逐章

口径
----
- 阿拉伯数字：`\\d+(\\.\\d+)?`，每个数算一次。
- 中文数词：连续数词 + 可选量词（年/天/倍/成/项/章/层/人/家/种/次/周/月/秒/分/度/级/步/件/轮/代/页/条/节/个/两/半）。
- 密度 = 命中数 ÷ 去标签字符数 × 1000。
- 序数（第一、一一、一并）不计：中文数词必须跟量词，或本身是「半／两」+量词。

注意
----
密度只说明"有没有量"，不说明"量对不对"。每节至少一个数，是下限，不是目标。
"""
import re
import sys
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CN = "一二三四五六七八九十百千万亿半两"
NUM_A = re.compile(r"\d+(?:\.\d+)?")
NUM_C = re.compile(r"[" + CN + r"]+(?:个|年|天|周|月|次|倍|成|小时|分钟|秒|项|章|节|条|页|人|种|层|步|件|家|轮|代|级|度|分|两|半)")
TAG = re.compile(r"<[^>]+>")


def text_of(path):
    t = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    t = html.unescape(TAG.sub(" ", t))
    return re.sub(r"\s+", "", t)


def density(t):
    a = len(NUM_A.findall(t))
    c = len(NUM_C.findall(t))
    n = max(1, len(t))
    return a, c, (a + c) / n * 1000


def items():
    for line in (ROOT / "inventory.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        yield f[1]


def main():
    if len(sys.argv) > 1:
        repo = sys.argv[1]
        for f in sorted((ROOT / repo / "source").glob("ch*.html")):
            a, c, d = density(text_of(f))
            print(f"{f.name}\t阿拉伯 {a}\t中文 {c}\t合计 {d:.1f}/千字")
        return
    rows = []
    for repo in items():
        src = ROOT / repo / "source"
        files = sorted(src.glob("ch*.html")) or sorted(src.glob("paper.md"))
        if not files:
            continue
        A = C = N = 0
        for f in files:
            t = text_of(f)
            a, c, _ = density(t)
            A += a
            C += c
            N += len(t)
        rows.append((repo, A, C, (A + C) / max(1, N) * 1000, N))
    for repo, a, c, d, n in sorted(rows, key=lambda r: r[3]):
        print(f"{repo:24s} 阿拉伯 {a:5d}  中文 {c:5d}  合计 {d:6.1f}/千字  字符 {n}")


if __name__ == "__main__":
    main()

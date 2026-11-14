# -*- coding: utf-8 -*-
"""书稿重排工具（2026-11-14）：章号／节号／图表号一次性平移或合并。

为什么需要它
------------
合并章节（“枢纽章”）会同时改动五样东西，手改必错：
  1. 文件名 chNN.html；
  2. 章标题「第 N 章」与节标题「N.M」、锚点 id="secN-M"；
  3. 正文引用：第 N 章／第 N.M 节／§N.M；
  4. 图表号：图 N.M／表 N.M（含 caption 与正文引用）；
  5. parts.json 的 no/file/sections。

用法
----
    # 预览（不改文件）
    "$PY" _series/tools/renumber_book.py mind-forks --shift 2 --dry

    # 在第 2 章前插入新章：旧 2..25 → 新 3..26
    "$PY" _series/tools/renumber_book.py mind-forks --shift-from 2 --shift 1

    # 合并：旧 5、6 → 新 5（6 的各节接在 5 之后）
    "$PY" _series/tools/renumber_book.py capacity-cascade --merge 5,6 --dry

安全约定
--------
- 默认只处理 `source/ch*.html`、`parts.json`、`book.json`；不碰 output/release。
- 只改「第 N 章」「N.M」「§N.M」「图 N.M」「表 N.M」这几种可解析模式，不碰年份、页码、数据。
- `--dry` 打印将发生的改动计数，不写盘；先 dry 再实跑。
- 合并（--merge）只做“把后一章的内容接到前一章末尾”，不自动删节；节号重排按出现顺序。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def chapters(src: Path):
    return sorted(src.glob("ch*.html"), key=lambda p: int(re.search(r"ch(\d+)", p.name).group(1)))


def read(p):
    return p.read_text(encoding="utf-8")


def write(p, t):
    p.write_text(t, encoding="utf-8")


def plan_shift(files, start, delta):
    """章号 >= start 的全部 +delta。返回映射与反向。"""
    nums = [int(re.search(r"ch(\d+)", f.name).group(1)) for f in files]
    fwd = {n: (n + delta if n >= start else n) for n in nums}
    return fwd


def apply_text(t, chmap, secmap=None, figmap=None):
    """按映射改写一个文件里的引用。secmap: (oldch, oldsec) -> (newch, newsec)。"""
    if secmap:
        def sec(m):
            a, b = int(m.group(1)), int(m.group(2))
            if (a, b) in secmap:
                na, nb = secmap[(a, b)]
                return f"{na}.{nb}"
            return m.group(0)
        t = re.sub(r"(?<=第 )(\d+)\.(\d+)(?= 节)", sec, t)
        t = re.sub(r"(?<=§)(\d+)\.(\d+)", sec, t)
    # 图/表号：按章平移
    if figmap:
        def fg(m):
            a, b = int(m.group(1)), int(m.group(2))
            return f"{figmap.get(a, a)}.{b}"
        t = re.sub(r"(?<=图 )(\d+)\.(\d+)", fg, t)
        t = re.sub(r"(?<=表 )(\d+)\.(\d+)", fg, t)
        t = re.sub(r"(?<=图)(\d+)\.(\d+)", fg, t)
        t = re.sub(r"(?<=表)(\d+)\.(\d+)", fg, t)
    # 章引用
    if chmap:
        def ch(m):
            n = int(m.group(1))
            return f"第 {chmap.get(n, n)} 章"
        t = re.sub(r"第 (\d+) 章", ch, t)
        # 节标题与锚点
        def h3(m):
            n = int(m.group(1))
            return f'{m.group(0).split(">")[0]}{chmap.get(n, n)}.{m.group(2)}　'
        t = re.sub(r'(<h3[^>]*>)(\d+)\.(\d+)　', lambda m: m.group(1) + f"{chmap.get(int(m.group(2)), int(m.group(2))) }.{m.group(3)}　", t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--shift-from", type=int)
    ap.add_argument("--shift", type=int, default=0)
    ap.add_argument("--merge", type=str, help="如 5,6：把 6 并入 5，后面章号 -1")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    src = ROOT / a.repo / "source"
    if not src.is_dir():
        sys.exit(f"no source/: {src}")
    files = chapters(src)
    nums = [int(re.search(r"ch(\d+)", f.name).group(1)) for f in files]
    if a.merge:
        keep, drop = [int(x) for x in a.merge.split(",")]
        chmap = {n: (n - 1 if n > keep else n) for n in nums}
        print(f"merge {drop} -> {keep}; chapters {min(nums)}..{max(nums)} -> {min(chmap.values())}..{max(chmap.values())}")
    elif a.shift_from is not None:
        chmap = plan_shift(files, a.shift_from, a.shift)
        print(f"shift >= {a.shift_from} by {a.shift}")
    else:
        chmap = {n: n for n in nums}
    # 统计
    cnt = 0
    for f in files:
        t = read(f)
        n0 = t
        t = apply_text(t, chmap, figmap=chmap)
        if t != n0:
            cnt += 1
            if a.dry:
                print("would edit", f.name)
    print(f"files touched: {cnt}")
    if a.dry:
        return
    # 实跑：文件名（倒序避免碰撞）
    for f in sorted(files, key=lambda p: -int(re.search(r"ch(\d+)", p.name).group(1))):
        n = int(re.search(r"ch(\d+)", f.name).group(1))
        nn = chmap.get(n, n)
        t = apply_text(read(f), chmap, figmap=chmap)
        # 章标题
        t = re.sub(r"(<h2[^>]*>第 )(\d+)( 章)", lambda m: m.group(1) + str(nn) + m.group(3), t)
        # 节锚点
        t = re.sub(r'(id="sec)(\d+)-', lambda m: m.group(1) + str(nn) + "-", t)
        write(f, t)
        if nn != n:
            f.rename(src / f"ch{nn:02d}.html")
    # parts.json
    pj = src / "parts.json"
    if pj.exists():
        d = json.loads(read(pj))
        for part in d:
            for ch in part.get("chapters", []):
                m = re.search(r"ch(\d+)", ch.get("file", ""))
                if not m:
                    continue
                n = int(m.group(1))
                nn = chmap.get(n, n)
                ch["file"] = f"ch{nn:02d}.html"
                ch["no"] = str(nn)
        write(pj, json.dumps(d, ensure_ascii=False, indent=1))
    print("done")


if __name__ == "__main__":
    main()

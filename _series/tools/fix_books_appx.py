#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""书：附录按类归并（spec v2 §4）——不是"删掉附录"，是"把散落的附录归成六件"。

九个书仓共 111 个附录，最差一本 28 个。归并规则按**性质**而不是按顺序：

    A 形式化与证明     数学、定理、公理、形式化
    B 数据与案例       案例、数据、表、编码、指标、年表、坐标
    C 协议与稳健性     协议、复现、稳健、敏感性、检验、测量
    D 可证伪登记簿     登记（唯一必须保留的 append-only 证据）
    E 工具与清单       工具、手册、模板、工作表、卡片、议题、路线图、检查表
    F 增补             上游、前沿、演化、哲学、对话、对照、失败、边界
    参考文献、术语表   移出附录序列（不进字母）

同类多件合并为一件：保留第一件的文件，其余以 `h3.appx-sub` 追加，内容一字不删。
F 是**待迁入正文的暂存区**——下一轮按 §5.5 的映射把它们写成章节。

用法： python fix_books_appx.py [--apply] [--book X]
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade", "entropy-spiral",
         "impossibility-triangle", "interpretation-tradeoff", "emergence-critical",
         "hotspot-bills", "mind-forks"]

BUCKETS = [
    ("A", "形式化与证明", ("形式化", "数学", "证明", "定理", "公理", "最小数学")),
    ("B", "数据与案例", ("案例", "数据", "总表", "表", "编码", "指标", "年表", "坐标", "数字", "矩阵")),
    ("C", "协议与稳健性", ("协议", "复现", "稳健", "敏感性", "检验", "测量", "测度", "校准")),
    ("D", "可证伪登记簿", ("登记",)),
    ("E", "工具与清单", ("工具", "手册", "模板", "工作表", "卡片", "议题", "路线图", "用法", "练习", "检查", "清单", "导读")),
]
F_NAME = "增补：上游、边界与对话"
OUT_SEQ = (("参考文献", re.compile(r"参考文献")), ("术语表", re.compile(r"术语表|术语与符号")))


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def strip_h2(h):
    return re.sub(r"^附\s*录\s*[A-Z]{1,2}\s*[　 ]*", "", h)


def bucket_of(title):
    t = strip_h2(title)
    for letter, name, kws in BUCKETS:
        if any(k in t for k in kws):
            return letter, name
    return "F", F_NAME


def parse_back(t):
    m = re.search(r"BACK = \[(.*?)\n\]", t, re.S)
    if not m:
        return None
    return re.findall(r'\(\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)', m.group(1))


def rewrite_back(t, items):
    body = "".join(f'        ("{a}", "{b}", "{c}"),\n' for a, b, c in items)
    return re.sub(r"BACK = \[.*?\n\]", "BACK = [\n" + body.rstrip("\n") + "\n]", t, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--book")
    a = ap.parse_args()
    for b in ([a.book] if a.book else BOOKS):
        bp = os.path.join(ROOT, b, "build_book.py")
        src = os.path.join(ROOT, b, "source")
        if not os.path.exists(bp):
            continue
        t = open(bp, encoding="utf-8").read()
        items = parse_back(t)
        if not items:
            print(f"{b}: 无法解析 BACK")
            continue
        apx = [x for x in items if x[1].startswith("appendix")]
        if not apx:
            print(f"{b}: 无附录")
            continue

        groups = {}
        out_seq = []
        for title, f, anchor in apx:
            for nm, pat in OUT_SEQ:
                if pat.search(title):
                    out_seq.append((nm, f, anchor))
                    break
            else:
                letter, name = bucket_of(title)
                groups.setdefault(letter, []).append((title, f, anchor))

        order = [l for l, _, _ in BUCKETS if l in groups]
        if "F" in groups:
            order.append("F")
        print(f"=== {b}: {len(apx)} 附录 → {len(order)} 件 + {len(out_seq)} 出序列")
        for l in order:
            g = groups[l]
            nm = dict((x[0], x[1]) for x in [(q[0], q[1]) for q in BUCKETS])
            name = dict((q[0], q[1]) for q in BUCKETS).get(l, F_NAME)
            tot = sum(cn(open(os.path.join(src, f), encoding="utf-8").read()) for _, f, _ in g)
            print(f"    {l} {name[:18]:20} {len(g):2} 件 {tot:6} 字  ← " +
                  " / ".join(strip_h2(x[0])[:12] for x in g[:6]) + ("…" if len(g) > 6 else ""))
        if not a.apply:
            continue

        # 0) 正文里的「附录 X」引用按旧→新字母重映射（合并后仍然指得到）
        refmap = {}
        for title, f, anchor in items:
            if not f.startswith("appendix"):
                continue
            p0 = os.path.join(src, f)
            h = open(p0, encoding="utf-8", newline="").read()
            m0 = re.search(r'<h2 class="chapter">([^<]*)</h2>', h)
            old = None
            if m0:
                mm = re.match(r"^附\s*录\s*([A-Z]{1,2})", m0.group(1))
                if mm:
                    old = mm.group(1)
            if not old:
                mm = re.match(r"appendix_([a-z]{1,2})", f)
                if mm:
                    old = mm.group(1).upper()
            if not old:
                continue
            for nm, pat in OUT_SEQ:
                if pat.search(title):
                    refmap[old] = nm
                    break
            else:
                refmap[old] = dict((x[0], x[1]) for x in [(q[0], q[1]) for q in BUCKETS]).get(
                    bucket_of(title)[0], F_NAME)
        changed = 0
        for fn in sorted(os.listdir(src)):
            if not fn.endswith(".html"):
                continue
            p0 = os.path.join(src, fn)
            h = open(p0, encoding="utf-8", newline="").read()
            orig = h
            for old in sorted(refmap, key=len, reverse=True):
                new = refmap[old]
                if new in ("参考文献", "术语表"):
                    h = re.sub(rf"附\s*录\s*{old}(?![A-Z0-9])", new, h)
                else:
                    h = re.sub(rf"附\s*录\s*{old}(?![A-Z0-9])", "附录 " + new, h)
            if h != orig:
                open(p0, "w", encoding="utf-8", newline="").write(h)
                changed += 1
        print(f"    引用重映射：{len(refmap)} 个字母，改动 {changed} 个文件")

        # 1) 出序列：改标题
        seq_items = []
        for nm, f, anchor in out_seq:
            p = os.path.join(src, f)
            h = open(p, encoding="utf-8", newline="").read()
            m = re.search(r'<h2 class="chapter">([^<]*)</h2>', h)
            if m:
                h = h.replace(m.group(0), f'<h2 class="chapter">{nm}</h2>', 1)
                open(p, "w", encoding="utf-8", newline="").write(h)
            seq_items.append((nm, f, anchor))

        # 2) 每类合并：第一件为宿主，其余降为 h3 追加
        seq_apx = []
        for i, l in enumerate(order):
            g = groups[l]
            host_title, host_f, host_anchor = g[0]
            host_p = os.path.join(src, host_f)
            body = open(host_p, encoding="utf-8", newline="").read()
            m = re.search(r'<h2 class="chapter">([^<]*)</h2>', body)
            name = dict((q[0], q[1]) for q in BUCKETS).get(l, F_NAME)
            head = f'<h2 class="chapter">附录 {chr(65 + i)}　{name}</h2>'
            body = body.replace(m.group(0), head, 1) if m else head + "\n" + body
            for title, f, _ in g[1:]:
                sub_p = os.path.join(src, f)
                sub = open(sub_p, encoding="utf-8", newline="").read()
                sm = re.search(r'<h2 class="chapter">([^<]*)</h2>', sub)
                if sm:
                    sub = sub.replace(sm.group(0), f'<h3 class="appx-sub">{strip_h2(sm.group(1))}</h3>', 1)
                body = body.rstrip() + "\n\n" + sub
                os.remove(sub_p)
            open(host_p, "w", encoding="utf-8", newline="").write(body)
            seq_apx.append((f"附录 {chr(65 + i)}　{name}", host_f, host_anchor))

        # 3) 重组 BACK
        non = [(x, f, an) for x, f, an in items if not f.startswith("appendix")]
        new_back = non + seq_items + seq_apx
        open(bp, "w", encoding="utf-8").write(rewrite_back(t, new_back))
        print(f"    写回 BACK：{len(new_back)} 项（附录 {len(seq_apx)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

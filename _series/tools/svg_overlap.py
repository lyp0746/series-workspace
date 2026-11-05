#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SVG 元素位置检查：文字包围盒是否互相重叠、是否越出 viewBox。

不做逐像素渲染，只用 x/y、font-size、text-anchor 估算轴对齐包围盒。
用法：python _series/tools/svg_overlap.py [repo ...]
"""
from __future__ import annotations
import glob, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def css_sizes(s):
    out = {}
    for m in re.finditer(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}", s):
        fm = re.search(r"font-size\s*:\s*([\d.]+)px", m.group(2))
        if fm:
            out[m.group(1)] = float(fm.group(1))
    return out


def text_width(txt, fs):
    if txt.strip().startswith("$") or "\\" in txt:
        t = txt.replace("$", "")
        for cmd in ["mathdefault", "lambda", "delta", "omega", "infty", "cdot", "sqrt",
                    "mathrm", "mathbf", "text", "left", "right", "sum", "int", "pi",
                    "rho", "beta", "alpha", "gamma", "mu", "sigma", "ln", "log"]:
            t = t.replace("\\" + cmd, "x")
        t = re.sub(r"\\[a-zA-Z]+", "", t)
        t = t.replace("{", "").replace("}", "").replace("^", "").replace("_", "")
        return max(fs * 0.5, len(t) * fs * 0.55)
    w = 0.0
    for ch in txt:
        if CJK.match(ch):
            w += fs
        elif ch == " ":
            w += fs * 0.30
        else:
            w += fs * 0.56
    return w


def parse_texts(s, default_fs=12.0):
    sizes = css_sizes(s)
    out = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", s, re.S):
        attr, body = m.group(1), m.group(2)
        body = re.sub(r"<[^>]+>", "", body)
        body = (body.replace("&amp;", "&").replace("&lt;", "<")
                    .replace("&gt;", ">").replace("&nbsp;", " "))
        if not body.strip():
            continue
        xm = re.search(r'\bx="([-\d.]+)"', attr)
        ym = re.search(r'\by="([-\d.]+)"', attr)
        if not xm or not ym:
            continue
        x, y = float(xm.group(1)), float(ym.group(1))
        fs = None
        fm = re.search(r"font-size\s*:\s*([\d.]+)px", attr)
        if fm:
            fs = float(fm.group(1))
        if fs is None:
            cm = re.search(r'class="([^"]+)"', attr)
            if cm:
                for c in cm.group(1).split():
                    if c in sizes:
                        fs = sizes[c]
                        break
        if fs is None:
            fs = default_fs
        anchor = "start"
        am = re.search(r'text-anchor="([^"]+)"', attr)
        if am:
            anchor = am.group(1)
        w = text_width(body, fs)
        rot = re.search(r'transform="rotate\(\s*(-?[\d.]+)[\s,]+([-\d.]+)[\s,]+([-\d.]+)\s*\)"', attr)
        if rot and abs(abs(float(rot.group(1))) - 90) < 5:
            # 旋转 90°：水平宽度变成字高，垂直高度变成文本长度
            h = fs * 1.0
            if anchor == "middle":
                y0 = y - w / 2
            elif anchor == "end":
                y0 = y - w
            else:
                y0 = y
            box = (x - h * 0.78, y0, x + h * 0.22, y0 + w)
            out.append({"text": body.strip(), "box": box, "fs": fs})
            continue
        if anchor == "middle":
            x0 = x - w / 2
        elif anchor == "end":
            x0 = x - w
        else:
            x0 = x
        # 基线之上约 0.78em，之下 0.22em
        box = (x0, y - fs * 0.78, x0 + w, y + fs * 0.22)
        out.append({"text": body.strip(), "box": box, "fs": fs})
    # matplotlib：文字转路径，用 <g id="text_N"> 的注释与 translate/scale 估算
    for m in re.finditer(r'<g id="text_\d+">\s*<!--\s*(.*?)\s*-->\s*<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+) ([-\d.]+)\)">', s, re.S):
        txt, x, y = m.group(1), float(m.group(2)), float(m.group(3))
        sy = abs(float(m.group(5)))
        if "-->" in txt or len(txt) > 80:
            continue
        fs = sy * 100
        w = text_width(txt, fs)
        box = (x, y - fs * 0.78, x + w, y + fs * 0.22)
        out.append({"text": txt, "box": box, "fs": fs})
    return out


def overlap(a, b):
    x0 = max(a[0], b[0]); x1 = min(a[2], b[2])
    y0 = max(a[1], b[1]); y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / max(1e-9, min(aa, bb))


def check(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', s)
    if not vb:
        return []
    vx, vy, vw, vh = map(float, vb.groups())
    texts = parse_texts(s)
    issues = []
    for t in texts:
        b = t["box"]
        if b[0] < vx - 1 or b[1] < vy - 1 or b[2] > vx + vw + 1 or b[3] > vy + vh + 1:
            issues.append(("out", t["text"], tuple(round(v, 1) for v in b)))
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            r = overlap(texts[i]["box"], texts[j]["box"])
            if r > 0.12:
                issues.append((f"overlap {r:.0%}", texts[i]["text"], texts[j]["text"]))
    return issues


def main():
    repos = sys.argv[1:]
    if not repos:
        repos = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d, "assets", "svg"))]
    total = 0
    for r in repos:
        files = sorted(glob.glob(os.path.join(ROOT, r, "assets", "svg", "*.svg")))
        bad = []
        for f in files:
            iss = check(f)
            if iss:
                bad.append((f, iss))
        print(f"== {r}: {len(files)} SVG, {len(bad)} with issues")
        for f, iss in bad:
            print("  ", os.path.basename(f))
            for it in iss[:6]:
                print("     ", it)
        total += sum(len(i) for _, i in bad)
    print("total issues", total)


if __name__ == "__main__":
    main()

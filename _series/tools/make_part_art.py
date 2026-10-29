#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为每本书的每一部分生成一页扉页插图（SVG）。

设计语言（与系列封面一致）：暗色渐变 #0e1117 → #151a23 → #0b0e14，顶部金线 #b8862f，
细金线母题（每本书一种），大号轮郭数字（序号），大量留白。
文字不写进 SVG（保持可选中、可检索），只画图形与数字。
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade", "entropy-spiral",
         "impossibility-triangle", "interpretation-tradeoff", "emergence-critical",
         "hotspot-bills", "mind-forks"]

GOLD = "#b8862f"
W, H = 794, 1123


def frame():
    return (f'<rect x="28" y="28" width="{W-56}" height="{H-56}" fill="none" '
            f'stroke="{GOLD}" stroke-opacity="0.28" stroke-width="0.8"/>'
            f'<line x1="28" y1="96" x2="{W-28}" y2="96" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.4"/>')


def numeral(n, total):
    """右下角巨型序号（轮廓数字），以及右下的一段进度刻度。"""
    x, y = W - 150, H - 96
    ticks = "".join(
        f'<line x1="{W-28-14*(total-i)}" y1="{H-64}" x2="{W-28-14*(total-i)}" y2="{H-64-(14 if i < n else 6)}" '
        f'stroke="{GOLD}" stroke-opacity="{0.85 if i < n else 0.3}" stroke-width="1"/>'
        for i in range(total))
    return (f'<text x="{x}" y="{y}" font-family="Georgia, Times New Roman, serif" font-size="210" '
            f'fill="none" stroke="{GOLD}" stroke-opacity="0.34" stroke-width="1.2" '
            f'text-anchor="end">{n:02d}</text>' + ticks)


def motif(kind):
    g = f'stroke="{GOLD}" fill="none" stroke-width="1" stroke-opacity="0.55"'
    if kind == "six":
        out = []
        for i in range(6):
            import math
            a = math.pi / 3 * i
            cx, cy = W / 2 + 150 * math.cos(a), 430 + 150 * math.sin(a)
            out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="46" {g}/>')
            out.append(f'<line x1="{W/2:.0f}" y1="430" x2="{cx:.0f}" y2="{cy:.0f}" {g} stroke-opacity="0.25"/>')
        return "".join(out)
    if kind == "lattice":
        out = []
        for i in range(9):
            x = 120 + i * 64
            out.append(f'<line x1="{x}" y1="210" x2="{x}" y2="640" {g} stroke-opacity="{0.12 if i==4 else 0.4}"/>')
        for j in range(7):
            y = 230 + j * 62
            out.append(f'<line x1="110" y1="{y}" x2="{W-110}" y2="{y}" {g} stroke-opacity="{0.12 if j==3 else 0.35}"/>')
        return "".join(out)
    if kind == "cascade":
        out = []
        for i in range(7):
            w = 520 - i * 66
            out.append(f'<rect x="{W/2-w/2:.0f}" y="{228+i*58}" width="{w}" height="26" {g} stroke-opacity="{0.5-i*0.05:.2f}" rx="2"/>')
        return "".join(out)
    if kind == "spiral":
        pts = []
        import math
        for k in range(0, 520, 4):
            r = 8 + k * 0.29
            a = k / 22.0
            pts.append(f"{W/2 + r*math.cos(a):.0f},{430 + r*math.sin(a) * 0.92:.0f}")
        return f'<polyline points="{" ".join(pts)}" {g}/>'
    if kind == "triangle":
        pts = f"{W/2},220 {W/2+230},620 {W/2-230},620"
        return (f'<polygon points="{pts}" {g} stroke-opacity="0.6"/>'
                f'<line x1="{W/2}" y1="220" x2="{W/2}" y2="470" {g} stroke-opacity="0.3" stroke-dasharray="4 7"/>'
                f'<circle cx="{W/2}" cy="220" r="5" fill="{GOLD}" fill-opacity="0.8"/>'
                f'<circle cx="{W/2+230}" cy="620" r="5" fill="{GOLD}" fill-opacity="0.8"/>'
                f'<circle cx="{W/2-230}" cy="620" r="5" fill="none" stroke="{GOLD}" stroke-opacity="0.8"/>')
    if kind == "layers":
        out = []
        for i in range(5):
            ang = -12 + i * 6
            out.append(f'<g transform="rotate({ang} {W/2} 430)">'
                       f'<rect x="{W/2-250+i*10}" y="{260+i*26}" width="500" height="300" {g} '
                       f'stroke-opacity="{0.18+i*0.08:.2f}" rx="4"/></g>')
        return "".join(out)
    if kind == "sigmoid":
        pts = []
        import math
        for i in range(0, 121):
            x = 120 + i * 4.6
            y = 620 - 340 / (1 + math.exp(-(i - 58) / 9.0))
            pts.append(f"{x:.0f},{y:.0f}")
        return (f'<polyline points="{" ".join(pts)}" {g}/>'
                f'<line x1="120" y1="430" x2="{W-110}" y2="430" {g} stroke-opacity="0.28" stroke-dasharray="5 8"/>')
    if kind == "columns":
        hs = [90, 140, 210, 320, 260, 380, 300, 200, 150, 110]
        out = [f'<line x1="120" y1="640" x2="{W-110}" y2="640" {g} stroke-opacity="0.4"/>']
        for i, h in enumerate(hs):
            out.append(f'<rect x="{132+i*46}" y="{640-h}" width="26" height="{h}" {g} stroke-opacity="0.45"/>')
        return "".join(out)
    if kind == "fork":
        out = []
        for i, dx in enumerate((-190, -95, 0, 95, 190)):
            out.append(f'<path d="M{W/2} 640 C{W/2} 520 {W/2+dx} 470 {W/2+dx} 250" {g} stroke-opacity="{0.25+0.1*i:.2f}"/>')
        return "".join(out)
    return ""


KIND = {
    "knowledge-tradeoffs": "six",
    "distinction-evolution": "lattice",
    "capacity-cascade": "cascade",
    "entropy-spiral": "spiral",
    "impossibility-triangle": "triangle",
    "interpretation-tradeoff": "layers",
    "emergence-critical": "sigmoid",
    "hotspot-bills": "columns",
    "mind-forks": "fork",
}


def svg(kind, n, total):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="#0e1117"/><stop offset="0.55" stop-color="#151a23"/><stop offset="1" stop-color="#0b0e14"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.36" r="0.6">
    <stop offset="0" stop-color="{GOLD}" stop-opacity="0.10"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{frame()}
{motif(kind)}
{numeral(n, total)}
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    a = ap.parse_args()
    for b in ([a.book] if a.book else BOOKS):
        pj = os.path.join(ROOT, b, "source", "parts.json")
        if not os.path.exists(pj):
            continue
        parts = json.load(open(pj, encoding="utf-8"))
        outdir = os.path.join(ROOT, b, "assets", "svg")
        os.makedirs(outdir, exist_ok=True)
        n = 0
        for i, p in enumerate(parts, 1):
            f = os.path.join(outdir, f"part-{i:02d}.svg")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(svg(KIND[b], i, len(parts)))
            n += 1
        print(f"{b:24} {n} 张扉页插图（{KIND[b]}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

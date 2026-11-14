# -*- coding: utf-8 -*-
"""figstyle.py —— 全系列 PNG 图件的统一风格（2026-11 起）。

目标：所有论文里的 PNG 图"不重叠、留白合理、字够大、无色盲陷阱、无重复标题"。

用法（在各仓的 make_figures.py 顶部）：

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../_series/tools"))
    from figstyle import setup, savefig, PALETTE, GRID

    setup()                       # 一次性：字体、字号、线宽、配色、negative sign
    ...
    savefig("assets/figures/fig03.png")   # 300 dpi、去掉多余边、不写标题

约定（写进 review 里，改图时逐条核对）：
1. **图里不写标题**。标题由书稿的 `图 N.M　…` 题注承担；图内再写一遍就是重复。
2. **字号下限**：正文 10pt 时，图内最小字号 ≥ 7pt（本模块默认 8）。
3. **不重叠**：用 `constrained_layout`，不要手工 `tight_layout` 叠加；多子图统一 `sharex/sharey`。
4. **色彩**：只用 PALETTE（Okabe–Ito 色盲友好 8 色），不上渐变、不上阴影、不用纯红/纯绿对比。
5. **线**：1.6pt；网格 0.5pt 浅灰；坐标轴只留左、下两条（去掉上右框）。
6. **导出**：300 dpi、`bbox_inches="tight"`、白底、无透明。
7. **中文**：字体链 `Microsoft YaHei → SimHei → Noto Sans CJK SC → DejaVu Sans`。
8. **每张图必须能回答一个问题**：如果去掉标题后读者看不出"这张图在比什么"，那不是风格问题，是图本身没设计好。
"""

import os

# Okabe–Ito：色盲友好、印刷安全
PALETTE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#F0E442",
    "grey": "#595959",
    "black": "#000000",
}
CYCLE = [PALETTE[k] for k in ("blue", "orange", "green", "vermillion", "purple", "sky", "grey")]
GRID = dict(color="#DDDDDD", linewidth=0.5, alpha=0.9)


def setup(fontsize=8.5, figsize=(6.4, 3.6)):
    """统一 rcParams。必须在画图之前调用一次。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": fontsize,
        "axes.labelsize": fontsize,
        "axes.titlesize": fontsize + 1,      # 图内标题尽量不用；保留给子图 (a)(b) 标签
        "xtick.labelsize": fontsize - 0.5,
        "ytick.labelsize": fontsize - 0.5,
        "legend.fontsize": fontsize - 0.5,
        "figure.figsize": figsize,
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "lines.linewidth": 1.6,
        "lines.markersize": 4,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.linewidth": 0.5,
        "grid.color": "#DDDDDD",
        "grid.alpha": 0.9,
        "axes.prop_cycle": __import__("cycler").cycler(color=CYCLE),
        "legend.frameon": False,
        "axes.axisbelow": True,
    })
    plt.rcParams["figure.constrained_layout.use"] = True
    return plt


def savefig(path, **kw):
    """300 dpi、紧边、白底。传 title= 会被忽略（图内不写标题）。"""
    import matplotlib.pyplot as plt
    kw.pop("title", None)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        bad = check_overlaps(plt.gcf())
    except Exception:
        bad = []
    if bad:
        print("  ! overlap", os.path.basename(str(path)), [(a, b) for a, b, _ in bad][:4])
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="white", **kw)
    plt.close()
    print("wrote", path)


def check_overlaps(fig=None, thresh=2.0):
    """返回互相重叠的文本对（像素面积 > thresh）。用于目检之前的机器自检。"""
    import matplotlib.pyplot as plt
    fig = fig or plt.gcf()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items, seen = [], set()
    for ax in fig.axes:
        texts = list(ax.texts) + [ax.title, ax.xaxis.label, ax.yaxis.label] + list(fig.texts)
        texts += ax.get_xticklabels() + ax.get_yticklabels()
        if ax.get_legend():
            texts += ax.get_legend().get_texts()
        for t in texts:
            if id(t) in seen or not t.get_visible() or not t.get_text().strip():
                continue
            if abs(t.get_rotation()) % 180 > 1:   # 旋转标签的外接框会假重叠
                continue
            seen.add(id(t))
            try:
                bb = t.get_window_extent(renderer=r)
            except Exception:
                continue
            if bb.width <= 0 or bb.height <= 0:
                continue
            key = (t.get_text(), round(bb.x0, 1), round(bb.y0, 1))
            if key in seen:
                continue
            seen.add(key)
            items.append((t.get_text()[:18], bb))
    bad = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][0] == items[j][0]:
                continue
            a, b = items[i][1], items[j][1]
            w = min(a.x1, b.x1) - max(a.x0, b.x0)
            h = min(a.y1, b.y1) - max(a.y0, b.y0)
            if w > thresh and h > thresh:
                bad.append((items[i][0], items[j][0], round(w * h)))
    return bad


def seqmap(name, light="#FFFFFF"):
    """单色序列 colormap：白 → PALETTE[name]。替代 "Blues"/"Reds"/"Oranges" 等默认色图，
    保证热图也只用 Okabe–Ito 的一族色相。"""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("seq_" + name, [light, PALETTE[name]])

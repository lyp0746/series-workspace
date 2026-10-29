# -*- coding: utf-8 -*-
"""长沙府驿道 GIS 试点：节点、分段距离、最近邻与网络图。

输入：stations.csv（28 个节点，含经纬度与置信度）
输出：data/gis_stats.json、assets/charts/fig08.png

方法：等距圆柱投影（以 28.2N, 113.0E 为原点），距离为球面近似；
分段按论文正文的走廊顺序；置信度 A/B/C 随点标注。
"""
import csv
import json
import os
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)
CH = os.path.join(BASE, "assets", "charts"); os.makedirs(CH, exist_ok=True)

plt.rcParams.update({"font.family": ["SimHei", "Microsoft YaHei"], "axes.unicode_minus": False,
                     "figure.dpi": 180, "savefig.dpi": 180, "font.size": 10})

RED, BLUE, GREEN, GOLD, GRAY = "#b3261e", "#1f4e79", "#2e6b4f", "#a8791f", "#5f6368"
ROUTE_CN = {"北": "北线（官驿）", "西": "西线（黑茶）", "东": "东线（花炮）", "南": "南线（矿产）"}
ROUTE_COL = {"北": RED, "西": BLUE, "东": GREEN, "南": GOLD}

ROUTES = {
    "北": ["长沙总铺", "黄花铺", "永安铺", "枫浆桥铺", "蕉溪铺", "浏阳总铺", "北盛铺", "乌龙铺", "沙市铺", "龙伏铺", "社港铺"],
    "西": ["玉潭铺", "双凫铺", "黄材铺"],
    "东": ["浏阳总铺", "大瑶铺", "金刚铺", "上栗驿"],
    "南": ["飞羊铺", "中路铺", "衡州"],
}

nodes = {}
with open(os.path.join(BASE, "stations.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        nodes[r["name"]] = {"name": r["name"], "town": r["modern_town"],
                            "lat": float(r["lat"]), "lon": float(r["lon"]),
                            "route": r["route"], "conf": r["confidence"]}

LAT0, LON0 = 28.2, 113.0
def xy(n):
    return ((n["lon"] - LON0) * 111.32 * np.cos(np.deg2rad(LAT0)),
            (n["lat"] - LAT0) * 110.57)

def seg_km(a, b):
    (x1, y1), (x2, y2) = xy(a), xy(b)
    return float(np.hypot(x2 - x1, y2 - y1))

segments = defaultdict(list)
route_len = {}
for route, names in ROUTES.items():
    pts = [nodes[n] for n in names if n in nodes]
    d = [seg_km(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    segments[route] = d
    route_len[route] = float(np.sum(d))

# nearest neighbour among all nodes
coords = np.array([[*xy(n)] for n in nodes.values()])
names = list(nodes)
nnd = []
for i in range(len(coords)):
    d = np.hypot(coords[:, 0] - coords[i, 0], coords[:, 1] - coords[i, 1])
    d[i] = np.inf
    nnd.append(float(d.min()))
nnd = np.array(nnd)

north = np.array(segments["北"])
commercial = np.array(segments["东"] + segments["南"] + segments["西"])
mwu = stats.mannwhitneyu(north, commercial, alternative="two-sided")

stats_out = {
    "n_nodes": len(nodes),
    "by_route": {r: {"n_nodes": len(ROUTES[r]),
                     "n_segments": len(segments[r]),
                     "mean_km": float(np.mean(segments[r])) if segments[r] else None,
                     "median_km": float(np.median(segments[r])) if segments[r] else None,
                     "cv": float(np.std(segments[r]) / np.mean(segments[r])) if segments[r] else None,
                     "length_km": route_len[r]} for r in ROUTES},
    "nnd_mean": float(nnd.mean()), "nnd_median": float(np.median(nnd)),
    "north_mean": float(north.mean()), "commercial_mean": float(commercial.mean()),
    "mwu_p": float(mwu.pvalue),
    "conf_count": {c: sum(1 for n in nodes.values() if n["conf"].startswith(c)) for c in "ABC"},
}
json.dump(stats_out, open(os.path.join(DATA, "gis_stats.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ---------------- figure ----------------
fig, ax = plt.subplots(figsize=(8.4, 7.2))
fig.subplots_adjust(left=.06, right=.98, top=.90, bottom=.10)
for route, seq in ROUTES.items():
    pts = [nodes[n] for n in seq if n in nodes]
    xs, ys = zip(*[xy(p) for p in pts])
    ax.plot(xs, ys, "-", color=ROUTE_COL[route], lw=1.8, alpha=.75, zorder=2)
for name, n in nodes.items():
    x, y = xy(n)
    c = ROUTE_COL.get(n["route"], GRAY)
    marker = "o" if n["conf"].startswith("A") else ("s" if n["conf"].startswith("B") else "^")
    ax.scatter([x], [y], s=46, color=c, edgecolor="white", lw=.8, marker=marker, zorder=3)
label = {"长沙总铺": (8, 6), "浏阳总铺": (8, -10), "社港铺": (8, 4), "沙市铺": (-34, 8),
         "北盛铺": (-34, -12), "蕉溪铺": (-38, 6), "大瑶铺": (8, -10), "金刚铺": (8, 4),
         "玉潭铺": (-38, 6), "黄材铺": (-38, -10), "益阳": (-10, 8), "衡州": (8, -10),
         "中路铺": (8, 4), "上栗驿": (8, 4)}
for name, off in label.items():
    if name in nodes:
        x, y = xy(nodes[name])
        ax.annotate(name, (x, y), xytext=off, textcoords="offset points", fontsize=8.2)
ax.set_aspect("equal")
ax.set_xlabel("东西向（km，以 113.0°E 为原点）", fontsize=9.2)
ax.set_ylabel("南北向（km，以 28.2°N 为原点）", fontsize=9.2)
ax.grid(alpha=.18)
ax.set_title("图8　长沙府驿道试点：28 个节点的经纬投影", fontsize=12.5, fontweight="bold", loc="left")
handles = [plt.Line2D([], [], color=ROUTE_COL[r], lw=2, label=ROUTE_CN[r]) for r in ROUTES]
handles += [plt.Line2D([], [], marker="o", color=GRAY, ls="", label="A 级坐标"),
            plt.Line2D([], [], marker="s", color=GRAY, ls="", label="B 级"),
            plt.Line2D([], [], marker="^", color=GRAY, ls="", label="C 级")]
ax.legend(handles=handles, fontsize=7.6, frameon=False, loc="lower left", ncol=2)
fig.text(.5, .02, "注：距离为经纬投影近似；节点置信度 A/B/C 见表；C 级点只示意，不用于精确里程。",
         ha="center", fontsize=7.6, color="#666666")
fig.savefig(os.path.join(CH, "fig08.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

print(json.dumps(stats_out, ensure_ascii=False, indent=2))

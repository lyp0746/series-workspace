# -*- coding: utf-8 -*-
"""导出 schemes.csv，并画图 1—17（v2）。

图序（正文出现顺序）：
 1 条带  2 分布  3 传统  4 恒等式  5 分区距离  6 分窗口  7 模板
 8 分辨率  9 门  10 漂移  11 事件/进程与命名  12 同刀异名
 13 κ  14 敏感性  15 区域  16 扩展语料  17 时间轴叠放
"""
import csv
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
from schemes import SCHEMES, FIELDS, rows  # noqa: E402

plt.rcParams.update({
    "font.family": ["SimHei", "Microsoft YaHei"],
    "axes.unicode_minus": False,
    "figure.dpi": 180, "savefig.dpi": 180,
    "axes.edgecolor": "#333333", "axes.linewidth": 0.8,
    "font.size": 9.5, "figure.facecolor": "white",
})

RED, BLUE, GREEN, GRAY, GOLD = "#b3261e", "#1f4e79", "#2e6b4f", "#6b6b6b", "#a8791f"
TP = {"european": RED, "global": BLUE, "china": GREEN, "other": GRAY,
      "premodern_europe": "#7a5c3e", "islamic": GOLD, "african": "#6b4c9a",
      "south_asian": "#b5651d", "east_asian_premodern": "#3f6d6d",
      "americas": "#8a3b5c"}
TCN = {"european": "欧洲中心", "global": "全球史", "china": "中国教材", "other": "补充",
       "premodern_europe": "前现代欧洲", "islamic": "伊斯兰", "african": "非洲",
       "south_asian": "南亚", "east_asian_premodern": "东亚（前现代）", "americas": "美洲"}
ERA_C = {"ancient": "#cbb89d", "medieval": "#8a6d3b", "early_modern": "#d99a3d",
         "modern": "#b3261e", "contemporary": "#1f4e79", "sacred": "#8a3b5c"}
ERA_N = {"ancient": "古代", "medieval": "中世纪", "early_modern": "近代早期",
         "modern": "近代/现代", "contemporary": "当代", "sacred": "圣史"}
NAME_C = {"event": "#b3261e", "process": "#1f4e79", "space": "#4a7fa5",
          "dynastic": "#8a6d3b", "sacred": "#8a3b5c", "era": "#9a9a94"}
NAME_N = {"event": "事件", "process": "过程", "space": "空间",
          "dynastic": "王朝", "sacred": "圣史", "era": "时代"}

STATS = json.load(open(os.path.join(BASE, "data", "stats.json"), encoding="utf-8"))
KAPPA = json.load(open(os.path.join(BASE, "data", "kappa.json"), encoding="utf-8"))


def save(fig, name):
    fig.savefig(os.path.join(BASE, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", name)


def write_csv():
    p = os.path.join(BASE, "data", "schemes.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows())
    print("   data/schemes.csv (%d rows)" % len(SCHEMES))


def short(name, n=24):
    s = name.strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def src_meta():
    return STATS["SOURCES"]


def ordered_core():
    src = {k: v for k, v in src_meta().items()
           if v["series"] == "core" and v["tradition"] != "other"}
    rank = {"european": 0, "global": 1, "china": 2}
    return sorted(src.items(), key=lambda kv: (rank[kv[1]["tradition"]],
                                               kv[1]["year_published"], kv[0]))


# ------------------------------------------------------------------ 1
def fig01():
    items = ordered_core()
    fig, ax = plt.subplots(figsize=(10.0, 11.6))
    ys = np.arange(len(items))[::-1]
    for y, (name, m) in zip(ys, items):
        ax.axhline(y, color="#eeeeea", lw=0.6, zorder=0)
        allb = [r for r in SCHEMES if r["source"] == name and r["boundary_year"] is not None
                and 400 <= r["boundary_year"] <= 2000]
        for r in allb:
            if r["level"] != "part":
                ax.plot([r["boundary_year"]], [y], marker="|", ms=5.5,
                        color=TP[m["tradition"]], alpha=0.55, zorder=2)
        for x in m["part"]:
            ax.scatter([x], [y], s=24, color=TP[m["tradition"]], zorder=3,
                       edgecolor="white", linewidth=0.5)
    ax.set_yticks(ys)
    ax.set_yticklabels([short(n, 20) for n, _ in items], fontsize=8.0)
    for lab, (name, m) in zip(ax.get_yticklabels(), items):
        lab.set_color(TP[m["tradition"]])
    for t in ("european", "global", "china"):
        idx = [y for y, (_, m) in zip(ys, items) if m["tradition"] == t]
        ax.text(-0.30, np.mean(idx), TCN[t], transform=ax.get_yaxis_transform(),
                rotation=90, va="center", ha="center", fontsize=9.5,
                color=TP[t], fontweight="bold")
    for x in (476, 1500, 1750, 1914):
        ax.axvline(x, color="#c9c9c4", lw=0.7, ls=(0, (4, 4)), zorder=0)
        ax.text(x, len(items) - 0.2, str(x), ha="center", va="bottom",
                fontsize=7.5, color="#8a8a84")
    ax.set_xlim(380, 2020); ax.set_ylim(-1, len(items) + 0.6)
    ax.set_xlabel("边界年（圆点＝顶层分区，竖线＝章级分区）")
    ax.grid(axis="x", color="#f0f0ec", lw=0.5); ax.set_axisbelow(True)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=TP[t], label=TCN[t])
                       for t in ("european", "global", "china")],
              loc="upper center", bbox_to_anchor=(0.5, -0.055), frameon=False,
              fontsize=8.8, ncol=3)
    fig.suptitle("图 1　三组传统的边界年条带：46 部核心来源、195 条边界", fontsize=12.5,
                 fontweight="bold", y=0.995)
    fig.text(0.5, 0.005, "每行一部来源；同一时间轴上，三种传统切线不同。", ha="center",
             fontsize=8, color="#666666")
    fig.tight_layout(rect=(0.02, 0.02, 1, 0.98))
    save(fig, "fig01.png")


# ------------------------------------------------------------------ 2
def fig02():
    w1, w1t = STATS["W1"], STATS["W1T"]
    years = [r["boundary_year"] for r in SCHEMES if r["series"] == "core"
             and r["boundary_year"] is not None and 400 <= r["boundary_year"] <= 2000]
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.3),
                             gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    bins = np.arange(400, 2050, 25)
    ax.hist(years, bins=bins, color="#d9d3c6", edgecolor="#8f887a", lw=0.5)
    from scipy.ndimage import gaussian_filter1d
    c, e = np.histogram(years, bins=bins)
    xs = (e[:-1] + e[1:]) / 2
    ax.plot(xs, gaussian_filter1d(c.astype(float), 2.0), color=RED, lw=1.6)
    for y, dx, dy in ((476, 0, 8), (1000, 0, 13), (1500, -18, 22), (1640, 0, 8),
                      (1750, -16, 26), (1789, 6, 10), (1914, -14, 8), (1945, 8, 8)):
        k = c[np.argmin(np.abs(xs - y))]
        ax.annotate(str(y), (y, k), textcoords="offset points", xytext=(dx, dy),
                    ha="center", fontsize=7.6, color="#333333",
                    arrowprops=dict(arrowstyle="-", color="#999999", lw=0.6,
                                    shrinkA=0, shrinkB=2) if dy > 12 else None)
    ax.set_xlabel("边界年"); ax.set_ylabel("边界条数（25 年一格）")
    ax.set_title("(a) 分布：九成年份是空白", fontsize=10)
    ax.set_xlim(400, 2020); ax.set_ylim(0, 46)

    ax = axes[1]
    top = w1["top"][:10]
    names = [str(t[0]) for t in top][::-1]
    vals = [t[1] for t in top][::-1]
    ax.barh(names, vals, color=RED, alpha=0.85)
    for i, v in enumerate(vals):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=8.5, color="#333333")
    ax.axvline(w1["null_top10"] * w1["n"] / 10, color=GRAY, ls="--", lw=1)
    ax.text(max(vals) * 1.16, 4.6, "虚线：零模型下每年平均次数", fontsize=7.2,
            color=GRAY, rotation=90, va="center", ha="left")
    ax.set_xlabel("出现次数")
    ax.set_title("(b) 前十：%.1f%%（模板级 %.1f%%）"
                 % (w1["top10"] * 100, w1t["top10"] * 100), fontsize=10)
    ax.set_xlim(0, max(vals) * 1.36)
    fig.suptitle("图 2　边界年集中在少数年份，其余是长尾", fontsize=12.5,
                 fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig02.png")


# ------------------------------------------------------------------ 3
def boot_ci(x, n=2000, seed=1):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    meds = [np.median(rng.choice(x, len(x), replace=True)) for _ in range(n)]
    return float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


def fig03():
    src = src_meta()
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8))
    rng = np.random.default_rng(7)
    for ax, field, title in ((axes[0], "part", "(a) 全部顶层边界"),
                             (axes[1], "ms", "(b) 进入近代的第一条边界")):
        for i, t in enumerate(("european", "global", "china")):
            vals = []
            for name, m in src.items():
                if m["series"] != "core" or m["tradition"] != t or m["scope"] == "nation":
                    continue
                if field == "part":
                    vals += m["part"]
                elif m["ms"] is not None:
                    vals.append(m["ms"])
            vals = np.array(vals, float)
            y = 2 - i
            ax.scatter(vals + rng.normal(0, 9, len(vals)), y + rng.normal(0, 0.075, len(vals)),
                       s=17, color=TP[t], alpha=0.55, linewidths=0)
            lo, hi = boot_ci(vals)
            ax.plot([lo, hi], [y, y], color=TP[t], lw=2.4, solid_capstyle="butt")
            ax.scatter([np.median(vals)], [y], s=90, color="white", edgecolor=TP[t],
                       lw=2, zorder=4)
            ax.text(402, y + 0.26, "%s　中位 %d（n=%d）" % (TCN[t], int(np.median(vals)), len(vals)),
                    fontsize=8.4, color=TP[t])
        for x in (476, 1000, 1200, 1500, 1640, 1750, 1914):
            ax.axvline(x, color="#ded9cd", lw=0.7, ls=(0, (3, 4)), zorder=0)
        ax.set_yticks([2, 1, 0]); ax.set_yticklabels([])
        ax.set_ylim(-0.6, 2.7); ax.set_xlim(400, 2020)
        ax.set_xlabel("年份"); ax.set_title(title, fontsize=10)
        ax.text(0.99, 0.02, "三部国别通史不计入本图", transform=ax.transAxes,
                ha="right", fontsize=7.2, color="#8a8a84")
    for x, tx in ((476, "476"), (1000, "1000"), (1200, "1200"), (1500, "1500"),
                  (1640, "1640"), (1750, "1750"), (1914, "1914")):
        axes[1].text(x, -0.52, tx, ha="center", fontsize=7.2, color="#8a8a84")
    fig.suptitle("图 3　三组传统的重心不同，门也不同", fontsize=12.5,
                 fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig03.png")


# ------------------------------------------------------------------ 4 恒等式
def fig04():
    ident = STATS["ID"]
    years = np.array(ident["years"]); obs = np.array(ident["obs"]); pred = np.array(ident["pred"])
    fig, ax = plt.subplots(figsize=(9.2, 4.5))
    for a, b in ((1450, 1550), (1750, 1850)):
        ax.axvspan(a, b, color="#f3e6c8", alpha=0.8, zorder=0)
        ax.text((a + b) / 2, 55, "预测带", ha="center", fontsize=7.4, color="#8a7238")
    ax.plot(years, pred * 100, color=GRAY, lw=4, alpha=0.55, label="边际分布给出的预期", zorder=2)
    ax.plot(years, obs * 100, color=BLUE, lw=1.6, drawstyle="steps-post",
            label="观测的跨传统分歧", zorder=3)
    ax.annotate("1453：%.0f%%" % (obs[years == 1453][0] * 100),
                (1453, obs[years == 1453][0] * 100), xytext=(1230, 56),
                fontsize=8.5, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8))
    ax.text(0.98, 0.96, "R² = %.4f　最大残差 %.1e\n两条线重合不是拟合，是恒等式"
            % (ident["r2"], ident["max_resid"]),
            transform=ax.transAxes, ha="right", va="top", fontsize=8.2, color="#333333",
            bbox=dict(fc="white", ec="#dddddd", lw=0.6))
    ax.set_xlim(400, 2020); ax.set_ylim(0, 62)
    ax.set_xlabel("年份"); ax.set_ylabel("跨传统来源对中「一方已近代」的比例（%）")
    ax.legend(loc="upper left", fontsize=8.2, frameon=False)
    fig.suptitle("图 4　交叉曲线没有独立信息：它完全由近代起点的边际分布决定",
                 fontsize=12, fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig04.png")


# ------------------------------------------------------------------ 5 分区距离
def fig05():
    W = STATS["W3"]
    keys = W["keys"]
    src = src_meta()
    tr = [src[k]["tradition"] for k in keys]
    order = sorted(range(len(keys)), key=lambda i: ({"european": 0, "global": 1, "china": 2}[tr[i]], keys[i]))
    keys = [keys[i] for i in order]
    tr = [tr[i] for i in order]
    # recompute matrix in ordered form from MDS? use stats pair info only -> rebuild ARI here
    sys.path.insert(0, os.path.join(BASE, "analysis"))
    import stats as st
    rows_ = st.load()
    s2 = st.by_source(rows_)
    D = st.distance_matrix(keys, s2)
    A = 1 - D

    fig = plt.figure(figsize=(11.6, 6.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 1],
                          wspace=0.28, hspace=0.42)
    ax = fig.add_subplot(gs[:, 0])
    cmap = LinearSegmentedColormap.from_list("ari", ["#f7f4ec", "#d9b25f", "#7a2b1e"])
    im = ax.imshow(A, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks([]); ax.set_yticks([])
    start = 0
    for t in ("european", "global", "china"):
        n = tr.count(t)
        ax.add_patch(Rectangle((start - 0.5, start - 0.5), n, n, fill=False,
                               ec=TP[t], lw=1.6))
        ax.text(start + n / 2, len(keys) + 0.2, TCN[t], ha="center", fontsize=8.5, color=TP[t])
        start += n
    ax.set_title("(a) 40 部来源的分区相似度（ARI）", fontsize=10, pad=22)
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cb.set_label("ARI", fontsize=8)

    ax = fig.add_subplot(gs[0, 1])
    ts = ["european", "global", "china"]
    x = np.arange(3)
    ax.bar(x - 0.19, [W["within"][t] for t in ts], 0.36, color=[TP[t] for t in ts],
           label="组内")
    ax.bar(x + 0.19, [W["between"][t] for t in ts], 0.36, color=[TP[t] for t in ts],
           alpha=0.35, label="组间")
    for i, t in enumerate(ts):
        ax.text(i - 0.19, W["within"][t] + 0.015, "%.2f" % W["within"][t], ha="center", fontsize=7.5)
        ax.text(i + 0.19, W["between"][t] + 0.015, "%.2f" % W["between"][t], ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels([TCN[t] for t in ts], fontsize=8.5)
    ax.set_ylim(0, 1); ax.set_ylabel("平均 ARI")
    ax.set_title("(b) 组内 vs 组间：Δ=%.3f，p=%.4f" % (W["diff"], W["p"]), fontsize=9.5)
    ax.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper left")

    ax = fig.add_subplot(gs[1, 1])
    co = np.array(W["mds"]["coords"])
    for t in ts:
        ix = [i for i in range(len(keys)) if tr[i] == t]
        ax.scatter(co[ix, 0], co[ix, 1], s=26, color=TP[t], label=TCN[t],
                   alpha=0.8, linewidths=0)
    ax.set_xlabel("MDS-1"); ax.set_ylabel("MDS-2")
    ax.set_title("(c) 二维 MDS：前两维解释 %.0f%%" % (W["mds_share2"] * 100), fontsize=9.5)
    ax.legend(fontsize=7.2, frameon=False, loc="best")
    fig.suptitle("图 5　分区距离：传统是真实的块，但只解释 29% 的方差", fontsize=12.5,
                 fontweight="bold", y=1.0)
    save(fig, "fig05.png")


# ------------------------------------------------------------------ 6 分窗口
def fig06():
    W = STATS["W3"]
    pairs = list(W["pair"].keys())
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    y = np.arange(len(pairs))
    full = [W["pair"][p] for p in pairs]
    mod = [W["pair_1500"][p] for p in pairs]
    for i in range(len(pairs)):
        ax.plot([mod[i], full[i]], [i, i], color="#bbbbbb", lw=1.6, zorder=1)
        ax.scatter([full[i]], [i], s=70, color=BLUE, zorder=3, label="400—2000" if i == 0 else None)
        ax.scatter([mod[i]], [i], s=70, color=GOLD, zorder=3, marker="s",
                   label="1500—2000" if i == 0 else None)
        ax.text(max(full[i], mod[i]) + 0.02, i, "全窗 %.2f／近代段 %.2f" % (full[i], mod[i]),
                va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels([p.replace("european", "欧洲").replace("global", "全球")
                        .replace("china", "中国").replace("-", "—") for p in pairs])
    ax.set_xlim(0.1, 0.85); ax.set_xlabel("平均 ARI（越高越像）")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.set_title("图 6　相似性取决于窗口：全窗上中国—欧洲最像，近代段上中国—全球最像",
                 fontsize=11.5, fontweight="bold", loc="left")
    fig.tight_layout()
    save(fig, "fig06.png")


# ------------------------------------------------------------------ 7 模板
def fig07():
    tpl = STATS["TEMPLATES"]
    sizes = sorted((len(v) for v in tpl.values()), reverse=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4),
                             gridspec_kw={"width_ratios": [1, 1.7]})
    ax = axes[0]
    from collections import Counter
    c = Counter(sizes)
    ks = sorted(c)
    ax.bar([str(k) for k in ks], [c[k] for k in ks], color=RED, alpha=0.85)
    for i, k in enumerate(ks):
        ax.text(i, c[k] + 0.3, str(c[k]), ha="center", fontsize=8.5)
    ax.set_xlabel("同一模板被几部来源使用"); ax.set_ylabel("模板数")
    ax.set_title("(a) 32 套模板，4 套被重复使用", fontsize=10)

    ax = axes[1]
    big = [kv for kv in sorted(tpl.items(), key=lambda kv: -len(kv[1])) if len(kv[1]) > 1]
    for i, (cut, names) in enumerate(big):
        y = len(big) - 1 - i
        ax.axhline(y, color="#eeeeea", lw=0.6, zorder=0)
        for yr in eval(cut) if isinstance(cut, str) else cut:
            ax.scatter([yr], [y], s=34, color=RED, zorder=3)
        ax.text(402, y + 0.18, "%d 部：%s" % (len(names), short(names[0], 16)),
                fontsize=7.4, color="#444444")
    ax.set_yticks([]); ax.set_xlim(400, 2020); ax.set_ylim(-0.6, len(big) - 0.1)
    ax.set_xlabel("边界年")
    ax.set_title("(b) 被复制的模板：同一组切线，不同的书", fontsize=10)
    fig.suptitle("图 7　分期是模板复制：40 部来源只用了 32 套顶层切线", fontsize=12.5,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig07.png")


# ------------------------------------------------------------------ 8 分辨率
def fig08():
    M = STATS["W4"]["metrics"]
    labels = {"raw": "原始条数（窗内）", "fixed": "每 1600 年", "rate": "每边界跨度千年（旧口径）"}
    fig, ax = plt.subplots(figsize=(9.4, 4.2))
    x = np.arange(3)
    w = 0.26
    scopes = ["world", "region", "nation"]
    cols = {"world": BLUE, "region": RED, "nation": GREEN}
    for j, key in enumerate(("raw", "fixed", "rate")):
        vals = [M[key]["means"][s] for s in scopes]
        ax.bar(x + (j - 1) * w, vals, w, color=["#9ecae1", "#4292c6", "#08519c"][j],
               label=labels[key])
        for i, v in enumerate(vals):
            ax.text(i + (j - 1) * w, v + 0.12, "%.1f" % v, ha="center", fontsize=7.4)
    ax.set_xticks(x)
    ax.set_xticklabels(["世界（31）", "区域（12）", "国别（3）"])
    ax.set_ylabel("每千年顶层边界数")
    ax.set_ylim(0, 13)
    ax.legend(fontsize=8, frameon=False)
    ax.annotate("旧口径的 11.4 是跨度伪影", (2 + w, 11.4), xytext=(1.55, 9.4),
                fontsize=7.6, color="#08519c",
                arrowprops=dict(arrowstyle="-", color="#08519c", lw=0.8))
    ax.text(0.99, 0.97, "KW p：原始 0.008／固定窗 0.008／旧口径 0.29",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.8, color="#555555")
    fig.suptitle("图 8　分辨率对归一化敏感：唯一稳健的是世界史最粗", fontsize=12.5,
                 fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig08.png")


# ------------------------------------------------------------------ 9 门
def fig09():
    G = STATS["GATES"]
    years = sorted(int(y) for y in G if not str(y).startswith("_"))
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.3),
                             gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    for y in years:
        d = G[str(y)]
        col = RED if d["support"]["european"] >= 2 else (BLUE if d["support"]["global"] >= 2 else GREEN)
        ax.scatter([y], [d["penetration"]], s=18 + d["total"] * 5, color=col, alpha=0.75,
                   edgecolor="white", linewidth=0.6, zorder=3)
        off = {476: (0, 10), 1000: (0, 10), 1500: (0, 11), 1640: (-20, -15),
               1648: (16, 6), 1750: (-16, -16), 1789: (18, 6), 1800: (0, -16),
               1914: (0, 11), 1917: (0, -16), 1945: (-18, 6)}.get(y)
        if off:
            ax.annotate(str(y), (y, d["penetration"]), textcoords="offset points",
                        xytext=off, ha="center", fontsize=7.4, color="#333333")
    ax.set_ylim(0.4, 3.6); ax.set_yticks([1, 2, 3])
    ax.set_ylabel("穿透率：几个传统把它当顶层门")
    ax.set_xlabel("年份"); ax.set_xlim(400, 2020)
    ax.axhline(3, color="#dddddd", lw=0.8, zorder=0)
    ax.text(405, 3.08, "只有 1500 与 1914 穿透 3/3", fontsize=8, color="#555555")
    ax.set_title("(a) 门的通货（点大小＝使用该门的来源数）", fontsize=10)

    ax = axes[1]
    W = STATS["W5"]
    ts = ["european", "global", "china"]
    x = np.arange(3)
    ax.bar(x - 0.22, [W[t]["p_has"] for t in ts], 0.42, color=[TP[t] for t in ts], label="出现率")
    ax.bar(x + 0.22, [W[t]["exclusive"] or 0 for t in ts], 0.42, color=[TP[t] for t in ts],
           alpha=0.4, label="排他性")
    for i, t in enumerate(ts):
        ax.text(i - 0.22, W[t]["p_has"] + 0.02, "%.2f" % W[t]["p_has"], ha="center", fontsize=7.6)
        ax.text(i + 0.22, (W[t]["exclusive"] or 0) + 0.02, "%.2f" % (W[t]["exclusive"] or 0),
                ha="center", fontsize=7.6)
    ax.set_xticks(x); ax.set_xticklabels([TCN[t] for t in ts], fontsize=8.5)
    ax.set_ylim(0, 1.1); ax.set_ylabel("比例")
    ax.set_title("(b) 1500：三组都保留，排他性不同", fontsize=10)
    ax.legend(fontsize=7.6, frameon=False, ncol=2, loc="upper center",
              bbox_to_anchor=(0.5, -0.18))
    fig.suptitle("图 9　1500 的存亡：出现率相近，排他性相反", fontsize=12.5,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig09.png")


# ------------------------------------------------------------------ 10 漂移
def fig10():
    w6 = STATS["W6"]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.6),
                             gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    for t in ("european", "global", "china"):
        pts = w6[t]["pts"]
        x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
        ax.scatter(x, y, s=30, color=TP[t], alpha=0.75, label=TCN[t], linewidths=0)
        if len(x) > 3:
            b, a = np.polyfit(x, y, 1)
            xs = np.linspace(x.min() - 2, x.max() + 2, 20)
            ax.plot(xs, a + b * xs, color=TP[t], lw=1.2, alpha=0.8)
    ax.set_xlabel("出版年（实际使用的版次）")
    ax.set_ylabel("进入近代的第一条顶层边界年")
    ax.set_xlim(1935, 2035); ax.set_ylim(1260, 1870)
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    ax.text(0.98, 0.96, "ρ：欧洲 %.2f（p=%.2f）\n　　全球 %.2f（p=%.2f）\n　　中国 %.2f（p=%.2f）"
            % (w6["european"]["rho"], w6["european"]["p"], w6["global"]["rho"],
               w6["global"]["p"], w6["china"]["rho"], w6["china"]["p"]),
            transform=ax.transAxes, ha="right", va="top", fontsize=7.6, color="#444444",
            bbox=dict(fc="white", ec="#dddddd", lw=0.6))
    ax.set_title("(a) 横截面：只有方向，没有强度", fontsize=10)

    ax = axes[1]
    S = src_meta()
    ap11 = S["AP 世界史（2011 框架）"]["part"]
    ap19 = S["AP 世界史：现代（课程框架）"]["part"]
    for i, (lab, ys, col) in enumerate((("AP 2011", ap11, GOLD), ("AP 2019", ap19, BLUE))):
        y = 1 - i
        ax.axhline(y, color="#eeeeea", lw=0.6)
        for v in ys:
            ax.scatter([v], [y], s=40, color=col, zorder=3)
            ax.text(v, y + 0.16, str(v), ha="center", fontsize=7.4, color=col)
    ax.set_yticks([1, 0]); ax.set_yticklabels(["AP 2011", "AP 2019"])
    ax.set_xlim(550, 2000); ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel("边界年")
    ax.set_title("(b) 唯一的版本对照：改的是古代的门", fontsize=10)
    ax.text(0.02, 0.06, "近代起点 1450 未变；\n600 改为 1200，1914 改为 1900。",
            transform=ax.transAxes, fontsize=7.8, color="#555555")
    fig.suptitle("图 10　出版年与漂移：方向为负，强度不足；版本改动落在古代", fontsize=12.5,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig10.png")


# ------------------------------------------------------------------ 11 事件/进程与命名
def fig11():
    W7 = STATS["W7"]; W8 = STATS["W8"]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.3))
    ax = axes[0]
    ts = ["european", "global", "china"]
    ev = [W7["by_trad"][t]["event"] * 100 for t in ts]
    pr = [W7["by_trad"][t]["process"] * 100 for t in ts]
    x = np.arange(3); w = 0.36
    ax.bar(x - w / 2, ev, w, color=[TP[t] for t in ts], label="事件年 ±3 年")
    ax.bar(x + w / 2, pr, w, color=[TP[t] for t in ts], alpha=0.35, label="进程年 ±3 年")
    for i in range(3):
        ax.text(i - w / 2, ev[i] + 1.3, "%.0f%%" % ev[i], ha="center", fontsize=8)
        ax.text(i + w / 2, pr[i] + 1.3, "%.0f%%" % pr[i], ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([TCN[t] for t in ts], fontsize=9)
    ax.set_ylim(0, 100); ax.set_ylabel("边界落在窗口内的比例（%）")
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.set_title("(a) 年份：事件刻度 vs 进程刻度", fontsize=10)

    ax = axes[1]
    types = ["event", "process", "space", "dynastic", "sacred", "era"]
    left = np.zeros(3)
    for typ in types:
        vals = np.array([W8["by_trad"][t].get(typ, 0) * 100 for t in ts])
        ax.barh([TCN[t] for t in ts], vals, left=left, color=NAME_C[typ],
                label=NAME_N[typ], height=0.55)
        for i, v in enumerate(vals):
            if v >= 9:
                ax.text(left[i] + v / 2, i, "%.0f" % v, ha="center", va="center",
                        fontsize=7.6, color="white")
        left += vals
    ax.set_xlim(0, 100); ax.set_xlabel("时期名的类型构成（%）")
    ax.legend(fontsize=7.2, frameon=False, ncol=6, loc="upper center",
              bbox_to_anchor=(0.5, -0.16))
    ax.set_title("(b) 命名：事件／时代 vs 过程／空间", fontsize=10)
    fig.suptitle("图 11　两套标记系统，在年份上与在命名上都分得开", fontsize=12.5,
                 fontweight="bold", y=1.04)
    fig.tight_layout()
    save(fig, "fig11.png")


# ------------------------------------------------------------------ 12 同刀异名
def fig12():
    W8 = STATS["W8"]
    C = W8["cells"]
    M = np.array([[C["same_cut|same_name"], C["same_cut|diff_name"]],
                  [C["diff_cut|same_name"], C["diff_cut|diff_name"]]], float)
    R = M / M.sum(1, keepdims=True)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    im = ax.imshow(R, cmap="YlOrBr", vmin=0, vmax=1)
    lab = [["同刀同语", "同刀异语"], ["异刀同语", "异刀异语"]]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, "%s\n%d 对（%.0f%%）" % (lab[i][j], M[i, j], R[i, j] * 100),
                    ha="center", va="center", fontsize=11,
                    color="white" if R[i, j] > 0.55 else "#333333")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["同名（同一命名register）", "异名"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["同切线（±5 年）", "异切线"])
    ax.set_title("图 12　同刀异名：切线相同时，%.0f%% 用不同命名"
                 % (W8["diff_name_share"] * 100), fontsize=11.8, fontweight="bold")
    ax.text(0.0, -0.26, "40 部来源两两比较的全部边界对（共 %d 对）；颜色为该行内的比例。\n"
                        "同切线而命名不同的例子：1500＝近代早期／全球网络的成形／走向整体的世界。"
            % W8["total"], transform=ax.transAxes, fontsize=7.6, color="#666666")
    fig.tight_layout()
    save(fig, "fig12.png")


# ------------------------------------------------------------------ 13 κ
def fig13():
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2),
                             gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    fields = [("year", "边界年"), ("era", "时代标签"), ("level", "分区层级"), ("row", "整行")]
    ks = [KAPPA[f]["kappa"] for f, _ in fields]
    cols = [GREEN if k >= 0.7 else (GOLD if k >= 0.6 else RED) for k in ks]
    ax.bar([n for _, n in fields], ks, color=cols, alpha=0.9, width=0.6)
    for i, k in enumerate(ks):
        ax.text(i, k + 0.02, "%.2f" % k, ha="center", fontsize=9)
    ax.axhline(0.7, color="#333333", ls="--", lw=1)
    ax.axhline(0.6, color=RED, ls=":", lw=1)
    ax.set_ylim(0, 1.06); ax.set_ylabel("Cohen's κ（9 部来源／32 条，n=32）")
    ax.set_title("(a) 年份可抄，层级不可抄", fontsize=10)
    ax = axes[1]
    conf = KAPPA["level"]["conf"]
    M = np.array([[conf.get(a, {}).get(b, 0) for b in ("part", "chapter")]
                  for a in ("part", "chapter")], float)
    ax.imshow(M, cmap="BuPu", vmin=0, vmax=M.max() * 1.15)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=15,
                    color="white" if M[i, j] > M.max() * 0.6 else "#333333")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["复编 part", "复编 chapter"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["首轮 part", "首轮 chapter"])
    ax.set_title("(b) 层级判定混淆表：κ=%.2f" % KAPPA["level"]["kappa"], fontsize=10)
    fig.suptitle("图 13　编码一致性：分歧在「哪一层算边界」，不在年份", fontsize=12.5,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig13.png")


# ------------------------------------------------------------------ 14 敏感性
def fig14():
    S = STATS["SENS"]
    labels = ["基线", "含章级", "含国别", "含维基", "现代→modern"]
    keys = ["基线", "含章级", "含国别", "含维基", "中国现代→modern"]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3))
    ax = axes[0]
    for t, col in (("european", RED), ("global", BLUE), ("china", GREEN)):
        vals = [S[k]["y1500"][t] * 100 for k in keys]
        ax.plot(labels, vals, marker="o", color=col, label=TCN[t], lw=1.6)
        for x, v in zip(labels, vals):
            ax.text(x, v + 2, "%.0f" % v, ha="center", fontsize=7.4, color=col)
    ax.set_ylim(0, 105); ax.set_ylabel("含 1500 顶层边界的来源比例（%）")
    ax.tick_params(axis="x", labelsize=8)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    ax.set_title("(a) 出现率：层级与国别两个口径最敏感", fontsize=10)

    ax = axes[1]
    pairs = [("european-china", "欧洲—中国", RED), ("global-china", "全球—中国", BLUE),
             ("european-global", "欧洲—全球", GOLD)]
    for k, lab, col in pairs:
        vals = [S[x]["pair"][k] for x in keys]
        ax.plot(labels, vals, marker="o", color=col, label=lab, lw=1.6)
        for x, v in zip(labels, vals):
            ax.text(x, v + 0.012, "%.2f" % v, ha="center", fontsize=7.2, color=col)
    ax.set_ylim(0.3, 0.72); ax.set_ylabel("平均 ARI")
    ax.tick_params(axis="x", labelsize=8)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    ax.set_title("(b) 分区相似度：方向不变，幅度随口径移动", fontsize=10)
    fig.suptitle("图 14　敏感性：中位数不变，比例与相似度随两个口径移动", fontsize=12.3,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig14.png")


# ------------------------------------------------------------------ 15 区域
def fig15():
    reg = STATS["REGION"]
    core = ["european", "global", "china", "other"]
    regions = ["欧洲", "亚洲", "非洲", "美洲", "全球"]
    cols = {"欧洲": "#b3261e", "亚洲": "#2e6b4f", "非洲": "#6b4c9a",
            "美洲": "#8a3b5c", "全球": "#1f4e79"}
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4),
                             gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    left = np.zeros(len(core))
    for r in regions:
        vals = np.array([reg.get(g, {}).get(r, 0) for g in core], float)
        tot = np.array([sum(reg.get(g, {}).values()) or 1 for g in core], float)
        sh = vals / tot * 100
        ax.barh([TCN[g] for g in core], sh, left=left, color=cols[r], label=r, height=0.55)
        for i, (v, l) in enumerate(zip(sh, left)):
            if v >= 8:
                ax.text(l + v / 2, i, "%.0f" % v, ha="center", va="center",
                        fontsize=8.5, color="white")
        left += sh
    ax.set_xlim(0, 100); ax.set_xlabel("边界所属区域的构成（%）")
    ax.legend(ncol=5, fontsize=8, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, 1.16))
    ax.set_title("(a) 核心 46 部：非洲 0 条", fontsize=10)

    ax = axes[1]
    ext = ["premodern_europe", "islamic", "african", "east_asian_premodern",
           "south_asian", "americas"]
    E = STATS["EXT"]
    counts = [E["regions"].get(g, 0) for g in ext]
    ax.barh([TCN[g] for g in ext], counts, color=[TP[g] for g in ext], height=0.55)
    for i, v in enumerate(counts):
        ax.text(v + 0.08, i, str(v), va="center", fontsize=8.5)
    ax.set_xlim(0, 3.6); ax.set_xlabel("来源数")
    ax.set_title("(b) 扩展 14 部：把非洲、美洲、南亚补上", fontsize=10)
    fig.suptitle("图 15　区域覆盖：核心语料里非洲 0 条，扩展语料把它补上", fontsize=12.3,
                 fontweight="bold", y=1.02)
    fig.tight_layout()
    save(fig, "fig15.png")


# ------------------------------------------------------------------ 16 扩展语料
def fig16():
    E = STATS["EXT"]
    ext = [r for r in SCHEMES if r["series"] == "extended"]
    names = sorted({r["source"] for r in ext},
                   key=lambda s: ({"premodern_europe": 0, "islamic": 1, "african": 2,
                                   "east_asian_premodern": 3, "south_asian": 4,
                                   "americas": 5}[
                                       next(x["tradition"] for x in ext if x["source"] == s)],
                                  s))
    fig = plt.figure(figsize=(11.6, 5.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.3, 1], wspace=0.16)
    ax = fig.add_subplot(gs[0, 0])
    for i, s in enumerate(names):
        y = len(names) - 1 - i
        rs = [r for r in ext if r["source"] == s]
        tr = rs[0]["tradition"]
        ax.axhline(y, color="#eeeeea", lw=0.6, zorder=0)
        ys = [r["boundary_year"] for r in rs if r["boundary_year"] is not None]
        if ys:
            for v in ys:
                ax.scatter([v], [y], s=30, color=TP[tr], zorder=3)
        elif E["sources"][s]["explicit"]:
            ax.scatter([-330], [y], marker="D", s=34, color=TP[tr], zorder=3)
            ax.text(-300, y, "本土纪年", fontsize=7, color=TP[tr], va="center")
        else:
            ax.add_patch(Rectangle((-470, y - 0.18), 210, 0.36, color="#e6e2d8", lw=0))
            ax.text(-365, y, "仅时期名", fontsize=7, color="#666666", va="center", ha="center")
        ax.text(-500, y, short(s, 15), ha="right", va="center", fontsize=7.4, color=TP[tr])
    ax.set_xlim(-500, 1750); ax.set_ylim(-0.7, len(names) - 0.2)
    ax.set_yticks([])
    ax.axvline(0, color="#cccccc", lw=0.8, ls=":")
    ax.set_xlabel("边界年（公元）")
    ax.set_title("(a) 14 部扩展来源：有年份、只有本土纪年、只有时期名", fontsize=10)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=TP[t], label=TCN[t]) for t in
                       ("premodern_europe", "islamic", "african",
                        "east_asian_premodern", "south_asian", "americas")],
              fontsize=6.8, frameon=False, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.13))

    ax = fig.add_subplot(gs[0, 1])
    cal = E["calendars"]
    order = ["AD", "AH", "AM", "reign", "laukika", "mixed", "none"]
    lab = {"AD": "公元", "AH": "希吉拉", "AM": "世界纪年", "reign": "王朝纪年",
           "laukika": "Laukika", "mixed": "混用", "none": "无年份"}
    vals = [cal.get(k, 0) for k in order]
    ax.barh([lab[k] for k in order], vals, color=[GRAY if k == "none" else GOLD for k in order])
    for i, v in enumerate(vals):
        ax.text(v + 0.08, i, str(v), va="center", fontsize=8)
    ax.set_xlim(0, 5); ax.set_xlabel("来源数")
    ax.set_title("(b) 纪年的零点是六套，不是一套", fontsize=10)
    fig.suptitle("图 16　扩展语料：边界年不是普遍变量", fontsize=12.5,
                 fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig16.png")


# ------------------------------------------------------------------ 17 时间轴
def fig17():
    pick = [("Spielvogel《西方文明史简编》第9版", "欧洲中心：Spielvogel（2017）"),
            ("Bentley & Ziegler《传统与相遇》第6版", "全球史：Bentley & Ziegler（2015）"),
            ("《中外历史纲要（下）》人教版", "中国教材：人教版《纲要（下）》（2019）")]
    src = src_meta()
    fig, axes = plt.subplots(3, 1, figsize=(10.6, 5.0), sharex=True)
    for ax, (name, label) in zip(axes, pick):
        bs = sorted([r for r in SCHEMES if r["source"] == name
                     and r["boundary_year"] is not None and 400 <= r["boundary_year"] <= 2000
                     and r["level"] == "part"],
                    key=lambda r: r["boundary_year"])
        prev, prev_era = 400, "ancient"
        for i, r in enumerate(bs):
            y = r["boundary_year"]
            if y - prev > 1:
                ax.add_patch(Rectangle((prev, 0.18), y - prev, 0.64,
                                       color=ERA_C.get(prev_era, "#cccccc"), alpha=0.9, lw=0))
                if y - prev > 95:
                    ax.text((prev + y) / 2, 0.5, ERA_N.get(prev_era, prev_era), ha="center",
                            va="center", fontsize=7.4,
                            color="white" if prev_era in ("modern", "contemporary") else "#2b2b2b")
            ax.plot([y] * 2, [0.14, 0.86], color="white", lw=1.5)
            lev = {0: 1.00, 1: 1.15, 2: 1.30, 3: 1.45}[i % 4]
            ax.plot([y] * 2, [0.86, lev - 0.02], color="#888888", lw=0.7)
            ax.text(y, lev, str(y), ha="center", va="bottom", fontsize=7.0, color="#333333")
            prev, prev_era = y, r["era"]
        ax.add_patch(Rectangle((prev, 0.18), 2000 - prev, 0.64,
                               color=ERA_C.get(prev_era, "#cccccc"), alpha=0.9, lw=0))
        if 2000 - prev > 95:
            ax.text((prev + 2000) / 2, 0.5, ERA_N.get(prev_era, prev_era), ha="center",
                    va="center", fontsize=7.4,
                    color="white" if prev_era in ("modern", "contemporary") else "#2b2b2b")
        ax.set_xlim(400, 2000); ax.set_ylim(0, 1.56)
        ax.set_yticks([])
        ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=8.5)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
    axes[-1].set_xlabel("年份")
    handles = [Rectangle((0, 0), 1, 1, color=ERA_C[e]) for e in
               ("ancient", "medieval", "early_modern", "modern", "contemporary")]
    axes[-1].legend(handles, ["古代", "中世纪", "近代早期", "近代/现代", "当代"], ncol=5,
                    fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.35))
    fig.suptitle("图 17　同一条时间轴，三种切法", fontsize=12.5, fontweight="bold", y=1.0)
    fig.tight_layout()
    save(fig, "fig17.png")


def main():
    write_csv()
    for fn in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
               fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17):
        fn()
    print("完成：fig01—fig17.png + data/schemes.csv")


if __name__ == "__main__":
    main()

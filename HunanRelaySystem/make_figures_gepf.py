# -*- coding: utf-8 -*-
"""Figures for the rewritten Hunan relay paper (GEPF version).

    python make_figures_gepf.py     -> fig01.png … fig07.png

All values are the paper's B/C-grade estimates; the figures are labelled
accordingly (a schematic is a schematic, a fit is a fit).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

plt.rcParams.update({
    "font.family": ["SimHei", "Microsoft YaHei"],
    "axes.unicode_minus": False,
    "figure.dpi": 180, "savefig.dpi": 180,
    "axes.edgecolor": "#333333", "axes.linewidth": .8,
    "font.size": 10,
})
BASE = os.path.dirname(os.path.abspath(__file__))
RED, BLUE, GREEN, GOLD, GRAY = "#b3261e", "#1f4e79", "#2e6b4f", "#a8791f", "#5f6368"
P_RED, P_BLUE, P_GREEN, P_GOLD = "#fbe9e7", "#e8eff6", "#e6f1ea", "#faf1dd"


def save(fig, name):
    fig.savefig(os.path.join(BASE, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", name)


# ------------------------------------------------------------------ fig01 GEPF
def fig01():
    fig, ax = plt.subplots(figsize=(10.6, 6.2))
    fig.subplots_adjust(left=.03, right=.97, top=.88, bottom=.08)
    ax.set_xlim(-0.35, 10); ax.set_ylim(0, 6); ax.axis("off")

    def layer(y, h, fc, ec, title, sub, items):
        ax.add_patch(FancyBboxPatch((0.55, y), 7.3, h, boxstyle="round,pad=.05,rounding_size=.12",
                                    fc=fc, ec=ec, lw=1.5))
        ax.text(0.80, y + h - .22, title, fontsize=11, fontweight="bold", color=ec, va="top")
        ax.text(0.80, y + h - .50, sub, fontsize=8.2, color="#444444", va="top")
        for i, t in enumerate(items):
            ax.text(0.80 + i * 1.78, y + .22, t, fontsize=8.2, color="#222222")

    layer(4.30, 1.30, P_RED, RED, "F　财政—制度（快层，十年—百年）",
          "驿费、商税、区划、地名编码", ["驿传支出", "税基与商税", "撤县设市／并镇", "地名保护名录"])
    layer(2.45, 1.30, P_GOLD, GOLD, "E　经济（中层，百年—数百年）",
          "商品流、市场网络、产业", ["黑茶／花炮／矿产", "商驿与转运", "墟市与商号", "陆水联运"])
    layer(0.60, 1.30, P_GREEN, GREEN, "G／P　地理—人口（底层，数百年—千年）",
          "山河、驿道、河道；镇村、人口", ["湘江与捞刀河", "驿道与驿铺", "镇村体系", "人口分布"])

    # up arrows in the gaps, labels horizontal to the right
    for x, y1, y2, lab in [(2.55, 1.95, 2.40, "运输成本↓ → 市场半径↑"),
                           (2.55, 3.80, 4.25, "税基↑ → 驿道投资")]:
        ax.add_patch(FancyArrowPatch((x, y1), (x, y2), arrowstyle="-|>", mutation_scale=14,
                                     lw=1.6, color=GRAY))
        ax.text(x + .15, (y1 + y2) / 2, lab, va="center", ha="left", fontsize=7.8, color=GRAY)
    ax.add_patch(FancyArrowPatch((6.3, 3.80), (6.3, 4.25), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.6, color=GRAY))
    ax.text(6.45, 4.02, "商税与驿费", va="center", ha="left", fontsize=7.8, color=GRAY)
    ax.add_patch(FancyArrowPatch((6.3, 1.95), (6.3, 2.40), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.6, color=GRAY))
    ax.text(6.45, 2.17, "墟市与商号", va="center", ha="left", fontsize=7.8, color=GRAY)

    # feedback on the left, outside the boxes
    ax.add_patch(FancyArrowPatch((0.22, 4.95), (0.22, 1.25), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.4, color=RED, linestyle="--",
                                 connectionstyle="arc3,rad=.0"))
    ax.text(0.10, 3.10, "区划调整、地名编码", rotation=90, va="center", ha="right",
            fontsize=7.8, color=RED)

    ax.annotate("", xy=(9.05, 5.55), xytext=(9.05, 0.65),
                arrowprops=dict(arrowstyle="<->", color="#7b4b94", lw=1.6))
    ax.text(9.25, 3.10, "τ ＝ 制度调整时间 ／ 市场变化时间（层间错配）", rotation=90,
            va="center", fontsize=8.2, color="#7b4b94")

    ax.text(0.55, 5.78, "重置：铁路、裁驿（1913）、撤县设市（1993／2017）", fontsize=8.6, color="#444444")
    ax.set_title("图1　GEPF 三层模型：慢的地缘—人口，中的经济，快的制度", fontsize=12.5,
                 fontweight="bold", loc="left")
    ax.text(0.55, 0.20, "注：层间箭头是机制假设，不是已估计的路径系数；τ 的方向来自《错位的时间》第 2.7、8 章。",
            fontsize=7.6, color="#666666")
    save(fig, "fig01.png")


# ------------------------------------------------------------------ fig02 prefectures
def fig02():
    names = ["长沙", "永州", "常德", "衡州", "岳州"]
    shops = [186, 106, 60, 44, 35]
    land = [85, 50, 40, 30, 30]
    water = [15, 50, 60, 70, 70]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    fig.subplots_adjust(left=.09, right=.97, top=.86, bottom=.16)
    ax.bar(x, shops, width=.6, color=GOLD, alpha=.85)
    for i, v in enumerate(shops):
        ax.text(i, v + 4, str(v), ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylabel("驿铺数（B/C 级估计）", fontsize=9.6)
    ax.set_ylim(0, 215); ax.grid(alpha=.2, axis="y")
    ax.set_title("图2　五府驿铺数与水陆配置", fontsize=12.5, fontweight="bold", loc="left")
    ax2 = ax.twinx()
    ax2.plot(x, water, "o-", color=BLUE, lw=1.8, label="水运占比")
    ax2.set_ylim(0, 100); ax2.set_ylabel("水运占比（%）", fontsize=9.6, color=BLUE)
    ax2.tick_params(axis="y", colors=BLUE)
    ax2.legend(fontsize=8, loc="upper right", frameon=False)
    fig.text(.5, .03, "注：长沙 186 为已确认下限；其余四府按府志逐条统计。水运占比为 B/C 级估计。",
             ha="center", fontsize=7.6, color="#666666")
    save(fig, "fig02.png")


# ------------------------------------------------------------------ fig03 flows
def fig03():
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    fig.subplots_adjust(left=.03, right=.97, top=.86, bottom=.12)
    ax.set_xlim(-0.35, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.add_patch(FancyBboxPatch((4.05, 2.45), 1.9, .9, boxstyle="round,pad=.06,rounding_size=.12",
                                fc=P_GOLD, ec=GOLD, lw=1.6))
    ax.text(5.0, 2.90, "长沙总枢纽", ha="center", va="center", fontsize=10.5,
            fontweight="bold", color="#6b4a0f")

    flows = [("安化黑茶\n600 万两", 1.4, 4.6, 1.0, BLUE, "经益阳转水运"),
             ("浏阳花炮\n280 万两", 8.5, 4.4, .7, RED, "东线陆运"),
             ("衡州矿产\n500 万两", 8.5, 1.4, .9, GREEN, "南线水陆并行"),
             ("常德粮食\n250 万两", 1.4, 1.4, .6, GOLD, "西洞庭水运")]
    for lab, x, y, w, col, note in flows:
        ax.annotate("", xy=(4.05 if x < 5 else 5.95, 2.9), xytext=(x + (1.0 if x < 5 else -1.0), y),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1 + 3 * w, alpha=.55,
                                    connectionstyle="arc3,rad=%.2f" % (0.15 if x < 5 else -0.15),
                                    shrinkA=4, shrinkB=18))
        ax.text(x, y + .35, lab, ha="center", va="bottom", fontsize=8.6, fontweight="bold", color=col)
        ax.text(x, y - .42, note, ha="center", va="top", fontsize=7.4, color="#555555")

    ax.text(0.2, 5.75, "图3　商品流向与节点流量（B 级估计，线宽示意交易额）", fontsize=12.5,
            fontweight="bold")
    ax.text(.2, .35, "注：交易额为量级估计，不等于增加值；四线合计约 1,630 万两，与全省 2,000—3,000 万两不冲突。",
            fontsize=7.6, color="#666666")
    save(fig, "fig03.png")


# ------------------------------------------------------------------ fig04 distance
def fig04():
    lines = ["北线（官驿）", "西线（黑茶）", "东线（花炮）", "南线（矿产）"]
    dist = [9.0, 4.1, 3.7, 5.5]
    cv = [.15, .18, .21, .25]
    trade = [50, 600, 280, 500]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.4, 4.4),
                                 gridspec_kw={"width_ratios": [1, 1.15]})
    fig.subplots_adjust(left=.08, right=.98, top=.82, bottom=.20, wspace=.30)
    cols = [RED, BLUE, GREEN, GOLD]
    x = np.arange(4)
    ax.bar(x, dist, yerr=[d * c for d, c in zip(dist, cv)], capsize=4,
           color=cols, alpha=.8, width=.6)
    for i, d in enumerate(dist):
        ax.text(i, d + .45, "%.1f" % d, ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(["北", "西", "东", "南"])
    ax.set_ylabel("镇间道路距离（km，均值±变异）", fontsize=9.2)
    ax.set_ylim(0, 11); ax.grid(alpha=.2, axis="y")
    ax.set_title("(a) 四条线路的镇间距离", fontsize=10.5, fontweight="bold", loc="left")

    for i in range(4):
        bx.scatter(dist[i], trade[i], s=90, color=cols[i], edgecolor="white", zorder=3)
        bx.annotate(lines[i], (dist[i], trade[i]), xytext=(7, 6), textcoords="offset points",
                    fontsize=8.2)
    bx.set_xlabel("镇间道路距离（km）", fontsize=9.2)
    bx.set_ylabel("年交易额（万两，B/C 级）", fontsize=9.2)
    bx.set_xlim(2.5, 10.5); bx.set_ylim(0, 720); bx.grid(alpha=.2)
    bx.set_title("(b) 距离与交易额不呈单调关系", fontsize=10.5, fontweight="bold", loc="left")
    fig.suptitle("图4　镇间密度与商品类型：易损性与批次频率比交易额更能解释密度",
                 fontsize=12, fontweight="bold", y=.98)
    fig.text(.5, .03, "注：距离为现代镇间道路距离（约 16—20 里），不是驿制间距（驿 30 里、铺 10 里）；n=4，只作描述。",
             ha="center", fontsize=7.4, color="#666666")
    save(fig, "fig04.png")


# ------------------------------------------------------------------ fig05 cost
def fig05():
    items = ["驿马", "驿夫", "驿铺", "驿船"]
    vals = [160000, 9000, 5100, 750]
    total = sum(vals)
    share = [v / total * 100 for v in vals]
    cols = [RED, GOLD, GREEN, BLUE]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.4),
                                   gridspec_kw={"width_ratios": [1.45, 1]})
    fig.subplots_adjust(left=.12, right=.98, top=.755, bottom=.20, wspace=.34)

    # (a) absolute values on a log axis, so 750 and 160000 are both readable
    y = np.arange(len(items))[::-1]
    ax1.barh(y, vals, color=cols, alpha=.85, height=.55)
    ax1.set_xscale("log")
    ax1.set_yticks(y); ax1.set_yticklabels(items, fontsize=9.2)
    ax1.set_xlim(300, 400000)
    for yy, v, sh in zip(y, vals, share):
        ax1.text(v * 1.15, yy, "%s 两（%.1f%%）" % (format(v, ","), sh), va="center", fontsize=8.4)
    ax1.set_xlabel("年费（两，对数轴）", fontsize=9.2)
    ax1.grid(alpha=.2, axis="x")
    ax1.set_title("(a) 分项年费", fontsize=10.4, fontweight="bold", loc="left")

    # (b) shares, with small slices labelled outside
    wedges, _ = ax2.pie(vals, colors=cols, startangle=90, counterclock=False,
                        wedgeprops=dict(width=.42, edgecolor="white", linewidth=1.2))
    ax2.text(0, 0, "合计\n17.5 万两", ha="center", va="center", fontsize=8.6, color="#333333")
    # dominant slice labelled inside the ring; small slices in one line below
    w = wedges[0]
    ang = np.deg2rad((w.theta1 + w.theta2) / 2)
    ax2.text(np.cos(ang) * .78, np.sin(ang) * .78, "驿马 91.5%", ha="center", va="center",
             fontsize=8.4, color="white", fontweight="bold")
    ax2.text(0, -1.34, "驿夫 5.1%｜驿铺 2.9%｜驿船 0.4%", ha="center", va="center",
             fontsize=7.8, color="#444444")
    ax2.set_aspect("equal")
    ax2.set_title("(b) 支出结构", fontsize=10.4, fontweight="bold", loc="left")

    fig.suptitle("图5　年支出结构（合计约 174,850 两）", fontsize=12.2, fontweight="bold", y=.975)
    fig.text(.5, .055, "交易额 2,000 万两 ÷ 支出 17.5 万两 ≈ 114 : 1（这不是社会收益—成本比）",
             ha="center", fontsize=8.6, color="#333333")
    fig.text(.5, .015, "注：驿马单价与数量为 B/C 级估计；支出为九府四州合计。",
             ha="center", fontsize=7.4, color="#666666")
    save(fig, "fig05.png")


# ------------------------------------------------------------------ fig06 toponym
def fig06():
    T = np.array([0, 9, 33, 34, 32, 70])
    ret = np.array([52, 95, 18, 55, 72, 11])
    names = ["长沙县", "宁乡", "浏阳", "湘潭", "茶陵", "衡州"]
    X = np.column_stack([np.ones_like(T), T])
    beta, *_ = np.linalg.lstsq(X, ret, rcond=None)
    pred = X @ beta
    r2 = 1 - ((ret - pred) ** 2).sum() / ((ret - ret.mean()) ** 2).sum()

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.6, 4.4),
                                 gridspec_kw={"width_ratios": [1.15, 1]})
    fig.subplots_adjust(left=.08, right=.98, top=.82, bottom=.20, wspace=.28)
    tt = np.linspace(-3, 75, 100)
    ax.plot(tt, beta[0] + beta[1] * tt, color=RED, lw=2,
            label="OLS：y = %.1f − %.2f T（R² = %.2f）" % (beta[0], -beta[1], r2))
    ax.scatter(T, ret, s=70, color=BLUE, edgecolor="white", zorder=3)
    for x, y, n in zip(T, ret, names):
        if n == "宁乡":
            ax.annotate(n, (x, y), xytext=(8, 6), textcoords="offset points", fontsize=8.4,
                        color=RED, fontweight="bold")
        else:
            ax.annotate(n, (x, y), xytext=(6, -12), textcoords="offset points", fontsize=7.8)
    ax.set_xlabel("撤县／设市至 2026 年（年）", fontsize=9.2)
    ax.set_ylabel("驿铺地名保留率（%）", fontsize=9.2)
    ax.set_xlim(-4, 78); ax.set_ylim(0, 108); ax.grid(alpha=.2)
    ax.legend(fontsize=7.8, frameon=False, loc="upper right")
    ax.set_title("(a) 截面关系（n=6）：方向为负，斜率不显著", fontsize=10.2, fontweight="bold", loc="left")

    order = np.argsort(ret)
    bx.barh([names[i] for i in order], ret[order],
            color=[RED if names[i] == "宁乡" else BLUE for i in order], alpha=.75)
    for i, v in zip(range(len(order)), ret[order]):
        bx.text(v + 2, i, "%d%%" % v, va="center", fontsize=8)
    bx.set_xlim(0, 110); bx.set_xlabel("保留率（%）", fontsize=9.2)
    bx.grid(alpha=.2, axis="x")
    bx.set_title("(b) 六县对比", fontsize=10.2, fontweight="bold", loc="left")
    fig.suptitle("图6　地名保留率：县际截面，方向负但斜率不显著", fontsize=12,
                 fontweight="bold", y=.98)
    fig.text(.5, .03, "注：OLS 斜率 %.2f（95%% CI %.2f—%.2f），R² = %.2f；n=6，只作方向，不能读成“每年下降 %.2f%%”。"
             % (beta[1], -1.95, 0.17, r2, -beta[1]),
             ha="center", fontsize=7.2, color="#666666")
    save(fig, "fig06.png")


# ------------------------------------------------------------------ fig07 time
def fig07():
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(10.6, 6.6),
                                 gridspec_kw={"height_ratios": [1.1, 1], "hspace": .55})
    fig.subplots_adjust(left=.09, right=.97, top=.88, bottom=.12)

    phases = [(1368, 1450, "扩张"), (1450, 1700, "官商分化"), (1700, 1840, "均衡"),
              (1840, 1911, "替代"), (1911, 1949, "裁驿"), (1949, 1978, "重组"),
              (1978, 2026, "地名侵蚀")]
    cols = [GOLD, GREEN, BLUE, "#7b4b94", GRAY, "#8fa8c4", RED]
    for (s, e, lab), c in zip(phases, cols):
        ax.axvspan(s, e, color=c, alpha=.18, lw=0)
        ax.text((s + e) / 2, 575, lab, ha="center", va="bottom", fontsize=7.8, color="#333333",
                rotation=0)
    ax.plot([1368, 1450, 1700, 1840, 1911, 1949, 1978, 2026],
            [80, 510, 500, 510, 300, 150, 120, 100], "-o", color=RED, lw=2, ms=4)
    ax.set_xlim(1360, 2032); ax.set_ylim(0, 640)
    ax.set_ylabel("驿铺数（估计）", fontsize=9.2)
    ax.set_xlabel("公元", fontsize=9.2)
    ax.set_title("(a) 三百年：驿铺数量（B/C 级估计）与阶段", fontsize=10.4,
                 fontweight="bold", loc="left")
    ax.grid(alpha=.15, axis="x")

    t = np.linspace(1840, 1960, 300)
    n = 512 / (1 + np.exp(.104 * (t - 1912)))
    bx.plot(t, n, color=RED, lw=2.2, label="Logistic 拟合：512 / (1+e^{0.104(t−1912)})")
    pts = [(1840, 510), (1895, 440), (1925, 100), (1949, 30)]
    bx.scatter([p[0] for p in pts], [p[1] for p in pts], color=BLUE, zorder=3, s=45,
               label="四个时点的量级估计")
    bx.axvline(1913, color=GRAY, ls="--", lw=1)
    bx.text(1915, 420, "1913 裁驿", fontsize=8, color=GRAY)
    bx.set_xlabel("年份", fontsize=9.2); bx.set_ylabel("驿铺数", fontsize=9.2)
    bx.set_ylim(0, 560); bx.grid(alpha=.2)
    bx.legend(fontsize=7.6, frameon=False, loc="upper right")
    bx.set_title("(b) 替代的 S 型：曲线是拟合，不是实测", fontsize=10.4,
                 fontweight="bold", loc="left")
    fig.suptitle("图7　三百年演化与 1913 年的重置", fontsize=12.5, fontweight="bold", y=.97)
    save(fig, "fig07.png")


if __name__ == "__main__":
    print("building Hunan figures ...")
    for f in [fig01, fig02, fig03, fig04, fig05, fig06, fig07]:
        f()
    print("done")

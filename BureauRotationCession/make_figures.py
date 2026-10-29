# -*- coding: utf-8 -*-
"""Generate fig01.png ... fig12.png and cases.csv for the paper.

Design rules (after a first draft produced overlapping labels):
  * one idea per figure; annotations live in their own empty zone;
  * no rotated text over arrows or over other text;
  * long explanations go to the figure caption (in the paper), not the canvas.

Run:  python make_figures.py
"""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from matplotlib.ticker import FuncFormatter

plt.rcParams.update({
    "font.family": ["SimHei", "Microsoft YaHei"],
    "axes.unicode_minus": False,
    "figure.dpi": 180,
    "savefig.dpi": 180,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "font.size": 10,
    "figure.facecolor": "white",
})

BASE = os.path.dirname(os.path.abspath(__file__))

RED, BLUE, GREEN, GOLD, GRAY = "#b3261e", "#1f4e79", "#2e6b4f", "#a8791f", "#5f6368"
P_RED, P_BLUE, P_GREEN, P_GOLD = "#fbe9e7", "#e8eff6", "#e6f1ea", "#faf1dd"
PATH_CN = {"ritual": "礼制与相职", "inner": "内廷（侍从型）",
           "outer": "外派（监察副贰型）", "military": "军职型"}
PATH_COL = {"ritual": GOLD, "inner": RED, "outer": BLUE, "military": GREEN}
PATH_SHORT = {"ritual": "礼制·相职", "inner": "内廷", "outer": "外派", "military": "军职"}

from data_cases import CASES, PERIODS  # noqa: E402

PATH_CN = {"ritual": "礼制与相职", "inner": "内廷（侍从型）",
           "outer": "外派（监察副贰型）", "military": "军职型"}
PATH_COL = {"ritual": GOLD, "inner": RED, "outer": BLUE, "military": GREEN}
PATH_SHORT = {"ritual": "礼制·相职", "inner": "内廷", "outer": "外派", "military": "军职"}

def save(fig, name):
    fig.savefig(os.path.join(BASE, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", name)


def card(ax, x, y, w, h, fc, ec, title, body, tcol, tsize=11, bsize=8.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc=fc, ec=ec, lw=1.3, transform=ax.transAxes, zorder=1))
    ax.text(x + 0.03, y + h - 0.055, title, transform=ax.transAxes, fontsize=tsize,
            fontweight="bold", color=tcol, va="top", zorder=2)
    ax.text(x + 0.03, y + h - 0.125, body, transform=ax.transAxes, fontsize=bsize,
            color="#333333", va="top", linespacing=1.55, zorder=2)


def write_cases():
    with open(os.path.join(BASE, "cases.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "官职", "时期", "路径", "起家年", "正官化/常设/失控年", "退出年",
                    "保", "让", "触发事件", "结局", "结局类型", "等级", "核心案例"])
        for c in CASES:
            w.writerow([c[0], c[1], c[2], PATH_CN[c[3]], c[4], c[5], c[6], c[7], c[8],
                        c[9], c[10], c[11], c[12], "是" if c[13] else ""])
    print("   cases.csv  (n=%d)" % len(CASES))


# ------------------------------------------------------------------ fig01
def fig01():
    fig = plt.figure(figsize=(10.6, 6.4))
    ax = fig.add_axes([0.01, 0.10, 0.60, 0.78])
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    C_, A_, T_ = np.array([0.50, 0.90]), np.array([0.09, 0.12]), np.array([0.91, 0.12])
    ax.add_patch(Polygon([C_, A_, T_], closed=True, fc="#fcfcfc", ec="#b0b0b0", lw=1.1, ls="--"))

    # inner frontier: two shrunk triangles, visually nested and clearly labelled once
    cen = np.array([0.50, 0.38])
    for s in (0.80, 0.60):
        pts = [cen + s * (V - cen) for V in (C_, A_, T_)]
        ax.add_patch(Polygon(pts, closed=True, fill=False, ec=GOLD, lw=1.0, alpha=0.55))

    ax.text(0.50, 0.335, "ψ > 0：可达前沿向内收缩", ha="center", va="center",
            fontsize=9.2, color=GOLD)

    for V, name, ha, va, dx, dy in [
            (C_, "C　看得准", "center", "bottom", 0.00, 0.035),
            (A_, "A　拼得上", "center", "top", 0.00, -0.035),
            (T_, "T　传得下去", "center", "top", 0.00, -0.035)]:
        ax.plot([V[0]], [V[1]], "o", ms=9, color="#222222", zorder=5)
        ax.text(V[0] + dx, V[1] + dy, name, ha=ha, va=va, fontsize=13.5, fontweight="bold")

    # edge labels, placed on the edges but pushed toward the centroid, no overlaps
    def edge_label(P, Q, text, col, rot, frac=0.52, off=0.055):
        M = P + frac * (Q - P)
        d = cen - M
        d = d / np.linalg.norm(d) * off
        ax.text(M[0] + d[0], M[1] + d[1], text, rotation=rot, ha="center", va="center",
                fontsize=9.6, color=col, fontweight="bold",
                bbox=dict(fc="white", ec="none", pad=1.2))

    edge_label(A_, T_, "正官体系：保 A、T，让出 C", GRAY, 0, frac=0.5, off=0.075)
    edge_label(C_, A_, "内廷：保 C、T，让出 A", RED, 58, frac=0.50, off=0.050)
    edge_label(C_, T_, "外派：保 C、A，让出 T", BLUE, -58, frac=0.50, off=0.050)

    # right-hand cards (three paths + one note), no text over the triangle
    axr = fig.add_axes([0.635, 0.10, 0.35, 0.80]); axr.axis("off")
    axr.set_xlim(0, 1); axr.set_ylim(0, 1)
    axr.text(0, 0.985, "三条路径，各让出一项", fontsize=11.5, fontweight="bold", va="top")
    card(axr, 0.00, 0.745, 1.00, 0.205, P_GRAY := "#f1f1f1", "#9e9e9e",
         "正官体系　保 A、T", "品秩、编制、职掌齐备；程序繁复、层级多。\n"
         "账单：对具体事务既慢又远 → 三公虚化、尚书台阁化。", GRAY)
    card(axr, 0.00, 0.505, 1.00, 0.205, P_RED, RED,
         "内廷使职　保 C、T", "近侍、文书、宦官：信息直达，诏令由此出入。\n"
         "账单：不入正官体系，难与既有体制拼合。", RED)
    card(axr, 0.00, 0.265, 1.00, 0.205, P_BLUE, BLUE,
         "外派使职　保 C、A", "监察、都督、节度：贴近地方，兼理军民财政。\n"
         "账单：中央政令难达，T 崩塌即割据。", BLUE)
    axr.text(0.0, 0.215, "共同机制：想补第三项，就必须支付起家时依赖的那一项。",
             fontsize=8.8, color="#444444", va="top", wrap=True)
    axr.text(0.0, 0.150, "所以“禁戒”只能关掉一个名，关不掉让渡本身。",
             fontsize=8.8, color="#444444", va="top")

    fig.suptitle("图1　官制的三项要求与三条路径：至多同时满足两项", fontsize=13,
                 fontweight="bold", y=0.965)
    fig.text(0.5, 0.035, "注：三角是组织坐标，不是可行域的精确形状；ψ>0 是三角成立的条件，ψ≈0 时三项可同时逼近满格。",
             ha="center", fontsize=8, color="#666666")
    save(fig, "fig01.png")


# ------------------------------------------------------------------ fig07
def fig07():
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    fig.subplots_adjust(left=0.11, right=0.98, top=0.86, bottom=0.16)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])

    for (x0, y0, fc, ec) in [(0, 1, P_GREEN, GREEN), (1, 1, P_RED, RED),
                             (0, 0, "#f2f2f2", "#b5b5b5"), (1, 0, P_BLUE, BLUE)]:
        ax.add_patch(Rectangle((x0, y0), 1, 1, fc=fc, ec=ec, lw=1.2))

    data = [
        (0.06, 1.90, "有兵权 · 无诏令权", GREEN, "大将军　中领军　都督\n节度使（未兼枢密）"),
        (1.06, 1.90, "诏令权 + 兵权", RED, "曹操　司马昭　刘裕　赵匡胤\n神策中尉（唐末）"),
        (0.06, 0.90, "两项皆无", GRAY, "正官 · 三公 · 九卿"),
        (1.06, 0.90, "有诏令权 · 无兵权", BLUE, "尚书　中书　门下　翰林\n内阁　司礼监　军机处"),
    ]
    for x, y, t, col, ex in data:
        ax.text(x, y, t, fontsize=12, fontweight="bold", color=col, va="top")
        ax.text(x, y - 0.42, ex, fontsize=8.6, color="#333333", va="top", linespacing=1.7)

    ax.text(0.06, 0.14, "保 A、T，让出 C", fontsize=9, color=GRAY)
    ax.text(1.06, 0.14, "军权 = C＋A；诏令权 = C＋T\n两权交集是 C；重合者占满三项", fontsize=9, color=RED)

    ax.axhline(1, color="#333333", lw=1.3)
    ax.axvline(1, color="#333333", lw=1.3)
    ax.set_xlabel("诏令权（C＋T）　→", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("兵权（C＋A）　→", fontsize=10.5, fontweight="bold")

    fig.suptitle("图7　诏令权与兵权的四象限：两权合一即占满三项", fontsize=13,
                 fontweight="bold", y=0.955)
    fig.text(0.5, 0.045, "注：中古的禅代多循“先录尚书事（诏令）、再大将军／都督中外诸军事（兵权）、"
                         "后相国加九锡”的顺序；该顺序是路径描述，不是充分条件。",
             ha="center", fontsize=8, color="#666666")
    save(fig, "fig07.png")


# ------------------------------------------------------------------ fig04
def fig04():
    """Swimlane grid: rows = lines, columns = eras. Labels never collide by construction."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.2, 8.6),
                                   gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.46})
    fig.subplots_adjust(left=0.10, right=0.985, top=0.885, bottom=0.10)

    def swim(ax, cols, lanes, cells, title):
        n, m = len(lanes), len(cols)
        for j in range(m + 1):
            ax.axvline(j - 0.5, color="#ececec", lw=0.8, zorder=0)
        for i in range(n + 1):
            ax.axhline(i - 0.5, color="#ececec", lw=0.8, zorder=0)
        for i, (name, col) in enumerate(lanes):
            ax.text(-0.62, n - 1 - i, name, ha="right", va="center", fontsize=9.6,
                    fontweight="bold", color=col)
        for (i, j), items in cells.items():
            col = lanes[i][1]
            y = n - 1 - i
            for k, t in enumerate(items):
                ax.text(j, y + (0.19 if k == 0 else -0.05), t, ha="center", va="center",
                        fontsize=7.8, color="#222222")
        for j, c in enumerate(cols):
            ax.text(j, n - 0.30, c, ha="center", va="bottom", fontsize=8.4, color="#444444")
        ax.set_xlim(-0.5, m - 0.5); ax.set_ylim(-0.55, n - 0.10)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ["top", "right", "left", "bottom"]:
            ax.spines[s].set_visible(False)
        ax.set_title(title, loc="left", fontsize=11, fontweight="bold")

    cols1 = ["西周", "春秋战国", "秦汉", "魏晋", "南北朝", "隋唐前期",
             "中晚唐", "五代", "宋", "元", "明", "清"]
    lanes1 = [("正官·礼制", GOLD), ("内廷线", RED), ("外派线", BLUE), ("军职线", GREEN)]
    cells1 = {
        (0, 0): ["宗法封建"], (0, 1): ["世卿世禄", "谷禄官僚"], (0, 2): ["三公九卿", "察举"],
        (0, 3): ["九品中正"], (0, 4): ["门下审署"], (0, 5): ["三省六部"],
        (0, 6): ["使职化"], (0, 8): ["官职差遣"], (0, 9): ["行省"], (0, 10): ["废丞相"],
        (0, 11): ["九品十八阶"],
        (1, 2): ["尚书", "领尚书事"], (1, 3): ["中书监", "侍中"],
        (1, 4): ["中书舍人", "典签"], (1, 5): ["同平章事", "翰林"],
        (1, 6): ["枢密使", "神策中尉"], (1, 7): ["枢密使"], (1, 8): ["翰林", "二府"],
        (1, 10): ["内阁", "司礼监"], (1, 11): ["南书房", "军机处"],
        (2, 1): ["郡守", "监御史"], (2, 2): ["刺史", "州牧"], (2, 3): ["都督"],
        (2, 4): ["行台", "典签"], (2, 5): ["节度使", "转运使"],
        (2, 6): ["节度使", "监军"], (2, 8): ["通判", "转运使"],
        (2, 10): ["巡抚", "巡按"], (2, 11): ["总督", "藩臬"],
        (3, 2): ["期门·羽林", "八校尉"], (3, 3): ["领军·护军"], (3, 4): ["领军"],
        (3, 5): ["府兵·十六卫"], (3, 6): ["神策军"], (3, 7): ["殿前都点检"],
        (3, 8): ["三衙"], (3, 10): ["五军都督府"], (3, 11): ["八旗·绿营"],
    }
    swim(ax1, cols1, lanes1, cells1, "（a）前 1046 — 1911：同一单元格里，往往是两三条线同时在长")

    cols2 = ["1901—1911", "1912—1927", "1928—1949", "1950—1977",
             "1978—1992", "1993—2012", "2013—2026"]
    lanes2 = [("机构", GOLD), ("人事", RED), ("监察", BLUE), ("技术 τ", GREEN)]
    cells2 = {
        (0, 0): ["督办政务处", "责任内阁"], (0, 1): ["国务院制"], (0, 2): ["五院"],
        (0, 3): ["政务院→国务院"], (0, 4): ["机构改革"], (0, 5): ["大部制"],
        (0, 6): ["监察委", "机构改革"],
        (1, 0): ["废科举", "留学选官"], (1, 1): ["文官考试"], (1, 2): ["铨叙部"],
        (1, 3): ["干部管理"], (1, 4): ["公务员条例"], (1, 5): ["公务员法"],
        (1, 6): ["职务职级并行"],
        (2, 0): ["都察院改"], (2, 1): ["监察院"], (2, 2): ["中统", "军统"],
        (2, 3): ["纪委"], (2, 4): ["监察部"], (2, 5): ["巡视"], (2, 6): ["监察委", "派驻"],
        (3, 0): ["电报"], (3, 1): ["电话"], (3, 2): ["无线电"], (3, 3): ["电话网"],
        (3, 4): ["传真"], (3, 5): ["互联网"], (3, 6): ["移动政务"],
    }
    swim(ax2, cols2, lanes2, cells2, "（b）1901 — 2026：现代转型的四条线")

    fig.suptitle("图4　官制流变的事件网格：每一格是“谁在长”，不是“谁取代谁”", fontsize=13,
                 fontweight="bold", y=0.96)
    fig.text(0.5, 0.025, "注：按时代分列，格内列出该时代活跃的主要官称；同一官职可跨列存续，"
                         "此图只标“首次出现或转折”。“典签”同时属内廷与外派，按其主要功能两列并见。",
             ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig04.png")


# ------------------------------------------------------------------ fig05
def fig05():
    """Period summary: how many cases in each period retain C / A / T."""
    rows = []
    for p in PERIODS:
        cs = [c for c in CASES if c[2] == p]
        if not cs:
            continue
        n = len(cs)
        share = []
        for key in ["C", "A", "T"]:
            k = sum(1 for c in cs if key in c[7])
            share.append(k / n)
        rang = {}
        for c in cs:
            for t in ("C", "A", "T"):
                if t in c[8]:
                    rang[t] = rang.get(t, 0) + 1
        main_rang = max(rang, key=rang.get) if rang else "—"
        reps = "、".join(c[1] for c in cs[:2])
        rows.append((p, n, share, main_rang, reps, cs[0][3]))

    H = len(rows) + 2.2
    fig, ax = plt.subplots(figsize=(10.6, 9.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.07)
    ax.set_xlim(0, 10.4); ax.set_ylim(0, H); ax.axis("off")

    xs = {"时期": 0.10, "n": 3.30, "C": 3.95, "A": 4.95, "T": 5.95, "让出(主频)": 6.95, "代表官职": 7.75}
    top = H - 0.55
    for k, x in xs.items():
        ax.text(x, top, k, fontsize=9.6, fontweight="bold",
                ha="left" if k in ("时期", "代表官职") else "center")
    ax.plot([0.10, 10.30], [top - 0.30, top - 0.30], color="#999999", lw=1.0)

    y = top - 0.95
    for p, n, share, main_rang, reps, path in rows:
        ax.text(xs["时期"], y, p, fontsize=8.6, va="center",
                color=PATH_COL[path], fontweight="bold")
        ax.text(xs["n"], y, str(n), fontsize=8.4, va="center", ha="center")
        for key, s in zip(["C", "A", "T"], share):
            ax.add_patch(Rectangle((xs[key] - 0.42, y - 0.34), 0.84, 0.68,
                                   fc=plt.cm.Greens(0.12 + 0.70 * s), ec="white", lw=1.2))
            ax.text(xs[key], y, "%d%%" % round(100 * s), fontsize=7.8, ha="center",
                    va="center", color=("#10351f" if s > 0.55 else "#333333"))
        ax.text(xs["让出(主频)"], y, main_rang, fontsize=8.4, va="center", ha="center",
                color="#444444")
        ax.text(xs["代表官职"], y, reps, fontsize=7.4, va="center")
        y -= 1.0

    fig.suptitle("图5　分期编码汇总（n=%d）：每一期里，哪一项最常被让出" % len(CASES),
                 fontsize=13, fontweight="bold", y=0.963)
    fig.text(0.5, 0.022, "注：C／A／T 列为该时期案例中“保有该项”的比例（同一案例可同时保两项，故三列不互补）；"
                         "“让出”为主频项。逐案编码见附录 A 与 cases.csv。",
             ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig05.png")


# ------------------------------------------------------------------ fig02
def fig02():
    def psi(c, a, t):
        return (c * a + a * t + c * t) / 3.0

    def max_sum(lam, K):
        g = np.linspace(0, 1, 121)
        C, A = np.meshgrid(g, g)
        best = 0.0
        for c, a in zip(C.ravel(), A.ravel()):
            lo, hi = 0.0, 1.0
            for _ in range(40):
                mid = (lo + hi) / 2
                if c + a + mid + lam * psi(c, a, mid) <= K:
                    lo = mid
                else:
                    hi = mid
            best = max(best, c + a + lo)
        return best

    lams = np.linspace(0, 0.6, 25)
    sums3 = [max_sum(l, 3.0) for l in lams]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.9),
                                   gridspec_kw={"width_ratios": [1.05, 1]})
    fig.subplots_adjust(left=0.085, right=0.985, top=0.80, bottom=0.16, wspace=0.20)

    ax1.plot(lams, sums3, color=RED, lw=2.4)
    ax1.axhline(3, color="#9e9e9e", lw=0.9, ls=":")
    ax1.set_xlabel("交互惩罚强度 λ", fontsize=9.8)
    ax1.set_ylabel("可达的最大 c + a + t", fontsize=9.8)
    ax1.set_ylim(2.35, 3.10); ax1.set_xlim(0, 0.62)
    ax1.grid(alpha=0.20)
    ax1.set_title("(a) 记账不等式：ψ>0 时满格不可达", fontsize=10.6,
                  fontweight="bold", loc="left")
    ax1.text(0.03, 3.055, "λ = 0：三项可同时满格（三角不成立）", fontsize=8.2, color=RED)
    ax1.text(0.035, 2.44, "缺口随 λ 扩大", fontsize=8.2, color=RED)
    ax1.text(0.30, 2.38, "c + a + t + λψ ≤ K", fontsize=10, color="#333333",
             bbox=dict(fc="#f4f4f4", ec="#cccccc", pad=4))

    ax2.set_xlim(0, 1); ax2.set_ylim(-0.12, 1.0); ax2.axis("off")
    nodes = {"CT": (0.50, 0.86, "内廷　C＋T", "让出 A", RED, P_RED),
             "AT": (0.12, 0.16, "正官　A＋T", "让出 C", GRAY, "#f1f1f1"),
             "CA": (0.88, 0.16, "外派　C＋A", "让出 T", BLUE, P_BLUE)}
    for k, (x, y, t1, t2, col, fc) in nodes.items():
        ax2.text(x, y, t1 + "\n" + t2, ha="center", va="center", fontsize=9.2,
                 color=col, fontweight="bold", linespacing=1.7,
                 bbox=dict(boxstyle="round,pad=0.42,rounding_size=0.12", fc=fc, ec=col, lw=1.3))
    edges = [((0.50, 0.79), (0.12, 0.23), "共保 T", -0.055),
             ((0.50, 0.79), (0.88, 0.23), "共保 C", 0.055),
             ((0.22, 0.16), (0.78, 0.16), "共保 A", 0.055)]
    for (x1, y1), (x2, y2), lab, off in edges:
        ax2.annotate("", xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle="<->", color="#9e9e9e", lw=1.2,
                                     shrinkA=26, shrinkB=26))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = (y2 - y1), -(x2 - x1)
        n = (dx ** 2 + dy ** 2) ** 0.5
        ax2.text(mx + dx / n * off * 0.9, my + dy / n * off * 0.9, lab, fontsize=8.4,
                 color=GRAY, ha="center", va="center",
                 bbox=dict(fc="white", ec="none", pad=1.5))
    ax2.text(0.50, -0.03, "三条边 = 三种“两项组合”；补上第三项，就要换掉原来两项之一",
             ha="center", va="center", fontsize=8.6, color="#333333")
    ax2.text(0.50, -0.10, "轮换 = 在三边之间换位；禁戒 = 只拆掉其中一条边",
             ha="center", va="center", fontsize=8.2, color="#666666")
    ax2.set_title("(b) 轮换：三条边上只有两项，换位即换账", fontsize=10.6,
                  fontweight="bold", loc="left")

    fig.suptitle("图2　记账不等式与轮换的结构（a 为数值演示，b 为关系示意）", fontsize=12.5,
                 fontweight="bold", y=0.965)
    fig.text(0.5, 0.03, "注：ψ 取两两乘积的均值；λ 与 K 为归一化后的示意值，不代表任何实测代价。",
             ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig02.png")


# ------------------------------------------------------------------ fig06
def fig06():
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.6, 4.8))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.20, wspace=0.26)
    rng = np.random.default_rng(7)

    for path in ["inner", "outer", "military", "ritual"]:
        xs, ys = [], []
        for c in CASES:
            if c[3] != path:
                continue
            lag = c[5] - c[4]
            xs.append(c[4] + rng.normal(0, 14))
            ys.append(max(lag, 0.5))
        ax.scatter(xs, ys, s=34, color=PATH_COL[path], alpha=0.8,
                   edgecolor="white", lw=0.7, label=PATH_SHORT[path], zorder=3)
    ax.set_yscale("log")
    ax.set_xlim(-380, 2080)
    ax.set_xlabel("起家年代（公元，负数＝公元前）", fontsize=9.6)
    ax.set_ylabel("起家 → 正官化／常设化（年）", fontsize=9.6)
    ax.grid(alpha=0.20)
    ax.legend(fontsize=8.4, loc="upper right", frameon=False)
    ax.set_title("(a) 每个点是一个官职（n=%d）" % len(CASES), fontsize=10.5,
                 fontweight="bold", loc="left")

    data, labels, cols = [], [], []
    for path in ["inner", "outer", "military"]:
        data.append([max(c[5] - c[4], 0.5) for c in CASES if c[3] == path])
        labels.append(PATH_SHORT[path]); cols.append(PATH_COL[path])
    bp = bx.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.5,
                    medianprops=dict(color="#222222", lw=1.5))
    for patch, col in zip(bp["boxes"], cols):
        patch.set_facecolor(col); patch.set_alpha(0.30); patch.set_edgecolor(col)
    for i, d in enumerate(data):
        bx.scatter(np.full(len(d), i + 1) + rng.normal(0, 0.045, len(d)), d,
                   s=20, color=cols[i], alpha=0.75, zorder=3)
        bx.text(i + 1, 480, "n=%d" % len(d), ha="center", fontsize=8, color="#444444")
    bx.set_yscale("log"); bx.set_ylim(0.4, 800)
    bx.set_ylabel("年（对数轴）", fontsize=9.6)
    bx.set_title("(b) 两组中位数重叠：时滞不能区分路径", fontsize=10.5, fontweight="bold", loc="left")
    bx.grid(alpha=0.20, axis="y")

    fig.suptitle("图6　从起家到正官化的时滞（全样本；年代为约值）", fontsize=12.5,
                 fontweight="bold", y=0.96)
    fig.text(0.5, 0.03, "注：内廷中位数 34 年、外派 29 年（Mann–Whitney p≈0.33）：差异不显著，"
                        "故“内廷快、外派慢”作为假说被本样本打掉，时滞不能用作区分两条线的证据。",
             ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig06.png")


# ------------------------------------------------------------------ fig09
def fig09():
    d = np.linspace(0, 3000, 500)
    L, T_ev = 12.0, 60.0

    def tau(v):
        return (2 * d / v + L) / T_ev

    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.86, bottom=0.22)

    curves = [(90, "汉唐常驿　≈90 km/日", GOLD),
              (150, "宋元急脚　≈150 km/日", GREEN),
              (250, "唐宋急递　≈250 km/日", BLUE),
              (300, "清代加急　≈300 km/日", "#7b4b94")]
    for v, lab, col in curves:
        ax.plot(d, tau(v), color=col, lw=1.9, label=lab)
    ax.plot(d, np.full_like(d, L / T_ev), color=RED, lw=1.6, ls="--",
            label="电报以后：只剩组织时延 L/T")

    ax.axhline(1.0, color="#9e9e9e", lw=0.9)
    ax.fill_between(d, 0, 1, color=P_BLUE, alpha=0.55, lw=0)
    ax.fill_between(d, 1, 1.9, color=P_RED, alpha=0.50, lw=0)
    ax.text(2970, 1.16, "τ > 1：必须预先授权", ha="right", va="bottom", fontsize=9, color=RED)
    ax.text(2970, 0.16, "τ < 1：中央可亲裁", ha="right", va="center", fontsize=9, color=BLUE)

    for x, y, lab, dx, dy in [(1100, tau(250)[np.argmin(abs(d - 1100))], "范阳—长安（755）", -90, 0.22),
                              (1900, tau(300)[np.argmin(abs(d - 1900))], "广州—北京（1673）", -90, 0.22)]:
        ax.plot([x], [y], "o", ms=7, mfc="white", mec="#222222", mew=1.4, zorder=5)
        ax.annotate(lab, xy=(x, y), xytext=(x + dx, y + dy), fontsize=8.2,
                    ha="right", arrowprops=dict(arrowstyle="-", color="#888888", lw=0.7))

    ax.set_xlim(0, 3000); ax.set_ylim(0, 1.9)
    ax.set_xlabel("边镇到都城的距离 d（km，直线近似）", fontsize=10)
    ax.set_ylabel("时间错配 τ =（2d/v + L）/ T_event", fontsize=10)
    ax.grid(alpha=0.20)
    ax.legend(fontsize=8.2, loc="upper left", frameon=False)

    fig.suptitle("图9　τ 随距离与通信速度变化：授权的必要性，不等于失控的充分性",
                 fontsize=12.5, fontweight="bold", y=0.965)
    fig.text(0.5, 0.045, "参数：L = 12 日（议决与拟诏），T_event = 60 日（事态巩固）；曲线为示意模型。"
                         "范阳（τ≈0.45）与广州（τ≈0.41）都在 τ<1 时出事。", ha="center",
             fontsize=7.8, color="#666666")
    save(fig, "fig09.png")


# ------------------------------------------------------------------ fig08
def fig08():
    periods = [
        ("西周春秋战国", {"正官": 1, "内廷": 0, "外派": 1, "军职": 1}),
        ("秦—西汉", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("东汉", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("三国", {"正官": 1, "内廷": 2, "外派": 1, "军职": 2}),
        ("两晋", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("十六国", {"正官": 0, "内廷": 1, "外派": 2, "军职": 2}),
        ("南朝", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("北朝", {"正官": 1, "内廷": 1, "外派": 2, "军职": 2}),
        ("隋", {"正官": 1, "内廷": 1, "外派": 1, "军职": 1}),
        ("唐前期", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("中晚唐", {"正官": 1, "内廷": 3, "外派": 2, "军职": 1}),
        ("五代十国", {"正官": 1, "内廷": 1, "外派": 2, "军职": 2}),
        ("辽", {"正官": 1, "内廷": 1, "外派": 2, "军职": 1}),
        ("宋", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("西夏", {"正官": 1, "内廷": 0, "外派": 1, "军职": 1}),
        ("金", {"正官": 1, "内廷": 1, "外派": 1, "军职": 1}),
        ("元", {"正官": 1, "内廷": 1, "外派": 2, "军职": 1}),
        ("明", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
        ("清前期", {"正官": 1, "内廷": 2, "外派": 1, "军职": 1}),
        ("晚清", {"正官": 1, "内廷": 1, "外派": 1, "军职": 1}),
        ("民国", {"正官": 1, "内廷": 2, "外派": 1, "军职": 1}),
        ("1949—1978", {"正官": 1, "内廷": 2, "外派": 1, "军职": 1}),
        ("1978—2012", {"正官": 1, "内廷": 1, "外派": 2, "军职": 1}),
        ("2012—2026", {"正官": 1, "内廷": 2, "外派": 2, "军职": 1}),
    ]
    keys = ["正官", "内廷", "外派", "军职"]
    cols = {"正官": GOLD, "内廷": RED, "外派": BLUE, "军职": GREEN}

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(11.0, 7.4),
                                 gridspec_kw={"height_ratios": [1.05, 1], "hspace": 0.55})
    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.16)

    xs = np.arange(len(periods))
    bottoms = np.zeros(len(periods))
    for k in keys:
        vals = np.array([p[1][k] for p in periods], dtype=float)
        ax.bar(xs, vals, bottom=bottoms, width=0.68, color=cols[k], alpha=0.88,
               label=k, edgecolor="white", lw=0.6)
        bottoms += vals
    ax.set_xticks(xs)
    ax.set_xticklabels([p[0] for p in periods], rotation=42, ha="right", fontsize=7.6)
    ax.set_ylim(0, 9.2)
    ax.set_ylabel("并立线数（本文编码）", fontsize=9.4)
    ax.legend(fontsize=8.0, ncol=4, loc="upper left", frameon=False)
    ax.grid(alpha=0.18, axis="y")
    ax.set_title("(a) 多线并立是常态；分裂期与异族政权同样如此", fontsize=10.6,
                 fontweight="bold", loc="left")
    for i, lab in [(2, "汉末"), (10, "唐末"), (13, "宋"), (18, "清")]:
        ax.annotate(lab, xy=(i, bottoms[i] + 0.12), xytext=(i, bottoms[i] + 0.95),
                    ha="center", fontsize=7.4, color="#333333",
                    arrowprops=dict(arrowstyle="-", color="#999999", lw=0.7))

    fusion = [0.25, 0.85, 0.95, 0.35, 0.60, 0.80, 0.55, 0.40, 0.30, 0.30,
              0.95, 0.85, 0.35, 0.30, 0.55, 0.45, 0.50, 0.45, 0.20, 0.55,
              0.60, 0.55, 0.35, 0.45]
    fc = [("#d98b84" if v > 0.5 else "#8fa8c4") for v in fusion]
    bx.bar(xs, fusion, width=0.66, color=fc, edgecolor="white", lw=0.6)
    bx.axhline(0.5, color=RED, lw=0.9, ls="--")
    bx.text(len(xs) - 0.6, 0.53, "阈值", ha="right", fontsize=7.6, color=RED)
    bx.set_xticks(xs)
    bx.set_xticklabels([p[0] for p in periods], rotation=42, ha="right", fontsize=7.6)
    bx.set_ylim(0, 1.10)
    bx.set_ylabel("融合度（编码 0—1）", fontsize=9.4)
    bx.grid(alpha=0.18, axis="y")
    bx.set_title("(b) 线数不预测稳定；共同项是“是否有一条线占满三项”", fontsize=10.6,
                 fontweight="bold", loc="left")
    bx.text(0.02, 0.93, "红：存在融合线（临界风险）", transform=bx.transAxes,
            fontsize=8.0, color="#b3261e")
    bx.text(0.02, 0.86, "蓝：无融合线（多线牵制或顶点驻留）", transform=bx.transAxes,
            fontsize=8.0, color="#3f5f88")

    fig.suptitle("图8　并立线的数量与融合：一个被案例表部分反驳的假说", fontsize=12.5,
                 fontweight="bold", y=0.965)
    save(fig, "fig08.png")


# ------------------------------------------------------------------ fig03
def fig03():
    fig, ax = plt.subplots(figsize=(9.8, 5.8))
    fig.subplots_adjust(left=0.03, right=0.98, top=0.80, bottom=0.08)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

    ax.add_patch(FancyBboxPatch((0.3, 3.70), 9.4, 1.45, boxstyle="round,pad=0.05,rounding_size=0.12",
                                fc=P_BLUE, ec=BLUE, lw=1.4))
    ax.text(0.55, 4.92, "慢层：品秩与官阶", fontsize=10.5, fontweight="bold", color=BLUE)
    ax.text(0.55, 4.64, "稳定、可传承、可比较", fontsize=8.2, color="#33506b")
    for i, t in enumerate(["汉：秩石／比秩", "魏晋：九品官品", "唐宋：散阶·寄禄官",
                           "明清：九品十八阶", "2019：职级序列"]):
        ax.text(0.55 + i * 1.82, 3.97, t, fontsize=8.0)

    ax.add_patch(FancyBboxPatch((0.3, 1.30), 9.4, 1.45, boxstyle="round,pad=0.05,rounding_size=0.12",
                                fc=P_RED, ec=RED, lw=1.4))
    ax.text(0.55, 2.52, "快层：差遣与使职", fontsize=10.5, fontweight="bold", color=RED)
    ax.text(0.55, 2.24, "随事而设、随事而罢", fontsize=8.2, color="#6d2620")
    for i, t in enumerate(["汉：领／录尚书事", "唐：同平章事·节度使", "宋：差遣·权知",
                           "明清：巡抚·军机章京", "当代：专班·督办·巡视"]):
        ax.text(0.55 + i * 1.82, 1.57, t, fontsize=8.0)

    for x, lab in [(2.0, "宋：官以寄禄、职以示荣、\n差遣以治事"),
                   (5.0, "唐：官品留在原官，\n实权由加衔授予"),
                   (8.0, "2019：职务与职级\n并行")]:
        ax.annotate("", xy=(x, 3.63), xytext=(x, 2.82),
                    arrowprops=dict(arrowstyle="<->", color=GOLD, lw=1.6))
        ax.text(x + 0.16, 3.22, lab, ha="left", va="center", fontsize=7.8,
                color=GOLD, linespacing=1.5)

    ax.set_title("图3　快慢分层：权力走快层，身份走慢层", fontsize=12.5,
                 fontweight="bold", loc="left", pad=12)
    ax.text(0, 5.72, "功能：让“调配权力”与“承受身份”解耦——不推翻品秩体系，也能换人、换事。",
            fontsize=8.6, color="#444444")
    ax.text(0, 0.55, "代价：名与实脱节 → 冗官、冗费，以及“名不正”的政治攻击（ψ 的制度形态）。",
            fontsize=8.6, color="#444444")
    save(fig, "fig03.png")


# ------------------------------------------------------------------ fig10
def fig10():
    a = b = 1.0

    def follow(hs, eta0):
        out = []
        prev = eta0
        for h in hs:
            r = np.roots([b, 0, -a, -h])
            r = np.real(r[np.abs(np.imag(r)) < 1e-9])
            nxt = r[np.argmin(np.abs(r - prev))]
            out.append((h, nxt)); prev = nxt
        return np.array(out)

    up = follow(np.linspace(-1.6, 1.6, 1200), -1.47)
    dn = follow(np.linspace(1.6, -1.6, 1200), 1.47)
    hsp = 2 / (3 * np.sqrt(3))

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.4, 4.5))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.80, bottom=0.20, wspace=0.28)

    ax.plot(up[:, 0], up[:, 1], color=BLUE, lw=2.2, label="授权逐步加深")
    ax.plot(dn[:, 0], dn[:, 1], color=RED, lw=2.2, ls="--", label="收权逐步推进")
    for h in (-hsp, hsp):
        ax.axvline(h, color="#b0b0b0", lw=0.9, ls=":")
    ax.set_xlabel("控制参数 h（军权与财权的集中度）", fontsize=9.6)
    ax.set_ylabel("序参量 η（中央对地方的有效控制）", fontsize=9.6)
    ax.legend(fontsize=8.2, loc="lower right", frameon=False)
    ax.grid(alpha=0.18)
    ax.set_title("(a) 一阶：崩解有滞后，回不去", fontsize=10.6, fontweight="bold", loc="left")
    ax.annotate("跳变点", xy=(-hsp, -0.77), xytext=(-1.15, -0.15), fontsize=8.2,
                color="#444444", arrowprops=dict(arrowstyle="->", color="#888888", lw=0.8))

    h2 = np.linspace(-1, 1, 400)
    eta = np.sqrt(np.clip(h2, 0, None))
    bx.plot(h2, eta, color=GREEN, lw=2.2)
    bx.set_xlabel("控制参数 h", fontsize=9.6)
    bx.set_ylabel("η", fontsize=9.6)
    bx.grid(alpha=0.18)
    bx.set_title("(b) 二阶：日常轮换，连续可逆", fontsize=10.6, fontweight="bold", loc="left")
    bx.text(-0.95, 0.78, "η ~ (h − h_c)^β\n无潜热、无滞后", fontsize=8.8, color=GREEN)

    fig.suptitle("图10　两种“变天”：日常轮换是二阶，体制崩解是一阶（类比模型，C 级）",
                 fontsize=12.2, fontweight="bold", y=0.96)
    fig.text(0.5, 0.03, "注：模型取 U(η) = −η²/2 + η⁴/4 − hη；社会历史中的 η 无法独立测量，"
                        "此图只作方向示意，不构成相变判定。", ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig10.png")


# ------------------------------------------------------------------ fig11
def fig11():
    years = np.arange(1800, 2027)
    d = 1900.0

    def v_tech(y):
        if y < 1880:
            return 300.0
        if y < 1930:
            return 3000.0
        if y < 1995:
            return 30000.0
        return 300000.0

    tech, org = [], []
    for y in years:
        tech.append(2 * d / v_tech(y))
        org.append(14.0 if y < 1880 else 9.0 if y < 1911 else 7.0 if y < 1949
                   else 8.0 if y < 1978 else 6.0 if y < 2012 else 5.0)
    tech, org = np.array(tech), np.array(org)

    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.85, bottom=0.24)
    ax.step(years, tech + org, where="post", color=RED, lw=2.4, label="总时延")
    ax.step(years, tech, where="post", color=BLUE, lw=1.8, ls="--", label="技术时延")
    ax.step(years, org, where="post", color=GOLD, lw=1.8, ls=":", label="组织时延")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 80)
    ax.set_xlim(1798, 2028)
    ax.set_ylabel("决策闭环时延（日，对数轴）", fontsize=9.8)
    ax.set_xlabel("年份", fontsize=9.8)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=8.4, loc="lower left", frameon=False)
    for x, lab in [(1880, "电报"), (1930, "电话"), (1995, "互联网"), (2012, "移动政务")]:
        ax.axvline(x, color="#b0b0b0", lw=0.8, ls="-.")
        ax.text(x + 1.5, 72, lab, rotation=90, va="top", fontsize=7.8, color="#555555")
    ax.annotate("地板：组织时延\n不随带宽下降", xy=(2024, 5.0), xytext=(1972, 0.30),
                fontsize=8.4, color=GOLD,
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=0.9))
    ax.set_title("图11　τ 的两次断崖与一个地板", fontsize=12.5, fontweight="bold", loc="left")
    fig.text(0.5, 0.045, "参数：北京—广州 1900 km；技术速度取分段常数。纵轴是同一次请示—批复闭环的时延量级，"
                         "不是任何具体事件的实测；组织时延为示意值。", ha="center",
             fontsize=7.8, color="#666666")
    save(fig, "fig11.png")


# ------------------------------------------------------------------ fig12
def fig12():
    fig, ax = plt.subplots(figsize=(8.8, 6.8))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.83, bottom=0.20)
    ax.set_xlim(0, 6); ax.set_ylim(0.08, 1.16)
    ax.axvline(2.7, color="#c8c8c8", lw=1.0, ls="--")
    ax.axhline(0.55, color="#c8c8c8", lw=1.0, ls="--")

    quad = [(0.12, 1.12, "三阶段循环", GREEN, "单线走完 C+T → A+T → C+A → 危机", "left"),
            (5.92, 1.12, "临界／一阶崩解", RED, "某线同时占满三项，整体报废", "right"),
            (0.12, 0.145, "顶点驻留", GRAY, "长期只保两项、不补第三项", "left"),
            (5.92, 0.145, "分裂并行", BLUE, "多线各占一个顶点，互相牵制", "right")]
    for x, y, t, col, sub, ha in quad:
        ax.text(x, y + 0.045, t, fontsize=11.5, fontweight="bold", color=col, va="bottom", ha=ha)
        ax.text(x, y - 0.005, sub, fontsize=8.0, color=col, va="top", ha=ha)

    pts = [(1.2, 0.40, "西周—春秋", GOLD, 8, 4), (2.1, 0.62, "秦—西汉", GOLD, 8, 4),
           (2.4, 0.80, "隋—盛唐", GOLD, 8, 4), (3.1, 0.33, "宋", BLUE, 9, 3),
           (3.0, 0.25, "清", BLUE, -9, -13), (3.3, 0.46, "明", BLUE, 8, 4),
           (3.6, 0.68, "五代", BLUE, 8, 4), (4.3, 0.90, "东汉", RED, 8, 4),
           (4.6, 0.80, "中晚唐", RED, 8, 4), (4.2, 0.62, "民国", RED, 8, 4),
           (3.9, 0.50, "当代", BLUE, 8, 4), (2.9, 0.68, "魏晋南朝", GOLD, -55, 2)]
    for x, y, lab, col, dx, dy in pts:
        ax.scatter(x, y, s=100, color=col, alpha=0.85, edgecolor="white", lw=1.2, zorder=3)
        ax.annotate(lab, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=8.2,
                    ha="right" if dx < 0 else "left")

    ax.set_xlabel("并立线数（1 → 5+）", fontsize=10)
    ax.set_ylabel("单线融合度（是否有一线占满三项）", fontsize=10, labelpad=8)
    ax.set_title("图12　四种演化模式的定位图（编码地图，不是测量）", fontsize=12.5,
                 fontweight="bold")
    fig.text(0.5, 0.045, "注：坐标为本文对史料的定性编码。这张图的作用，是让“属于哪种模式”成为可争论的问题，"
                         "而不是给出精确位置。", ha="center", fontsize=7.8, color="#666666")
    save(fig, "fig12.png")


if __name__ == "__main__":
    print("building figures ...")
    write_cases()
    for f in [fig01, fig02, fig03, fig04, fig05, fig06,
              fig07, fig08, fig09, fig10, fig11, fig12]:
        f()
    print("done.")

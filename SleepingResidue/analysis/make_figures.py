# -*- coding: utf-8 -*-
"""生成 7 幅图与全部表（含 cases.csv），数据来自 data/cases.py（单一来源）。

运行：python analysis/make_figures.py
"""
import csv, os, sys, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import cases  # noqa: E402

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C_REC, C_REI, C_SIL, C_ACC = "#2f6f9f", "#b3701f", "#8a8a8a", "#a8322d"
ROWS = cases.table()
ST = cases.stats()


# ---------------- 表 ----------------
def write_cases_csv():
    with open(ROOT / "cases.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cases.FIELDS + ["silence", "lag"])
        w.writeheader()
        for r in ROWS:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in w.fieldnames})


def write_tables():
    # 表 1：案例总表
    out = ["| 编号 | 案例 | 提出年 | 重新承认 | 沉寂（年） | 解码器 | 解码器滞后（年） | 旧坐标 | 结果 | 等级 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(ROWS, key=lambda x: (x["outcome"] != "恢复", -(x["silence"] or 0))):
        out.append(f'| {r["id"]} | {r["case"]} | {r["t_prop"]} | {r["t_rev"] if r["t_rev"] is not None else "—"} | '
                   f'{r["silence"] if r["silence"] is not None else "—"} | {r["decoder"]} | '
                   f'{r["lag"] if r["lag"] is not None else "—"} | {r["coord_old"]} | {r["outcome"]} | {r["grade"]} |')
    (ROOT / "data" / "table_cases.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2：三分组的统计
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    rei = [r for r in ROWS if r["outcome"] == "重发明"]
    sil = [r for r in ROWS if r["outcome"] == "沉默"]
    out = ["| 组 | n | 沉寂年数（中位／范围） | 解码器滞后（中位／范围） | 有解码器 | 命题可重建 |", "|---|---|---|---|---|---|"]
    def rng(xs):
        xs = [x for x in xs if x is not None]
        return f"{int(np.median(xs))}／{min(xs)}—{max(xs)}" if xs else "—"
    out.append(f'| 恢复 | {len(rec)} | {rng([r["silence"] for r in rec])} | {rng([r["lag"] for r in rec])} | '
               f'{sum(1 for r in rec if r["decoder"] and r["t_dec"] is not None)}/{len(rec)} | '
               f'{sum(1 for r in rec if r["derivable"] == "可")}/{len(rec)} |')
    out.append(f'| 重发明 | {len(rei)} | {rng([r["silence"] for r in rei])} | — | 0/{len(rei)} | '
               f'{sum(1 for r in rei if r["derivable"] == "可")}/{len(rei)} |')
    out.append(f'| 沉默 | {len(sil)} | 永久 | — | 0/{len(sil)} | '
               f'{sum(1 for r in sil if r["derivable"] == "可")}/{len(sil)} |')
    (ROOT / "data" / "table_groups.md").write_text("\n".join(out), encoding="utf-8")

    # 表 3：坐标 × 结果
    coords = ["不合法", "异常", "被误解", "接收端成本", "主动撤回"]
    outs = ["恢复", "重发明", "沉默"]
    out = ["| 旧范式坐标 | 恢复 | 重发明 | 沉默 | 合计 | 恢复时的去向 |", "|---|---|---|---|---|---|"]
    for c in coords:
        rs = [r for r in ROWS if r["coord_old"] == c]
        recs = [r for r in rs if r["outcome"] == "恢复"]
        dest = "、".join(sorted({r["coord_new"] for r in recs})) or "—"
        out.append(f'| {c} | {sum(1 for r in rs if r["outcome"] == "恢复")} | '
                   f'{sum(1 for r in rs if r["outcome"] == "重发明")} | '
                   f'{sum(1 for r in rs if r["outcome"] == "沉默")} | {len(rs)} | {dest} |')
    (ROOT / "data" / "table_coords.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4：三标记
    def m1(r): return 1 if r["resid"] != "无" else 0
    def m2(r): return 1 if (r["t_dec"] is not None and r["lag"] is not None and r["lag"] >= 0) else 0
    def m3(r): return 1 if r["derivable"] in ("难", "不可") else 0
    out = ["| 编号 | 案例 | ①残余可检 | ②解码器跃迁 | ③重建成本高于翻译 | 命中 | 结果 | 判定 |", "|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        h = m1(r) + m2(r) + m3(r)
        out.append(f'| {r["id"]} | {r["case"]} | {"●" if m1(r) else "○"} | {"●" if m2(r) else "○"} | '
                   f'{"●" if m3(r) else "○"} | {h}/3 | {r["outcome"]} | '
                   f'{"符合" if (h >= 2) == (r["outcome"] == "恢复") else "不符合"} |')
    (ROOT / "data" / "table_marks.md").write_text("\n".join(out), encoding="utf-8")
    return rec, rei, sil, m1, m2, m3


def fisher():
    """两个 2×2 精确检验，数据驱动。"""
    from math import comb
    def fisher_exact(a, b, c, d):
        n = a + b + c + d
        def p(x):
            return comb(a + b, x) * comb(c + d, a + c - x) / comb(n, a + c)
        obs = p(a)
        lo = max(0, a + c - (c + d)); hi = min(a + b, a + c)
        return sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs + 1e-12)
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    non = [r for r in ROWS if r["outcome"] != "恢复"]
    a = sum(1 for r in rec if r["t_dec"] is not None and r["lag"] is not None and r["lag"] >= 0)
    c = sum(1 for r in non if r["t_dec"] is not None and r["lag"] is not None and r["lag"] >= 0)
    p_dec = fisher_exact(a, len(rec) - a, c, len(non) - c)
    rei = [r for r in ROWS if r["outcome"] == "重发明"]
    b1 = sum(1 for r in rec if r["derivable"] == "可")
    d1 = sum(1 for r in rei if r["derivable"] == "可")
    p_der = fisher_exact(d1, len(rei) - d1, b1, len(rec) - b1)
    return p_dec, p_der, (a, len(rec), c, len(non)), (d1, len(rei), b1, len(rec))


# ---------------- 图 ----------------
def fig01():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    def box(x, y, w, h, t, fc, fs=8.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#333", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.55)
    box(.2, 4.35, 9.4, .95, "① 残余可检：被压掉的东西在主流范式的异常清单上留下了可重复、可测量的残留", "#e9eff5")
    box(.2, 3.15, 9.4, .95, "② 解码器跃迁：另一套工具或另一个领域的问题，使旧信息重新可读（不是有人重读旧文献）", "#eef2e6")
    box(.2, 1.95, 9.4, .95, "③ 重建成本高于翻译：把旧命题翻成当代语言，比从零重建它更便宜", "#f7efe2")
    for y in (4.3, 3.1, 1.9):
        ax.add_patch(FancyArrowPatch((4.9, y - .18), (4.9, y - .28), arrowstyle="-", lw=.7, color="#999"))
    box(.2, .35, 2.9, 1.15, "微观：个体\n编码与检索失败", "#f2f0ec")
    box(3.4, .35, 2.9, 1.15, "中观：共同体\n范式压缩与索引断裂", "#e8eeea")
    box(6.6, .35, 3.0, 1.15, "宏观：跨范式\n重新解码", "#efe9e2")
    ax.text(.2, 5.25, "图 1　遗忘的三个尺度与重新发现的三个条件（示意）", fontsize=9.8, fontweight="bold")
    ax.text(.2, .02, "注：三条标记不是打分项，②是必要条件（见 4.2 节）；示意图，不按比例。", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ROOT / "fig01_mechanism.png", bbox_inches="tight"); plt.close(fig)


def fig02():
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    rec.sort(key=lambda r: r["silence"])
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ys = np.arange(len(rec))
    ax.barh(ys, [r["silence"] for r in rec], height=.55, color="#cfdbe6", edgecolor="#9fb2c4", zorder=2)
    for y, r in zip(ys, rec):
        if r["lag"] is not None:
            ax.plot(r["silence"] - r["lag"], y, "o", ms=5.5, color=C_ACC, zorder=4)
        ax.plot(r["silence"], y, "|", ms=11, color=C_REC, mew=1.6, zorder=5)
    ax.set_yticks(ys); ax.set_yticklabels([f'{r["id"]} {r["case"]}' for r in rec], fontsize=7.6)
    ax.set_xlabel("距原始提出的年数（0 = 提出年）")
    ax.set_title("图 2　沉寂中位 36 年，而解码器出现到被承认的中位滞后只有 1 年", fontsize=9.6, loc="left")
    ax.plot([], [], "o", color=C_ACC, label="解码器可用"); ax.plot([], [], "|", ms=10, color=C_REC, label="重新承认")
    ax.legend(fontsize=7.6, frameon=False, loc="lower right", bbox_to_anchor=(1.0, .02))
    ax.set_xlim(0, 205)
    ax.text(6, len(ys) - .45, "灰条 = 沉寂期", fontsize=7.4, color="#4a5a6a")
    fig.tight_layout(); fig.savefig(ROOT / "fig02_lag.png", bbox_inches="tight"); plt.close(fig)


def fig03():
    coords = ["不合法", "异常", "被误解", "接收端成本", "主动撤回"]
    outs = ["恢复", "重发明", "沉默"]
    M = np.zeros((len(coords), len(outs)))
    for r in ROWS:
        if r["coord_old"] in coords:
            M[coords.index(r["coord_old"]), outs.index(r["outcome"])] += 1
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=max(3, M.max()))
    ax.set_xticks(range(len(outs))); ax.set_xticklabels(outs, fontsize=8.6)
    ax.set_yticks(range(len(coords))); ax.set_yticklabels(coords, fontsize=8.6)
    for i in range(len(coords)):
        for j in range(len(outs)):
            if M[i, j]:
                ids = " ".join(r["id"] for r in ROWS if r["coord_old"] == coords[i] and r["outcome"] == outs[j])
                ax.text(j, i, f"{int(M[i,j])}\n{ids}", ha="center", va="center", fontsize=6.4,
                        color="white" if M[i, j] > M.max() * .6 else "#222")
    ax.set_title("图 3　旧范式坐标 × 结果：四种坐标，四条不同的回归路径", fontsize=9.4, loc="left")
    ax.grid(False)
    fig.tight_layout(); fig.savefig(ROOT / "fig03_coords.png", bbox_inches="tight"); plt.close(fig)


def fig04():
    p_dec, p_der, (a1, a2, c1, c2), (d1, d2, b1, b2) = fisher()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    # (a) 解码器 × 结果
    ax = axes[0]
    M = np.array([[a1, a2 - a1], [c1, c2 - c1]])
    ax.imshow(M, cmap="Blues", vmin=0, vmax=11)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=13,
                    color="white" if M[i, j] > 6 else "#222")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["恢复", "重发明／沉默"], fontsize=8)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["有解码器", "无解码器"], fontsize=8)
    ax.set_title(f"（a）解码器是必要条件\nFisher p = {p_dec:.4f}", fontsize=8.8, loc="left")
    ax.grid(False)
    # (b) 可重建性 × 结果
    ax = axes[1]
    M = np.array([[b1, b2 - b1], [d1, d2 - d1]])
    ax.imshow(M, cmap="Oranges", vmin=0, vmax=9)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=13,
                    color="white" if M[i, j] > 4 else "#222")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["恢复", "重发明"], fontsize=8)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["可重建", "难／不可重建"], fontsize=8)
    ax.set_title(f"（b）重发明只发生在可重建时\nFisher p = {p_der:.3f}", fontsize=8.8, loc="left")
    ax.grid(False)
    fig.suptitle("图 4　两个必要条件，而不是一张打分表", fontsize=9.6, x=.012, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .9)); fig.savefig(ROOT / "fig04_necessary.png", bbox_inches="tight"); plt.close(fig)


def fig05():
    rows = ROWS
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 4); ax.set_ylim(-.6, len(rows) + 1.7); ax.axis("off")
    for j, name in enumerate(["①残余可检", "②解码器", "③重建更贵"]):
        ax.text(1.68 + j * .7, len(rows) + .55, name, ha="center", fontsize=7.8)
    ax.text(3.72, len(rows) + .55, "命中", ha="center", fontsize=7.8)
    for i, r in enumerate(rows):
        y = len(rows) - i
        col = {"恢复": C_REC, "重发明": C_REI, "沉默": C_SIL}[r["outcome"]]
        ax.text(.05, y, f'{r["id"]}  {r["case"]}', fontsize=7.2, va="center", color=col)
        m1 = r["resid"] != "无"
        m2 = r["t_dec"] is not None and r["lag"] is not None and r["lag"] >= 0
        m3 = r["derivable"] in ("难", "不可")
        for j, v in enumerate([m1, m2, m3]):
            ax.add_patch(plt.Rectangle((1.45 + j * .7, y - .34), .46, .68,
                                       fc=col if v else "#f2f2f2", ec="#cccccc", lw=.6))
        ax.text(3.75, y, f"{int(m1)+int(m2)+int(m3)}/3", ha="center", fontsize=7.4)
    ax.text(.05, -.45, "蓝＝恢复　橙＝重发明　灰＝沉默", fontsize=7.2, color="#555")
    ax.text(.05, len(rows) + 1.3, "图 5　逐案的三标记命中：恢复组 11/11 命中 ≥2，但沉默的燃素说也命中 2", fontsize=9.4)
    fig.tight_layout(); fig.savefig(ROOT / "fig05_marks.png", bbox_inches="tight"); plt.close(fig)


def fig06():
    marks = [("① 序参量跃变", "不可判", "「什么在变」无公认定义；\n引用网络或范式距离皆可换", "#bdbdbd"),
             ("② 临界慢化", "未通过", "无冲击前的高频序列；\n旧范式无「恢复时间」", C_ACC),
             ("③ 宏观更好用", "未测", "需跨案例面板与\n明确的预测目标", "#bdbdbd")]
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
    for i, (n, v, why, c) in enumerate(marks):
        x = .15 + i * 3.3
        ax.add_patch(FancyBboxPatch((x, .55), 3.05, 2.05, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc="white", ec="#bbb", lw=.9))
        ax.add_patch(FancyBboxPatch((x, 2.16), 3.05, .44, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=c, ec="none"))
        ax.text(x + 1.52, 2.38, n, ha="center", va="center", fontsize=8.6,
                color="white" if c == C_ACC else "#222")
        ax.text(x + 1.52, 1.78, v, ha="center", va="center", fontsize=10.5, fontweight="bold",
                color=C_ACC if c == C_ACC else "#3a3a3a")
        ax.text(x + 1.52, 1.12, why, ha="center", va="center", fontsize=7.2, color="#333", linespacing=1.6)
    ax.text(.15, 3.05, "图 6　把「范式转移」当临界事件来检验：又是「缺哪一格」", fontsize=9.6, fontweight="bold")
    ax.text(.15, .12, "判据同《涌现的临界》第三章；本例说明「科学革命是相变」目前仍是隐喻级。", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ROOT / "fig06_paradigm.png", bbox_inches="tight"); plt.close(fig)


def fig07():
    """与既有文献的定位：文献类型 × 是否给出必要条件。"""
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.plot([1, 9.2], [2.6, 2.6], color="#bbb", lw=1)
    ax.plot([5.1, 5.1], [.35, 4.4], color="#bbb", lw=1)
    ax.text(1.05, 4.45, "给出条件（本文）", fontsize=8, color="#333")
    ax.text(5.3, 4.45, "不给条件（只给相关性）", fontsize=8, color="#333")
    ax.text(.05, 4.45, "", fontsize=8)
    ax.text(.3, 3.35, "机制\n解释", fontsize=7.6, ha="center", color="#333", rotation=90, va="center")
    ax.text(.3, 1.35, "现象\n描述", fontsize=7.6, ha="center", color="#333", rotation=90, va="center")
    ax.text(3.0, 3.35, "本文：三条件＋两必要条件\n（残余／解码器／重建成本）", fontsize=7.8, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.4", fc="#e9eff5", ec="#9fb2c4"))
    ax.text(3.0, 1.35, "拉卡托斯：保护带重组\n（机制，但无判据）", fontsize=7.8, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.4", fc="#f4f4f1", ec="#d5d2c8"))
    ax.text(7.2, 3.35, "Merton：多重发现\n（无判据）", fontsize=7.8, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.4", fc="#f4f4f1", ec="#d5d2c8"))
    ax.text(7.2, 1.35, "沉睡美人／延迟承认：\n引文分布（无机制）", fontsize=7.8, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=.4", fc="#f4f4f1", ec="#d5d2c8"))
    ax.text(.2, .05, "图 7　本文在既有文献中的位置：把「延迟承认」从相关性描述推到一个必要条件结构", fontsize=9.2)
    fig.tight_layout(); fig.savefig(ROOT / "fig07_position.png", bbox_inches="tight"); plt.close(fig)


def write_appendix():
    """附录 A 的两张表：事实字段与判定字段。"""
    out = ["| 编号 | 案例 | 命题 | 提出 | 承认 | 沉寂 | 解码器 | 解码器年 | 滞后 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["case"]} | {r["claim"]} | {r["t_prop"]} | '
                   f'{r["t_rev"] if r["t_rev"] is not None else "—"} | '
                   f'{r["silence"] if r["silence"] is not None else "—"} | {r["decoder"]} | '
                   f'{r["t_dec"] if r["t_dec"] is not None else "—"} | '
                   f'{r["lag"] if r["lag"] is not None else "—"} |')
    (ROOT / "data" / "table_a1.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 编号 | 残余信号 | 旧坐标 | 新坐标 | 结局 | 翻译成本 | 可重建 | 等级 | 出处 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["resid"]} | {r["coord_old"]} | {r["coord_new"]} | {r["outcome"]} | '
                   f'{r["trans"]} | {r["derivable"]} | {r["grade"]} | {r["note"]} |')
    (ROOT / "data" / "table_a2.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 编号 | 案例 | 提出 | 解码器可用 | 重新承认 | 沉寂 | 滞后 | 结果 |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(ROWS, key=lambda x: x["t_prop"]):
        out.append(f'| {r["id"]} | {r["case"]} | {r["t_prop"]} | {r["t_dec"] if r["t_dec"] is not None else "—"} | '
                   f'{r["t_rev"] if r["t_rev"] is not None else "—"} | '
                   f'{r["silence"] if r["silence"] is not None else "—"} | '
                   f'{r["lag"] if r["lag"] is not None else "—"} | {r["outcome"]} |')
    (ROOT / "data" / "table_time.md").write_text("\n".join(out), encoding="utf-8")


def write_dec_table():
    """解码器类型 × 恢复速度。"""
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    order = ["编纂型", "邻域型", "理论型", "仪器型", "载体型"]
    out = ["| 解码器类型 | 案例数 | 滞后（中位／范围） | 案例 | 含义 |", "|---|---|---|---|---|"]
    meaning = {"编纂型": "一次编纂或翻译决定即可", "邻域型": "邻域提出需要它的问题",
               "理论型": "等待一套形式化语汇", "仪器型": "等待仪器做出并测到", "载体型": "等待文本被公开或读出"}
    for t in order:
        rs = [r for r in rec if r["dec_type"] == t]
        if not rs:
            continue
        lags = [r["lag"] for r in rs if r["lag"] is not None]
        rng = f"{int(np.median(lags))}／{min(lags)}—{max(lags)}" if lags else "—"
        out.append(f'| {t} | {len(rs)} | {rng} | {"、".join(r["id"] for r in rs)} | {meaning[t]} |')
    (ROOT / "data" / "table_dec.md").write_text("\n".join(out), encoding="utf-8")


def fig08():
    rec = [r for r in ROWS if r["outcome"] == "恢复" and r["dec_type"] != "—"]
    order = ["编纂型", "邻域型", "理论型", "仪器型", "载体型"]
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    for i, t in enumerate(order):
        ys = [r["lag"] for r in rec if r["dec_type"] == t]
        xs = [i + (j - (len(ys) - 1) / 2) * .08 for j in range(len(ys))]
        ax.scatter(xs, ys, s=26, color=C_ACC, alpha=.8, zorder=3, edgecolor="white", lw=.5)
        if ys:
            ax.plot([i - .28, i + .28], [np.median(ys)] * 2, color="#333", lw=1.4, zorder=4)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, fontsize=8.6)
    ax.set_ylabel("解码器滞后（年）")
    ax.set_title("图 8　三类解码器的速度差别：编纂最快，仪器最慢", fontsize=9.6, loc="left")
    ax.text(.02, .93, "横线为组内中位；每点为一个恢复案例", transform=ax.transAxes, fontsize=7.4, color="#555")
    fig.tight_layout(); fig.savefig(ROOT / "fig08_dectype.png", bbox_inches="tight"); plt.close(fig)


def fig09():
    """判据树：三条标记的先后顺序本身是判据。"""
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")
    def node(x, y, t, fc="#eef2f6", fs=8.0):
        ax.add_patch(FancyBboxPatch((x - 1.15, y - .32), 2.3, .64, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x, y, t, ha="center", va="center", fontsize=fs, linespacing=1.4)
    node(5, 4.55, "有残余信号？（标记①）", "#dbe7f1")
    node(2.3, 3.2, "永久沉默\n（载体销毁）", "#eeeeee")
    node(5, 3.2, "有解码器？（标记②）", "#dbe7f1")
    node(7.7, 3.2, "永久沉默\n（等不到解码器）", "#eeeeee")
    node(3.3, 1.75, "命题可由新框架重建？（标记③）", "#e6ecdf")
    node(7.0, 1.75, "恢复（翻译路径）", "#cfdbe6")
    node(3.3, .45, "重发明（归属断裂）", "#f0e2cb")
    for a, b in [((5, 4.23), (2.3, 3.52)), ((5, 4.23), (5, 3.52)), ((5, 2.88), (7.7, 2.88)),
                 ((5, 2.88), (3.3, 2.07)), ((5, 2.88), (7.0, 2.07))]:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=.9, color="#777"))
    ax.text(3.4, 3.9, "无", fontsize=7.4, color="#555"); ax.text(5.15, 3.75, "有", fontsize=7.4, color="#555")
    ax.text(8.05, 2.62, "无", fontsize=7.4, color="#555"); ax.text(4.2, 2.55, "有", fontsize=7.4, color="#555")
    ax.text(3.3, 1.2, "否（重建更贵）→ 翻译", fontsize=7, color="#555", ha="center")
    ax.text(3.3, .95, "是（可重建）→ 重造", fontsize=7, color="#555", ha="center")
    ax.annotate("", xy=(3.3, .8), xytext=(3.3, 1.4), arrowprops=dict(arrowstyle="-|>", lw=.8, color="#777"))
    ax.text(.15, 5.0, "图 9　判据树：先问残余，再问解码器，最后问可重建性", fontsize=9.6, fontweight="bold")
    ax.text(.15, .05, "注：②是必要条件；①③只决定沉默的类型与恢复的形态。", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(ROOT / "fig09_tree.png", bbox_inches="tight"); plt.close(fig)


def fig10():
    """决策空间：翻译成本 × 重建成本。"""
    lvl = {"低": 1, "中": 2, "高": 3}
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for r in ROWS:
        if r["trans"] not in lvl or r["outcome"] == "沉默":
            continue
        x = lvl[r["derivable"]] if r["derivable"] in lvl else {"可": 1, "难": 3, "不可": 4}[r["derivable"]]
        y = lvl[r["trans"]]
        col = C_REI if r["outcome"] == "重发明" else C_REC
        ax.scatter(x, y, s=46, color=col, alpha=.85, zorder=3, edgecolor="white", lw=.6)
        ax.annotate(r["id"], (x, y), xytext=(4, 4), textcoords="offset points", fontsize=6.4, color="#333")
    ax.plot([.6, 4.4], [.6, 4.4], ls="--", lw=1, color="#999")
    ax.set_xlim(.5, 4.5); ax.set_ylim(.5, 3.5)
    ax.set_xticks([1, 3, 4]); ax.set_xticklabels(["可重建\n(成本低)", "难重建", "不可重建\n(成本极高)"], fontsize=8)
    ax.set_yticks([1, 2, 3]); ax.set_yticklabels(["低", "中", "高"], fontsize=8.6)
    ax.set_xlabel("重建成本"); ax.set_ylabel("翻译成本")
    ax.text(3.9, 1.15, "对角线：\n翻译与重建同价", fontsize=7, color="#777", ha="right")
    ax.set_title("图 10　翻译与重建的决策空间：重发明全部落在'重建不贵'一侧", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT / "fig10_decision.png", bbox_inches="tight"); plt.close(fig)


def write_degree():
    from data.cases import REC_DEGREE
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    out = ["| 编号 | 案例 | 术语保留 | 作者保留 | 方法保留 |", "|---|---|---|---|---|"]
    for r in rec:
        d = REC_DEGREE.get(r["id"], (0, 0, 0))
        mk = lambda v: "●" if v else "○"
        out.append(f'| {r["id"]} | {r["case"]} | {mk(d[0])} | {mk(d[1])} | {mk(d[2])} |')
    n = len(rec)
    sums = [sum(REC_DEGREE.get(r["id"], (0, 0, 0))[i] for r in rec) for i in range(3)]
    out.append(f"| **合计** | {n} 例 | **{sums[0]}/{n}** | **{sums[1]}/{n}** | **{sums[2]}/{n}** |")
    (ROOT / "data" / "table_degree.md").write_text("\n".join(out), encoding="utf-8")
    return sums, n


def fig11():
    from data.cases import REC_DEGREE
    rec = [r for r in ROWS if r["outcome"] == "恢复"]
    names = ["术语保留", "作者保留", "方法保留"]
    vals = [sum(REC_DEGREE.get(r["id"], (0, 0, 0))[i] for r in rec) / len(rec) * 100 for i in range(3)]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    bars = ax.barh(range(3), vals, color=[C_ACC, C_REI, C_REC], height=.55, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + 1.5, i, f"{v:.0f}%", va="center", fontsize=9)
    ax.set_yticks(range(3)); ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 108); ax.set_xlabel("恢复案例中的保留率（%）")
    ax.set_title("图 11　恢复是分层的：方法最先回来，术语最后回来", fontsize=9.6, loc="left")
    ax.invert_yaxis()
    fig.tight_layout(); fig.savefig(ROOT / "fig11_degree.png", bbox_inches="tight"); plt.close(fig)


def fig12():
    """档案记忆 × 索引记忆（9.5 节）。"""
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([.5, 1.5]); ax.set_xticklabels(["档案完好", "档案缺失"], fontsize=9)
    ax.set_yticks([.5, 1.5]); ax.set_yticklabels(["索引完好", "索引缺失"], fontsize=9)
    ax.set_xlabel("档案记忆（东西在不在）"); ax.set_ylabel("索引记忆（读不读得懂）")
    cells = {(0, 1): ("已服务／被吸收\nC16 C23", "#f2f2f2"),
             (1, 1): ("永久沉默\nC15", "#e8e8e8"),
             (0, 0): ("同代即被接受\n（不在样本）", "#fafafa"),
             (1, 0): ("等待解码器\n其余 21 例", "#dbe7f1")}
    for (i, j), (t, c) in cells.items():
        ax.add_patch(plt.Rectangle((i, j), 1, 1, fc=c, ec="#999", lw=.9))
        ax.text(i + .5, j + .5, t, ha="center", va="center", fontsize=8, linespacing=1.7, color="#222")
    ax.set_title("图 12　两种记忆的四种组合：数字化只补了左边这一列", fontsize=9.4, loc="left")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(False)
    fig.tight_layout(); fig.savefig(ROOT / "fig12_two_memories.png", bbox_inches="tight"); plt.close(fig)


def fig13():
    """沉寂期分布：恢复组直方图 + 重发明/沉默的位置。"""
    rec = [r["silence"] for r in ROWS if r["outcome"] == "恢复" and r["silence"] is not None]
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    bins = [0, 20, 40, 60, 80, 100, 150, 200, 2500]
    ax.hist(rec, bins=bins, color=C_REC, alpha=.85, zorder=3, edgecolor="white")
    ax.set_xscale("symlog", linthresh=100)
    ax.set_xlabel("沉寂年数（对数刻度，100 年内为线性）"); ax.set_ylabel("案例数")
    ax.axvline(np.median(rec), color=C_ACC, ls="--", lw=1.2)
    ax.text(np.median(rec) * 1.06, ax.get_ylim()[1] * .9, f"中位 {np.median(rec):.0f} 年", fontsize=7.6, color=C_ACC)
    for r in ROWS:
        if r["outcome"] == "重发明" and r["silence"] is not None:
            ax.plot(r["silence"], .35, "^", ms=6, color=C_REI, zorder=4)
    ax.text(.98, .72, "▲ 重发明（99—1813 年）", transform=ax.transAxes, ha="right", fontsize=7.4, color=C_REI)
    ax.set_title("图 13　恢复组集中在 15—60 年，重发明在 100 年之外", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT / "fig13_dist.png", bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    write_cases_csv()
    write_tables()
    write_appendix(); write_dec_table(); write_degree()
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07()
    fig08(); fig09(); fig10(); fig11(); fig12(); fig13()
    p_dec, p_der, tab1, tab2 = fisher()
    print("Fisher p(decoder):", round(p_dec, 5), "| p(derivable):", round(p_der, 4))
    print("figs:", sorted(p.name for p in ROOT.glob("fig0*.png")))
    print("stats:", {k: v for k, v in ST.items() if not isinstance(v, list)})

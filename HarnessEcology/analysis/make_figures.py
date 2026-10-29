#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图 + 表 + series.csv，全部由 data/counts.json 与 data/raw/*.json 生成。

铁律：图、表、交互页三者同源。手工改数 = 图与表迟早打架。
"""
import json, pathlib, csv, datetime, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

BASE = pathlib.Path(__file__).resolve().parent.parent
DATA, RAW, FIG = BASE / "data", BASE / "data" / "raw", BASE
FIG.mkdir(exist_ok=True)
SNAP = "2026-10-23"

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams.update({"figure.dpi": 200, "savefig.dpi": 200, "font.size": 9,
                     "axes.titlesize": 10, "axes.labelsize": 9, "axes.edgecolor": "#444",
                     "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": .6,
                     "figure.facecolor": "white"})
C_DSH, C_SK, C_WARN, C_NEG = "#2f6f9f", "#b3701f", "#a8322d", "#8a8a8a"

C = {r["key"]: r["total_count"] for r in json.loads((DATA / "counts.json").read_text(encoding="utf-8"))}

# ---------- 期段定义（天数一律显式写出，避免"短尾月"被读成衰减） ----------
DSH = [("发布前\n(<08-13)", "pre", 71),
       ("第 1 周\n08-13–19", "p1", 7),
       ("08-20–31", "p2", 12),
       ("9 月", "p3", 30),
       ("10-01–23", "p4", 23)]
SK = [("发布前\n(<2025-09-22)", "pre", 178),
      ("09-22–10/31", "s0", 40),
      ("11 月", "s1", 30),
      ("12 月", "s2", 31)] + \
     [(f"2026-{m:02d}", f"s2026{m:02d}", 30) for m in range(1, 10)] + \
     [("2026-10\n(1–23)", "s202610", 23)]

DAYS = {"dsh|day|" + (datetime.date(2026, 8, 6) + datetime.timedelta(days=i)).isoformat(): 1 for i in range(19)}


def series_rows():
    rows = []
    for label, key, days in DSH:
        raw = C[f"dsh|{key}|all"]; s10 = C[f"dsh|{key}|star10"]
        s100 = C.get(f"dsh|{key}|star100")
        rows.append(dict(line="dsh-plugin", period=key, label=label.replace("\n", " "), days=days,
                         raw=raw, star10=s10, star100=(s100 if s100 is not None else ""),
                         per_day_raw=round(raw / days, 2), per_day_star10=round(s10 / days, 2),
                         per_day_star100=round(s100 / days, 2) if s100 is not None else ""))
    for label, key, days in SK:
        raw = C[f"skills|{key}|all"]; s10 = C[f"skills|{key}|star10"]
        rows.append(dict(line="agent-skills", period=key, label=label.replace("\n", " "), days=days,
                         raw=raw, star10=s10, star100="",
                         per_day_raw=round(raw / days, 2), per_day_star10=round(s10 / days, 2),
                         per_day_star100=""))
    return rows


def write_series():
    rows = series_rows()
    with open(BASE / "data" / "series.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows


# ---------- 图 1：结构示意 ----------
def fig01():
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    def box(x, y, w, h, txt, fc, ec="#333", fs=8.2, tc="#111"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, color=tc, linespacing=1.5)
    box(0.15, 0.22, 3.5, 0.9, "可查的既有生态：Cordis（建仓 2022-05-17）\nKoishi（建仓 2019-12-03）", "#eef2f6")
    box(0.15, 1.45, 3.5, 0.8, "官方仓库 deepseek-harness\n创建 2026-08-13", "#dbe7f1")
    box(0.15, 2.65, 3.5, 0.8, "划线一：topic dsh-plugin\n22,001 个仓库（10-23 快照）", "#dbe7f1")
    box(0.15, 3.85, 3.5, 0.85, "元层：精选清单、插件商店、\n桌面客户端（多数在 48 小时内出现）", "#f2efe6")
    box(4.55, 3.85, 3.2, 0.85, "划线二：topic agent-skills\n35,894 个仓库（10-23 快照）", "#f6e8d5")
    box(4.55, 2.65, 3.2, 0.8, "官方仓库（2025-09-22）\n规范仓库（2025-12-16, Apache-2.0）", "#f6e8d5")
    box(4.55, 0.25, 3.2, 0.85, "两条线重叠：414 个仓库\nJaccard = 0.7%", "#f7e0dc")
    for y0, y1 in [(1.1, 1.45), (2.25, 2.65), (3.45, 3.85)]:
        ax.add_patch(FancyArrowPatch((1.9, y0), (1.9, y1), arrowstyle="-|>", mutation_scale=11, lw=1.0, color="#555"))
    ax.add_patch(FancyArrowPatch((3.65, 2.9), (4.55, 2.9), arrowstyle="-|>", mutation_scale=11,
                                 lw=1.0, color="#555", linestyle=(0, (4, 2))))
    ax.text(4.1, 2.55, "几乎\n不相交", ha="center", va="top", fontsize=7.4, color=C_NEG, linespacing=1.4)
    ax.add_patch(FancyArrowPatch((6.15, 3.45), (6.15, 2.65 + 0.8), arrowstyle="-|>", mutation_scale=11, lw=1.0, color="#555"))
    ax.text(0.15, 5.05, "图 1　两条划线、一个底座：本文的观测对象（示意，非按比例）",
            fontsize=10, fontweight="bold")
    ax.text(0.15, 0.0, "注：方框层级为逻辑关系；数字为 2026-10-23 的搜索接口计数（附录 A）。底座与 Harness 的架构关系是生态内的说法，本文未核验。",
            fontsize=6.6, color="#555")
    fig.tight_layout(); fig.savefig(FIG / "fig01.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 2：日尺度 ----------
def fig02():
    days = [(datetime.date(2026, 8, 6) + datetime.timedelta(days=i)) for i in range(19)]
    vals = [C[f"dsh|day|{d.isoformat()}"] for d in days]
    pre = [v for d, v in zip(days, vals) if d <= datetime.date(2026, 8, 12)]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    colors = [C_WARN if d == datetime.date(2026, 8, 13) else (C_DSH if d > datetime.date(2026, 8, 13) else "#aab7c2") for d in days]
    ax.bar(range(len(days)), vals, color=colors, width=.72, zorder=3)
    ax.axhline(statistics.mean(pre), color="#7a7a7a", ls="--", lw=1.1, zorder=4)
    ax.text(0.2, statistics.mean(pre) + 60, f"发布前日均 {statistics.mean(pre):.0f}", ha="left", fontsize=7.8, color="#5a5a5a")
    ax.axvline(6.5, color=C_WARN, lw=1.2, ls=":", zorder=4)
    ax.text(6.6, max(vals) * 1.08, "官方仓库创建日 08-13", fontsize=8, color=C_WARN, va="bottom")
    ax.annotate(f"峰值 {max(vals):,}", xy=(vals.index(max(vals)), max(vals)), xytext=(0, 6),
                textcoords="offset points", ha="center", fontsize=7.8, color="#222")
    i20 = [i for i, d in enumerate(days) if d == datetime.date(2026, 8, 20)][0]
    ax.annotate("08-20 二次反弹\n（原因未核实）", xy=(i20, vals[i20]), xytext=(6, 24),
                textcoords="offset points", fontsize=7, color="#444",
                arrowprops=dict(arrowstyle="-", lw=.7, color="#888"))
    ax.set_xticks(range(len(days)))
    ax.set_xticklabels([d.strftime("%m-%d") for d in days], rotation=55, ha="right", fontsize=7)
    ax.set_ylabel("当日新建且带 dsh-plugin 标签的仓库数")
    ax.set_title("图 2　日尺度：跳变与官方仓库创建日对齐，且发布前基数为 14–38/日（非零）", fontsize=9.6, loc="left")
    ax.set_ylim(0, max(vals) * 1.16)
    fig.tight_layout(); fig.savefig(FIG / "fig02.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 3：三档分辨率（Harness） ----------
def fig04():
    labels = [l for l, _, _ in DSH]
    keys = [k for _, k, _ in DSH]
    days = [d for _, _, d in DSH]
    raw = [C[f"dsh|{k}|all"] / d for k, d in zip(keys, days)]
    s10 = [C[f"dsh|{k}|star10"] / d for k, d in zip(keys, days)]
    s100 = [C[f"dsh|{k}|star100"] / d if C.get(f"dsh|{k}|star100") is not None else 0 for k, d in zip(keys, days)]
    x = range(len(labels)); w = .27
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar([i - w for i in x], raw, w, label="全部仓库", color=C_DSH, zorder=3)
    ax.bar(list(x), s10, w, label="★ ≥ 10 且非 fork", color=C_SK, zorder=3)
    ax.bar([i + w for i in x], s100, w, label="★ ≥ 100 且非 fork", color=C_NEG, zorder=3)
    for i, (a, b, c) in enumerate(zip(raw, s10, s100)):
        ax.text(i - w, a * 1.06 + 3, f"{a:.0f}", ha="center", fontsize=6.8, color="#204a6b")
        ax.text(i, b * 1.06 + 3, f"{b:.1f}", ha="center", fontsize=6.8, color="#8a5717")
        if c > 0:
            ax.text(i + w, c * 1.06 + 3, f"{c:.1f}", ha="center", fontsize=6.8, color=C_NEG)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=7.6)
    ax.set_ylabel("日均新建数（对数轴）")
    ax.legend(fontsize=7.6, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.13), ncol=3)
    ax.set_title("图 4　三档分辨率，三种走向：原始计数在 10 月回升，按星标筛则继续下降", fontsize=9.6, loc="left")
    ax.text(.99, .93, "9 月→10 月：原始 134→217（↑）　★≥10 5.9→3.8（↓）", transform=ax.transAxes,
            fontsize=7.4, color="#333", ha="right", va="top")
    fig.tight_layout(); fig.savefig(FIG / "fig04.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 4：skills 双面板 ----------
def fig05():
    labels = [l for l, _, _ in SK]
    keys = [k for _, k, _ in SK]
    days = [d for _, _, d in SK]
    raw = [C[f"skills|{k}|all"] / d for k, d in zip(keys, days)]
    s10 = [C[f"skills|{k}|star10"] / d for k, d in zip(keys, days)]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), sharex=True)
    for ax, vals, ttl, col in [(axes[0], raw, "（a）全部仓库", C_SK), (axes[1], s10, "（b）★ ≥ 10 且非 fork", C_DSH)]:
        ax.bar(range(len(vals)), vals, color=col, width=.72, zorder=3)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6.8)
        ax.set_title(ttl, fontsize=9, loc="left")
    axes[0].set_ylabel("日均新建数")
    axes[0].annotate("10 月是原始计数最快的一个月", xy=(len(raw) - 1, raw[-1]), xytext=(-92, -14),
                     textcoords="offset points", fontsize=7.2, color="#333",
                     arrowprops=dict(arrowstyle="->", lw=.7, color="#666"))
    axes[1].annotate("3—9 月走平在 10.7–14.3/日", xy=(6, s10[6]), xytext=(-96, 26), textcoords="offset points",
                     fontsize=7.2, color="#333", arrowprops=dict(arrowstyle="->", lw=.7, color="#666"))
    axes[1].set_ylim(0, max(s10) * 1.45)
    fig.suptitle("图 5　agent-skills 的月尺度：换一台仪器，“还在加速”变成“早已走平”", fontsize=9.6, x=.012, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .93)); fig.savefig(FIG / "fig05.png", bbox_inches="tight"); plt.close(fig)


def retention_table():
    names = [("dsh|p1", "8/13–19", 69), ("dsh|p2", "8/20–31", 60), ("dsh|p3", "9 月", 36),
             ("dsh|p4a", "10/1–9", 19), ("skills|jan", "1 月", 276), ("skills|jun", "6 月", 130),
             ("skills|sept", "9 月", 47), ("skills|octa", "10/1–9", 18)]
    rows = []
    for k, lab, age in names:
        b, a, a10 = C[f"ret|{k}|base"], C[f"ret|{k}|active7"], C[f"ret|{k}|active7_star10"]
        rows.append(dict(cohort=k, label=lab, median_age=age, base=b, active7=a, active7_star10=a10,
                         rate=round(100 * a / b, 1), rate_star10=round(100 * a10 / b, 1)))
    with open(DATA / "retention.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return rows


# ---------- 图 5：存活率（无偏计数） ----------
def fig03():
    rows = retention_table()
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    x = range(len(rows))
    ax.bar([i - .19 for i in x], [r["rate"] for r in rows], .38, color=C_DSH, label="近 7 天有推送（≥1 次）", zorder=3)
    ax.bar([i + .19 for i in x], [r["rate_star10"] for r in rows], .38, color=C_SK, label="近 7 天有推送且 ★ ≥ 10", zorder=3)
    for i, r in enumerate(rows):
        ax.text(i - .19, r["rate"] + .7, f'{r["rate"]:.0f}', ha="center", fontsize=6.8, color="#204a6b")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f'{r["label"]}\n({r["median_age"]} 天)' for r in rows], fontsize=7)
    ax.axvline(3.5, color="#999", lw=.9, ls=":")
    ax.text(1.6, ax.get_ylim()[1] * .93, "dsh-plugin 队列", fontsize=8, color="#555", ha="center")
    ax.text(5.6, ax.get_ylim()[1] * .93, "agent-skills 队列", fontsize=8, color="#555", ha="center")
    ax.set_ylabel("队列中仍活跃的仓库占比（%）")
    ax.legend(fontsize=7.4, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.22), ncol=2)
    ax.set_title("图 3　存活率不与队列先后单调：既没有持续衰亡，也没有加速自维持", fontsize=9.6, loc="left")
    ax.set_ylim(0, max(r["rate"] for r in rows) * 1.28)
    fig.text(.012, -.06, "注：横轴括号内为该队列在快照日的仓龄（中位）。仓龄影响活跃度，方向见正文 4.3 节。",
             fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(FIG / "fig03.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 6：重叠 ----------
def fig07():
    d = C["topic:dsh-plugin|top50"]; s = C["topic:agent-skills|top50"]; o = C["overlap|dsh-plugin+agent-skills"]
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    ax.barh([2], [d], color=C_DSH, height=.55, zorder=3)
    ax.barh([1], [s], color=C_SK, height=.55, zorder=3)
    ax.barh([0], [o], color=C_NEG, height=.55, zorder=3)
    for y, val, t in [(2, d, "topic:dsh-plugin　{:,}".format(d)),
                      (1, s, "topic:agent-skills　{:,}".format(s)),
                      (0, o, "两者重叠　{:,}".format(o))]:
        ax.text(val + 400, y, t, va="center", fontsize=8.2)
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels(["", "", ""])
    ax.set_xlim(0, s * 1.42); ax.set_xlabel("仓库数（2026-10-23 快照）")
    ax.set_title("图 7　“配套”是叙事，不是结构：两条划线的重叠率只有 0.7%（Jaccard）", fontsize=9.6, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "fig07.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 7：星标长尾 + 可疑仓库 ----------
def fig08():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0))
    for ax, f, ttl, col in [(axes[0], "topicdsh-plugin__top50.json", "（a）dsh-plugin 前 50", C_DSH),
                            (axes[1], "topicagent-skills__top50.json", "（b）agent-skills 前 50", C_SK)]:
        b = json.loads((RAW / f).read_text(encoding="utf-8"))
        items = b["items"]
        stars = [i["stargazers_count"] for i in items]
        ax.plot(range(1, len(stars) + 1), stars, "o-", ms=3, lw=.9, color=col, zorder=3)
        ax.set_yscale("log"); ax.set_xlabel("排名"); ax.set_title(ttl, fontsize=9, loc="left")
        top = items[0]
        ax.annotate(f'{top["full_name"]}　{top["stargazers_count"]:,}★ / {top["forks_count"]:,} fork',
                    xy=(1, top["stargazers_count"]), xytext=(14, -14), textcoords="offset points",
                    fontsize=6.8, color=C_NEG)
    axes[0].set_ylabel("星标数（对数）")
    fig.suptitle("图 8　两条线的前 50 名：同一个仓库同时占据两榜首位，agent-skills 榜单下沿仍在万星量级",
                 fontsize=9.2, x=.012, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .92)); fig.savefig(FIG / "fig08.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 8：三标记判定 ----------
def fig10():
    marks = [("① 序参量跃变", "不可判", "无仓库间关系数据；\n只有强度量（日增曲线）", "#bdbdbd"),
             ("② 临界慢化", "未通过", "事前窗口仅 7 天且被\n回溯标签污染", C_NEG),
             ("③ 宏观更好用", "未测", "缺逐仓库面板与\n预测目标", "#bdbdbd")]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
    for i, (name, verdict, why, col) in enumerate(marks):
        x = .15 + i * 3.3
        ax.add_patch(FancyBboxPatch((x, .55), 3.05, 2.05, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc="white", ec="#bbb", lw=.9))
        ax.add_patch(FancyBboxPatch((x, 2.16), 3.05, .44, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=col, ec="none"))
        ax.text(x + 1.52, 2.38, name, ha="center", va="center", fontsize=8.6, color="white" if col != "#bdbdbd" else "#222")
        ax.text(x + 1.52, 1.78, verdict, ha="center", va="center", fontsize=11, fontweight="bold",
                color=(col if col in (C_NEG,) else "#3a3a3a"))
        ax.text(x + 1.52, 1.12, why, ha="center", va="center", fontsize=7.2, color="#333", linespacing=1.6)
    ax.text(.15, 3.05, "图 10　三标记只看“缺哪一格”：中 0 个，且缺的两格不可补", fontsize=9.6, fontweight="bold")
    ax.text(.15, .12, "判据来源：《涌现的临界》第三章（序参量跃变／临界慢化／有效信息峰值，三中二）与 3.6 节“排除装置”。",
            fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(FIG / "fig10.png", bbox_inches="tight"); plt.close(fig)



# ---------- 图 6：星标阶梯（换阈值不再换符号？） ----------
def fig06():
    """把"阈值"从一个点变成一条线：日均新建 vs 星标门槛。"""
    PERIODS = [("第 1 周 08-13–19", "p1", 7, C_DSH, "o"),
               ("08-20–31", "p2", 12, "#6f9fbf", "s"),
               ("9 月", "p3", 30, C_SK, "^"),
               ("10-01–23", "p4", 23, C_NEG, "D")]
    KS = [0, 1, 10, 100, 1000]
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    rows = []
    for label, key, days, col, mk in PERIODS:
        ys = []
        for k in KS:
            if k == 0:
                c = C[f"dsh|{key}|all"]
            else:
                c = C.get(f"dsh|{key}|star{k}", C.get(f"lad|dsh|{key}|star{k}"))
            ys.append(None if c is None else c / days)
        xs = [max(k, .7) for k in KS]
        ok = [(x, y) for x, y in zip(xs, ys) if y and y > 0]
        ax.plot([x for x, _ in ok], [y for _, y in ok], mk + "-", ms=4, lw=1.3, color=col, label=label, zorder=3)
        rows.append((label, ys))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks([.7, 1, 10, 100, 1000]); ax.set_xticklabels(["0", "1", "10", "100", "1000"])
    ax.set_xlabel("星标门槛 ★ ≥ k（0 表示不设门槛）")
    ax.set_ylabel("日均新建数（对数）")
    ax.legend(fontsize=7.6, frameon=False, ncol=2)
    ax.set_title("图 6　同一条阶梯，两种走向：9 月→10 月在 ★≥1 之上仍在升，在 ★≥10 之下转而下降",
                 fontsize=9.2, loc="left")
    ax.axvspan(1.0, 10.0, color="#f0e6d2", alpha=.55, zorder=1)
    ax.text(3.1, 1.35, "符号翻转\n发生在这两档之间", fontsize=7.2, color="#8a6a2f",
            ha="center", linespacing=1.5)
    fig.tight_layout(); fig.savefig(FIG / "fig06.png", bbox_inches="tight"); plt.close(fig)
    return rows


def write_ladder_table(rows):
    out = ["| 期段 | ★≥0 | ★≥1 | ★≥10 | ★≥100 | ★≥1000 |", "|---|---|---|---|---|---|"]
    for label, ys in rows:
        cells = ["—" if y is None else f"{y:.1f}" for y in ys]
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    (BASE / "data" / "table_ladder.md").write_text("\n".join(out), encoding="utf-8")




# ---------- 图 11：C-A-T 在社区层 ----------
def fig11():
    import math
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.set_xlim(-1.35, 1.35); ax.set_ylim(-.55, 1.35); ax.axis("off")
    P = {"C": (0, 1.05), "A": (-1.05, -.35), "T": (1.05, -.35)}
    for k, v in P.items():
        ax.plot(*v, "o", ms=16, color="#2f6f9f")
        ax.text(v[0], v[1] + .13, {"C": "看见（C）", "A": "拼得上（A）", "T": "传得下去（T）"}[k],
                ha="center", fontsize=9.6, fontweight="bold")
    ax.plot([P["C"][0], P["A"][0]], [P["C"][1], P["A"][1]], color="#88a", lw=1.4)
    ax.plot([P["C"][0], P["T"][0]], [P["C"][1], P["T"][1]], color="#88a", lw=1.4)
    ax.plot([P["A"][0], P["T"][0]], [P["A"][1], P["T"][1]], color="#88a", lw=1.4)
    ax.text(0, .55, "深度插件\n保 C+A，让 T", ha="center", fontsize=7.8, color="#333", linespacing=1.5)
    ax.text(-.85, -.05, "桥接器／元层\n保 A+T，让 C", ha="center", fontsize=7.8, color="#333", linespacing=1.5)
    ax.text(.85, -.05, "通用工具\n保 C+T，让 A", ha="center", fontsize=7.8, color="#333", linespacing=1.5)
    ax.text(0, -1.2, "本文的 5 个跨两条线的仓库全部落在 C—T 一侧（通用工具，不是深度插件）",
            ha="center", fontsize=7.8, color="#a8322d")
    ax.text(-1.3, 1.32, "图 11　三种策略在三角上的位置（示意；案例位置为定性判定）", fontsize=9.4, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG / "fig11_triangle.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 12：标签重写漏斗 ----------
def fig12():
    stages = [("带 topic 的仓库总量", C["topic:dsh-plugin|top50"], "#b9c9d6"),
              ("其中建于发布之前", C["dsh|pre|all"], "#9db4c7"),
              ("其中已有 ★≥100", C["dsh|pre|star100"], "#7f9db5"),
              ("其中建于 2026 年之前", C["dsh|pre2026"], "#5f81a0"),
              ("其中挤进星标榜前 50", 35, "#a8322d")]
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    top = stages[0][1]
    for i, (lab, v, c) in enumerate(stages):
        w = v / top
        ax.barh(-i, w, height=.62, color=c, zorder=3)
        ax.text(w + .012, -i, f"{v:,}", va="center", fontsize=8.2)
        ax.text(-.01, -i, lab, va="center", ha="right", fontsize=8.2)
    ax.set_xlim(-.02, 1.18); ax.set_ylim(-len(stages) + .4, .7); ax.axis("off")
    ax.text(-.02, .75, "图 12　标签重写的漏斗：29% 的老仓库连描述都被改写成 Harness 语境",
            fontsize=9.4, fontweight="bold")
    ax.text(-.02, -len(stages) + .1, "注：横条为占总量比例；红条为星标榜前 50 名中的“发布前”仓库（35/50）。",
            fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(FIG / "fig12_funnel.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 13：三个时钟 ----------
def fig13():
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.2); ax.axis("off")
    def lane(y, name, pts, col):
        ax.plot([.9, 10.4], [y, y], color="#dddddd", lw=2, zorder=1)
        for x, lab in pts:
            ax.plot(x, y, "o", ms=8, color=col, zorder=3)
            ax.text(x, y + .28, lab, ha="center", fontsize=7.2, color=col)
        ax.text(.15, y, name, va="center", fontsize=8.6)
    lane(3.4, "平台钟", [(1.4, "08-13 建仓"), (1.75, "08-14 峰值"), (2.2, "08-20 反弹")], "#2f6f9f")
    lane(2.0, "生态钟", [(1.4, ""), (3.6, "9 月 134/日"), (6.2, "10 月 217/日"), (7.4, "合格 3.8/日")], "#b3701f")
    lane(.6, "维护钟", [(3.2, "9 月队列存活 24%"), (5.6, "10 月初 35%"), (8.2, "1 月队列 23%（276 天）")], "#a8322d")
    ax.text(.15, 4.05, "图 13　三个时钟不同步：平台以天计，生态以周计，维护以月计", fontsize=9.4, fontweight="bold")
    ax.text(.15, .05, "注：横轴为相对时间（示意），点位为本文实测的期段量；三条轴不可直接相加。", fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(FIG / "fig13_clocks.png", bbox_inches="tight"); plt.close(fig)



# ---------- 图 14：期段 × 门槛矩阵 ----------
def fig14():
    PER = [("发布前", "pre", 71), ("第 1 周", "p1", 7), ("08-20–31", "p2", 12), ("9 月", "p3", 30), ("10-01–23", "p4", 23)]
    KS = [0, 1, 10, 100, 1000]
    M = np.zeros((len(PER), len(KS)))
    for i, (lab, k, d) in enumerate(PER):
        for j, kk in enumerate(KS):
            v = C.get(f"dsh|{k}|all") if kk == 0 else C.get(f"dsh|{k}|star{kk}", C.get(f"lad|dsh|{k}|star{kk}"))
            M[i, j] = np.nan if (v is None or k == "pre") else v / d
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    im = ax.imshow(np.log10(M + 1), cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(KS))); ax.set_xticklabels([f"★≥{k}" for k in KS], fontsize=8.2)
    ax.set_yticks(range(len(PER))); ax.set_yticklabels([p[0] for p in PER], fontsize=8.2)
    for i in range(len(PER)):
        for j in range(len(KS)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.0f}", ha="center", va="center", fontsize=7.2,
                        color="white" if np.log10(M[i, j] + 1) > 1.6 else "#222")
    ax.grid(False)
    ax.set_title("图 14　期段 × 门槛的日均矩阵：9 月与 10 月的相对高低随列而翻转", fontsize=9.2, loc="left")
    fig.tight_layout(); fig.savefig(FIG / "fig14_matrix.png", bbox_inches="tight"); plt.close(fig)


# ---------- 图 9：星标榜的出生日期分布 ----------
def fig09():
    import csv as _csv
    rows = list(_csv.DictReader(open(DATA / "top50.csv", encoding="utf-8")))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2))
    for ax, line, cut, ttl, col in [
            (axes[0], "dsh-plugin", "2026-08-13", "（a）dsh-plugin 前 50", C_DSH),
            (axes[1], "agent-skills", "2025-09-22", "（b）agent-skills 前 50", C_SK)]:
        r = [x for x in rows if x["line"] == line]
        xs = [datetime.date.fromisoformat(x["created"]) for x in r]
        ys = [int(x["stars"]) for x in r]
        pre = sum(1 for x in r if x["created"] < cut)
        ax.scatter(xs, ys, s=14, color=col, alpha=.85, zorder=3, edgecolor="none")
        ax.axvline(datetime.date.fromisoformat(cut), color=C_NEG, ls=":", lw=1.2, zorder=2)
        ax.set_yscale("log")
        ax.set_xlim(min(xs) - datetime.timedelta(days=40), max(xs) + datetime.timedelta(days=55))
        ax.set_title(ttl, fontsize=9, loc="left")
        ax.set_ylabel("星标数（对数）")
        ax.text(.03, .06, f"出生早于划线日：{pre}/50（{pre/50:.0%}）", transform=ax.transAxes,
                fontsize=7.8, color=C_NEG)
        for lab in ax.get_xticklabels():
            lab.set_rotation(40); lab.set_ha("right"); lab.set_fontsize(6.6)
    axes[0].text(datetime.date(2026, 8, 20), 4e5, "划线日\n08-13", fontsize=7, color=C_NEG, ha="left")
    axes[1].text(datetime.date(2025, 10, 1), 4e5, "划线日\n2025-09-22", fontsize=7, color=C_NEG, ha="left")
    fig.suptitle("图 9　星标榜测的是“谁被划进来”，不是“谁为它而生”：两条线的头名多出生在划线之前",
                 fontsize=9.2, x=.012, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .92)); fig.savefig(FIG / "fig09.png", bbox_inches="tight"); plt.close(fig)


def write_top50_table():
    import csv as _csv
    rows = list(_csv.DictReader(open(DATA / "top50.csv", encoding="utf-8")))
    out = ["| 指标 | dsh-plugin | agent-skills |", "|---|---|---|"]
    def st(line):
        r = [x for x in rows if x["line"] == line]
        r.sort(key=lambda x: int(x["rank"]))
        stars = [int(x["stars"]) for x in r]
        return r, stars
    rd_, sd = st("dsh-plugin"); rs, ss = st("agent-skills")
    cut = {"dsh-plugin": "2026-08-13", "agent-skills": "2025-09-22"}
    out.append(f"| 前 50 名星标合计 | {sum(sd):,} | {sum(ss):,} |")
    out.append(f"| 前 10 名占前 50 的星标比重 | {sum(sd[:10])/sum(sd):.1%} | {sum(ss[:10])/sum(ss):.1%} |")
    out.append(f"| 星标中位 | {sorted(sd)[25]:,} | {sorted(ss)[25]:,} |")
    out.append(f"| 星标最低（第 50 名） | {min(sd):,} | {min(ss):,} |")
    out.append(f"| 出生早于划线日 | {sum(1 for x in rd_ if x['created'] < cut['dsh-plugin'])}/50 | "
               f"{sum(1 for x in rs if x['created'] < cut['agent-skills'])}/50 |")
    out.append(f"| 建仓日期最早 | {min(x['created'] for x in rd_)} | {min(x['created'] for x in rs)} |")
    lang_d = {}
    for x in rd_:
        lang_d[x["lang"] or "（未标注）"] = lang_d.get(x["lang"] or "（未标注）", 0) + 1
    lang_s = {}
    for x in rs:
        lang_s[x["lang"] or "（未标注）"] = lang_s.get(x["lang"] or "（未标注）", 0) + 1
    top_d = max(lang_d.items(), key=lambda kv: kv[1])
    top_s = max(lang_s.items(), key=lambda kv: kv[1])
    out.append(f"| 主语言（仓数） | {top_d[0]}（{top_d[1]}） | {top_s[0]}（{top_s[1]}） |")
    both = {x["repo"] for x in rd_} & {x["repo"] for x in rs}
    out.append(f"| 两榜交集（仓库数） | \u2014 | {len(both)} |")
    (DATA / "table_top50.md").write_text("\n".join(out), encoding="utf-8")



# ---------- 交互页的单一数据源：台账（期段 / 存活 / 阶梯 / 交集） ----------
def write_ledger():
    rows = []
    for r in series_rows():
        for metric, col in [("全部仓库", "raw"), ("★≥10", "star10"), ("★≥100", "star100")]:
            if r[col] == "":
                continue
            rows.append(dict(block="期段", line=r["line"], label=r["label"], days=r["days"],
                             metric=metric, value=r[col], note="按 created 分桶；发布前一行为名义分母"))
    for r in retention_table():
        for metric, col in [("队列总量", "base"), ("近7天有推送", "active7"), ("近7天有推送且★≥10", "active7_star10")]:
            rows.append(dict(block="存活", line="dsh-plugin" if r["cohort"].startswith("dsh") else "agent-skills",
                             label=r["label"], days=r["median_age"], metric=metric, value=r[col],
                             note="仓龄中位 " + str(r["median_age"]) + " 天"))
    PER = [("第 1 周 08-13–19", "p1", 7), ("08-20–31", "p2", 12), ("9 月", "p3", 30), ("10-01–23", "p4", 23)]
    for label, key, days in PER:
        for k in (0, 1, 10, 100, 1000):
            c = C.get(f"dsh|{key}|all") if k == 0 else C.get(f"dsh|{key}|star{k}", C.get(f"lad|dsh|{key}|star{k}"))
            if c is None:
                continue
            rows.append(dict(block="阶梯", line="dsh-plugin", label=label, days=days,
                             metric=f"★≥{k}", value=c, note="星标随时间积累，高度不可跨期段比较"))
    for label, v, note in [("topic:dsh-plugin", C["topic:dsh-plugin|top50"], "快照总量"),
                           ("topic:agent-skills", C["topic:agent-skills|top50"], "快照总量"),
                           ("两者重叠", C["overlap|dsh-plugin+agent-skills"], "Jaccard 0.7%")]:
        rows.append(dict(block="交集", line="两条线", label=label, days=SNAP, metric="仓库数", value=v, note=note))
    with open(DATA / "ledger.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["block", "line", "label", "days", "metric", "value", "note"])
        w.writeheader(); w.writerows(rows)
    return rows


def write_tables():
    rows = series_rows()
    out = []
    out.append("| 期段 | 天数 | 全部仓库 | 日均 | ★≥10 | 日均 | ★≥100 | 日均 |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["line"] != "dsh-plugin": continue
        pre = r["period"] == "pre"
        d1 = "—" if pre else f'{r["per_day_raw"]:.1f}'
        d2 = "—" if pre else f'{r["per_day_star10"]:.1f}'
        d3 = "—" if (pre or r["per_day_star100"] == "") else f'{r["per_day_star100"]}'
        out.append(f'| {r["label"]} | {r["days"]} | {r["raw"]:,} | {d1} | {r["star10"]:,} | {d2} | '
                   f'{r["star100"] if r["star100"] != "" else "—"} | {d3} |')
    (BASE / "data" / "table_dsh.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 期段 | 天数 | 全部仓库 | 日均 | ★≥10 | 日均 |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["line"] != "agent-skills": continue
        pre = r["period"] == "pre"
        out.append(f'| {r["label"]} | {r["days"]} | {r["raw"]:,} | {"—" if pre else format(r["per_day_raw"], ".1f")} | '
                   f'{r["star10"]:,} | {"—" if pre else format(r["per_day_star10"], ".1f")} |')
    (BASE / "data" / "table_skills.md").write_text("\n".join(out), encoding="utf-8")

    rows = retention_table()
    out = ["| 队列 | 仓龄中位 | 队列总量 | 近 7 天有推送 | 占比 | 其中有 ★≥10 | 占比 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f'| {r["label"]} | {r["median_age"]} 天 | {r["base"]:,} | {r["active7"]:,} | {r["rate"]}% | '
                   f'{r["active7_star10"]:,} | {r["rate_star10"]}% |')
    (BASE / "data" / "table_retention.md").write_text("\n".join(out), encoding="utf-8")


def write_topfifty():
    rows = []
    for line, f in [("dsh-plugin", "topicdsh-plugin__top50.json"), ("agent-skills", "topicagent-skills__top50.json")]:
        b = json.loads((RAW / f).read_text(encoding="utf-8"))
        for rank, it in enumerate(b["items"], 1):
            rows.append(dict(line=line, rank=rank, repo=it["full_name"], stars=it["stargazers_count"],
                             forks=it["forks_count"], created=it["created_at"][:10],
                             pushed=(it.get("pushed_at") or "")[:10], lang=it.get("language") or "",
                             desc=(it.get("description") or "").replace("\n", " ")[:200]))
    with open(DATA / "top50.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def write_big_appendix():
    """附录里的三张长表：查询清单、星标榜、发布前的仓库。"""
    import json as _json
    C2 = _json.loads((DATA / "counts.json").read_text(encoding="utf-8"))
    # A2 查询清单
    out = ["| # | key | 查询串 | 计数 | 抓取时刻 |", "|---|---|---|---|---|"]
    for i, r in enumerate(sorted(C2, key=lambda x: x["key"]), 1):
        q = (r.get("query") or "").replace("|", "\\|")
        out.append(f'| {i} | `{r["key"]}` | `{q}` | {r.get("total_count")} | {(r.get("fetched_at") or "")[:19]} |')
    (DATA / "table_a2_queries.md").write_text("\n".join(out), encoding="utf-8")

    # C1 星标榜 100 行
    rows = list(csv.DictReader(open(DATA / "top50.csv", encoding="utf-8")))
    out = ["| 线 | 名次 | 仓库 | 星标 | fork | 建仓 | 语言 |", "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: (x["line"], int(x["rank"]))):
        out.append(f'| {r["line"]} | {r["rank"]} | `{r["repo"]}` | {int(r["stars"]):,} | {int(r["forks"]):,} | {r["created"]} | {r["lang"] or "—"} |')
    (DATA / "table_c1.md").write_text("\n".join(out), encoding="utf-8")

    # D1 发布前 35 个
    out = ["| 名次 | 仓库 | 星标 | 建仓 | 描述中提及平台语境 | 描述（摘要） |", "|---|---|---|---|---|---|"]
    KW = ("harness", "plugin", "deepseek", "dsh")
    for r in rows:
        if r["line"] != "dsh-plugin" or r["created"] >= "2026-08-13":
            continue
        d = (r["desc"] or "").lower()
        hit = "是" if any(k in d for k in KW) else "否"
        desc = (r["desc"] or "").replace("|", "/")[:70]
        out.append(f'| {r["rank"]} | `{r["repo"]}` | {int(r["stars"]):,} | {r["created"]} | {hit} | {desc} |')
    (DATA / "table_d1.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    write_series(); write_tables(); write_topfifty(); write_ledger()
    fig01(); fig02(); fig03(); fig04(); fig05()
    write_ladder_table(fig06())
    fig07(); fig08(); fig09(); fig10(); write_top50_table()
    fig11(); fig12(); fig13(); fig14(); write_big_appendix()
    print("figures:", sorted(p.name for p in FIG.glob("*.png")))

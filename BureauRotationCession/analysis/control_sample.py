# -*- coding: utf-8 -*-
"""唐宋对照样本（试点）：官职类型的风险集与生存分析。

设计
----
* 单位：官职类型（不是每一次任命）。每行记录该类型在本朝的起始年、终止年、
  以及“性质变化”的年份与类型（正官化／虚化／割据／禁戒／降格）。
* 风险集：该类型在本朝存续的年份。无变化者按朝代结束删失。
* 分析：分线（内廷／外派／军职／正官）的发生率、发生率比（bootstrap CI）、
  Kaplan–Meier 与 log-rank；另做 50 年窗格的面板计数。
* 证据等级：事件年份为 B/C（正史与制度史通行系年）；编码为探索性，需专家复核。

输出
----
data/control_tangsong.csv
data/control_results.json
assets/charts/fig-risk-km.png
assets/charts/fig-risk-irr.png
data/control_snippet.md
"""
import json
import os
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CH = os.path.join(BASE, "assets", "charts")
os.makedirs(CH, exist_ok=True)

plt.rcParams.update({"font.family": ["SimHei", "Microsoft YaHei"], "axes.unicode_minus": False,
                     "figure.dpi": 180, "savefig.dpi": 180, "font.size": 10})

RED, BLUE, GREEN, GOLD, GRAY = "#b3261e", "#1f4e79", "#2e6b4f", "#a8791f", "#5f6368"
LINE_CN = {"inner": "内廷", "outer": "外派", "military": "军职", "regular": "正官"}
LINE_COL = {"inner": RED, "outer": BLUE, "military": GREEN, "regular": GRAY}

# id, dynasty, office, line, rank, start, end, events[(year,type)], note, grade
OFFICES = [
    # ---------------- 唐 ----------------
    ("T01", "唐", "尚书令", "inner", "高", 618, 907, [(626, "虚化")], "太宗即位后不授", "B"),
    ("T02", "唐", "中书令", "inner", "高", 618, 907, [], "正官，终唐之世", "B"),
    ("T03", "唐", "侍中", "inner", "高", 618, 907, [], "正官，唐后期权轻", "B"),
    ("T04", "唐", "同平章事", "inner", "中", 682, 907, [(723, "正官化")], "政事堂改中书门下", "B"),
    ("T05", "唐", "翰林学士", "inner", "中", 738, 907, [], "内相，未正官化于唐", "B"),
    ("T06", "唐", "枢密使", "inner", "中", 765, 907, [], "宦官传宣，五代正官化", "B"),
    ("T07", "唐", "神策中尉", "inner", "中", 796, 907, [(903, "禁戒")], "朱温诛宦官", "A"),
    ("T08", "唐", "中书舍人", "inner", "中", 618, 907, [], "掌诏诰常职", "B"),
    ("T09", "唐", "给事中", "inner", "中", 618, 907, [], "封驳之职", "B"),
    ("T10", "唐", "内侍监", "inner", "中", 684, 907, [(903, "禁戒")], "宦官首领，与神策同诛", "B"),
    ("T11", "唐", "刺史", "outer", "中", 618, 907, [(755, "割据")], "安史后藩镇化", "A"),
    ("T12", "唐", "都督", "outer", "中", 618, 907, [(711, "虚化")], "节度使取代", "B"),
    ("T13", "唐", "节度使", "outer", "高", 711, 907, [(755, "割据")], "安史之乱后自立", "A"),
    ("T14", "唐", "观察使", "outer", "中", 758, 907, [(780, "割据")], "与节度合一", "B"),
    ("T15", "唐", "转运使", "outer", "中", 760, 907, [], "财权使职，宋为正官", "B"),
    ("T16", "唐", "盐铁使", "outer", "中", 758, 907, [], "财权使职", "B"),
    ("T17", "唐", "团练使", "outer", "中", 755, 907, [], "地方军职", "C"),
    ("T18", "唐", "防御使", "outer", "中", 755, 907, [], "地方军职", "C"),
    ("T19", "唐", "留后", "outer", "中", 755, 907, [(763, "割据")], "河朔世袭", "B"),
    ("T20", "唐", "监军", "outer", "低", 740, 907, [], "宦官监军，未正官化", "B"),
    ("T21", "唐", "判官", "outer", "低", 755, 907, [], "幕职，宋降为选人", "B"),
    ("T22", "唐", "采访使", "outer", "中", 710, 907, [(758, "正官化")], "改观察处置使", "B"),
    ("T23", "唐", "按察使", "outer", "中", 627, 907, [(710, "虚化")], "采访使取代", "C"),
    ("T24", "唐", "县令", "regular", "中", 618, 907, [], "正官", "B"),
    ("T25", "唐", "十六卫大将军", "military", "高", 618, 907, [(750, "虚化")], "府兵坏，名存", "B"),
    ("T26", "唐", "羽林军", "military", "中", 662, 907, [], "禁军之一", "B"),
    ("T27", "唐", "神策军", "military", "高", 754, 907, [(903, "禁戒")], "宦官统禁军，903 解散", "A"),
    ("T28", "唐", "都统", "military", "高", 756, 907, [], "战时统帅", "C"),
    ("T29", "唐", "招讨使", "military", "中", 755, 907, [], "战时使职", "C"),
    ("T30", "唐", "折冲都尉", "military", "中", 618, 907, [(750, "虚化")], "府兵制瓦解", "B"),
    ("T31", "唐", "三师三公", "regular", "高", 618, 907, [], "尊位，本已虚", "B"),
    ("T32", "唐", "御史大夫", "outer", "高", 618, 907, [], "监察长官", "B"),
    ("T33", "唐", "九寺卿", "regular", "中", 618, 907, [], "事务官", "B"),
    # ---------------- 宋 ----------------
    ("S01", "宋", "同平章事", "inner", "高", 960, 1279, [], "宰相正官", "B"),
    ("S02", "宋", "参知政事", "inner", "中", 963, 1279, [(1000, "正官化")], "副相入宰执", "B"),
    ("S03", "宋", "枢密使", "inner", "高", 960, 1279, [], "二府之一", "A"),
    ("S04", "宋", "翰林学士", "inner", "中", 960, 1279, [], "清贵之职", "B"),
    ("S05", "宋", "台谏", "inner", "中", 1017, 1279, [(1200, "虚化")], "南宋权相压制", "B"),
    ("S06", "宋", "知制诰", "inner", "中", 960, 1279, [], "掌诏诰", "B"),
    ("S07", "宋", "入内内侍省", "inner", "中", 960, 1279, [], "宦官受限", "B"),
    ("S08", "宋", "走马承受", "inner", "低", 1000, 1279, [(1127, "禁戒")], "南宋废", "C"),
    ("S09", "宋", "转运使", "outer", "中", 960, 1279, [], "一路监司", "A"),
    ("S10", "宋", "提点刑狱", "outer", "中", 991, 1279, [], "监司", "A"),
    ("S11", "宋", "提举常平", "outer", "中", 1072, 1279, [], "监司", "B"),
    ("S12", "宋", "安抚使", "outer", "中", 1000, 1279, [], "路级军政", "B"),
    ("S13", "宋", "制置使", "outer", "高", 1130, 1279, [(1207, "割据")], "吴曦之叛", "C"),
    ("S14", "宋", "知州", "outer", "中", 960, 1279, [], "差遣", "A"),
    ("S15", "宋", "通判", "outer", "中", 963, 1279, [(1200, "降格")], "南宋降为副贰", "B"),
    ("S16", "宋", "知县", "outer", "低", 960, 1279, [], "差遣", "B"),
    ("S17", "宋", "判官", "outer", "低", 960, 1279, [], "选人阶官", "B"),
    ("S18", "宋", "节度使", "outer", "高", 960, 1279, [], "虚衔", "A"),
    ("S19", "宋", "观察使", "outer", "中", 960, 1279, [], "虚衔", "B"),
    ("S20", "宋", "防御使", "outer", "中", 960, 1279, [], "虚衔", "B"),
    ("S21", "宋", "留守", "outer", "高", 960, 1279, [], "陪都长官", "B"),
    ("S22", "宋", "宣抚使", "outer", "高", 1000, 1279, [], "战时军政", "C"),
    ("S23", "宋", "提举市舶", "outer", "中", 971, 1279, [], "财权监司", "B"),
    ("S24", "宋", "发运使", "outer", "中", 960, 1279, [(1100, "虚化")], "转般法坏", "C"),
    ("S25", "宋", "三司使", "inner", "高", 960, 1279, [(1080, "正官化")], "元丰改户部", "A"),
    ("S26", "宋", "审刑院", "inner", "中", 991, 1279, [(1080, "禁戒")], "元丰废", "B"),
    ("S27", "宋", "殿前都点检", "military", "高", 960, 1279, [(961, "禁戒")], "陈桥后不再授", "A"),
    ("S28", "宋", "三衙", "military", "高", 960, 1279, [], "分掌禁军", "A"),
    ("S29", "宋", "都统制", "military", "中", 1130, 1279, [], "南宋军职", "B"),
    ("S30", "宋", "厢军都指挥使", "military", "中", 960, 1279, [], "厢军役兵化", "B"),
    ("S31", "宋", "巡检", "outer", "低", 960, 1279, [], "地方治安", "B"),
    ("S32", "宋", "三师三公", "regular", "高", 960, 1279, [], "尊位", "B"),
    ("S33", "宋", "六部", "regular", "中", 1080, 1279, [], "元丰后正官", "A"),
    ("S34", "宋", "九寺五监", "regular", "中", 960, 1279, [(1100, "虚化")], "职事归六部", "C"),
]


def rows():
    out = []
    for (i, dyn, office, line, rank, start, end, events, note, grade) in OFFICES:
        first = min([e[0] for e in events]) if events else None
        out.append({
            "id": i, "dynasty": dyn, "office": office, "line": line, "rank": rank,
            "start": start, "end": end, "first_event": first,
            "event": 1 if first else 0,
            "event_type": events[0][1] if events else "",
            "note": note, "grade": grade,
        })
    return out


def km(times, events):
    """Return step points (t, S) for a sample."""
    order = np.argsort(times)
    t = np.asarray(times)[order]
    e = np.asarray(events)[order]
    s = 1.0
    pts = [(0, 1.0)]
    n = len(t)
    for i in range(n):
        if e[i]:
            at_risk = n - i
            s *= (1 - 1 / at_risk)
            pts.append((t[i], s))
    return pts


def logrank(groups):
    """groups: dict name -> (times, events). Returns chi2, p."""
    all_t = sorted({t for ts, es in groups.values() for t, e in zip(ts, es) if e})
    obs = defaultdict(float); exp = defaultdict(float)
    names = list(groups)
    for t in all_t:
        n = {}; d = {}
        for g in names:
            ts, es = groups[g]
            n[g] = sum(1 for x in ts if x >= t)
            d[g] = sum(1 for x, e in zip(ts, es) if x == t and e)
        N = sum(n.values()); D = sum(d.values())
        if N <= 1 or D == 0:
            continue
        for g in names:
            obs[g] += d[g]
            exp[g] += D * n[g] / N
    V = 0.0
    for t in all_t:
        n = {}; d = {}
        for g in names:
            ts, es = groups[g]
            n[g] = sum(1 for x in ts if x >= t)
            d[g] = sum(1 for x, e in zip(ts, es) if x == t and e)
        N = sum(n.values()); D = sum(d.values())
        if N <= 1:
            continue
        V += D * (N - D) * sum(n[g] * (N - n[g]) for g in names) / (N * N * (N - 1))
    chi2 = sum((obs[g] - exp[g]) ** 2 / max(exp[g], 1e-9) for g in names if exp[g] > 0)
    p = 1 - stats.chi2.cdf(chi2, df=max(1, len([g for g in names if exp[g] > 0]) - 1))
    return chi2, p


def poisson_ci(k, exposure, alpha=0.05):
    lo = stats.chi2.ppf(alpha / 2, 2 * k) / (2 * exposure) if k > 0 else 0.0
    hi = stats.chi2.ppf(1 - alpha / 2, 2 * k + 2) / (2 * exposure)
    return lo, hi


def main():
    R = rows()
    # CSV
    import csv
    with open(os.path.join(DATA, "control_tangsong.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0]))
        w.writeheader(); w.writerows(R)

    # exposure & events by line
    by = defaultdict(lambda: {"n": 0, "events": 0, "exposure": 0})
    for r in R:
        t = (r["first_event"] - r["start"]) if r["event"] else (r["end"] - r["start"])
        by[r["line"]]["n"] += 1
        by[r["line"]]["events"] += r["event"]
        by[r["line"]]["exposure"] += max(t, 1)
    for k, v in by.items():
        v["rate"] = v["events"] / v["exposure"] * 100
        lo, hi = poisson_ci(v["events"], v["exposure"])
        v["ci"] = (lo * 100, hi * 100)

    # bootstrap IRR outer vs inner (resample offices)
    rng = np.random.default_rng(11)
    inner = [r for r in R if r["line"] == "inner"]
    outer = [r for r in R if r["line"] == "outer"]

    def rate(group):
        ev = sum(r["event"] for r in group)
        ex = sum((r["first_event"] - r["start"]) if r["event"] else (r["end"] - r["start"]) for r in group)
        return ev / max(ex, 1)

    irr = rate(outer) / rate(inner)
    boots = []
    for _ in range(5000):
        b1 = [outer[i] for i in rng.integers(0, len(outer), len(outer))]
        b2 = [inner[i] for i in rng.integers(0, len(inner), len(inner))]
        boots.append(rate(b1) / max(rate(b2), 1e-9))
    irr_ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    # log-rank by line
    groups = {}
    for line in ["inner", "outer", "military", "regular"]:
        ts = []; es = []
        for r in R:
            if r["line"] != line:
                continue
            ts.append((r["first_event"] - r["start"]) if r["event"] else (r["end"] - r["start"]))
            es.append(r["event"])
        if ts:
            groups[line] = (ts, es)
    chi2, p = logrank(groups)

    # ---- mode of change: secession vs hollowing ----
    def kind(r):
        if not r["event"]:
            return "none"
        return "secession" if r["event_type"] == "割据" else "hollow"
    mode = defaultdict(lambda: defaultdict(int))
    for r in R:
        mode[r["line"]][kind(r)] += 1
    a = mode["outer"]["secession"]; b = mode["outer"]["hollow"] + mode["outer"]["none"]
    c_ = mode["inner"]["secession"]; d_ = mode["inner"]["hollow"] + mode["inner"]["none"]
    fisher = stats.fisher_exact([[a, b], [c_, d_]])

    res = {"n": len(R), "events": sum(r["event"] for r in R),
           "by_line": {k: {kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()} for k, v in by.items()},
           "irr_outer_inner": irr, "irr_ci": irr_ci, "logrank_chi2": chi2, "logrank_p": p,
           "mode": {k: dict(v) for k, v in mode.items()},
           "secession_table": [[a, b], [c_, d_]], "secession_fisher_p": float(fisher.pvalue),
           "lines": list(LINE_CN)}

    # figure A: stacked bars of change mode by line
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    lines = ["inner", "outer", "military", "regular"]
    cats = [("secession", "割据", RED), ("hollow", "虚化/禁戒/降格", GOLD), ("none", "无变化", "#c9c9c9")]
    bottom = np.zeros(len(lines))
    for key, lab, col in cats:
        vals = np.array([mode[l].get(key, 0) for l in lines])
        ax.bar([LINE_CN[l] for l in lines], vals, bottom=bottom, color=col, label=lab, width=.6)
        bottom += vals
    ax.set_ylabel("官职类型数"); ax.legend(frameon=False, fontsize=8)
    ax.set_title("图A　唐宋官职类型的结局构成（试点，n=%d）" % len(R), fontsize=11, fontweight="bold", loc="left")
    ax.grid(alpha=.2, axis="y")
    fig.text(.5, .01, "注：结局按首次性质变化计；无变化者按朝代结束删失。编码为探索性，B/C 级。",
             ha="center", fontsize=7.2, color="#666666")
    fig.savefig(os.path.join(CH, "fig-risk-modes.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # figure B: KM (any change)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for line, (ts, es) in groups.items():
        pts = km(ts, es)
        ax.step([p[0] for p in pts], [p[1] for p in pts], where="post",
                color=LINE_COL[line], lw=1.8, label=LINE_CN[line])
    ax.set_xlabel("自入本朝起的年数"); ax.set_ylabel("尚未发生性质变化的占比")
    ax.set_ylim(0, 1.02); ax.grid(alpha=.2); ax.legend(frameon=False, fontsize=8.5)
    ax.set_title("图B　“未变化”生存曲线：两线并无显著差异", fontsize=11, fontweight="bold", loc="left")
    fig.text(.5, .01, "log-rank χ²=%.2f，p=%.3f；样本小，只作描述。" % (chi2, p),
             ha="center", fontsize=7.2, color="#666666")
    fig.savefig(os.path.join(CH, "fig-risk-km.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # IRR forest
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    ax.errorbar([irr], [0], xerr=[[irr - irr_ci[0]], [irr_ci[1] - irr]], fmt="o", color=RED, capsize=4)
    ax.axvline(1, color=GRAY, ls="--", lw=1)
    ax.set_yticks([]); ax.set_xscale("log")
    ax.set_xlabel("发生率比 IRR（外派／内廷，对数轴）")
    ax.set_title("图B　外派 vs 内廷：性质变化的发生率比", fontsize=10.5, fontweight="bold", loc="left")
    ax.grid(alpha=.2, axis="x")
    fig.text(.5, .02, "点估计 %.2f，bootstrap 95%% CI %.2f—%.2f；试点样本，未控制朝代与品级。" % (irr, irr_ci[0], irr_ci[1]),
             ha="center", fontsize=7.2, color="#666666")
    fig.savefig(os.path.join(CH, "fig-risk-irr.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

    json.dump(res, open(os.path.join(DATA, "control_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # markdown snippet
    L = ["### 唐宋对照样本（试点）\n",
         "共 %d 个官职类型，%d 次性质变化。按线分：" % (len(R), res["events"]), "",
         "| 线 | 类型数 | 事件 | 暴露（类型·年） | 每 100 类型·年 | 95% CI |",
         "|---|---|---|---|---|---|"]
    for line in ["inner", "outer", "military", "regular"]:
        v = by[line]
        L.append("| %s | %d | %d | %d | %.2f | %.2f—%.2f |" % (
            LINE_CN[line], v["n"], v["events"], v["exposure"], v["rate"], v["ci"][0], v["ci"][1]))
    L += ["", "外派/内廷 IRR（任何变化）= %.2f（bootstrap 95%% CI %.2f—%.2f）；log-rank χ²=%.2f，p=%.3f。" % (
        irr, irr_ci[0], irr_ci[1], chi2, p), ""]
    L += ["| 线 | 割据 | 虚化/禁戒/降格 | 无变化 |", "|---|---|---|---|"]
    for l in ["inner", "outer", "military", "regular"]:
        L.append("| %s | %d | %d | %d |" % (LINE_CN[l], mode[l]["secession"], mode[l]["hollow"], mode[l]["none"]))
    L += ["", "割据集中在外派：%d/%d 对 %d/%d，Fisher p=%.3f。" % (
        a, a + b, c_, c_ + d_, fisher.pvalue), ""]
    open(os.path.join(DATA, "control_snippet.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()

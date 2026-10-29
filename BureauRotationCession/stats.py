# -*- coding: utf-8 -*-
"""Quantitative checks for the officialdom paper.

Outputs a Markdown fragment (stats_out.md) and stats.json, both derived from
data_cases.py, so the paper's numbers can be regenerated.

    python stats.py
"""
import json
import math
from collections import Counter

import numpy as np
from scipy import stats

from data_cases import CASES, PERIODS


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def boot_ci(x, stat=np.median, n=5000, seed=7):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    bs = [stat(rng.choice(x, size=len(x), replace=True)) for _ in range(n)]
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def group_outcome(t):
    if t == "割据":
        return "割据"
    if t in ("正官化", "存续"):
        return "制度化"
    return "虚化/降格/禁戒"


paths = {"inner": "内廷", "outer": "外派", "military": "军职", "ritual": "礼制·相职"}

# ---------- 1. path x outcome ----------
tab = {p: Counter() for p in paths}
for c in CASES:
    tab[c[3]][group_outcome(c[11])] += 1

# Fisher: outer vs inner on 割据 vs 制度化 (drop third category to keep 2x2 clean)
n_os = tab["outer"]["割据"]; n_oi = tab["outer"]["制度化"]
n_is = tab["inner"]["割据"]; n_ii = tab["inner"]["制度化"]
fisher_secede = stats.fisher_exact([[n_os, n_oi], [n_is, n_ii]])

# ---------- 2. 保/让 proportions ----------
rows = []
for p in ["inner", "outer", "military", "ritual"]:
    cs = [c for c in CASES if c[3] == p]
    n = len(cs)
    rec = {"path": paths[p], "n": n}
    for key in "CAT":
        k = sum(1 for c in cs if key in c[7])
        rec["keep_" + key] = (k, *wilson(k, n))
    for key in "CAT":
        k = sum(1 for c in cs if key in c[8])
        rec["give_" + key] = (k, *wilson(k, n))
    rows.append(rec)

# ---------- 3. lags ----------
lags = {}
for p in ["inner", "outer", "military"]:
    d = [c[5] - c[4] for c in CASES if c[3] == p]
    lags[p] = {"n": len(d), "median": float(np.median(d)),
               "q1": float(np.percentile(d, 25)), "q3": float(np.percentile(d, 75)),
               "ci": boot_ci(d), "values": d}
mwu = stats.mannwhitneyu(lags["inner"]["values"], lags["outer"]["values"],
                         alternative="two-sided")

# ---------- 4. fusion vs collapse by period ----------
fusion = {  # coded 0/1 per period, same order as PERIODS
    "西周—春秋战国": 0, "秦—西汉": 1, "东汉": 1, "三国": 0, "两晋": 1,
    "十六国": 1, "南朝": 1, "北朝": 0, "隋": 0, "唐前期": 0, "中晚唐": 1,
    "五代十国": 1, "辽": 0, "宋": 0, "西夏": 1, "金": 0, "元": 1, "明": 0,
    "清前期": 0, "晚清": 1, "民国": 1,
    "新中国（1949—1978）": 1, "新中国（1978—2012）": 0, "新中国（2012—2026）": 0,
}
collapse = {"东汉", "中晚唐"}  # 188 / 903-907; two体制性崩解
ft = [[sum(1 for p in PERIODS if fusion[p] and p in collapse),
       sum(1 for p in PERIODS if fusion[p] and p not in collapse)],
      [sum(1 for p in PERIODS if not fusion[p] and p in collapse),
       sum(1 for p in PERIODS if not fusion[p] and p not in collapse)]]
fisher_fusion = stats.fisher_exact(ft)

# ---------- 5. proscription forms ----------
forms = Counter()
for c in CASES:
    if c[11] == "禁戒":
        forms[c[3]] += 1
n_pros = sum(forms.values())

# ---------- 6. outcome mix by century bucket ----------
buckets = [("前1100—前1", -1100, -1), ("1—600", 1, 600), ("601—960", 601, 960),
           ("961—1368", 961, 1368), ("1369—1911", 1369, 1911), ("1912—2026", 1912, 2026)]
mix = []
for name, lo, hi in buckets:
    cs = [c for c in CASES if lo <= c[4] <= hi]
    oc = Counter(group_outcome(c[11]) for c in cs)
    mix.append((name, len(cs), dict(oc)))

out = {
    "n": len(CASES), "periods": len(PERIODS),
    "outcome_by_path": {paths[p]: dict(tab[p]) for p in tab},
    "fisher_secede_outer_vs_inner": {"table": [[n_os, n_oi], [n_is, n_ii]],
                                     "p": float(fisher_secede.pvalue)},
    "keep_give": rows,
    "lags": {paths[p]: {k: v for k, v in lags[p].items() if k != "values"} for p in lags},
    "mwu_p": float(mwu.pvalue),
    "fusion_collapse": {"table": ft, "p": float(fisher_fusion.pvalue)},
    "proscription_by_path": dict(forms),
    "outcome_by_century": mix,
}
json.dump(out, open("stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------- markdown ----------
L = []
L.append("### 量化结果（由 `stats.py` 生成）\n")
L.append("全样本 n=%d，分期 %d。\n" % (len(CASES), len(PERIODS)))

L.append("**结局 × 路径。** 把结局并为三类（制度化＝正官化或存续；虚化类＝虚化、降格、禁戒；割据）。\n")
L.append("| 路径 | n | 制度化 | 虚化类 | 割据 |")
L.append("|---|---|---|---|---|")
for p in ["inner", "outer", "military", "ritual"]:
    t = tab[p]
    L.append("| %s | %d | %d | %d | %d |" % (paths[p], sum(t.values()),
                                             t["制度化"], t["虚化/降格/禁戒"], t["割据"]))
L.append("\n外派线与内廷线的割据比：%d/%d vs %d/%d，Fisher 精确检验 p=%.3f。\n"
         % (n_os, n_os + n_oi, n_is, n_is + n_ii, fisher_secede.pvalue))

L.append("**保有与让出（含 Wilson 95%% 置信区间）。**\n")
L.append("| 路径 | n | 保 C | 保 A | 保 T | 让 C | 让 A | 让 T |")
L.append("|---|---|---|---|---|---|---|---|")
for r in rows:
    def f(key):
        k, p, lo, hi = r[key]
        return "%d%% (%d–%d)" % (round(100 * p), round(100 * lo), round(100 * hi))
    L.append("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
        r["path"], r["n"], f("keep_C"), f("keep_A"), f("keep_T"),
        f("give_C"), f("give_A"), f("give_T")))

L.append("\n**时滞（年）。**\n")
L.append("| 路径 | n | 中位数 | 四分位 | Bootstrap 95% CI |")
L.append("|---|---|---|---|---|")
for p in ["inner", "outer", "military"]:
    d = lags[p]
    L.append("| %s | %d | %.0f | %.0f–%.0f | %.0f–%.0f |" % (
        paths[p], d["n"], d["median"], d["q1"], d["q3"], d["ci"][0], d["ci"][1]))
L.append("\n内廷 vs 外派：Mann–Whitney U，p=%.3f。\n" % mwu.pvalue)

L.append("**融合线与崩解（按时期）。** 2×2：%s；Fisher p=%.3f。\n"
         % (ft, fisher_fusion.pvalue))

L.append("**禁戒（结局类型）分布。** 共 %d 例：%s。\n"
         % (n_pros, "，".join("%s %d" % (paths[k], v) for k, v in forms.items())))

L.append("**按世纪的结局构成。**\n")
L.append("| 时段 | n | 制度化 | 虚化类 | 割据 |")
L.append("|---|---|---|---|---|")
for name, n, oc in mix:
    L.append("| %s | %d | %d | %d | %d |" % (name, n, oc.get("制度化", 0),
                                             oc.get("虚化/降格/禁戒", 0), oc.get("割据", 0)))
L.append("")

open("stats_out.md", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))

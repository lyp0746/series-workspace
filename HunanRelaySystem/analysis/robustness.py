# -*- coding: utf-8 -*-
"""三项稳健性检验：地名 jackknife、成本蒙特卡洛、未来面板的功效。

输出：data/robustness.json、assets/charts/fig09.png
"""
import json
import os
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

# ---------------- 1. toponym ----------------
# (county, years since conversion, retention %, n stations)
TOP = [("宁乡", 9, 95, 23), ("长沙县", 0, 52, 25), ("浏阳", 33, 18, 26),
       ("湘潭", 34, 55, 30), ("茶陵", 0, 72, 13), ("衡州", 70, 11, 44)]
T = np.array([x[1] for x in TOP], float); Y = np.array([x[2] for x in TOP], float)

def ols(t, y):
    X = np.column_stack([np.ones_like(t), t])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    s2 = resid @ resid / (n - k)
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, r2

beta, se, r2 = ols(T, Y)
tcrit = stats.t.ppf(.975, len(T) - 2)
ci = (beta[1] - tcrit * se[1], beta[1] + tcrit * se[1])

jack = []
for i in range(len(T)):
    m = np.ones(len(T), bool); m[i] = False
    b, _, _ = ols(T[m], Y[m])
    jack.append((TOP[i][0], b[0], b[1]))
drop_nx = ols(np.delete(T, 0), np.delete(Y, 0))
drop_zero = ols(T[T > 0], Y[T > 0])
spear = stats.spearmanr(T, Y)

# ---------------- 2. cost Monte Carlo ----------------
rng = np.random.default_rng(20261021)
land = rng.uniform(25, 35, 20000)
water = rng.uniform(8, 15, 20000)
allland = rng.uniform(50, 70, 20000)
save = 1 - (land + water) / allland
save_pct = save * 100
cost = {"mean": float(save_pct.mean()), "p5": float(np.percentile(save_pct, 5)),
        "p95": float(np.percentile(save_pct, 95)), "share_gt_25": float((save_pct > 25).mean())}

# ---------------- 3. power for a future panel ----------------
delta, sd = 10.0, 15.0
z_a, z_b = stats.norm.ppf(.975), stats.norm.ppf(.8)
n_per_group = int(np.ceil(2 * (z_a + z_b) ** 2 * sd ** 2 / delta ** 2))

out = {"toponym": {"slope": float(beta[1]), "intercept": float(beta[0]), "ci": [float(ci[0]), float(ci[1])],
                   "r2": float(r2), "spearman_rho": float(spear.statistic), "spearman_p": float(spear.pvalue),
                   "jackknife": [{"dropped": k, "slope": float(b)} for k, a, b in jack],
                   "drop_ningxiang_slope": float(drop_nx[0][1]), "drop_zero_slope": float(drop_zero[0][1])},
       "cost": cost, "power": {"delta": delta, "sd": sd, "n_per_group": n_per_group}}
json.dump(out, open(os.path.join(DATA, "robustness.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ---------------- figure ----------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.2),
                               gridspec_kw={"width_ratios": [1, 1.1]})
fig.subplots_adjust(left=.08, right=.98, top=.82, bottom=.20, wspace=.30)

names = [k for k, _, _ in jack] + ["全样本"]
vals = [b for _, _, b in jack] + [beta[1]]
cols = [GRAY] * len(jack) + [RED]
ax1.barh(names, vals, color=cols, alpha=.85)
ax1.axvline(0, color="#333", lw=.8)
for i, v in enumerate(vals):
    ax1.text(v - .05, i, "%.2f" % v, va="center", ha="right", fontsize=7.8, color="#333")
ax1.set_xlabel("斜率（百分点／年）", fontsize=9)
ax1.set_title("(a) 地名斜率：逐一剔除一个县", fontsize=10.2, fontweight="bold", loc="left")
ax1.grid(alpha=.18, axis="x")

ax2.hist(save_pct, bins=40, color=GOLD, alpha=.85)
ax2.axvline(cost["mean"], color=RED, lw=1.6, label="均值 %.1f%%" % cost["mean"])
ax2.axvline(25, color=GRAY, ls="--", lw=1, label="25% 参考线")
ax2.set_xlabel("联运相对全陆路的节省（%）", fontsize=9)
ax2.set_ylabel("频数", fontsize=9)
ax2.set_title("(b) 成本节省的蒙特卡洛分布", fontsize=10.2, fontweight="bold", loc="left")
ax2.legend(fontsize=7.8, frameon=False)
ax2.grid(alpha=.18, axis="y")

fig.suptitle("图9　两项稳健性检验：地名斜率对单县不敏感，成本节省集中在 20%—40%",
             fontsize=11.8, fontweight="bold", y=.97)
fig.text(.5, .03, "注：地名样本 n=6，斜率只作县际截面描述；成本为参数区间（陆运 25—35、水运 8—15、全陆 50—70 两/吨）下的 2 万次抽样。",
         ha="center", fontsize=7.4, color="#666666")
fig.savefig(os.path.join(CH, "fig09.png"), bbox_inches="tight", facecolor="white")
plt.close(fig)

print(json.dumps(out, ensure_ascii=False, indent=2))

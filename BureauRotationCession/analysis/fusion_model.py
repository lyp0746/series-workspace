# -*- coding: utf-8 -*-
"""说明性模型：预算约束 + 交互惩罚 ψ 下的“融合—禁戒”循环。

每个“官职”持有 (c,a,t)；每步把最弱一项补高，再投影回可行域
c+a+t+λψ ≤ K，ψ=(ca+at+ct)/3。若三项同时 >0.9 → 记为一次融合；
随后把 a 压低（模拟禁戒），继续。比较 λ=0（无交互惩罚，K=3）与
λ>0（K=2）的融合频率。

输出：data/fusion_model.json、assets/charts/figA1.png
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)
CH = os.path.join(BASE, "assets", "charts"); os.makedirs(CH, exist_ok=True)
plt.rcParams.update({"font.family": ["SimHei", "Microsoft YaHei"], "axes.unicode_minus": False,
                     "figure.dpi": 180, "savefig.dpi": 180, "font.size": 10})
RED, BLUE, GRAY = "#b3261e", "#1f4e79", "#5f6368"


def psi(x):
    c, a, t = x
    return (c * a + a * t + c * t) / 3


def project(v, K, lam):
    v = np.clip(v, 0, 1)
    if v.sum() + lam * psi(v) <= K:
        return v
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        w = np.clip(v - mid, 0, 1)
        if w.sum() + lam * psi(w) <= K:
            lo = mid
        else:
            hi = mid
    return np.clip(v - lo, 0, 1)


def run(lam, K, q=0.0, steps=600, n=30, seed=1):
    """q = 每步出现“紧急预算”（K=3，允许三项同时逼近满格）的概率。"""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.2, 0.9, size=(n, 3))
    events = 0
    for _ in range(steps):
        emergency = rng.random() < q
        Keff = K + 2.5 if emergency else K
        for i in range(n):
            k = int(np.argmin(x[i]))
            e = np.zeros(3); e[k] = 1
            x[i] = project(x[i] + 0.08 * (e - 1 / 3), Keff, lam)
            if x[i].min() > 0.85:
                events += 1
                x[i, 1] = 0.55  # 禁戒：抽掉 A
        if rng.random() < 0.3:
            i = rng.integers(0, n); k = rng.integers(0, 3)
            x[i, k] = max(0.0, x[i, k] - 0.2)
    return events / (steps * n) * 100


def main():
    res = {}
    for lam, K, q, label in [(0.5, 2.0, 0.0, "λ=0.5，无紧急预算"),
                             (0.5, 2.0, 0.02, "λ=0.5，q=2%"),
                             (0.5, 2.0, 0.05, "λ=0.5，q=5%"),
                             (0.0, 2.0, 0.05, "λ=0，q=5%")]:
        res[label] = run(lam, K, q)
    json.dump(res, open(os.path.join(DATA, "fusion_model.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(list(res.keys()), list(res.values()), color=[BLUE, "#7b4b94", RED], alpha=.85)
    for i, v in enumerate(res.values()):
        ax.text(i, v + 0.01, "%.2f" % v, ha="center", fontsize=9)
    ax.set_ylabel("每 100 官职·步的融合次数", fontsize=9.2)
    ax.set_title("图A1　说明性模型：融合需要紧急预算，ψ 抬高门槛", fontsize=11, fontweight="bold", loc="left")
    ax.grid(alpha=.2, axis="y")
    fig.text(.5, .02, "注：参数为示意值；模型只演示“预算只够两项时，补第三项会周期性触发融合—禁戒”，不是历史测量。",
             ha="center", fontsize=7.2, color="#666666")
    fig.savefig(os.path.join(CH, "figA1.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

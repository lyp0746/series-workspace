# -*- coding: utf-8 -*-
"""审阅用探针（不属于正文分析）：检验几处可深化/需修正的地方。

运行：python analysis/review_probe.py

六项：
  A. 分区距离（ARI）：组内/组间、置换检验、PERMANOVA 式 R²、分窗口
  B. 模板复制：不同顶层切线组合数、模板级 W1/W2
  C. 门的通货：跨传统穿透率（精确年，每传统≥2 部）
  D. W3 恒等式：交叉曲线是否由边际分布完全决定
  E. W4 归一化：三种口径下的分辨率排序
  F. 多重比较：BH 校正
"""
import itertools
import sys
import os
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
sys.path.insert(0, os.path.join(BASE, "analysis"))
import stats as st  # noqa: E402
from collections import Counter  # noqa: E402
from scipy.stats import kruskal  # noqa: E402

rows = st.load()
srcs = st.by_source(rows)
KEYS = [k for k in srcs if srcs[k]["tradition"] != "other"]
KEYS_W = [k for k in KEYS if srcs[k]["scope"] != "nation"]
TR = {k: srcs[k]["tradition"] for k in KEYS}


def ari(a, b):
    ca, cb = sorted(set(a)), sorted(set(b))
    idx = {v: i for i, v in enumerate(ca)}
    jdx = {v: i for i, v in enumerate(cb)}
    M = np.zeros((len(ca), len(cb)))
    for x, y in zip(a, b):
        M[idx[x], jdx[y]] += 1
    n = M.sum()
    s = lambda x: x * (x - 1) / 2  # noqa: E731
    sij, si, sj, sn = s(M).sum(), s(M.sum(1)).sum(), s(M.sum(0)).sum(), s(n)
    den = (si + sj) / 2 - si * sj / sn
    return np.nan if abs(den) < 1e-12 else (sij - si * sj / sn) / den


def dist_matrix(keys, lo=400, hi=2000, recode=False):
    years = np.arange(lo, hi + 1)
    E = {}
    for k in keys:
        seq = []
        for y in years:
            e = st.era_at(srcs[k]["all"], y)
            if recode and srcs[k]["tradition"] == "china" and e == "contemporary" and y < 1945:
                e = "modern"
            seq.append(e)
        E[k] = seq
    n = len(keys)
    D = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        D[i, j] = D[j, i] = 1 - ari(E[keys[i]], E[keys[j]])
    return D


def perm_test(D, keys, n=2000, seed=20261022):
    tr = [TR[k] for k in keys]
    obs = _within_between(D, tr)
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n):
        p = list(rng.permutation(tr))
        if _within_between(D, p) >= obs:
            cnt += 1
    return obs, (cnt + 1) / (n + 1)


def _within_between(D, tr):
    w, b = [], []
    for i, j in itertools.combinations(range(len(tr)), 2):
        (w if tr[i] == tr[j] else b).append(D[i, j])
    return float(np.mean(b) - np.mean(w))


def r2(D, groups):
    n = len(groups)
    iu = np.triu_indices(n, 1)
    ss_tot = (D[iu] ** 2).sum() / n
    ss_w = 0.0
    for u in set(groups):
        ix = [i for i in range(n) if groups[i] == u]
        m = len(ix)
        if m < 2:
            continue
        sub = D[np.ix_(ix, ix)][np.triu_indices(m, 1)]
        ss_w += (sub ** 2).sum() / m
    return float((ss_tot - ss_w) / ss_tot)


def A():
    print("A. 分区距离（ARI，400—2000）")
    D = dist_matrix(KEYS_W)
    obs, p = perm_test(D, KEYS_W)
    print("   n=%d  组间距离−组内距离 %.3f  置换 p=%.4f" % (len(KEYS_W), obs, p))
    for t in ("european", "global", "china"):
        ix = [i for i in range(len(KEYS_W)) if TR[KEYS_W[i]] == t]
        w = [D[i, j] for i, j in itertools.combinations(ix, 2)]
        b = [D[i, j] for i in ix for j in range(len(KEYS_W)) if TR[KEYS_W[j]] != t]
        print("   %-9s 组内 ARI %.3f（n=%d）  组间 %.3f" % (t, 1 - np.mean(w), len(ix), 1 - np.mean(b)))
    for a, b in itertools.combinations(("european", "global", "china"), 2):
        v = [D[i, j] for i in range(len(KEYS_W)) for j in range(i + 1, len(KEYS_W))
             if {TR[KEYS_W[i]], TR[KEYS_W[j]]} == {a, b}]
        print("   %s—%s ARI %.3f" % (a, b, 1 - np.mean(v)))
    print("   R² tradition %.2f   R² scope %.2f"
          % (r2(D, [TR[k] for k in KEYS_W]),
             r2(D, [srcs[k]["scope"] for k in KEYS_W])))
    Dm = dist_matrix(KEYS_W, 1500, 2000)
    for a, b in itertools.combinations(("european", "global", "china"), 2):
        v = [Dm[i, j] for i in range(len(KEYS_W)) for j in range(i + 1, len(KEYS_W))
             if {TR[KEYS_W[i]], TR[KEYS_W[j]]} == {a, b}]
        print("   1500—2000：%s—%s ARI %.3f" % (a, b, 1 - np.nanmean(v)))
    # 去掉 3 部单一断点论证性著作
    mono = {"Pomeranz《大分流》", "Bayly《现代世界的诞生 1780—1914》", "Osterhammel《世界的转型》"}
    keys = [k for k in KEYS_W if k not in mono]
    D2 = dist_matrix(keys)
    for t in ("global",):
        ix = [i for i in range(len(keys)) if TR[keys[i]] == t]
        w = [D2[i, j] for i, j in itertools.combinations(ix, 2)]
        print("   去掉 3 部论证性著作后 within %s ARI %.3f（n=%d）" % (t, 1 - np.mean(w), len(ix)))


def B():
    print("B. 模板复制")
    tpl = {}
    for k in KEYS_W:
        tpl.setdefault(tuple(int(y) for y in srcs[k]["part_years"]), []).append(k)
    print("   来源 %d 部，不同顶层切线组合 %d 套" % (len(KEYS_W), len(tpl)))
    for c, v in sorted(tpl.items(), key=lambda kv: -len(kv[1]))[:6]:
        if len(v) > 1:
            print("   %d 部同模板 %s" % (len(v), c))
    allyears = [y for c in tpl for y in c]
    cnt = Counter(allyears)
    top = cnt.most_common(10)
    print("   模板级边界 %d 条；前十占比 %.3f（来源级 0.697）"
          % (len(allyears), sum(c for _, c in top) / len(allyears)))
    print("   ", top)
    for t in ("european", "global", "china"):
        ts = [c for c, v in tpl.items()
              if Counter(TR[k] for k in v).most_common(1)[0][0] == t]
        print("   %-9s 模板 %d：1000—1225 %.2f  1750±15 %.2f  1500 %.2f  1640 %.2f  1917 %.2f"
              % (t, len(ts),
                 np.mean([any(1000 <= y <= 1225 for y in c) for c in ts]),
                 np.mean([any(1735 <= y <= 1765 for y in c) for c in ts]),
                 np.mean([any(1450 <= y <= 1550 for y in c) for c in ts]),
                 np.mean([any(1635 <= y <= 1645 for y in c) for c in ts]),
                 np.mean([any(1915 <= y <= 1919 for y in c) for c in ts])))


def C():
    print("C. 门的通货（精确年；某传统≥2 部才计入该传统）")
    sup = Counter((r["tradition"], r["boundary_year"]) for r in rows if r["level"] == "part")
    yrs = sorted({y for (_, y), c in sup.items() if c >= 2})
    rank = {"european": 0, "global": 1, "china": 2}
    for y in yrs:
        tt = [t for t in rank if sup[(t, y)] >= 2]
        if len(tt) >= 2:
            print("   %5d  %d/3   eur %2d  glob %2d  chn %2d"
                  % (y, len(tt), sup[("european", y)], sup[("global", y)], sup[("china", y)]))


def D():
    print("D. W3 恒等式检验")
    keys = [k for k in KEYS if srcs[k]["ms"] is not None]
    years = np.arange(400, 2001)
    M = {k: srcs[k]["ms"] <= years for k in keys}
    pairs = [(a, b) for a, b in itertools.combinations(keys, 2) if TR[a] != TR[b]]
    obs = sum((M[a] != M[b]).astype(float) for a, b in pairs) / len(pairs)
    pred = np.zeros(len(years))
    wsum = 0
    for t1, t2 in itertools.combinations(("european", "global", "china"), 2):
        A_ = [k for k in keys if TR[k] == t1]
        B_ = [k for k in keys if TR[k] == t2]
        p1 = np.mean([M[k] for k in A_], axis=0)
        p2 = np.mean([M[k] for k in B_], axis=0)
        pred += len(A_) * len(B_) * (p1 * (1 - p2) + p2 * (1 - p1))
        wsum += len(A_) * len(B_)
    pred /= wsum
    r2v = 1 - ((obs - pred) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
    print("   观测曲线与边际预期曲线的 R² = %.4f（1.0000 即恒等式）" % r2v)
    print("   最大残差 %.2e" % np.abs(obs - pred).max())


def E():
    print("E. W4 的三种归一化")
    for label, fn in (
        ("原始条数（窗内）", lambda s: len(s["part_years"])),
        ("每 1600 年", lambda s: len(s["part_years"]) / 1.6),
        ("每边界跨度千年（现用）",
         lambda s: len(s["part_years"]) / (max(int(s["part_years"].max() - s["part_years"].min()), 100) / 1000)),
    ):
        out = {}
        for sc in ("world", "region", "nation"):
            v = [fn(s) for s in srcs.values() if s["scope"] == sc]
            out[sc] = round(float(np.mean(v)), 2)
        H, p = kruskal(*[[fn(s) for s in srcs.values() if s["scope"] == sc]
                         for sc in ("world", "region", "nation")])
        print("   %-22s world %.2f  region %.2f  nation %.2f   KW p=%.3f"
              % (label, out["world"], out["region"], out["nation"], p))


def F():
    print("F. BH 校正（读当前 stats.json 的七条主检验）")
    import json
    o = json.load(open(os.path.join(BASE, "data", "stats.json"), encoding="utf-8"))
    ps = {"W1": o["W1"]["p_top10"], "W2": o["W2"]["kruskal"]["p"],
          "W3": o["W3"]["p"], "W4": min(v["p"] for v in o["W4"]["metrics"].values()),
          "W5": 1.0, "W6": min(v["p"] for v in o["W6"].values()), "W7": 1e-100}
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m = len(items)
    q, prev = {}, 1.0
    for i in range(m - 1, -1, -1):
        k, pv = items[i]
        prev = min(prev, pv * m / (i + 1))
        q[k] = min(1.0, prev)
    print("   ", [(k, round(q[k], 4)) for k, _ in items])


if __name__ == "__main__":
    for fn in (A, B, C, D, E, F):
        fn()
        print()

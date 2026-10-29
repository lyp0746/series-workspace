# -*- coding: utf-8 -*-
"""分析核心 v2：核心语料（46 部）与扩展语料（14 部）。

新增（相对 v1）：
  * 模板层：去重后的顶层切线组合，模板级 W1/W2 与模板置换
  * 分区距离：ARI 矩阵、组内/组间、PERMANOVA 式 R²、MDS、分窗口
  * 恒等式：交叉曲线与边际预期的 R²（识别性检验）
  * 分辨率三口径：原始条数 / 固定窗 / 边界跨度
  * 门：穿透率、分量、排他性
  * 命名层：六类名称的分布与"同刀异名"列联
  * 扩展语料：显式年、纪年零点、与核心的门重叠
"""
import itertools
import json
import os
import sys
from collections import Counter
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
from schemes import SCHEMES, sources  # noqa: E402

CORE_WIN = (400, 2000)
ERA_ORDER = ["ancient", "medieval", "early_modern", "modern", "contemporary"]
TRAD_ORDER = ["european", "global", "china"]
TRAD_CN = {"european": "欧洲中心", "global": "全球史", "china": "中国教材",
           "other": "补充（维基）", "premodern_europe": "前现代欧洲",
           "islamic": "伊斯兰", "african": "非洲", "south_asian": "南亚",
           "east_asian_premodern": "东亚（前现代）", "americas": "美洲"}
SCOPE_CN = {"world": "世界", "region": "区域", "nation": "国别"}
GENRE_CN = {"survey": "教材/通史", "reference": "工具书", "argument": "论证性著作",
            "curriculum": "课程框架", "chronicle": "编年史",
            "sacred_history": "圣史", "treatise": "论说"}
NAME_CN = {"event": "事件", "process": "过程", "space": "空间",
           "dynastic": "王朝", "sacred": "圣史", "era": "时代"}
COLORS = {"european": "#b3261e", "global": "#1f4e79", "china": "#2e6b4f",
          "other": "#8a8a8a", "premodern_europe": "#7a5c3e", "islamic": "#a8791f",
          "african": "#6b4c9a", "south_asian": "#b5651d",
          "east_asian_premodern": "#3f6d6d", "americas": "#8a3b5c"}

EVENTS = {476: "西罗马灭亡", 1453: "君士坦丁堡陷落", 1492: "哥伦布抵达美洲",
          1517: "九十五条论纲", 1640: "英国议会召开", 1648: "威斯特伐利亚和约",
          1789: "法国大革命", 1848: "欧洲革命", 1914: "一战爆发", 1917: "十月革命",
          1945: "二战结束", 1991: "苏联解体"}
PROCESS = {600: "古典之后", 1000: "欧亚复兴", 1200: "蒙古网络", 1400: "全球网络",
           1750: "工业化", 1800: "大分流"}


def _win(y):
    return y is not None and CORE_WIN[0] <= y <= CORE_WIN[1]


def load(include_other=True, include_chapter=True, series="core"):
    out = []
    for r in SCHEMES:
        if r["series"] != series:
            continue
        if not include_other and r["tradition"] == "other":
            continue
        if not include_chapter and r["level"] == "chapter":
            continue
        if r["boundary_year"] is None:
            continue
        if series == "core" and not _win(r["boundary_year"]):
            continue
        out.append(r)
    return out


def by_source(rows=None):
    rows = rows if rows is not None else load()
    out = {}
    for r in rows:
        d = out.setdefault(r["source"], dict(
            source=r["source"], tradition=r["tradition"], scope=r["scope"],
            genre=r["genre"], year_published=r["year_published"],
            part=[], chapter=[], all=[]))
        d["all"].append(r)
        (d["part"] if r["level"] == "part" else d["chapter"]).append(r)
    for d in out.values():
        d["part_years"] = np.array(sorted({x["boundary_year"] for x in d["part"]}), int)
        ms = [x["boundary_year"] for x in d["part"]
              if x["era"] in ("early_modern", "modern")]
        d["ms"] = min(ms) if ms else None
    return out


def era_at(src_rows, y):
    cur = "ancient"
    for r in sorted(src_rows, key=lambda z: z["boundary_year"]):
        if r["boundary_year"] <= y:
            cur = r["era"]
        else:
            break
    return cur


# ---------------------------------------------------------------- 模板
def templates(keys=None):
    rows = load()
    srcs = by_source(rows)
    if keys is None:
        keys = [k for k in srcs if srcs[k]["tradition"] != "other"]
    tpl = {}
    for k in keys:
        c = tuple(int(y) for y in srcs[k]["part_years"])
        tpl.setdefault(c, []).append(k)
    return tpl


def w1(rows):
    ys = np.array([r["boundary_year"] for r in rows], int)
    vals, cnt = np.unique(ys, return_counts=True)
    order = np.argsort(-cnt)
    top = [(int(vals[i]), int(cnt[i])) for i in order[:12]]
    top10 = cnt[order[:10]].sum() / len(ys)
    p = cnt / cnt.sum()
    rng = np.random.default_rng(20261022)
    src_n = [len(s["all"]) for s in by_source(rows).values()]
    sims = []
    for _ in range(2000):
        draw = []
        for n in src_n:
            draw.extend(rng.integers(CORE_WIN[0], CORE_WIN[1] + 1, n))
        v, c = np.unique(draw, return_counts=True)
        sims.append(np.sort(c)[::-1][:10].sum() / max(len(draw), 1))
    sims = np.array(sims)
    return dict(n=len(ys), top=top, top5=float(cnt[order[:5]].sum() / len(ys)),
                top10=float(top10), hhi=float((p ** 2).sum()),
                null_top10=float(sims.mean()), p_top10=float((sims >= top10).mean()))


def w1_template(tpl, seed=20261022):
    years = [y for c in tpl for y in c]
    cnt = np.array(sorted(((Counter(years)[y], y) for y in set(years)), reverse=True))
    vals = cnt[:, 0]
    obs = vals[:10].sum() / len(years)
    sizes = [len(c) for c in tpl.values()]
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(2000):
        draw = []
        for n in sizes:
            draw.extend(rng.integers(CORE_WIN[0], CORE_WIN[1] + 1, n))
        v, c = np.unique(draw, return_counts=True)
        sims.append(np.sort(c)[::-1][:10].sum() / max(len(draw), 1))
    sims = np.array(sims)
    return dict(n_templates=len(tpl), n_boundaries=len(years),
                top10=float(obs), null_top10=float(sims.mean()),
                p=float((sims >= obs).mean()),
                top=[(int(y), int(c)) for c, y in cnt[:12]])


# ---------------------------------------------------------------- W2
def _shares(srcs, years_key="part_years"):
    out = {}
    for t in TRAD_ORDER:
        ss = [s for s in srcs.values() if s["tradition"] == t]
        if not ss:
            continue
        py = np.concatenate([s[years_key] for s in ss])
        ms = np.array([s["ms"] for s in ss if s["ms"] is not None])
        out[t] = dict(
            n=len(ss), n_b=sum(len(s["part"]) + len(s["chapter"]) for s in ss),
            median_part=float(np.median(py)),
            median_ms=float(np.median(ms)) if len(ms) else None,
            pre=float(np.mean([any(1000 <= y <= 1225 for y in s[years_key]) for s in ss])),
            late=float(np.mean([any(1735 <= y <= 1765 for y in s[years_key]) for s in ss])),
            y1640=float(np.mean([any(1635 <= y <= 1645 for y in s[years_key]) for s in ss])),
            y1917=float(np.mean([any(1915 <= y <= 1919 for y in s[years_key]) for s in ss])),
            y1500=float(np.mean([any(1450 <= y <= 1550 for y in s[years_key]) for s in ss])),
        )
    return out


def w2(srcs):
    from scipy.stats import kruskal, fisher_exact
    out = _shares(srcs)
    groups = [np.concatenate([s["part_years"] for s in srcs.values()
                              if s["tradition"] == t]) for t in TRAD_ORDER]
    H, pH = kruskal(*groups)
    out["kruskal"] = dict(H=float(H), p=float(pH))
    for key, name in (("pre", "pre_fisher"), ("late", "late_fisher")):
        a = [any((1000 <= y <= 1225) if key == "pre" else (1735 <= y <= 1765)
                 for y in s["part_years"]) for s in srcs.values() if s["tradition"] == "european"]
        b = [any((1000 <= y <= 1225) if key == "pre" else (1735 <= y <= 1765)
                 for y in s["part_years"]) for s in srcs.values() if s["tradition"] == "global"]
        tab = [[sum(a), len(a) - sum(a)], [sum(b), len(b) - sum(b)]]
        out[name] = dict(table=tab, p=float(fisher_exact(tab)[1]))
    return out


def w2_template(tpl, tr_map):
    out = {}
    for t in TRAD_ORDER:
        cs = [c for c, v in tpl.items()
              if Counter(tr_map[k] for k in v).most_common(1)[0][0] == t]
        if not cs:
            continue
        out[t] = dict(
            n=len(cs),
            pre=float(np.mean([any(1000 <= y <= 1225 for y in c) for c in cs])),
            late=float(np.mean([any(1735 <= y <= 1765 for y in c) for c in cs])),
            y1640=float(np.mean([any(1635 <= y <= 1645 for y in c) for c in cs])),
            y1917=float(np.mean([any(1915 <= y <= 1919 for y in c) for c in cs])),
            y1500=float(np.mean([any(1450 <= y <= 1550 for y in c) for c in cs])),
        )
    return out


# ---------------------------------------------------------------- 分区距离
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
    return np.nan if abs(den) < 1e-12 else float((sij - si * sj / sn) / den)


def _era_seq(m, lo, hi):
    return [era_at(m["all"], y) for y in range(lo, hi + 1)]


def distance_matrix(keys, srcs, lo=400, hi=2000):
    E = {k: _era_seq(srcs[k], lo, hi) for k in keys}
    n = len(keys)
    D = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        D[i, j] = D[j, i] = 1 - ari(E[keys[i]], E[keys[j]])
    return D


def w3(keys, srcs, D, seed=20261022):
    tr = [srcs[k]["tradition"] for k in keys]
    w, b = [], []
    for i, j in itertools.combinations(range(len(keys)), 2):
        (w if tr[i] == tr[j] else b).append(D[i, j])
    obs = float(np.mean(b) - np.mean(w))
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(2000):
        p = list(rng.permutation(tr))
        ww, bb = [], []
        for i, j in itertools.combinations(range(len(p)), 2):
            (ww if p[i] == p[j] else bb).append(D[i, j])
        if np.mean(bb) - np.mean(ww) >= obs:
            cnt += 1
    out = dict(n=len(keys), diff=obs, p=(cnt + 1) / 2001,
               within={}, between={}, pair={}, ari={})
    for t in TRAD_ORDER:
        ix = [i for i in range(len(keys)) if tr[i] == t]
        if len(ix) > 1:
            ww = [D[i, j] for i, j in itertools.combinations(ix, 2)]
            out["within"][t] = float(1 - np.mean(ww))
        bb = [D[i, j] for i in ix for j in range(len(keys)) if tr[j] != t]
        out["between"][t] = float(1 - np.mean(bb))
    for a, b_ in itertools.combinations(TRAD_ORDER, 2):
        v = [D[i, j] for i in range(len(keys)) for j in range(i + 1, len(keys))
             if {tr[i], tr[j]} == {a, b_}]
        out["pair"]["%s-%s" % (a, b_)] = float(1 - np.mean(v))
    out["within_mean"] = float(1 - np.mean(w))
    out["between_mean"] = float(1 - np.mean(b))
    out["r2_tradition"] = _r2(D, tr)
    out["r2_scope"] = _r2(D, [srcs[k]["scope"] for k in keys])
    # 分窗口
    Dm = distance_matrix(keys, srcs, 1500, 2000)
    for a, b_ in itertools.combinations(TRAD_ORDER, 2):
        v = [Dm[i, j] for i in range(len(keys)) for j in range(i + 1, len(keys))
             if {tr[i], tr[j]} == {a, b_}]
        out["pair_1500"] = out.get("pair_1500", {})
        out["pair_1500"]["%s-%s" % (a, b_)] = float(1 - np.nanmean(v))
    # MDS
    n = len(keys)
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    ev = np.linalg.eigvalsh(B)[::-1]
    pos = ev[ev > 1e-9]
    out["mds_share2"] = float(pos[:2].sum() / pos.sum())
    wv, vv = np.linalg.eigh(B)
    wv, vv = wv[::-1], vv[:, ::-1]
    coords = vv[:, :2] * np.sqrt(np.maximum(wv[:2], 0))
    out["mds"] = dict(eig=[float(x) for x in pos[:5]],
                      coords=[[float(x) for x in row] for row in coords])
    out["keys"] = keys
    return out


def _r2(D, groups):
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


# ---------------------------------------------------------------- 恒等式
def identity(rows, seed=20261022):
    srcs = by_source(rows)
    keys = [k for k in srcs if srcs[k]["tradition"] in TRAD_ORDER and srcs[k]["ms"] is not None]
    years = np.arange(CORE_WIN[0], CORE_WIN[1] + 1)
    M = {k: srcs[k]["ms"] <= years for k in keys}
    pairs = [(a, b) for a, b in itertools.combinations(keys, 2)
             if srcs[a]["tradition"] != srcs[b]["tradition"]]
    obs = sum((M[a] != M[b]).astype(float) for a, b in pairs) / len(pairs)
    pred = np.zeros(len(years))
    wsum = 0
    for t1, t2 in itertools.combinations(TRAD_ORDER, 2):
        A = [k for k in keys if srcs[k]["tradition"] == t1]
        B = [k for k in keys if srcs[k]["tradition"] == t2]
        p1 = np.mean([M[k] for k in A], axis=0)
        p2 = np.mean([M[k] for k in B], axis=0)
        pred += len(A) * len(B) * (p1 * (1 - p2) + p2 * (1 - p1))
        wsum += len(A) * len(B)
    pred /= wsum
    r2 = 1 - ((obs - pred) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
    # 朴素带检验：两条预设带 vs 随机移带（用于说明"若到此为止"会得到什么）
    def band_mean(a, b):
        m = (years >= a) & (years <= b)
        return float(obs[m].mean())
    obs_band = np.mean([band_mean(1450, 1550), band_mean(1750, 1850)])
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(2000):
        a = rng.integers(400, 1900)
        b = rng.integers(400, 1900)
        sims.append(np.mean([band_mean(a, a + 100), band_mean(b, b + 100)]))
    sims = np.array(sims)
    band_p = float((sims >= obs_band).mean())
    return dict(npairs=len(pairs), r2=float(r2), band_p=band_p, band_mean=float(obs_band),
                max_resid=float(np.abs(obs - pred).max()),
                years=years.tolist(),
                obs=[round(float(x), 5) for x in obs],
                pred=[round(float(x), 5) for x in pred])


# ---------------------------------------------------------------- W4
def w4(srcs):
    from scipy.stats import kruskal
    recs = []
    for s in srcs.values():
        y = s["part_years"]
        if len(y) < 1:
            continue
        span = max(int(y.max() - y.min()), 100)
        recs.append(dict(source=s["source"], scope=s["scope"], tradition=s["tradition"],
                         genre=s["genre"], n=int(len(y)), span=span,
                         raw=float(len(y)), fixed=float(len(y) / 1.6),
                         rate=float(len(y) / (span / 1000))))
    out = {"recs": recs, "metrics": {}}
    for key in ("raw", "fixed", "rate"):
        groups = [[r[key] for r in recs if r["scope"] == sc]
                  for sc in ("world", "region", "nation")]
        groups = [g for g in groups if len(g) > 1]
        H, p = kruskal(*groups)
        out["metrics"][key] = dict(
            means={sc: float(np.mean([r[key] for r in recs if r["scope"] == sc]))
                   for sc in ("world", "region", "nation")},
            ns={sc: len([r for r in recs if r["scope"] == sc])
                for sc in ("world", "region", "nation")},
            H=float(H), p=float(p))
    return out


# ---------------------------------------------------------------- W5 门
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def gates(rows):
    """穿透率（3 个传统中几个使用）、分量、排他性。"""
    srcs = by_source(rows)
    tr = {k: srcs[k]["tradition"] for k in srcs}
    sup = {}
    for r in rows:
        if r["level"] == "part":
            sup.setdefault(r["boundary_year"], {}).setdefault(r["tradition"], 0)
            sup[r["boundary_year"]][r["tradition"]] += 1
    out = {}
    for y, d in sorted(sup.items(), key=lambda kv: -sum(kv[1].values())):
        pen = sum(1 for t in TRAD_ORDER if d.get(t, 0) >= 2)
        if sum(d.values()) < 3:
            continue
        out[int(y)] = dict(
            penetration=pen, support={t: d.get(t, 0) for t in TRAD_ORDER},
            total=sum(d.values()),
            weight={t: float(np.mean([1350 <= v <= 1650 for v in srcs[k]["part_years"]]))
                    for t, k in [(t, None) for t in []]})
    # 1500 的分量与排他性
    for t in TRAD_ORDER:
        ks = [k for k in srcs if tr[k] == t]
        w = [np.mean([1350 <= y <= 1650 for y in srcs[k]["part_years"]]) for k in ks]
        entry = [k for k in ks if srcs[k]["ms"] is not None and 1450 <= srcs[k]["ms"] <= 1550]
        excl = [sum(1 for y in srcs[k]["part_years"]
                    if 1300 <= y <= 1700 and abs(y - 1500) > 60) == 0 for k in entry]
        out.setdefault("_summary", {})[t] = dict(
            weight=float(np.mean(w)), n=len(ks),
            entry=len(entry), entry_share=len(entry) / len(ks),
            exclusive=float(np.mean(excl)) if excl else None, n_entry=len(excl))
    return out


def w5(srcs):
    out = {}
    for t in TRAD_ORDER:
        ss = [s for s in srcs.values() if s["tradition"] == t]
        has = [any(1450 <= y <= 1550 for y in s["part_years"]) for s in ss]
        entry = [s["ms"] is not None and 1450 <= s["ms"] <= 1550 for s in ss]
        w = [np.mean([1350 <= y <= 1650 for y in s["part_years"]]) for s in ss]
        ex = []
        for s in ss:
            if s["ms"] is not None and 1450 <= s["ms"] <= 1550:
                ex.append(all(abs(int(y) - s["ms"]) > 200 for y in s["part_years"]
                              if int(y) != s["ms"]))
        out[t] = dict(n=len(ss), k_has=int(sum(has)), p_has=float(np.mean(has)),
                      ci_has=wilson(int(sum(has)), len(ss)),
                      k_entry=int(sum(entry)), p_entry=float(np.mean(entry)),
                      ci_entry=wilson(int(sum(entry)), len(ss)),
                      w1500=float(np.mean(w)),
                      exclusive=float(np.mean(ex)) if ex else None, n_ex=len(ex))
    return out


# ---------------------------------------------------------------- W6
def w6(srcs):
    from scipy.stats import spearmanr
    out = {}
    for t in TRAD_ORDER:
        ss = [s for s in srcs.values() if s["tradition"] == t and s["ms"] is not None]
        x = np.array([s["year_published"] for s in ss], float)
        y = np.array([s["ms"] for s in ss], float)
        rho, p = spearmanr(x, y)
        out[t] = dict(n=len(x), rho=float(rho), p=float(p),
                      slope=float(np.polyfit(x, y, 1)[0]) if len(x) > 2 else None,
                      pts=[(int(a), int(b), s["source"]) for a, b, s in zip(x, y, ss)])
    return out


# ---------------------------------------------------------------- W7
def w7(rows, seed=20261022):
    ys = np.array([r["boundary_year"] for r in rows], int)
    ev = np.array(sorted(EVENTS))
    pv = np.array(sorted(PROCESS))
    tol = 3
    al = ((ys[:, None] - ev[None, :]).__abs__() <= tol).any(axis=1)
    ap = ((ys[:, None] - pv[None, :]).__abs__() <= tol).any(axis=1)
    exp = ev.size * (2 * tol + 1) / (CORE_WIN[1] - CORE_WIN[0] + 1)
    # 来源级聚类自助
    by = {}
    for r in rows:
        by.setdefault(r["source"], []).append(r["boundary_year"])
    keys = list(by)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(2000):
        pick = rng.choice(keys, len(keys), replace=True)
        arr = np.concatenate([np.array(by[k]) for k in pick])
        boots.append(((arr[:, None] - ev[None, :]).__abs__() <= tol).any(axis=1).mean())
    by_trad = {}
    for t in TRAD_ORDER:
        sub = np.array([r["boundary_year"] for r in rows if r["tradition"] == t], int)
        by_trad[t] = dict(
            n=len(sub),
            event=float(((sub[:, None] - ev[None, :]).__abs__() <= tol).any(axis=1).mean()),
            process=float(((sub[:, None] - pv[None, :]).__abs__() <= tol).any(axis=1).mean()))
    return dict(n=len(ys), n_aligned=int(al.sum()), observed=float(al.mean()),
                expected=float(exp), ratio=float(al.mean() / exp),
                process_share=float(ap.mean()),
                ci=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                by_trad=by_trad,
                per_event={str(int(e)): dict(name=EVENTS[int(e)],
                                             k=int((np.abs(ys - e) <= tol).sum()))
                           for e in ev})


# ---------------------------------------------------------------- W8 命名
def w8(rows):
    by_trad = {}
    for t in TRAD_ORDER:
        c = Counter(r["name_type"] for r in rows if r["tradition"] == t)
        n = sum(c.values())
        by_trad[t] = {k: v / n for k, v in c.items()}
    cells = Counter()
    ss = by_source(rows)
    ks = [k for k in ss if ss[k]["tradition"] in TRAD_ORDER]
    for a, b in itertools.combinations(ks, 2):
        if ss[a]["tradition"] == ss[b]["tradition"]:
            continue
        for ra in ss[a]["all"]:
            for rb in ss[b]["all"]:
                cut = abs(ra["boundary_year"] - rb["boundary_year"]) <= 5
                same = ra["name_type"] == rb["name_type"]
                cells[("same_cut" if cut else "diff_cut",
                       "same_name" if same else "diff_name")] += 1
    tot = sum(cells.values())
    sc = cells[("same_cut", "same_name")] + cells[("same_cut", "diff_name")]
    return dict(by_trad=by_trad, total=tot,
                cells={"%s|%s" % k: v for k, v in cells.items()},
                same_cut=sc,
                same_name=cells[("same_cut", "same_name")],
                diff_name=cells[("same_cut", "diff_name")],
                diff_name_share=(cells[("same_cut", "diff_name")] / sc if sc else None))


# ---------------------------------------------------------------- 扩展语料
def extended():
    ext = [r for r in SCHEMES if r["series"] == "extended"]
    S = {s["source"]: s for s in sources() if s["series"] == "extended"}
    years = [r["boundary_year"] for r in ext if r["boundary_year"] is not None]
    core_years = set(r["boundary_year"] for r in SCHEMES
                     if r["series"] == "core" and r["boundary_year"] is not None)
    c = Counter(years)
    return dict(n_sources=len(S), n_rows=len(ext), n_dated=len(years),
                explicit=sum(1 for s in S.values() if s["explicit_year"]),
                calendars=dict(Counter(s["calendar"] for s in S.values())),
                regions=dict(Counter(s["tradition"] for s in S.values())),
                top=c.most_common(8),
                overlap=sorted(core_years & set(years)),
                sources={k: dict(tradition=v["tradition"], calendar=v["calendar"],
                                 explicit=v["explicit_year"],
                                 years=sorted({int(r["boundary_year"]) for r in ext
                                               if r["source"] == k
                                               and r["boundary_year"] is not None}))
                         for k, v in S.items()},
                rows=[dict(source=r["source"], year=r["boundary_year"],
                           name=r["period_name"], era=r["era"],
                           name_type=r["name_type"], note=r["note"],
                           tradition=r["tradition"], calendar=S[r["source"]]["calendar"],
                           explicit=S[r["source"]]["explicit_year"]) for r in ext])


# ---------------------------------------------------------------- 敏感性
def _build(include_chapter_as_part=False, include_nation=False,
           include_other=False, recode=False):
    rows = load(include_other=include_other, include_chapter=True)
    srcs = by_source(rows)
    if include_chapter_as_part:
        for d in srcs.values():
            d["part"] = list(d["all"])
            d["part_years"] = np.array(sorted({x["boundary_year"] for x in d["part"]}), int)
            ms = [x["boundary_year"] for x in d["part"]
                  if x["era"] in ("early_modern", "modern")]
            d["ms"] = min(ms) if ms else None
    if not include_nation:
        srcs = {k: v for k, v in srcs.items() if v["scope"] != "nation"}
    keys = [k for k in srcs if srcs[k]["tradition"] in TRAD_ORDER]
    years = np.arange(CORE_WIN[0], CORE_WIN[1] + 1)
    E = {}
    for k in keys:
        seq = []
        for y in years:
            e = era_at(srcs[k]["all"], y)
            if recode and srcs[k]["tradition"] == "china" and e == "contemporary" and y < 1945:
                e = "modern"
            seq.append(e)
        E[k] = seq
    D = np.zeros((len(keys), len(keys)))
    for i, j in itertools.combinations(range(len(keys)), 2):
        D[i, j] = D[j, i] = 1 - ari(E[keys[i]], E[keys[j]])
    return rows, srcs, keys, D


def _pair_ari(D, keys, srcs, a, b, mod=False):
    ix = [i for i in range(len(keys)) if srcs[keys[i]]["tradition"] == a]
    jx = [i for i in range(len(keys)) if srcs[keys[i]]["tradition"] == b]
    v = [D[i, j] for i in ix for j in jx]
    return float(1 - np.nanmean(v))


def sensitivity():
    variants = [
        ("基线", dict()),
        ("含章级", dict(include_chapter_as_part=True)),
        ("含国别", dict(include_nation=True)),
        ("含维基", dict(include_other=True)),
        ("中国现代→modern", dict(recode=True)),
    ]
    out = {}
    for label, kw in variants:
        rows, srcs, keys, D = _build(**kw)
        W = w2(srcs)
        out[label] = dict(
            n_sources=len(srcs), n_rows=len(rows),
            pre={t: W[t]["pre"] for t in TRAD_ORDER},
            late={t: W[t]["late"] for t in TRAD_ORDER},
            y1500={t: W[t]["y1500"] for t in TRAD_ORDER},
            median_ms={t: W[t]["median_ms"] for t in TRAD_ORDER},
            pair={
                "european-china": _pair_ari(D, keys, srcs, "european", "china"),
                "global-china": _pair_ari(D, keys, srcs, "global", "china"),
                "european-global": _pair_ari(D, keys, srcs, "european", "global")},
        )
    # 现代段的 recode 敏感性单独算
    _, srcs2, keys2, _ = _build()
    years = np.arange(1500, 2001)
    D2 = np.zeros((len(keys2), len(keys2)))
    for rec in (False, True):
        E = {}
        for k in keys2:
            seq = []
            for y in years:
                e = era_at(srcs2[k]["all"], y)
                if rec and srcs2[k]["tradition"] == "china" and e == "contemporary" and y < 1945:
                    e = "modern"
                seq.append(e)
            E[k] = seq
        Dm = np.zeros((len(keys2), len(keys2)))
        for i, j in itertools.combinations(range(len(keys2)), 2):
            Dm[i, j] = Dm[j, i] = 1 - ari(E[keys2[i]], E[keys2[j]])
        out.setdefault("_modern", {})["recode" if rec else "base"] = {
            "european-china": _pair_ari(Dm, keys2, srcs2, "european", "china"),
            "global-china": _pair_ari(Dm, keys2, srcs2, "global", "china"),
            "european-global": _pair_ari(Dm, keys2, srcs2, "european", "global")}
    return out


def region_counts():
    out = {}
    for r in SCHEMES:
        out.setdefault(r["tradition"], {}).setdefault(r["region"], 0)
        out[r["tradition"]][r["region"]] += 1
    return out


def compute():
    rows = load()
    srcs = by_source(rows)
    srcs_w = {k: v for k, v in srcs.items() if v["scope"] != "nation"}
    keys = [k for k in srcs_w if srcs_w[k]["tradition"] in TRAD_ORDER]
    D = distance_matrix(keys, srcs_w)
    tpl = templates(keys)
    tr_map = {k: srcs[k]["tradition"] for k in srcs}
    out = dict(window=list(CORE_WIN), n_sources=len(srcs), n_rows=len(rows),
               n_rows_all=sum(1 for r in SCHEMES if r["series"] == "core"),
               W1=w1(rows), W1T=w1_template(tpl),
               W2=w2(srcs_w), W2T=w2_template(tpl, tr_map),
               W3=w3(keys, srcs_w, D), ID=identity(rows),
               W4=w4(srcs), W5=w5(srcs_w), GATES=gates(rows),
               W6=w6(srcs_w), W7=w7(rows), W8=w8(rows),
               EXT=extended(), SENS=sensitivity(), REGION=region_counts(),
               TEMPLATES={str(k): v for k, v in tpl.items()})
    # 体裁分层：只留 survey / curriculum
    glob_survey = {k: v for k, v in srcs_w.items()
                   if v["tradition"] == "global" and v["genre"] in ("survey", "curriculum")}
    glob_all = {k: v for k, v in srcs_w.items() if v["tradition"] == "global"}
    if glob_survey:
        gs = list(glob_survey.values())
        out["GENRE"] = dict(
            global_survey_n=len(gs),
            pre_survey=float(np.mean([any(1000 <= y <= 1225 for y in s["part_years"]) for s in gs])),
            late_survey=float(np.mean([any(1735 <= y <= 1765 for y in s["part_years"]) for s in gs])),
            y1500_survey=float(np.mean([any(1450 <= y <= 1550 for y in s["part_years"]) for s in gs])),
            within_survey=float(1 - np.mean([D[keys.index(a), keys.index(b)]
                                             for a, b in itertools.combinations(glob_survey, 2)
                                             if a in keys and b in keys])),
            within_all=float(1 - np.mean([D[keys.index(a), keys.index(b)]
                                          for a, b in itertools.combinations(glob_all, 2)
                                          if a in keys and b in keys])),
            ms_survey=float(np.median([s["ms"] for s in glob_survey.values()
                                       if s["ms"] is not None])))
    out["SOURCES"] = {s["source"]: dict(
        tradition=s["tradition"], scope=s["scope"], genre=s["genre"],
        series=s["series"], year_published=s["year_published"],
        calendar=s["calendar"], explicit=s["explicit_year"],
        part=sorted(set(map(int, (srcs[s["source"]]["part_years"]
                                  if s["source"] in srcs else [])))),
        all=sorted({int(x["boundary_year"]) for x in SCHEMES
                    if x["source"] == s["source"] and x["boundary_year"] is not None}),
        ms=(None if s["source"] not in srcs or srcs[s["source"]]["ms"] is None
            else int(srcs[s["source"]]["ms"])))
        for s in sources()}
    return out


# ---------------------------------------------------------------- BH
def bh(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out = {}
    prev = 1.0
    for i in range(m - 1, -1, -1):
        k, p = items[i]
        q = min(prev, p * m / (i + 1))
        out[k] = min(1.0, q)
        prev = q
    return out


if __name__ == "__main__":
    o = compute()
    with open(os.path.join(BASE, "data", "stats.json"), "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)
    print("sources", o["n_sources"], "rows", o["n_rows"])
    print("W1", o["W1"]["top10"], o["W1"]["p_top10"], "| template", o["W1T"]["top10"],
          o["W1T"]["n_templates"])
    print("W2", {t: (round(v["pre"], 2), round(v["late"], 2)) for t, v in o["W2"].items()
                 if isinstance(v, dict) and "pre" in v})
    print("W3 diff", round(o["W3"]["diff"], 3), "p", o["W3"]["p"],
          "R2", round(o["W3"]["r2_tradition"], 2),
          {k: round(v, 3) for k, v in o["W3"]["pair"].items()})
    print("ID r2", o["ID"]["r2"], "maxres", o["ID"]["max_resid"])
    print("W4", {k: (round(v["p"], 3), {s: round(m, 1) for s, m in v["means"].items()})
                  for k, v in o["W4"]["metrics"].items()})
    print("W5", {t: (round(v["p_has"], 2), round(v["w1500"], 2), v["exclusive"])
                 for t, v in o["W5"].items()})
    print("W6", {t: (round(v["rho"], 2), round(v["p"], 3)) for t, v in o["W6"].items()})
    print("W7", round(o["W7"]["observed"], 3), o["W7"]["ci"],
          {t: round(v["event"], 2) for t, v in o["W7"]["by_trad"].items()})
    print("W8", {t: {k: round(x, 2) for k, x in v.items()} for t, v in o["W8"]["by_trad"].items()},
          "diff_name", round(o["W8"]["diff_name_share"], 2))
    print("EXT", o["EXT"]["n_sources"], o["EXT"]["explicit"], o["EXT"]["calendars"],
          "overlap", o["EXT"]["overlap"])
    print("BH", bh({"W1": o["W1"]["p_top10"], "W2": o["W2"]["kruskal"]["p"],
                    "W3": o["W3"]["p"], "W4": min(v["p"] for v in o["W4"]["metrics"].values()),
                    "W5": o["W2"]["pre_fisher"]["p"], "W6": min(v["p"] for v in o["W6"].values()),
                    "W7": 1e-100}))

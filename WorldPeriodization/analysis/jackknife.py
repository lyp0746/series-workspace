# -*- coding: utf-8 -*-
"""W1 的稳健性：留一来源（leave-one-source-out）与留一传统。

问题：§3.1 的“边界年高度集中”会不会是某一部来源撑起来的？如果删掉任意一部，集中度是否仍然
显著高于零模型？

做法：
  * 对每个来源 k，删掉它的全部边界行，重算顶层前十份额（W1）与模板级前十份额（W1T）；
  * 零模型：按剩余来源的条数，在 [400,2000] 上均匀散布，2000 次模拟（与主分析同种子规则）；
  * 报告留一样本的 min／median／max 与“仍然 p<0.05 的比例”。

输出：analysis/results/jackknife.json
用法：python analysis/jackknife.py
"""
import json
import os
import sys
from collections import Counter

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "analysis"))
import stats as S  # noqa: E402

OUT = os.path.join(BASE, "analysis", "results", "jackknife.json")
SEED = 20261022


def top10_share(years):
    if not years:
        return float("nan")
    c = Counter(years)
    return sum(v for _, v in c.most_common(10)) / len(years)


def null_top10(sizes, n_sim=2000, seed=SEED):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_sim):
        draw = []
        for n in sizes:
            draw.extend(rng.integers(S.CORE_WIN[0], S.CORE_WIN[1] + 1, n))
        c = Counter(draw)
        vals.append(sum(v for _, v in c.most_common(10)) / max(len(draw), 1))
    return float(np.mean(vals)), float(np.percentile(vals, 95))


def main():
    rows = S.load()
    keys = sorted({r["source"] for r in rows})
    res = {"n_sources": len(keys), "loo": [], "by_tradition": []}

    base_years = [r["boundary_year"] for r in rows]
    base_tpl = S.templates()
    res["baseline"] = dict(n=len(base_years), top10=round(top10_share(base_years), 4),
                           n_templates=len(base_tpl))

    for k in keys:
        sub = [r for r in rows if r["source"] != k]
        if len(sub) < 20:
            continue
        years = [r["boundary_year"] for r in sub]
        sizes = [len(s["all"]) for s in S.by_source(sub).values()]
        mean, q95 = null_top10(sizes)
        obs = top10_share(years)
        # 模板级：删掉该来源后重算模板
        tpl = S.templates([x for x in keys if x != k])
        tyears = [y for c in tpl for y in c]
        tob = top10_share(tyears)
        res["loo"].append(dict(source=k, n=len(years), top10=round(obs, 4),
                               null_mean=round(mean, 4), null_q95=round(q95, 4),
                               p=round(float(null_top10(sizes, 200, SEED + hash(k) % 1000)[0] >= obs), 3),
                               top10_template=round(tob, 4), n_templates=len(tpl)))

    for tr in ("european", "global", "china"):
        sub = [r for r in rows if r["tradition"] != tr]
        years = [r["boundary_year"] for r in sub]
        sizes = [len(s["all"]) for s in S.by_source(sub).values()]
        mean, q95 = null_top10(sizes)
        res["by_tradition"].append(dict(dropped=tr, n=len(years),
                                        top10=round(top10_share(years), 4),
                                        null_mean=round(mean, 4), null_q95=round(q95, 4)))

    obs_all = [x["top10"] for x in res["loo"]]
    tobs = [x["top10_template"] for x in res["loo"]]
    res["summary"] = dict(
        loo_n=len(obs_all),
        top10_min=round(min(obs_all), 4), top10_median=round(float(np.median(obs_all)), 4),
        top10_max=round(max(obs_all), 4),
        template_min=round(min(tobs), 4), template_max=round(max(tobs), 4),
        all_above_q95=bool(all(x["top10"] > x["null_q95"] for x in res["loo"])),
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res["summary"], ensure_ascii=False, indent=1))
    print("基线:", res["baseline"])
    for t in res["by_tradition"]:
        print("  删", t["dropped"], "→ top10", t["top10"], "零模型均值", t["null_mean"])


if __name__ == "__main__":
    main()

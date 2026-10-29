# -*- coding: utf-8 -*-
"""W8：复编一致性（Cohen's κ，逐字段）。

比对 coder A（data/schemes.py）与 coder B（data/recode_b.py）在 9 部来源上的判定。
κ 逐字段计算：boundary_year（精确年）、era（5 类）、level（2 类）。
另报"整行完全一致"的比例，作为更严格的指标。
"""
import json
import os
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
from schemes import SCHEMES  # noqa: E402
from recode_b import RECODE  # noqa: E402


def kappa(pairs):
    """pairs = [(a, b)]；返回 κ、观测一致率、期望一致率、混淆表。"""
    n = len(pairs)
    a_vals = [a for a, _ in pairs]
    b_vals = [b for _, b in pairs]
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a_vals), Counter(b_vals)
    cats = set(ca) | set(cb)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    conf = {}
    for a, b in pairs:
        conf.setdefault(str(a), Counter())[str(b)] += 1
    return dict(n=n, po=po, pe=pe, kappa=k,
                conf={a: dict(c) for a, c in conf.items()})


def main():
    idx = {(r["source"], r["boundary_year"]): r for r in SCHEMES}
    pairs = []
    for b in RECODE:
        a = idx.get((b["source"], b["boundary_year"]))
        if a is None:
            raise SystemExit("复编行无法对齐：%s %s" % (b["source"], b["boundary_year"]))
        pairs.append((a, b))

    out = {}
    out["year"] = kappa([(a["boundary_year"], b["year_b"]) for a, b in pairs])
    out["era"] = kappa([(a["era"], b["era_b"]) for a, b in pairs])
    out["level"] = kappa([(a["level"], b["level_b"]) for a, b in pairs])
    out["row"] = kappa([((a["boundary_year"], a["era"], a["level"]),
                         (b["year_b"], b["era_b"], b["level_b"])) for a, b in pairs])
    out["n_sources"] = len({b["source"] for b in RECODE})
    out["n_items"] = len(pairs)
    out["n_sources_total"] = len({r["source"] for r in SCHEMES})
    out["disagreements"] = [
        dict(source=a["source"], year=a["boundary_year"], period=a["period_name"],
             a_era=a["era"], b_era=b["era_b"], a_level=a["level"], b_level=b["level_b"],
             a_year=a["boundary_year"], b_year=b["year_b"])
        for a, b in pairs
        if (a["boundary_year"], a["era"], a["level"]) != (b["year_b"], b["era_b"], b["level_b"])]
    # 与 W8 阈值比较
    out["pass"] = {f: bool(out[f]["kappa"] >= 0.7) for f in ("year", "era", "level")}
    out["min_kappa"] = min(out[f]["kappa"] for f in ("year", "era", "level"))

    p = os.path.join(BASE, "data", "kappa.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for f in ("year", "era", "level", "row"):
        print("%-6s n=%d po=%.3f pe=%.3f kappa=%.3f" %
              (f, out[f]["n"], out[f]["po"], out[f]["pe"], out[f]["kappa"]))
    print("min kappa %.3f  pass %s" % (out["min_kappa"], out["pass"]))
    print("disagreements:", len(out["disagreements"]))
    for d in out["disagreements"]:
        print("  ", d["source"], d["year"], d["period"], "| era", d["a_era"], "->", d["b_era"],
              "| level", d["a_level"], "->", d["b_level"])
    print("wrote", p)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""合并唐宋 67 类与明清 42 类，加入 rank/border，检验“外派→变化”是否只是
“高阶＋边疆”的代理（A），以及“路径→形态、不→概率”是否跨朝代成立（B）。

输出：data/control_all.csv、data/all_results.json
"""
import csv
import json
import os

import numpy as np
from scipy import optimize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

BORDER = {  # 常设于边疆/前线 = 1
    "都督": 1, "节度使": 1, "团练使": 1, "防御使": 1, "留后": 1, "监军": 1,
    "都统": 1, "招讨使": 1, "安抚使": 1, "制置使": 1, "宣抚使": 1, "都统制": 1,
    "镇守中官": 1, "巡抚": 1, "总督": 1, "巡按御史": 1, "巡按": 1,
    "都指挥使": 1, "总兵": 1, "驻防将军": 1, "八旗": 1, "绿营": 1, "提督": 1,
    "督抚": 1,
}
RANK = {"高": 2, "中": 1, "低": 0}


def load(p):
    return list(csv.DictReader(open(os.path.join(DATA, p), encoding="utf-8-sig")))


def logistic(X, y):
    X = np.asarray(X, float); y = np.asarray(y, float)
    def nll(b):
        z = X @ b
        return np.sum(np.logaddexp(0, z) - y * z)
    res = optimize.minimize(nll, np.zeros(X.shape[1]), method="BFGS")
    b = res.x
    p = 1 / (1 + np.exp(-X @ b))
    W = np.diag(p * (1 - p))
    cov = np.linalg.pinv(X.T @ W @ X)
    se = np.sqrt(np.diag(cov))
    return b, se


def main():
    rows = []
    for r in load("control_tangsong.csv"):
        rows.append(dict(id=r["id"], dyn=r["dynasty"], office=r["office"], line=r["line"],
                         rank=r["rank"], border=BORDER.get(r["office"], 0),
                         start=int(r["start"]), end=int(r["end"]),
                         event=int(r["event"]), event_type=r["event_type"]))
    for r in load("control_extended.csv"):
        rows.append(dict(id=r["id"], dyn=r["dyn"], office=r["office"], line=r["line"],
                         rank=r["rank"], border=int(r["border"]),
                         start=int(r["start"]), end=int(r["end"]),
                         event=int(r["event"]), event_type=r["event_type"]))
    with open(os.path.join(DATA, "control_all.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    y = np.array([r["event"] for r in rows])
    X = np.column_stack([
        np.ones(len(rows)),
        [1 if r["line"] == "outer" else 0 for r in rows],
        [1 if r["line"] == "military" else 0 for r in rows],
        [1 if r["line"] == "regular" else 0 for r in rows],
        [RANK[r["rank"]] for r in rows],
        [r["border"] for r in rows],
        [1 if r["dyn"] == "宋" else 0 for r in rows],
        [1 if r["dyn"] == "明" else 0 for r in rows],
        [1 if r["dyn"] == "清" else 0 for r in rows],
    ])
    names = ["intercept", "outer", "military", "regular", "rank", "border", "song", "ming", "qing"]
    b, se = logistic(X, y)
    OR = np.exp(b); lo = np.exp(b - 1.96 * se); hi = np.exp(b + 1.96 * se)

    # secession by line
    sec = [r for r in rows if r["event_type"] == "割据"]
    out = {"n": len(rows), "events": int(y.sum()),
           "secession": {"n": len(sec),
                         "outer": sum(1 for r in sec if r["line"] == "outer"),
                         "inner": sum(1 for r in sec if r["line"] == "inner")},
           "logit": {"names": names, "OR": [float(x) for x in OR],
                     "lo": [float(x) for x in lo], "hi": [float(x) for x in hi]}}
    json.dump(out, open(os.path.join(DATA, "all_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

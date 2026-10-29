# -*- coding: utf-8 -*-
"""扩展对照样本（唐/宋/明/清）＋ 品级、边疆协变量。

A：加入 rank（高/中/低）与 border（是否常设于边疆/前线），检验“外派→割据”
   是否只是“高阶＋边疆”的代理。
B：加入明（20 类）、清（22 类），检验“路径决定形态、不决定概率”是否跨朝代成立。

输出：data/control_extended.csv、data/extended_results.json
"""
import csv
import json
import os
from collections import Counter

import numpy as np
from scipy import stats, optimize


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)

# id, dyn, office, line, rank, border, start, end, event_year(None=无), type
MING_QING = [
    ("M01", "明", "内阁", "inner", "高", 0, 1402, 1644, None, ""),
    ("M02", "明", "司礼监", "inner", "中", 0, 1425, 1644, 1627, "禁戒"),
    ("M03", "明", "翰林院", "inner", "中", 0, 1368, 1644, None, ""),
    ("M04", "明", "六科给事中", "inner", "中", 0, 1368, 1644, None, ""),
    ("M05", "明", "厂卫", "inner", "中", 0, 1382, 1644, None, ""),
    ("M06", "明", "镇守中官", "outer", "中", 1, 1420, 1644, 1450, "禁戒"),
    ("M07", "明", "巡抚", "outer", "高", 1, 1430, 1644, 1500, "正官化"),
    ("M08", "明", "总督", "outer", "高", 1, 1450, 1644, 1460, "正官化"),
    ("M09", "明", "巡按御史", "outer", "中", 1, 1371, 1644, None, ""),
    ("M10", "明", "布政使", "outer", "中", 0, 1376, 1644, None, ""),
    ("M11", "明", "按察使", "outer", "中", 0, 1376, 1644, None, ""),
    ("M12", "明", "都指挥使", "outer", "高", 1, 1370, 1644, 1450, "虚化"),
    ("M13", "明", "五军都督府", "military", "高", 0, 1380, 1644, 1449, "虚化"),
    ("M14", "明", "京营", "military", "高", 0, 1400, 1644, 1500, "虚化"),
    ("M15", "明", "总兵", "military", "高", 1, 1400, 1644, None, ""),
    ("M16", "明", "六部", "regular", "高", 0, 1380, 1644, None, ""),
    ("M17", "明", "都察院", "regular", "高", 0, 1382, 1644, None, ""),
    ("M18", "明", "大理寺", "regular", "中", 0, 1368, 1644, None, ""),
    ("M19", "明", "国子监", "regular", "中", 0, 1368, 1644, None, ""),
    ("M20", "明", "三公", "regular", "高", 0, 1368, 1644, None, ""),
    ("Q01", "清", "军机处", "inner", "高", 0, 1732, 1911, None, ""),
    ("Q02", "清", "南书房", "inner", "中", 0, 1677, 1911, 1723, "虚化"),
    ("Q03", "清", "内阁", "inner", "高", 0, 1644, 1911, 1732, "虚化"),
    ("Q04", "清", "内务府", "inner", "中", 0, 1661, 1911, None, ""),
    ("Q05", "清", "督抚", "outer", "高", 1, 1644, 1911, 1900, "割据"),
    ("Q06", "清", "布政使", "outer", "中", 0, 1644, 1911, None, ""),
    ("Q07", "清", "按察使", "outer", "中", 0, 1644, 1911, None, ""),
    ("Q08", "清", "道员", "outer", "中", 0, 1644, 1911, None, ""),
    ("Q09", "清", "知府", "outer", "中", 0, 1644, 1911, None, ""),
    ("Q10", "清", "知县", "outer", "低", 0, 1644, 1911, None, ""),
    ("Q11", "清", "驻防将军", "outer", "高", 1, 1644, 1911, None, ""),
    ("Q12", "清", "八旗", "military", "高", 1, 1644, 1911, 1800, "虚化"),
    ("Q13", "清", "绿营", "military", "高", 1, 1644, 1911, 1800, "虚化"),
    ("Q14", "清", "提督", "military", "高", 1, 1644, 1911, None, ""),
    ("Q15", "清", "总兵", "military", "高", 1, 1644, 1911, None, ""),
    ("Q16", "清", "六部", "regular", "高", 0, 1644, 1911, None, ""),
    ("Q17", "清", "理藩院", "regular", "高", 0, 1636, 1911, None, ""),
    ("Q18", "清", "都察院", "regular", "高", 0, 1644, 1911, None, ""),
    ("Q19", "清", "总理衙门", "inner", "中", 0, 1861, 1911, 1901, "正官化"),
    ("Q20", "清", "责任内阁", "regular", "高", 0, 1911, 1911, 1911, "虚化"),
    ("Q21", "清", "巡按", "outer", "中", 1, 1644, 1911, 1660, "禁戒"),
    ("Q22", "清", "盐运使", "outer", "中", 0, 1644, 1911, None, ""),
]

RANK = {"高": 2, "中": 1, "低": 0}
LINE = {"inner": 0, "outer": 1, "military": 2, "regular": 3}


def rows():
    out = []
    for (i, dyn, office, line, rank, border, start, end, ey, et) in MING_QING:
        out.append(dict(id=i, dyn=dyn, office=office, line=line, rank=rank, border=border,
                        start=start, end=end, event=0 if ey is None else 1,
                        event_year=ey, event_type=et,
                        exposure=(ey if ey else end) - start))
    return out


def logistic(X, y, maxiter=200):
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
    R = rows()
    with open(os.path.join(DATA, "control_extended.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0])); w.writeheader(); w.writerows(R)

    y = np.array([r["event"] for r in R])
    X = np.column_stack([np.ones(len(R)),
                         [1 if r["line"] == "outer" else 0 for r in R],
                         [1 if r["line"] == "military" else 0 for r in R],
                         [1 if r["line"] == "regular" else 0 for r in R],
                         [RANK[r["rank"]] for r in R],
                         [r["border"] for r in R],
                         [1 if r["dyn"] == "清" else 0 for r in R]])
    b, se = logistic(X, y)
    OR = np.exp(b); lo = np.exp(b - 1.96 * se); hi = np.exp(b + 1.96 * se)

    # secession-only model (few events): descriptive
    sec = [r for r in R if r["event_type"] == "割据"]
    sec_out = [r for r in R if r["event_type"] == "割据" and r["line"] == "outer"]
    sec_in = [r for r in R if r["event_type"] == "割据" and r["line"] != "outer"]

    by_line = Counter(r["line"] for r in R)
    ev_line = Counter(r["line"] for r in R if r["event"])
    by_dyn = Counter(r["dyn"] for r in R)
    ev_dyn = Counter(r["dyn"] for r in R if r["event"])

    out = {"n": len(R), "events": int(y.sum()),
           "by_line": dict(by_line), "events_by_line": dict(ev_line),
           "by_dyn": dict(by_dyn), "events_by_dyn": dict(ev_dyn),
           "logit": {"names": ["intercept", "outer", "military", "regular", "rank", "border", "qing"],
                     "OR": [float(x) for x in OR], "lo": [float(x) for x in lo], "hi": [float(x) for x in hi]},
           "secession": {"n": len(sec), "outer": len(sec_out), "non_outer": len(sec_in)}}
    json.dump(out, open(os.path.join(DATA, "extended_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

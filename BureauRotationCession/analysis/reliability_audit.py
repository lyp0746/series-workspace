# -*- coding: utf-8 -*-
"""边界案例的盲复测（同一编码者）：检验“保/让”规则在 15 个歧义案例上的稳定性。

这不是独立的第二编码者，而是把存储标签遮住、按 codebook 重编一遍，
用一致率与 Cohen's κ 检查“规则本身是否足够清楚”。结果写入：
data/reliability_audit.csv、data/reliability_results.json
"""
import csv
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)

# id, 官职, 存储的保, 存储的让, 盲复测的保, 盲复测的让, 问题
ROWS = [
    ("I4", "侍中", "初C、T后A、T", "初A后C", "C、T（起家）", "A", "前后期转移：起家可判，转移点无规则"),
    ("I6", "同平章事", "C＋A（原官品）", "名分", "C、A", "T", "让出项是“名分”还是 T，规则未定义"),
    ("I9", "神策中尉", "C、T＋兵权", "A", "C、A、T（融合）", "—", "兵权是否算 A：算则三项全占，与“让 A”矛盾"),
    ("I11", "内阁大学士", "C、T", "A", "C、T", "A", "一致"),
    ("I14", "军机处", "C、T", "A", "C、T", "A", "一致"),
    ("O9", "监军", "C、T", "A", "C、T", "A", "一致"),
    ("O10", "通判", "初C、T后A", "初A后C", "C、T（起家）", "A", "前后期转移：同上"),
    ("O12", "巡抚", "C、A", "T", "C、A", "T", "一致"),
    ("O15", "典签", "C、T", "A", "C、T", "A", "一致"),
    ("M3", "中领军·中护军", "C、A", "T（对皇帝）", "C、A", "T（对皇帝）", "一致"),
    ("P66", "参知政事", "C、T", "A", "C、T", "A", "一致"),
    ("P73", "权相（平章军国事）", "C、T＋兵权", "A", "C、A、T（融合）", "—", "同神策：兵权归类歧义"),
    ("P90", "厂卫", "C、T", "A", "C、T", "A", "一致"),
    ("P103", "侍从室", "C、T", "A", "C、T", "A", "一致"),
    ("P120", "专班·攻坚指挥部", "C、T", "A", "C、T", "A", "一致"),
]

def norm(s):
    s = s.replace("初", "").replace("后", "")
    for ch in ["C", "A", "T", "＋", "、", " ", "（", "）", "(", ")", "对皇帝", "原官品", "起家"]:
        s = s.replace(ch, "")
    s = s.replace("，", "")
    # 归到三类：含 A/T/C 的组合 → 用“让出项”做分类
    return s

def main():
    with open(os.path.join(DATA, "reliability_audit.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "官职", "存储_保", "存储_让", "复测_保", "复测_让", "一致", "问题"])
        agree = 0
        for r in ROWS:
            a = 1 if (norm(r[2]) == norm(r[4]) or "融合" in r[4]) else 0
            # 融合案例按“不同”计（与存储的“让 A”不同）
            if "融合" in r[4]:
                a = 0
            agree += a
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], "是" if a else "否", r[6]])

    # Cohen's kappa on 3 categories of the conceded item: A / T / other
    def cat(s):
        if "融合" in s or "—" == s:
            return "fusion"
        if "A" in s:
            return "A"
        if "T" in s:
            return "T"
        return "other"

    stored = [cat(r[3]) for r in ROWS]
    recode = [cat(r[5]) for r in ROWS]
    n = len(ROWS)
    po = sum(1 for a, b in zip(stored, recode) if a == b) / n
    ca, cb = Counter(stored), Counter(recode)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 0.0

    out = {"n": n, "agreement": agree / n, "po": po, "kappa": kappa,
           "stored": dict(ca), "recode": dict(cb),
           "issues": [r[6] for r in ROWS if r[6] != "一致"]}
    json.dump(out, open(os.path.join(DATA, "reliability_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

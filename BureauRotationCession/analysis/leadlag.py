# -*- coding: utf-8 -*-
"""领先—滞后：融合线出现距断裂事件多少年？

对 28 起事件编码“事件前 30 年内是否已有融合线”，并区分事件类型。
关键区分：禅代（改朝换代）几乎都以融合线为前提；清洗、政变、割据则未必。
输出 data/event_leadlag.csv、data/leadlag.json
"""
import csv
import json
import os
from collections import Counter, defaultdict

from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)

# year, type, label, fusion_onset (None if no prior fusion line within 30y), note
EV = [
    (9, "禅代", "王莽代汉", -1, "安汉公—宰衡，已兼政务与名义"),
    (189, "废立", "董卓废少帝", None, "并州牧带兵入京，事先无诏令通道"),
    (189, "清洗", "袁绍诛宦官", None, "司隶校尉，无独立体系"),
    (196, "挟持", "曹操迎献帝", None, "兖州牧，尚未录尚书"),
    (220, "禅代", "曹丕代汉", 208, "曹操丞相—魏王，军政合一"),
    (249, "政变", "高平陵之变", None, "太傅，无兵权；靠禁军倒戈"),
    (254, "废立", "司马师废曹芳", 249, "录尚书事＋大将军"),
    (265, "禅代", "司马炎代魏", 249, "司马氏自高平陵起掌内外"),
    (291, "内战", "八王之乱", None, "诸王各拥兵，无单一融合线"),
    (371, "废立", "桓温废海西公", 369, "大司马＋扬州牧"),
    (420, "禅代", "刘裕代晋", 415, "相国—宋公，军政合一"),
    (479, "禅代", "萧道成代宋", 477, "领军＋录尚书事"),
    (502, "禅代", "萧衍代齐", 501, "大司马—梁公"),
    (528, "清洗", "河阴之变", None, "尔朱荣以兵入洛，无诏令体系"),
    (550, "禅代", "高洋代东魏", 549, "丞相—齐王"),
    (557, "禅代", "宇文觉代西魏", 556, "太师—周公"),
    (557, "禅代", "陈霸先代梁", 555, "丞相—陈王"),
    (581, "禅代", "杨坚代周", 580, "大丞相"),
    (618, "禅代", "李渊代隋", 617, "大丞相—唐王"),
    (755, "割据", "安史之乱", None, "三镇节度，无诏令"),
    (763, "割据", "河朔三镇", None, "节度使世袭，无中央通道"),
    (835, "清洗", "甘露之变", None, "李训、郑注以近臣谋诛宦官，未成"),
    (903, "清洗", "朱温诛宦官", 901, "梁王＋诸道兵马元帅"),
    (907, "禅代", "朱温代唐", 903, "诛宦官后控制昭宗"),
    (960, "禅代", "赵匡胤代周", 959, "殿前都点检＋归德军节度"),
    (1399, "内战", "靖难之役", None, "燕王拥兵，无中央诏令"),
    (1457, "政变", "夺门之变", None, "石亨等以禁军发动"),
    (1861, "政变", "辛酉政变", None, "内廷与恭亲王临时结盟"),
]


def main():
    rows = []
    for y, t, lab, onset, note in EV:
        lead = (y - onset) if onset is not None else None
        rows.append({"year": y, "type": t, "label": lab, "fusion_onset": onset,
                     "lead_years": lead, "prior_fusion": 1 if onset is not None else 0, "note": note})
    with open(os.path.join(DATA, "event_leadlag.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    by = defaultdict(lambda: [0, 0])
    for r in rows:
        by[r["type"]][0] += r["prior_fusion"]; by[r["type"]][1] += 1
    leads = [r["lead_years"] for r in rows if r["lead_years"] is not None]
    us = [r["lead_years"] for r in rows if r["type"] == "禅代"]

    a = by["禅代"][0]; b = by["禅代"][1] - a
    c = sum(v[0] for k, v in by.items() if k != "禅代")
    d = sum(v[1] - v[0] for k, v in by.items() if k != "禅代")
    fisher = stats.fisher_exact([[a, b], [c, d]])

    out = {"n": len(rows), "by_type": {k: {"prior_fusion": v[0], "n": v[1]} for k, v in by.items()},
           "lead_median": float(sorted(leads)[len(leads) // 2]) if leads else None,
           "lead_min": min(leads) if leads else None, "lead_max": max(leads) if leads else None,
           "usurp_prior": [a, by["禅代"][1]], "other_prior": [c, c + d],
           "fisher": {"table": [[a, b], [c, d]], "p": float(fisher.pvalue)},
           "usurp_leads": us}
    json.dump(out, open(os.path.join(DATA, "leadlag.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

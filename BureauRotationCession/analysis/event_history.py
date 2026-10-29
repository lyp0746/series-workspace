# -*- coding: utf-8 -*-
"""断裂事件史：禅代、废立、割据、清洗、政变（公元前 9 年—1861）。

用途：把“崩解”从 2 个王朝灭亡事件扩成 28 个宪制断裂事件，按 24 期计发生率，
比较“有融合线的时期”与“无融合线的时期”。注意：融合线与事件同期编码，
关联是描述性的，不是预测；真正的检验需要“融合在前、事件在后”的领先—滞后设计。

输出：data/rupture_events.csv、data/event_history.json
"""
import csv
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data"); os.makedirs(DATA, exist_ok=True)

PERIODS = [  # name, start, end, fusion
    ("西周—春秋战国", -1046, -222, 0), ("秦—西汉", -221, 25, 1), ("东汉", 25, 220, 1),
    ("三国", 220, 280, 0), ("两晋", 265, 420, 1), ("十六国", 304, 439, 1),
    ("南朝", 420, 589, 1), ("北朝", 386, 581, 0), ("隋", 581, 618, 0),
    ("唐前期", 618, 755, 0), ("中晚唐", 755, 907, 1), ("五代十国", 907, 960, 1),
    ("辽", 916, 1125, 0), ("宋", 960, 1279, 0), ("西夏", 1038, 1227, 1),
    ("金", 1115, 1234, 0), ("元", 1271, 1368, 0), ("明", 1368, 1644, 0),
    ("清前期", 1644, 1840, 0), ("晚清", 1840, 1911, 1),
]

EVENTS = [
    (9, "禅代", "王莽代汉"), (189, "废立", "董卓废少帝"), (189, "清洗", "袁绍诛宦官"),
    (196, "挟持", "曹操迎献帝"), (220, "禅代", "曹丕代汉"), (249, "政变", "高平陵之变"),
    (254, "废立", "司马师废曹芳"), (265, "禅代", "司马炎代魏"), (291, "内战", "八王之乱"),
    (371, "废立", "桓温废海西公"), (420, "禅代", "刘裕代晋"), (479, "禅代", "萧道成代宋"),
    (502, "禅代", "萧衍代齐"), (528, "清洗", "河阴之变"), (550, "禅代", "高洋代东魏"),
    (557, "禅代", "宇文觉代西魏"), (557, "禅代", "陈霸先代梁"), (581, "禅代", "杨坚代周"),
    (618, "禅代", "李渊代隋"), (755, "割据", "安史之乱"), (763, "割据", "河朔三镇"),
    (835, "清洗", "甘露之变"), (903, "清洗", "朱温诛宦官"), (907, "禅代", "朱温代唐"),
    (960, "禅代", "赵匡胤代周"), (1399, "内战", "靖难之役"), (1457, "政变", "夺门之变"),
    (1861, "政变", "辛酉政变"),
]


def period_of(year):
    for name, a, b, f in PERIODS:
        if a <= year <= b:
            return name, f
    return None, None


def main():
    rows = []
    for y, t, lab in EVENTS:
        p, f = period_of(y)
        rows.append({"year": y, "type": t, "label": lab, "period": p, "fusion": f})
    with open(os.path.join(DATA, "rupture_events.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    # period panel
    panel = []
    for name, a, b, f in PERIODS:
        ev = [r for r in rows if r["period"] == name]
        panel.append({"period": name, "years": b - a + 1, "events": len(ev),
                      "types": dict((t, sum(1 for r in ev if r["type"] == t)) for t in set(r["type"] for r in ev)),
                      "fusion": f})
    # rates
    def rate(fval):
        ex = sum(p["years"] for p in panel if p["fusion"] == fval)
        ev = sum(p["events"] for p in panel if p["fusion"] == fval)
        return ev, ex, ev / ex * 100
    f_ev, f_ex, f_rate = rate(1); n_ev, n_ex, n_rate = rate(0)
    # Fisher on periods with >=1 event vs fusion
    a1 = sum(1 for p in panel if p["fusion"] and p["events"] > 0)
    b1 = sum(1 for p in panel if p["fusion"] and p["events"] == 0)
    c1 = sum(1 for p in panel if not p["fusion"] and p["events"] > 0)
    d1 = sum(1 for p in panel if not p["fusion"] and p["events"] == 0)
    from scipy import stats
    fisher = stats.fisher_exact([[a1, b1], [c1, d1]])

    out = {"n_events": len(rows), "by_type": dict((t, sum(1 for r in rows if r["type"] == t))
                                                   for t in set(r["type"] for r in rows)),
           "panel": panel,
           "fusion": {"events": f_ev, "years": f_ex, "rate_per_100y": f_rate},
           "nonfusion": {"events": n_ev, "years": n_ex, "rate_per_100y": n_rate},
           "irr": f_rate / n_rate if n_rate else None,
           "fisher": {"table": [[a1, b1], [c1, d1]], "p": float(fisher.pvalue)}}
    json.dump(out, open(os.path.join(DATA, "event_history.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

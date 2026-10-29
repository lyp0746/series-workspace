# -*- coding: utf-8 -*-
"""锚点的压力测试：情景记忆的模拟对照实验。

**这不是 LLM 实验，是机制模拟。** 环境、日志、重建者、裁判全部由代码定义，参数显式；
它检验「架构的内部逻辑是否成立」，不检验「某个模型的表现」。

环境
----
五个页面，每个页面有一个「正确动作」和一个**表面标签**（返回／互动）。表面标签相同、
语义不同：只有信息流页的「返回」是「退回上一条」，其余页面的「返回」是「退回上一级／关闭弹窗／退出直播」。
> **这是负迁移的唯一来源**（与《同构的强度》M12 的例外清单同构）。

三个条件
--------
M0 无记忆： 只看表面标签，按默认映射选动作。
M1 摘要记忆：记住「最近一次的标签→动作」，跨页面照搬（摘要丢掉了 app/screen 两个字段）。
M2 情景唤起：书记员字段日志 + 五类线索检索 + K 路重建 + 带锚裁决（A 放行 / B 放行 / C 且高风险转人环）。

四个指标
--------
neg_transfer 负迁移率：执行「返回」但本页的返回语义不是「上一条」
mis_action   误动作率：不可逆动作做错（公开发言／回复／互动到错的对象）
latency_ms   端到端延迟（成本模型，见 COST）
escalations  每 100 步的人环接管次数

参数
----
p      单个重建者在「对象」上出错的概率
rho    共源程度：全体共享同一次错误抽样的概率
K      重建路数（M2 专用，按风险分级：高风险 K 路、低风险 K−2 路）
cover  锚点覆盖率：有字段日志的页面比例（决定 M2 的天花板）
"""

import csv
import itertools
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

# (app, screen, 正确动作, 表面标签, 是否不可逆)
PAGES = [
    ("douyin", "feed",     "fav_item", "返回", False),
    ("qq",     "chat",     "reply",    "返回", True),
    ("qq",     "settings", "toggle",   "返回", False),
    ("douyin", "popup",    "close",    "返回", False),
    ("douyin", "live",     "comment",  "互动", True),
]
KEYS = [p[0] + "/" + p[1] for p in PAGES]
TRUTH = {p[0] + "/" + p[1]: p[2] for p in PAGES}
SURFACE = {p[0] + "/" + p[1]: p[3] for p in PAGES}
RISK = {p[0] + "/" + p[1]: p[4] for p in PAGES}
# 表面标签的默认动作：**取信息流页的语义**（这就是「跨页面照搬」的原型）
DEFAULT = {"返回": "back_to_prev_item", "互动": "fav_item"}
BACK_LIKE = {"back_to_prev_item"}

COST = dict(base=40, fallback=60, reconstructor=300, judge=200, escalate=5000)


def pick_alt(truth, rng):
    """一个「像但不对」的动作。"""
    pool = ["back_to_prev_item", "fav_item", "reply", "toggle", "close", "comment"]
    pool = [a for a in pool if a != truth]
    return rng.choice(pool)


def claim(page, widget_known, p_err, shared_wrong, rng, bad=None):
    """一个重建者的复述：(动作, 是否对象级出错)。bad 非空表示账本已被污染。"""
    truth = bad if bad else TRUTH[page]
    if widget_known:
        if rng.random() < p_err * 0.2:          # 动作本身记错（低频）
            return pick_alt(truth, rng), True
        return truth, False
    if shared_wrong:                             # 共源：全体一起错
        return pick_alt(truth, rng), True
    if rng.random() < p_err:
        return pick_alt(truth, rng), True
    return truth, False


def judge(claims, page, widget_known, bad=None):
    """带锚裁决。返回 (等级 A/B/C, 采信动作, 是否全票)。bad 非空＝账本已被污染。"""
    acts = [c[0] for c in claims]
    top = max(set(acts), key=acts.count)
    unanimous = len(set(acts)) == 1
    if widget_known and unanimous and top == (bad or TRUTH[page]):
        return "A", top, True
    if unanimous:
        return "B", top, True            # 一致但无对象锚点，或一致地错（最危险的一种）
    if acts.count(top) > len(acts) // 2:
        return "B", top, False
    return "C", top, False


def run(cond, seeds=20, decisions=200, p_err=0.25, rho=0.5, K=3, cover=0.5):
    rows = []
    for s in range(seeds):
        rng = random.Random(1000 + s)
        log_ok = {k: rng.random() < cover for k in KEYS}      # 每个页面有没有日志（固定抽样）
        corrupted = {}                                         # M2w：被污染的对象字段
        widget_ok = {k: (log_ok[k] and rng.random() < 0.75) for k in KEYS}  # 对象字段是否完整
        last = {}                                              # M1：标签 → 最近动作（丢掉 app/screen）
        for t in range(decisions):
            page = rng.choice(KEYS)
            truth = TRUTH[page]
            spec = SURFACE[page]
            lat = COST["base"]
            esc = 0
            level = "-"
            unanimous = False

            if cond == "M0":
                act = DEFAULT[spec]
                lat += 30
            elif cond == "M1":
                # 摘要：标签→动作，跨页面照搬；若本页标签刚记过则用记忆，否则用默认
                act = last.get(spec, DEFAULT[spec])
                lat += 80
                last[spec] = truth if rng.random() < 0.85 else pick_alt(truth, rng)  # 摘要漂移
            else:  # M2 / M2w
                if not log_ok[page]:
                    act = DEFAULT[spec]
                    lat += COST["fallback"]
                else:
                    k = K if RISK[page] else max(1, K - 2)
                    shared_wrong = rng.random() < rho
                    bad = corrupted.get(page) if cond == "M2w" else None
                    claims = [claim(page, widget_ok[page], p_err, shared_wrong, rng, bad) for _ in range(k)]
                    level, act, unanimous = judge(claims, page, widget_ok[page], bad)
                    lat += k * COST["reconstructor"] + COST["judge"]
                    if level == "C" and RISK[page]:
                        esc = 1
                        lat += COST["escalate"]
                        act = truth
                    if cond == "M2w" and level in ("B", "C") and act != truth:
                        # 允许回写：错误的重建被当成账本，此后该页视为「有对象锚点」
                        widget_ok[page] = True
                        corrupted[page] = act
            neg = int(act in BACK_LIKE and page != "douyin/feed")
            mis = int(RISK[page] and act != truth)
            # 跨页面语义污染：执行了「别的页面的正确动作」
            conf = int(any(act == TRUTH[k] and k != page for k in KEYS))
            rows.append(dict(seed=s, t=t, bucket=t // 50, cond=cond, page=page, truth=truth, act=act, level=level,
                             unanimous=int(unanimous), neg=neg, mis=mis, conf=conf, lat=lat, esc=esc,
                             m2branch=int(cond == "M2" and log_ok[page]),
                             p=p_err, rho=rho, K=K, cover=cover))
    return rows


def summarize(rows):
    n = len(rows)
    branch = [r for r in rows if r["m2branch"]]
    low = [r for r in rows if not RISK[r["page"]]]
    high = [r for r in rows if RISK[r["page"]]]
    return dict(n=n,
                acc=sum(1 for r in rows if r["act"] == r["truth"]) / n,
                neg=sum(r["neg"] for r in rows) / n,
                mis=sum(r["mis"] for r in rows) / n,
                conf=sum(r["conf"] for r in rows) / n,
                lat=sum(r["lat"] for r in rows) / n,
                lat_low=sum(r["lat"] for r in low) / max(1, len(low)),
                lat_high=sum(r["lat"] for r in high) / max(1, len(high)),
                esc=100 * sum(r["esc"] for r in rows) / n,
                unan_wrong=(sum(1 for r in branch if r["unanimous"] and r["act"] != r["truth"]) / len(branch))
                           if branch else 0.0,
                branch=len(branch))


def main():
    allrows, summ = [], []
    for cond in ("M0", "M1", "M2", "M2w"):
        rows = run(cond)
        allrows += rows
        s = summarize(rows); s["cond"] = cond
        summ.append(s)
        print("%-3s acc=%.3f conf=%.3f mis=%.3f lat=%4.0f/%4.0fms esc=%5.2f/100 unanW=%.3f"
              % (cond, s["acc"], s["conf"], s["mis"], s["lat_low"], s["lat_high"], s["esc"], s["unan_wrong"]))

    sens = []
    for p_err, rho, K, cover in itertools.product([0.15, 0.25, 0.35], [0.0, 0.3, 0.7], [1, 3, 5], [0.2, 0.5, 0.9]):
        rows = run("M2", seeds=10, decisions=200, p_err=p_err, rho=rho, K=K, cover=cover)
        s = summarize(rows); s.update(p=p_err, rho=rho, K=K, cover=cover)
        sens.append(s)

    with open(OUT / "steps.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
    with open(OUT / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cond", "n", "acc", "neg", "mis", "conf", "lat", "lat_low", "lat_high", "esc", "unan_wrong", "branch"])
        w.writeheader(); w.writerows(summ)
    with open(OUT / "sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["p", "rho", "K", "cover", "n", "acc", "neg", "mis", "conf", "lat", "lat_low", "lat_high", "esc", "unan_wrong", "branch"])
        w.writeheader(); w.writerows(sens)
    # 覆盖率细扫（定位交叉点）
    cov = []
    for c in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
        rows = run("M2", seeds=20, decisions=400, p_err=0.25, rho=0.3, K=3, cover=c)
        s = summarize(rows); s["cover"] = c
        cov.append(s)
        print("   cover=%.2f acc=%.3f mis=%.3f esc=%.2f" % (c, s["acc"], s["mis"], s["esc"]))

    # 阈值的移动：三组参数各扫一遍，看交叉点会不会动
    thr_runs = []
    for tag, kw in [("基准 (p.25,ρ.3,K3)", dict(p_err=0.25, rho=0.3, K=3)),
                    ("低共源 (ρ=0)", dict(p_err=0.25, rho=0.0, K=3)),
                    ("高共源 (ρ=0.7)", dict(p_err=0.25, rho=0.7, K=3)),
                    ("弱重建 (p=0.35)", dict(p_err=0.35, rho=0.3, K=3)),
                    ("单路 (K=1)", dict(p_err=0.25, rho=0.3, K=1))]:
        pts = []
        for c in [0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            rows = run("M2", seeds=12, decisions=300, cover=c, **kw)
            s = summarize(rows)
            pts.append((c, s["mis"]))
        thr_runs.append(dict(tag=tag, points=pts))
        print("   thr", tag, ["%.2f:%.3f" % p for p in pts])
    with open(OUT / "coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cover", "n", "acc", "neg", "mis", "conf", "lat", "lat_low", "lat_high", "esc", "unan_wrong", "branch"])
        w.writeheader(); w.writerows(cov)

    import json as _j
    with open(OUT / "thresholds.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["tag", "cover", "mis"])
        for r in thr_runs:
            for c, m in r["points"]:
                w.writerow([r["tag"], c, m])
    # 时间分桶（M2 vs M2w）
    bucket = {}
    for r in allrows:
        if r["cond"] in ("M2", "M2w"):
            key = (r["cond"], r["bucket"])
            bucket.setdefault(key, []).append(r)
    with open(OUT / "drift.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["cond", "bucket", "n", "mis", "acc"])
        for (cond, b), rs in sorted(bucket.items()):
            n = len(rs)
            w.writerow([cond, b, n, sum(x["mis"] for x in rs) / n,
                        sum(1 for x in rs if x["act"] == x["truth"]) / n])
    json.dump(dict(summary=summ, coverage=cov, thresholds=thr_runs, params=COST), open(OUT / "results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("wrote results/: %d 步, %d 组敏感性" % (len(allrows), len(sens)))


if __name__ == "__main__":
    main()

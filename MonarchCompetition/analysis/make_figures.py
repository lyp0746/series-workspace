# -*- coding: utf-8 -*-
"""《开明君主与假竞争》——8 图 + 8 表；数据来自 data/prices.py 与 data/vendors.py。"""
import pathlib
import sys
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import prices as P
from data import vendors as V

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a"

S = P.S

LAB_ZH = {"openai": "OpenAI", "anthropic": "Anthropic", "google": "Google", "deepseek": "DeepSeek",
          "x-ai": "xAI", "moonshotai": "Kimi", "qwen": "Qwen", "z-ai": "智谱", "meta": "Meta"}


def save(fig, name):
    fig.savefig(ROOT / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


# ---------------------------------------------------------------- 表
def tables():
    # 表 1：四问 × 价格读数（本文的接口）
    out = ["| 问题 | 原判据（第十篇） | 本文加的一列：价格读数 | 判「答不出」的样子 | 证据等级 |",
           "|---|---|---|---|---|"]
    for q, old, new, fail, g in [
        ("Q1 瓶颈", "删掉这一项，哪项指标最先崩？",
         "价目表上最贵的那一栏是什么（输入／缓存／输出／工具调用）",
         "说不出「贵在哪一栏」，只能给出总价", "A／B"),
        ("Q2 置换", "不做这一步，哪一步会重复？",
         "缓存读价 ÷ 输出价：重放一次比重新判断便宜多少",
         "算不出重放与判断的价差，只能说「省了很多」", "A"),
        ("Q3 可写性", "能否写成十行以内的规则或状态机？",
         "价目 + 路由 + 缓存策略三者能否写成十行（本文实测：能）",
         "写完仍无法判定一个真实账单", "A"),
        ("Q4 承担者", "出事时谁被叫醒？他是否在场？",
         "同一年，同一年龄的价差由谁付：付钱的人、被训练的人、被替代的人",
         "只能列出「用户」这一类，无法区分在场与不在场", "B／C"),
    ]:
        out.append("| **%s** | %s | %s | %s | %s |" % (q, old, new, fail, g))
    (ROOT / "data" / "table_four.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2：九个实验室
    out = ["| 实验室 | 旗舰层（输出价／M） | 商品层（输出价／M） | 溢价 | 权重 | 最宽松许可 | T | 席位价 | 数据政策 | 等级 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for v in V.VENDORS:
        out.append("| %s | %s（%s） | %s（%s） | %s | %s | %s | %d | %s | %s | %s |" % (
            v["name"], "—" if v["flag_out"] is None else "$%.2f" % v["flag_out"], v["flag_model"],
            "—" if v["com_out"] is None else "$%.2f" % v["com_out"], v["com_model"],
            "—" if v["premium"] is None else "%.1f×" % v["premium"],
            v["open_weights"], v["license"], v["T"], v["seat_price"], v["data_policy"], v["grade"]))
    (ROOT / "data" / "table_vendors.md").write_text("\n".join(out), encoding="utf-8")

    # 表 3：RJS 分位
    out = ["| 分组 | n | 中位 | p25 | p75 | 说明 |", "|---|---|---|---|---|---|"]
    rs = [m["rjs"] for m in P.MODELS if m["rjs"]]
    out.append("| 全样本 | %d | %.1f | %.1f | %.1f | 快照内全部有缓存价的模型 |"
               % (len(rs), np.median(rs), np.percentile(rs, 25), np.percentile(rs, 75)))
    out.append("| 开放权重 | %d | %.1f | — | — | 权重可下载 |" % S["rjs_open"])
    out.append("| 闭源 | %d | %.1f | — | — | 权重不可下载 |" % S["rjs_closed"])
    for lab in P.LABS:
        n, med = S["lab_rjs"][lab]
        out.append("| %s（市场读数） | %d | %.1f | — | — | 该实验室全部登记模型的托管商价目 |" % (LAB_ZH[lab], n, med or 0))
    out.append("| **官方价目表（旗舰）** | — | — | — | — | 同一实验室自家页面上的输出÷缓存读 |")
    for lab, model, rjs, calc, g, _ in V.OFFICIAL_RJS:
        out.append("| %s（官方：%s） | — | %.0f | — | — | %s；%s |" % (LAB_ZH[lab], model, rjs, calc, g))
    (ROOT / "data" / "table_rjs.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4：28 个代表模型
    out = ["| 模型 | 层 | 输出 | 输入 | 缓存读 | RJS | 上下文 | 托管商 | 权重 | 许可 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for mid in P.FLAGSHIPS:
        m = P.BY_ID.get(mid)
        if not m:
            continue
        tier = "商品" if m["open_w"] else "旗舰"
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            m["id"].split("/", 1)[1], tier,
            "$%.2f" % m["out"] if m["out"] else "—",
            "$%.2f" % m["inp"] if m["inp"] else "—",
            "$%.3f" % m["cache"] if m["cache"] else "—",
            "%.1f×" % m["rjs"] if m["rjs"] else "—",
            "%dK" % (m["ctx"] // 1000) if m["ctx"] else "—",
            m["providers"] if m["providers"] is not None else "—",
            "开" if m["open_w"] else "闭",
            (m["license"] if isinstance(m["license"], str) and not str(m["license"]).startswith("ERR")
             else ("—" if not m["open_w"] else "待核"))))
    (ROOT / "data" / "table_models.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5：双层价目
    out = ["| 实验室 | 商品层最低输出价 | 旗舰层最高输出价 | 溢价 | 层数 | T |",
           "|---|---|---|---|---|---|"]
    vb = V.by_lab()
    for t in S["tiers"]:
        lay = "双层" if (t["commodity"] and t["flag"]) else ("只有商品层" if t["commodity"] else "只有旗舰层")
        out.append("| %s | %s | %s | %s | %s | %d |" % (
            LAB_ZH[t["lab"]],
            "$%.2f" % t["commodity"] if t["commodity"] else "—",
            "$%.2f" % t["flag"] if t["flag"] else "—",
            "%.1f×" % t["premium"] if t["premium"] else "—", lay, vb[t["lab"]]["T"]))
    prem = [t["premium"] for t in S["tiers"] if t["premium"]]
    out.append("| **合计** | 6 家双层 | — | 中位 %.1f×，区间 %.1f—%.1f× | — | — |"
               % (statistics.median(prem), min(prem), max(prem)))
    (ROOT / "data" / "table_tier.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6：席位价目
    out = ["| 实验室 | 产品 | 美元／月 | 计费形态 | 备注 | 等级 |", "|---|---|---|---|---|---|"]
    for lab, prod, price, form, note, g, _ in V.SEATS:
        out.append("| %s | %s | %.2f | %s | %s | %s |" % (lab, prod, price, form, note, g))
    (ROOT / "data" / "table_seats.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7：数据让渡矩阵
    out = ["| 价格位置 | 例子 | 数据政策 | 付出的是什么 | 等级 |", "|---|---|---|---|---|"]
    for pos, eg, pol, g, _ in V.DATA_MATRIX:
        pay = {"保留并用于训练": "钱 + 训练权", "不用于训练": "钱",
               "不出域": "算力 + 人力", "—": "—"}
        out.append("| %s | %s | %s | %s | %s |" % (pos, eg, pol, pay.get(pol, "—"), g))
    (ROOT / "data" / "table_data.md").write_text("\n".join(out), encoding="utf-8")

    # 表 8：十条命题
    out = ["| 编号 | 命题 | 否证条件 | 读数 | 状态 | 等级 |", "|---|---|---|---|---|---|"]
    for c in CLAIMS:
        out.append("| %s | %s | %s | %s | %s | %s |" % c)
    (ROOT / "data" / "table_claims.md").write_text("\n".join(out), encoding="utf-8")
    print("  8 tables")


CLAIMS = [
 ("T1", "重放—判断价差存在且很大（中位 ≥ 20 倍）",
  "中位 < 10 倍，或缓存读与输出价无系统差别", "中位 %.1f 倍（n=%d）" % (S["rjs_med"], S["n_rjs"]), "支持", "B"),
 ("T2", "闭源的重放—判断价差高于开放权重",
  "控制上下文长度后该差消失", "%.1f 对 %.1f；分档后只两档成立" % (S["rjs_closed"][1], S["rjs_open"][1]),
  "部分", "C"),
 ("T3", "同能力价格在 20 个月内下降 ≥ 100 倍",
  "同能力价格降幅 < 50%（同一基准、同一测量）", "官方博客给出约 150 倍（单一来源）", "支持（单源）", "B"),
 ("T4", "当月新模型的标价中位不降（降幅 < 30%）",
  "后六个月中位比前六个月低 30% 以上", "闭源 $6.00→$5.00（−17%），开放 $0.65→$0.60（−8%）", "支持", "B"),
 ("T5", "前沿旗舰的标价在观察窗内只升不降",
  "出现主流旗舰的公开下调（同模型、同区域、无封顶期）",
  "Gemini 4 Argon 官方公告 2026-12-01 起 $10→$20", "支持", "A"),
 ("T6", "钱与量分离：开放权重拿下多数 token，少数 spend",
  "开放权重 token 份额 < 50%，或 spend 份额 > 50%", "token %.0f—%.0f%%，spend %d%%"
  % (V.MARKET["token_open_floor"], V.MARKET["token_open_peak"], 100 - V.MARKET["spend_closed"]), "支持", "B"),
 ("T7", "双层是常态：过半实验室同时卖可自托管层与独占层",
  "双层实验室 < 3 家", "6／9 家；溢价中位 %.1f×" % statistics.median(
      [t["premium"] for t in S["tiers"] if t["premium"]]), "支持", "B"),
 ("T8", "双层溢价与可传递性（T 分）单调相关",
  "出现 T 分高而溢价更高、T 分低而溢价更低的成对反例",
  "反例成对：T=4 的 OpenAI 83.3× 对 T=3 的 Kimi 2.9×", "**否证**", "C"),
 ("T9", "席位（方向）价格不随执行单价下降：主流席位价落在 $12—$200",
  "出现主流席位价的公开腰斩，或席位价与执行价同向同幅下降",
  "取到 4 家、8 个价位，区间 $12.6—$200", "支持", "B"),
 ("T10", "低价的一半是数据：最低价档以训练权为对价",
  "无训练托管与首方最低价相差 < 20%", "约 2 倍（官方博客口径）", "支持", "B"),
]


# ---------------------------------------------------------------- 图
def fig01():
    rs = [(m["rjs"], m["open_w"]) for m in P.MODELS if m["rjs"]]
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    bins = np.logspace(0, np.log10(max(r for r, _ in rs)), 34)
    ax.hist([r for r, o in rs if not o], bins=bins, color=C1, alpha=.78, label="闭源（n=%d）" % S["rjs_closed"][0])
    ax.hist([r for r, o in rs if o], bins=bins, color=C2, alpha=.65, label="开放权重（n=%d）" % S["rjs_open"][0])
    ax.axvline(S["rjs_closed"][1], color=C1, ls="--", lw=1.1)
    ax.axvline(S["rjs_open"][1], color=C2, ls="--", lw=1.1)
    ax.text(S["rjs_closed"][1] * 1.12, ax.get_ylim()[1] * .92, "闭源中位 %.0f×" % S["rjs_closed"][1],
            fontsize=7.4, color=C1)
    ax.text(S["rjs_open"][1] * .93, ax.get_ylim()[1] * .78, "开放中位 %.0f×" % S["rjs_open"][1],
            fontsize=7.4, color=C2, ha="right")
    ax.set_xscale("log")
    ax.set_xlabel("重放—判断价差 RJS（输出单价 ÷ 缓存读单价，倍数，对数轴）")
    ax.set_ylabel("模型数")
    ax.set_title("图 1　一次「新判断」比一次「重放」贵多少：%d 个模型的价目表读数" % S["n_rjs"],
                 fontsize=9.4, loc="left")
    ax.legend(fontsize=7.6, frameon=False)
    save(fig, "fig01_rjs.png")


def fig02():
    o = [m["out"] for m in P.MODELS if m["out"] and m["open_w"]]
    c = [m["out"] for m in P.MODELS if m["out"] and not m["open_w"]]
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    rng = np.random.default_rng(7)
    ax.scatter(o, rng.normal(1, .045, len(o)), s=11, color=C2, alpha=.55, label="开放权重")
    ax.scatter(c, rng.normal(0, .045, len(c)), s=11, color=C1, alpha=.55, label="闭源")
    ax.boxplot([o, c], vert=False, positions=[1, 0], widths=.34, showfliers=False,
               medianprops=dict(color="#222", lw=1.4), boxprops=dict(color="#666"),
               whiskerprops=dict(color="#666"), capprops=dict(color="#666"))
    ax.set_xscale("log")
    ax.set_yticks([0, 1]); ax.set_yticklabels(["闭源", "开放权重"], fontsize=8)
    ax.set_xlabel("输出单价（美元／百万 token，对数轴）")
    ax.set_title("图 2　同一个「token」的两个价位：开放权重中位 \$%.2f，闭源中位 \$%.2f（%.1f 倍）"
                 % (S["out_open"][1], S["out_closed"][1], S["out_ratio"]), fontsize=9.4, loc="left")
    save(fig, "fig02_levels.png")


def fig03():
    ser = [s for s in S["series"] if s["n_open"] + s["n_closed"] >= 2]
    xs = [s["month"] for s in ser]
    idx = np.arange(len(xs))
    yc = [s["med_closed"] for s in ser]
    yo = [s["med_open"] for s in ser]
    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    ax.plot(idx, [v if v else np.nan for v in yc], "-o", color=C1, ms=3, lw=1.2, label="闭源：当月新模型标价中位")
    ax.plot(idx, [v if v else np.nan for v in yo], "-o", color=C2, ms=3, lw=1.2, label="开放权重：当月新模型标价中位")
    ax.set_yscale("log")
    ax.set_ylabel("输出单价（美元／M，对数轴）")
    step = max(1, len(xs) // 8)
    ax.set_xticks(idx[::step]); ax.set_xticklabels(xs[::step], rotation=40, fontsize=7, ha="right")
    ax.set_title("图 3　二十个月里，新进入市场的模型并没有变便宜（首尾六个月中位：闭源 \$%.2f→\$%.2f）"
                 % (S["vintage_first"][1], S["vintage_last"][1]), fontsize=9.4, loc="left")
    ax.legend(fontsize=7.4, frameon=False)
    save(fig, "fig03_vintage.png")


def fig04():
    M = V.MARKET
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    rows = [("闭源权重", 100 - M["spend_closed"], M["spend_closed"]),
            ("开放权重", round((M["token_open_floor"] + M["token_open_peak"]) / 2), 100 - M["spend_closed"])]
    for i, (name, tok, spd) in enumerate([("闭源权重", 100 - M["spend_closed"], M["spend_closed"]),
                                          ("开放权重", M["token_open_peak"], 100 - M["spend_closed"])]):
        y = 1 - i
        ax.plot([tok, spd], [y, y], color="#bbb", lw=2.2, zorder=1)
        ax.scatter([tok], [y], s=90, color=C2, zorder=3)
        ax.scatter([spd], [y], s=90, color=C1, zorder=3)
        ax.text(tok, y + .17, "token %d%%" % tok, ha="center", fontsize=7.8, color=C2)
        ax.text(spd, y + .17, "spend %d%%" % spd, ha="center", fontsize=7.8, color=C1)
        ax.text(-3, y, name, ha="right", va="center", fontsize=8.4)
    ax.set_xlim(0, 100); ax.set_ylim(-.55, 1.55)
    ax.set_yticks([]); ax.set_xlabel("平台份额（%）")
    ax.set_title("图 4　量与钱的分离：token 去了开放权重，钱留在闭源", fontsize=9.4, loc="left")
    ax.text(0, -0.48, "注：开放权重 token 份额为 2026 年 4—9 月的峰值区间（%d—%d%%）；spend 为闭源份额。"
            % (M["token_open_floor"], M["token_open_peak"]), fontsize=6.8, color="#555")
    save(fig, "fig04_sep.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    order = [t for t in S["tiers"]]
    xs = np.arange(len(order))
    for i, t in enumerate(order):
        if t["commodity"]:
            ax.scatter([i], [t["commodity"]], s=60, color=C2, zorder=3)
        if t["flag"]:
            ax.scatter([i], [t["flag"]], s=60, color=C1, zorder=3)
        if t["commodity"] and t["flag"]:
            ax.plot([i, i], [t["commodity"], t["flag"]], color="#ccc", lw=1.6, zorder=1)
            ax.text(i + .16, (t["commodity"] * t["flag"]) ** .5, "%.0f×" % t["premium"],
                    fontsize=7.2, color="#666", va="center")
    ax.set_yscale("log")
    ax.set_xticks(xs); ax.set_xticklabels([LAB_ZH[t["lab"]] for t in order], fontsize=7.8, rotation=25, ha="right")
    ax.set_ylabel("输出单价（美元／M，对数轴）")
    ax.set_title("图 5　同一家实验室的两个价目表：可自托管的一层与独占的一层", fontsize=9.4, loc="left")
    ax.scatter([], [], s=60, color=C2, label="商品层（权重可下载）")
    ax.scatter([], [], s=60, color=C1, label="旗舰层（权重不可下载）")
    ax.legend(fontsize=7.4, frameon=False, loc="upper left")
    save(fig, "fig05_tier.png")


def fig06():
    fig, ax = plt.subplots(figsize=(6.6, 2.7))
    for i, (lab, prod, price, form, note, g, _) in enumerate(V.SEATS):
        ax.scatter([price], [i], s=44, color=C1 if "Anthropic" in lab else (C3 if "OpenAI" in lab else C2), zorder=3)
        ax.text(price * 1.12, i, "%s %s" % (lab.split()[0], prod.replace("Coding Plan ", "")),
                fontsize=6.9, va="center")
    lo, hi = min(s[2] for s in V.SEATS), max(s[2] for s in V.SEATS)
    ax.axvspan(lo, hi, color="#f2ede3", zorder=0)
    ax.set_xscale("log")
    ax.set_yticks([]); ax.set_xlim(8, 400)
    ax.set_xlabel("席位价（美元／月，对数轴）　灰带：本文取到的全部席位价区间 \$%.1f—\$%.0f" % (lo, hi))
    ax.set_title("图 6　方向层的价目：席位定价不随执行单价下降", fontsize=9.4, loc="left")
    ax.text(8.6, -1.15, "对照：同一快照内输出单价从 \$0.42 到 \$50（%.0f 倍），席位价只跨 %.1f 倍。"
            % (50 / .42, hi / lo), fontsize=6.9, color="#555")
    save(fig, "fig06_seat.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

    def box(x, y, w, h, t, c="#f7f4ec"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06", fc=c, ec="#c9c0ad", lw=.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=7.8, linespacing=1.6)

    box(.2, 4.3, 4.5, 1.35, "Q1 瓶颈：预算（算力与资本）\n→ 与第十篇 T3「预算从不作主瓶颈」冲突", "#f6e9e6")
    box(5.1, 4.3, 4.5, 1.35, "Q2 置换：拆分（模型分层）+ 预计算（缓存 90%）\n+ 复制（多供应商路由）")
    box(.2, 2.55, 4.5, 1.35, "Q3 可写性：A（价目 + 路由 + 缓存，十行可写）\n→ 与第十篇「可写性低则代价不在场」冲突", "#f6e9e6")
    box(5.1, 2.55, 4.5, 1.35, "Q4 承担者：不在场者（被替代者、被训练者）\n在场性需加第五档：在场而不知情", "#f6e9e6")
    box(.2, .75, 9.4, 1.3, "第四问的两次修订是本文对第十篇的唯一实质修改：\n"
        "可写性高 ≠ 代价可见；在场 ≠ 知情。两处都不改十篇正文，只在本篇登记。", "#eef2f6")
    ax.text(.2, 5.85, "图 7　D21（agent 平台）的四问编码：两处与第十篇的既有结论相撞", fontsize=9.4, fontweight="bold")
    save(fig, "fig07_d21.png")


def fig08():
    props = [("T1", "重放—判断价差 ≥ 20×", 1.0), ("T2", "闭源价差高于开放（部分）", 0.5),
             ("T3", "同能力价降 ≥ 100×（单源）", 1.0), ("T4", "新模型标价不降", 1.0),
             ("T5", "旗舰标价只升不降", 1.0), ("T6", "钱与量分离", 1.0),
             ("T7", "双层是常态", 1.0), ("T8", "溢价与 T 分单调", 0.0),
             ("T9", "席位价不随执行降", 1.0), ("T10", "低价的一半是数据", 1.0)]
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ys = np.arange(len(props))[::-1]
    cols = {1.0: C1, .5: C4, 0.0: C3}
    ax.barh(ys, [p[2] for p in props], .55, color=[cols[p[2]] for p in props], zorder=3)
    for y, (i, t, v) in zip(ys, props):
        ax.text(-.02, y, "%s %s" % (i, t), ha="right", va="center", fontsize=7.4)
        ax.text(max(v, 0) + .02, y, {1.0: "支持", .5: "部分／待检验", 0.0: "否证"}[v],
                va="center", fontsize=7.2, color=cols[v])
    ax.set_yticks([]); ax.set_xlim(0, 1.3); ax.set_xticks([0, .5, 1.0])
    ax.set_xticklabels(["0", "0.5", "1"], fontsize=8)
    ax.set_title("图 8　自证：十条命题的最终状态（一条被数据打掉）", fontsize=9.4, loc="left")
    save(fig, "fig08_self.png")


def main():
    print("tables...")
    tables()
    print("figures...")
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08):
        f()


if __name__ == "__main__":
    main()

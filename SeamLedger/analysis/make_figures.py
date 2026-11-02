# -*- coding: utf-8 -*-
"""《接缝的账本》——8 图 + 10 表；数据来自 data/seams.py（单一来源）。"""
import csv
import pathlib
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import seams as D

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#ececec",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4 = "#2f6f9f", "#b3701f", "#a8322d", "#7a7a7a"
TC = {"逻辑矛盾": C3, "接口缺失": C1, "记账冲突": C2, "定理边界": C4}

ROWS = D.rows()
S = D.stats()
N = len(ROWS)


def save(fig, name):
    fig.savefig(ROOT / "assets" / "figures" / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


# ---------------------------------------------------------------- 表
def tables():
    # 表 1：四种冲突类型
    out = ["| 类型 | 判据 | 条数 | 它要求什么 | 典型条目 |", "|---|---|---:|---|---|"]
    need = {
        "逻辑矛盾": "两条命题不能同时为真；否定其一即可",
        "接口缺失": "两边都成立，但没有共同对象/共同语言",
        "记账冲突": "同一个词在两本账上指不同载体",
        "定理边界": "一条 no-go 定理排除了某一类方案",
    }
    ex = {"逻辑矛盾": "S13 背景独立；S25 信息悖论", "接口缺失": "S07 时间问题；S19 全息对偶",
          "记账冲突": "S09 非定域；S20 真空能", "定理边界": "S03 贝尔；S23 不可重整化"}
    for t in D.TYPES:
        out.append(f"| **{t}** | {need[t]} | {S['type'].get(t,0)} | {need[t].split('；')[0]} | {ex[t]} |")
    out.append(f"| **合计** | — | **{N}** | — | — |")
    (ROOT / "data" / "table_types.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2：六核心分布
    out = ["| 主核 | 条数 | 它在这批账目里问什么 | 最硬的一条 | 最软的一条 |", "|---|---:|---|---|---|"]
    ask = {"看见": "两边有没有共同的“可观察量”？", "选择": "哪一边被当作背景、哪一边被量子化？",
           "跟上": "两边有没有共同的时钟与因果结构？", "讲述": "两边说的“统一/实在”是不是同一件事？",
           "临界": "冲突是否落在相变/紫外/奇点这一类边界上？", "记住": "信息、熵与可恢复性记在哪本账上？"}
    hard = {"看见": "S03 贝尔（A）", "选择": "S13 背景独立（B）", "跟上": "S09 纠缠/光锥（A）",
            "讲述": "S19 全息对偶（B）", "临界": "S20 真空能（A 测量）", "记住": "S28 面积律（B）"}
    soft = {"看见": "S01 叠加度规（C）", "选择": "S16 宇宙边界（C）", "跟上": "S11 量子时钟（B）",
            "讲述": "S18 实在论（C）", "临界": "S24 渐近安全（C）", "记住": "S27 火墙（C）"}
    for c in D.CORES:
        out.append(f"| **{c}** | {S['core'].get(c,0)} | {ask[c]} | {hard[c]} | {soft[c]} |")
    out.append(f"| **合计** | **{N}** | — | — | — |")
    (ROOT / "data" / "table_cores.md").write_text("\n".join(out), encoding="utf-8")

    # 表 3：尺度 × 可测性
    out = ["| 尺度 | 直接 | 间接 | 不可测 | 合计 | 可直接测量占比 |", "|---|---:|---:|---:|---:|---:|"]
    for sc in D.SCALES:
        row = [S["scale_meas"].get((sc, m), 0) for m in D.MEAS]
        tot = sum(row)
        pct = row[0] / tot * 100 if tot else 0
        out.append(f"| {sc} | " + " | ".join(str(v) if v else "·" for v in row) + f" | {tot} | {pct:.0f}% |")
    tot = [sum(S["scale_meas"].get((sc, m), 0) for sc in D.SCALES) for m in D.MEAS]
    out.append("| **合计** | " + " | ".join(f"**{v}**" for v in tot) + f" | **{N}** | **{tot[0]/N*100:.0f}%** |")
    (ROOT / "data" / "table_scales.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4：三十条总表
    out = ["| 编号 | 账目 | 年 | 类型 | 主核 | 尺度 | 状态 | 可测 | 等级 | 同名不同物 |",
           "|---|---|---:|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["item"]} | {r["year"]} | {r["type"]} | {r["core"]} | '
                   f'{r["scale"]} | {r["status"]} | {r["meas"]} | {r["grade"]} | {r["name"]} |')
    (ROOT / "data" / "table_thirty.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5：六核心 × 六专著
    out = ["| 核心 | 专著 | 在本篇里的用法 | 关系 | 等级 |", "|---|---|---|---|---|"]
    for c, b, use, rel, g in [
        ("**看见**（主）", "《区分的语言》", "“共同可观察量”的判据：两边有没有同一个区分动作", "借用语言并检验", "乙／B"),
        ("**选择**（主）", "《选择的代价》", "“保哪一项／让哪一项”：背景、边界、对称性的取舍", "借用语言", "乙／B"),
        ("**跟上**（主）", "《错位的时间》", "时钟与因果结构：多时钟对齐、τ 的六重代理", "借用机制", "乙／B"),
        ("**讲述**（辅）", "《诠释的权衡》", "置信度分配：把“矛盾”降级为“接口缺失”的记账", "检验并修正", "乙／B"),
        ("**临界**（辅）", "《涌现的临界》", "紫外、奇点、真空能是否真是相变/临界现象", "检验并修正", "丙／C"),
        ("**记住**（辅）", "《遗忘的边界》", "信息、熵、可恢复性：容量—压缩—遗忘的账", "借用机制", "丙／C"),
    ]:
        out.append(f"| {c} | {b} | {use} | {rel} | {g} |")
    (ROOT / "data" / "table_six.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6：五条定理边界
    out = ["| 定理 | 它禁止什么 | 它不禁止什么 | 主核 | 等级 |", "|---|---|---|---|---|"]
    for a, b, c, d, e in [
        ("贝尔定理（1964）", "定域隐变量理论不能复现全部量子关联", "信号定域；量子场论的微观因果性", "看见", "A"),
        ("Weinberg–Witten（1980）", "无质量自旋 ≥2 复合态不能有协变守恒流", "引力子作为基本场；有效场论", "看见", "B"),
        ("Coleman–Mandula（1967）", "内部对称与时空对称的非平凡组合（在特定前提下）", "超对称；局域对称", "选择", "B"),
        ("无全局对称性（量子引力）", "量子引力中精确的全局对称", "低能有效理论中的近似全局对称", "看见", "B"),
        ("引力不可重整化（1986）", "纯微扰量子引力作为终极理论", "作为有效场论；非微扰方案", "临界", "B"),
    ]:
        out.append(f"| {a} | {b} | {c} | {d} | {e} |")
    (ROOT / "data" / "table_nogo.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7：六个候选纲领
    out = ["| 纲领 | 声称处理的账目 | 覆盖 | 最强的一项 | 最弱的一项 |", "|---|---:|---:|---|---|"]
    best = {"弦论/全息": "S19 全息对偶", "圈量子引力": "S02 面积谱", "渐近安全": "S24 固定点",
            "因果集/CDT": "S29 面积/体积", "量子参考系": "S06 参考系", "类比引力": "S10 Unruh"}
    worst = {"弦论/全息": "S13 非微扰背景独立", "圈量子引力": "S07 时间问题", "渐近安全": "S25 信息",
             "因果集/CDT": "S19 全息", "量子参考系": "S23 紫外", "类比引力": "S01 叠加度规"}
    counts = {p: sum(1 for r in ROWS if p in D.COVER[r["id"]]) for p in D.PROGRAMS}
    for p in sorted(D.PROGRAMS, key=lambda x: -counts[x]):
        out.append(f"| {p} | {counts[p]}/30 | {counts[p]/30*100:.0f}% | {best[p]} | {worst[p]} |")
    (ROOT / "data" / "table_candidates.md").write_text("\n".join(out), encoding="utf-8")

    # 表 8：十条命题
    out = ["| 编号 | 命题 | 检验/否证条件 | 状态 | 等级 |", "|---|---|---|---|---|"]
    for pid, claim, test, status, grade, core, scale in D.PROPOSITIONS:
        out.append(f"| {pid} | {claim} | {test} | {status} | {grade} |")
    (ROOT / "data" / "table_props.md").write_text("\n".join(out), encoding="utf-8")

    # 表 9：自证
    out = ["| 命题 | 状态 | 等级 | 它对本文做了什么 |", "|---|---|---|---|"]
    for pid, claim, test, status, grade, core, scale in D.PROPOSITIONS:
        out.append(f"| {pid} | {status} | {grade} | {claim} |")
    (ROOT / "data" / "table_self.md").write_text("\n".join(out), encoding="utf-8")

    # 表 10：敏感性
    sens = D.sensitivity()
    out = ["| 读法 | 逻辑矛盾 | 接口缺失 | 记账冲突 | 定理边界 |", "|---|---:|---:|---:|---:|"]
    for name in ["保守", "基准", "宽松"]:
        c = sens[name]
        out.append(f"| {name} | {c.get('逻辑矛盾',0)} | {c.get('接口缺失',0)} | {c.get('记账冲突',0)} | {c.get('定理边界',0)} |")
    (ROOT / "data" / "table_sensitivity.md").write_text("\n".join(out), encoding="utf-8")

    # 表 11：等级 × 状态
    out = ["| 等级 | " + " | ".join(D.STATUSES) + " | 合计 |", "|---|" + "---:|" * (len(D.STATUSES) + 1)]
    for g in "ABC":
        vals = [sum(1 for r in ROWS if r["grade"] == g and r["status"] == s) for s in D.STATUSES]
        out.append(f"| {g} | " + " | ".join(str(v) if v else "·" for v in vals) + f" | {sum(vals)} |")
    vals = [sum(1 for r in ROWS if r["status"] == s) for s in D.STATUSES]
    out.append("| **合计** | " + " | ".join(f"**{v}**" for v in vals) + f" | **{N}** |")
    (ROOT / "data" / "table_grade_status.md").write_text("\n".join(out), encoding="utf-8")

    # CSV：单一来源
    with open(ROOT / "seams.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=D.FIELDS)
        w.writeheader()
        w.writerows(ROWS)
    print("  tables: 11 + seams.csv")


# ---------------------------------------------------------------- 图
def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=9):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    fc=fc, ec="#555", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.25, 3.9, 3.0, 1.5, "量子力学\n态矢 / 希尔伯特", "#dbe7f1", 8.2)
    box(6.75, 3.9, 3.0, 1.5, "广义相对论\n度规 / 微分同胚", "#e9e1d2", 8.2)
    box(3.55, 4.25, 2.9, .8, "接缝\n（没有共同对象）", "#f4efe4", 8.0)
    ax.add_patch(FancyArrowPatch((3.3, 4.65), (3.55, 4.65), arrowstyle="<|-|>", mutation_scale=11, color="#777"))
    ax.add_patch(FancyArrowPatch((6.45, 4.65), (6.75, 4.65), arrowstyle="<|-|>", mutation_scale=11, color="#777"))

    labels = [("逻辑矛盾", "4 条：两条命题不能同时为真", C3),
              ("接口缺失", "13 条：都成立，但没有共同语言", C1),
              ("记账冲突", "8 条：同一个词指两个东西", C2),
              ("定理边界", "5 条：no-go 排除了某一类方案", C4)]
    for i, (t, s, c) in enumerate(labels):
        y = 3.1 - i * .72
        ax.add_patch(FancyBboxPatch((.7, y), .28, .28, boxstyle="round,pad=0.02", fc=c, ec="none"))
        ax.text(1.15, y + .14, t, fontsize=8.8, fontweight="bold", va="center")
        ax.text(2.7, y + .14, s, fontsize=7.8, color="#444", va="center")
    
    ax.text(.2, .12, "注：条数为本文三十条账目的基准编码；保守/宽松读法见第 3.6 节与表 10。",
            fontsize=7, color="#555")
    save(fig, "fig01_seams.png")


def fig02():
    vals = [S["type"].get(t, 0) for t in D.TYPES]
    fig, ax = plt.subplots(figsize=(6.3, 2.9))
    y = np.arange(len(D.TYPES))[::-1]
    ax.barh(y, vals, color=[TC[t] for t in D.TYPES], height=.58, zorder=3)
    for yy, v, t in zip(y, vals, D.TYPES):
        ax.text(v + .18, yy, f"{v}  ({v/N*100:.1f}%)", va="center", fontsize=8.8)
    ax.set_yticks(y); ax.set_yticklabels(D.TYPES)
    ax.set_xlim(0, max(vals) + 3.2); ax.set_xlabel("账目数")
    # ax.set_title("图 2　三十条账目里，逻辑矛盾只占 13%", fontsize=9.4, loc="left")
    save(fig, "fig02_types.png")


def fig03():
    M = np.array([[S["core_type"].get((c, t), 0) for t in D.TYPES] for c in D.CORES])
    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    ax.imshow(M, cmap="Blues", vmin=0, vmax=M.max() + .5, aspect="auto")
    ax.set_xticks(range(len(D.TYPES))); ax.set_xticklabels(D.TYPES, fontsize=8.4, rotation=20, ha="right")
    ax.set_yticks(range(len(D.CORES))); ax.set_yticklabels(D.CORES, fontsize=8.8)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, str(v) if v else "·", ha="center", va="center", fontsize=9,
                    color="white" if v >= 3 else "#333")
    ax.grid(False)
    # ax.set_title("图 3　六核心 × 四种接缝：没有哪个核心只对一种冲突负责", fontsize=9.4, loc="left")
    save(fig, "fig03_core_type.png")


def fig04():
    fig, ax = plt.subplots(figsize=(6.1, 3.0))
    bottoms = np.zeros(len(D.SCALES))
    colors = {"直接": C3, "间接": C2, "不可测": C1}
    for m in D.MEAS:
        vals = np.array([S["scale_meas"].get((sc, m), 0) for sc in D.SCALES])
        ax.bar(D.SCALES, vals, .52, bottom=bottoms, label=m, color=colors[m], alpha=.92, zorder=3)
        for i, v in enumerate(vals):
            if v:
                ax.text(i, bottoms[i] + v / 2, str(v), ha="center", va="center", fontsize=8,
                        color="white" if m != "间接" else "#222")
        bottoms += vals
    ax.set_ylabel("账目数"); ax.set_ylim(0, 11.5)
    ax.legend(fontsize=8, frameon=False, ncol=3, loc="upper right")
    # ax.set_title("图 4　尺度越靠近普朗克/宇宙，越不可直接测量", fontsize=9.4, loc="left")
    save(fig, "fig04_scale_meas.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    for t in D.TYPES:
        years = sorted(int(r["year"]) for r in ROWS if r["type"] == t)
        xs, ys, c = [], [], 0
        for y in range(1930, 2026):
            c += sum(1 for yy in years if yy == y)
            xs.append(y); ys.append(c)
        ax.plot(xs, ys, color=TC[t], lw=1.7, label=t)
    ax.set_xlim(1930, 2025); ax.set_ylim(0, 16)
    ax.set_xlabel("关键文献年份"); ax.set_ylabel("累计条数")
    ax.legend(fontsize=7.6, frameon=False, ncol=2, loc="upper left")
    # ax.set_title("图 5　四种接缝在不同年代累积：定理边界最早，记账冲突最晚", fontsize=9.4, loc="left")
    save(fig, "fig05_timeline.png")


def fig06():
    C = D.cover_rows()
    M = np.array([[r[p] for p in D.PROGRAMS] for r in C])
    fig, ax = plt.subplots(figsize=(5.2, 6.6))
    ax.imshow(M, cmap="Greens", vmin=0, vmax=1.3, aspect="auto")
    ax.set_xticks(range(len(D.PROGRAMS)))
    ax.set_xticklabels(D.PROGRAMS, fontsize=7.6, rotation=35, ha="right")
    ax.set_yticks(range(len(C))); ax.set_yticklabels([r["id"] for r in C], fontsize=6.6)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, "●" if M[i, j] else "", ha="center", va="center", fontsize=6,
                    color="white" if M[i, j] else "#ddd")
    ax.grid(False)
    # ax.set_title("图 6　六个候选纲领的“声称覆盖”：没有一个超过 60%", fontsize=9.3, loc="left")
    save(fig, "fig06_coverage.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.2, 3.1))
    for gi, g in enumerate("ABC"):
        for si, st in enumerate(D.STATUSES):
            v = sum(1 for r in ROWS if r["grade"] == g and r["status"] == st)
            if v:
                ax.scatter(si, 2 - gi, s=90 + v * 38, color={"A": C3, "B": C2, "C": C1}[g],
                           alpha=.75, edgecolor="white", lw=.8, zorder=3)
                ax.text(si, 2 - gi, str(v), ha="center", va="center", fontsize=8, color="white")
    ax.set_xticks(range(len(D.STATUSES))); ax.set_xticklabels(D.STATUSES, fontsize=8.2)
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels(["A", "B", "C"])
    ax.set_ylim(-.5, 2.5); ax.set_xlim(-.6, len(D.STATUSES) - .4)
    ax.set_ylabel("证据等级")
    # ax.set_title("图 7　A 级只出现在“已测/已证定理”，解释与开放几乎全是 C", fontsize=9.3, loc="left")
    save(fig, "fig07_grade_status.png")


def fig08():
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ys = np.arange(len(D.PROPOSITIONS))[::-1]
    cols = {"成立": C1, "部分": C2, "待检验": C4, "开放": "#8a7bb0", "证伪": C3, "撤回": "#555"}
    for y, p in zip(ys, D.PROPOSITIONS):
        pid, claim, test, status, grade, core, scale = p
        ax.plot([0, 1], [y, y], color="#ddd", lw=1, zorder=1)
        ax.scatter(1, y, s=70, color=cols[status], zorder=3)
        ax.text(-.03, y, pid, ha="right", va="center", fontsize=8.4)
        ax.text(1.06, y, f"{status} / {grade}", va="center", fontsize=7.8, color="#444")
    ax.set_xlim(-.25, 1.55); ax.set_ylim(-.6, len(D.PROPOSITIONS) - .4)
    ax.set_yticks([]); ax.set_xticks([])
    # ax.set_title("图 8　自证：十条命题里三条成立、两条部分、一条被自己证伪", fontsize=9.3, loc="left")
    save(fig, "fig08_self.png")


def main():
    (ROOT / "assets" / "figures").mkdir(parents=True, exist_ok=True)
    tables()
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08):
        f()
    print("done: 8 figures, 11 tables")


if __name__ == "__main__":
    main()

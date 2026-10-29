# -*- coding: utf-8 -*-
"""《领域的剖面》——8 图 + 8 表；数据来自 data/domains.py（单一来源）。"""
import csv
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import domains as D

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a"

ROWS = D.rows()
S = D.stats()
ACT = D.ACTIONS
PRE = D.PRESENCE


def save(fig, name):
    fig.savefig(ROOT / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


# ---------------------------------------------------------------- 表
def tables():
    # 表 1：四问与六核心
    out = ["| 问题 | 问什么 | 判据（答不出即不可用） | 对应核心 | 本文等级 |",
           "|---|---|---|---|---|"]
    for q, ask, crit, core, g in [
        ("Q1 瓶颈", "这个领域在为哪一项稀缺资源付账？", "删掉这一项，哪项指标最先崩？", "看见", "乙／B"),
        ("Q2 置换", "它合并／拆分／复制／预计算／抽象／绕开／试探了什么？", "不做这一步，哪一步会重复？", "选择", "乙／B"),
        ("Q3 可写性", "核心机制能否写成十行以内的规则或状态机？", "写出后，能否用它判定一个真实案例？", "讲述＋临界", "甲／B"),
        ("Q4 承担者", "代价最后由谁付？", "出事时谁被叫醒？他是否在场？", "讲述（扩展）", "乙／B"),
    ]:
        out.append(f"| **{q}** | {ask} | {crit} | {core} | {g} |")
    (ROOT / "data" / "table_four.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2：二十个领域
    out = ["| 编号 | 领域 | Q1 主／次瓶颈 | Q2 置换 | Q3 | Q4 主承担者（在场性） | 让出了什么 | 等级 |",
           "|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["domain"]} | {r["q1a"]}／{r["q1b"]} | {r["q2"].replace(",", "·")} | '
                   f'{r["q3"]} | {r["q4"]}（{r["presence"]}） | {r["gaveup"]} | {r["grade"]} |')
    (ROOT / "data" / "table_domains.md").write_text("\n".join(out), encoding="utf-8")
    with open(ROOT / "domains.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=D.FIELDS + ["q2l"])
        w.writeheader()
        w.writerows(ROWS)

    # 表 3：瓶颈分布
    out = ["| 稀缺资源 | 作为主瓶颈 | 作为次瓶颈 | 合计 |", "|---|---|---|---|"]
    for b in D.BOTTLENECKS:
        a, c = S["q1a"].get(b, 0), S["q1b"].get(b, 0)
        out.append(f"| {b} | {a or '·'} | {c or '·'} | {a + c or '·'} |")
    tot_a = sum(S["q1a"].values()); tot_b = sum(S["q1b"].values())
    out.append(f"| **合计** | **{tot_a}** | **{tot_b}** | **{tot_a + tot_b}** |")
    (ROOT / "data" / "table_bottleneck.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4：动作通用度
    out = ["| 置换动作 | 覆盖领域数 | 通用度 | 它在做什么 |", "|---|---|---|---|"]
    note = {"拆分": "把一件事切成可分别承担的部分", "预计算": "把判断提前算好，现场只查表",
            "复制": "用多份冗余换可用性", "试探": "先小步做，再用结果决定下一步",
            "绕开": "不解决它，改走另一条路", "抽象": "把差异隐藏，只留接口",
            "合并": "把两件事并为一次完成"}
    for a, n in sorted(S["actions"].items(), key=lambda kv: -kv[1]):
        u = "通用（≥14）" if n >= 14 else ("常见（8–13）" if n >= 8 else "专属（<8）")
        out.append(f"| {a} | {n}/20 | {u} | {note[a]} |")
    (ROOT / "data" / "table_actions.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5：可写性 × 在场性
    out = ["| 可写性 | 在场 | 延迟 | 分散 | 不在场 | 合计 | 可见代价占比 |", "|---|---|---|---|---|---|---|"]
    for w in "ABC":
        row = [S["cross"][(w, p)] for p in PRE]
        tot = sum(row)
        vis = (row[0] + row[1]) / tot * 100 if tot else 0
        out.append(f"| {w} | " + " | ".join(str(v) if v else "·" for v in row) +
                   f" | {tot} | {vis:.0f}% |")
    tot = [sum(S["cross"][(w, p)] for w in "ABC") for p in PRE]
    out.append("| **合计** | " + " | ".join(f"**{v}**" for v in tot) + f" | **{sum(tot)}** | — |")
    (ROOT / "data" / "table_cross.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6：主次互换改变结论的五个领域
    out = ["| 编号 | 领域 | 原判 | 若把次瓶颈升为主瓶颈 | 改判后的结论 |", "|---|---|---|---|---|"]
    for r in ROWS:
        if r["swap"] == "Y":
            out.append(f'| {r["id"]} | {r["domain"]} | {r["q1a"]}为主 | {r["q1b"]}为主 | {r["swapnote"]} |')
    (ROOT / "data" / "table_swap.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7：六核心 × 六专著
    out = ["| 核心 | 专著 | 在四问中的位置 | 关系 | 等级 |", "|---|---|---|---|---|"]
    for r in [("**看见**（主）", "《区分的语法》", "Q1：判断哪一项是瓶颈，等于判断在哪一项上划线", "**检验**：二十个领域全部落在七类之内，无新增类别", "乙／B"),
              ("**选择**（主）", "《选择的代价》", "Q2：置换动作就是「让出哪一项」的具体形态", "**检验**：拆分/复制/预计算三动作覆盖 17 以上，与 C-A-T 的支配关系一致", "乙／B"),
              ("**讲述**（主）", "《诠释的权衡》", "Q3 的等级判定；Q4 的承担者归属", "**扩展**：Q4 把「置信度分配」扩为「代价分配」", "乙／B"),
              ("**临界**（辅）", "《涌现的临界》", "Q3 的 C 级：写不出十行的地方，正是规则该换的地方", "借用方向", "丙／C"),
              ("**记住**", "《遗忘的边界》", "Q2 的「预计算」与「复制」是容量换时间", "借用机制", "丙／C"),
              ("**跟上**", "《错位的时间》", "Q1 的「延迟」；Q4 的「延迟承担」", "借用语言", "丙／C")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT / "data" / "table_six.md").write_text("\n".join(out), encoding="utf-8")

    # 表 8：依据 × 等级
    out = ["| 判定依据 | 领域数 | 等级分布 | 说明 |", "|---|---|---|---|"]
    basis_note = {"规范文本": "有公开的规范/标准/程序法可核验",
                  "公开统计": "有公开统计或行业数据支撑",
                  "公开文献": "有公开研究或报道描述其机制",
                  "推断": "无公开材料，按生活经验推断"}
    for b in ["规范文本", "公开统计", "公开文献", "推断"]:
        ids = [r["id"] for r in ROWS if r["basis"] == b]
        gs = {g: sum(1 for r in ROWS if r["basis"] == b and r["grade"] == g) for g in "ABC"}
        gtxt = "／".join(f"{g}{gs[g]}" for g in "ABC" if gs[g])
        out.append(f"| {b} | {len(ids)} | {gtxt} | {basis_note[b]} |")
    (ROOT / "data" / "table_basis.md").write_text("\n".join(out), encoding="utf-8")
    print("  tables: 8")


# ---------------------------------------------------------------- 图
def fig01():
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.0); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.6):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(3.55, 2.5, 2.9, 1.0, "一个领域\n（黑箱）", "#f2efe6", 9)
    box(.3, 4.55, 2.9, 1.05, "Q1 瓶颈\n为哪项稀缺资源付账", "#dbe7f1")
    box(3.55, 4.55, 2.9, 1.05, "Q2 置换\n合并/拆分/复制/…", "#e6ecdf")
    box(6.8, 4.55, 2.9, 1.05, "Q3 可写性\n能否写成十行", "#f2e6e6")
    box(3.55, .8, 2.9, 1.05, "Q4 承担者\n代价落在谁身上", "#f7efe2")
    for a, b in [((1.75, 4.55), (4.2, 3.55)), ((5.0, 4.55), (5.0, 3.55)),
                 ((8.25, 4.55), (5.8, 3.55)), ((5.0, 2.45), (5.0, 1.9))]:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, lw=1, color="#666"))
    ax.text(.2, 5.85, "图 1　四个问题是一个剖面，不是四个标签", fontsize=9.8, fontweight="bold")
    ax.text(.2, .12, "注：Q1 定「在哪一项上划线」，Q2 定「让出了什么」，Q3 定「能不能写清」，Q4 定「谁付账」。",
            fontsize=7, color="#555")
    save(fig, "fig01_four.png")


def fig02():
    bl = D.BOTTLENECKS
    a = [S["q1a"].get(b, 0) for b in bl]
    b = [S["q1b"].get(x, 0) for x in bl]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    x = np.arange(len(bl))
    ax.bar(x - .19, a, .36, label="作为主瓶颈", color=C1, zorder=3)
    ax.bar(x + .19, b, .36, label="作为次瓶颈", color=C2, alpha=.85, zorder=3)
    for i, v in enumerate(a):
        if v: ax.text(i - .19, v + .1, str(v), ha="center", fontsize=8)
    for i, v in enumerate(b):
        if v: ax.text(i + .19, v + .1, str(v), ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(bl, fontsize=9)
    ax.set_ylabel("领域数"); ax.set_ylim(0, 7.2); ax.legend(fontsize=8, frameon=False)
    ax.set_title("图 2　协调与延迟是主瓶颈，预算是「次瓶颈的常客、主瓶颈的陌生人」", fontsize=9.4, loc="left")
    save(fig, "fig02_bottleneck.png")


def fig03():
    M = np.array([[1 if a in r["q2l"] else 0 for a in ACT] for r in ROWS])
    fig, ax = plt.subplots(figsize=(4.6, 6.4))
    ax.imshow(M, cmap="Blues", vmin=0, vmax=1.35, aspect="auto")
    ax.set_xticks(range(len(ACT))); ax.set_xticklabels(ACT, fontsize=8.6, rotation=35, ha="right")
    ax.set_yticks(range(len(ROWS))); ax.set_yticklabels([r["id"] for r in ROWS], fontsize=6.6)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, "●" if M[i, j] else "", ha="center", va="center", fontsize=6,
                    color="white" if M[i, j] else "#ccc")
    ax.grid(False)
    ax.set_title("图 3　领域 × 置换动作：拆分几乎普遍，合并几乎不用", fontsize=9.2, loc="left")
    save(fig, "fig03_actions.png")


def fig04():
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    bottoms = np.zeros(3)
    colors = [C1, C2, C4, C3]
    for p, c in zip(PRE, colors):
        vals = np.array([S["cross"][(w, p)] for w in "ABC"])
        ax.bar(["A 可写", "B 部分可写", "C 写不出"], vals, .5, bottom=bottoms, label=p,
               color=c, alpha=.9, zorder=3)
        for i, v in enumerate(vals):
            if v >= 1:
                ax.text(i, bottoms[i] + v / 2, str(v), ha="center", va="center",
                        fontsize=8, color="white")
        bottoms += vals
    ax.set_ylabel("领域数"); ax.set_ylim(0, 14.6)
    ax.legend(fontsize=8, frameon=False, ncol=4, loc="upper center",
              bbox_to_anchor=(.5, -.10))
    ax.set_title("图 4　可写性 × 在场性：越写不出，代价越落在看不见的人身上", fontsize=9.4, loc="left")
    save(fig, "fig04_cross.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    xs = np.arange(len(ROWS))
    ys = [1 if r["swap"] == "Y" else 0 for r in ROWS]
    ax.scatter(xs, ys, s=42, c=[C3 if y else C1 for y in ys], zorder=3, edgecolor="white", lw=.6)
    for i, r in enumerate(ROWS):
        if r["swap"] == "Y":
            ax.annotate(r["domain"], (i, 1), textcoords="offset points", xytext=(0, 7),
                        ha="center", fontsize=7, color=C3)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["结论不变", "结论改变"], fontsize=8.6)
    ax.set_xticks(xs); ax.set_xticklabels([r["id"] for r in ROWS], fontsize=6.4, rotation=90)
    ax.set_ylim(-.4, 1.5)
    ax.set_title("图 5　主次瓶颈互换：5/20 的领域会改判（判据稳健度 75%）", fontsize=9.4, loc="left")
    save(fig, "fig05_swap.png")


def fig06():
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    cls = [("一类：以「正确」为主\n诉讼·临床·风控·保险", 1.35, 4.0, "#dbe7f1", "D02 D03 D06 D18"),
           ("二类：以「协调」为主\n供应链·规划·后勤·婚礼·架构", 4.05, 4.0, "#e6ecdf", "D04 D05 D10 D12 D15"),
           ("三类：以「延迟」为主\n分诊·新闻·应急·烹饪·面试", 6.75, 4.0, "#f2e6e6", "D01 D07 D20 D16 D17"),
           ("四类：以「容量」为主\n农业·策展·训练", 1.35, 1.5, "#f7efe2", "D09 D11 D13"),
           ("五类：以「注意力」为主\n分类·教材（+ 外交：以信任为主）", 5.4, 1.5, "#f2efe6", "D14 D19 D08")]
    for t, x, y, c, ids in cls:
        w = 3.0 if y > 3 else 3.6
        ax.add_patch(FancyBboxPatch((x, y), w, 1.5, boxstyle="round,pad=0.06,rounding_size=0.1",
                                    fc=c, ec="#666", lw=.9))
        ax.text(x + w / 2, y + 1.02, t, ha="center", va="center", fontsize=8.2, linespacing=1.6)
        ax.text(x + w / 2, y + .38, ids, ha="center", va="center", fontsize=6.8, color="#555")
    ax.text(.2, 5.25, "图 6　二十个领域压成五类：瓶颈决定类别，类别决定置换集的形状", fontsize=9.4, fontweight="bold")
    save(fig, "fig06_typology.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.0); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.4):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.4, 4.4, 2.6, .95, "看见\nQ1 划线", "#dbe7f1")
    box(3.7, 4.4, 2.6, .95, "选择\nQ2 让出", "#e6ecdf")
    box(7.0, 4.4, 2.6, .95, "讲述\nQ3 置信度 / Q4 代价", "#f2e6e6")
    box(.4, 1.5, 2.6, .95, "记住\n预计算·复制", "#f7efe2")
    box(3.7, 1.5, 2.6, .95, "跟上\n延迟·时钟", "#f7efe2")
    box(7.0, 1.5, 2.6, .95, "临界\n写不出的地方", "#f2efe6")
    ax.add_patch(FancyArrowPatch((1.7, 4.35), (1.7, 2.5), arrowstyle="-|>", mutation_scale=10, lw=1, color="#888"))
    ax.add_patch(FancyArrowPatch((5.0, 4.35), (5.0, 2.5), arrowstyle="-|>", mutation_scale=10, lw=1, color="#888"))
    ax.add_patch(FancyArrowPatch((8.3, 4.35), (8.3, 2.5), arrowstyle="-|>", mutation_scale=10, lw=1, color="#888"))
    ax.text(.2, 5.7, "图 7　四问的接口：上排是「判据」，下排是「它凭什么成立」", fontsize=9.6, fontweight="bold")
    ax.text(.2, .6, "注：Q4 是《讲述》的扩展——置信度分配之外，再加一列代价分配；不新增核心。",
            fontsize=7, color="#555")
    save(fig, "fig07_interface.png")


def fig08():
    props = [("T1", "四问可判（20 领域无新增类别）", 1.0),
             ("T2", "协调与延迟是主瓶颈", 1.0),
             ("T3", "预算从不作主瓶颈", 1.0),
             ("T4", "拆分最通用、合并最少用", 1.0),
             ("T5", "可写性越低，代价越不可见", 1.0),
             ("T6", "主次互换后判据仍成立（75%）", 0.75),
             ("T7", "Q4 可独立于 Q3 判定", 0.5),
             ("T8", "四问是六核心的操作化", 0.5),
             ("T9", "二十领域可穷举（无遗漏类型）", 0.0)]
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ys = np.arange(len(props))[::-1]
    cols = {1.0: C1, .75: C2, .5: C4, 0.0: C3}
    ax.barh(ys, [p[2] for p in props], .55, color=[cols[p[2]] for p in props], zorder=3)
    for y, (i, t, v) in zip(ys, props):
        ax.text(-.02, y, f"{i} {t}", ha="right", va="center", fontsize=7.6)
        ax.text(max(v, 0) + .02, y, {1.0: "支持", .75: "部分", .5: "待检验", 0.0: "撤回"}[v],
                va="center", fontsize=7.4, color=cols[v])
    ax.set_yticks([]); ax.set_xlim(0, 1.28); ax.set_xticks([0, .5, 1.0])
    ax.set_xticklabels(["0", "0.5", "1"], fontsize=8)
    ax.set_title("图 8　自证：九条命题的最终状态（一条撤回）", fontsize=9.4, loc="left")
    save(fig, "fig08_self.png")


def main():
    print("tables...")
    tables()
    print("figures...")
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08):
        f()


if __name__ == "__main__":
    main()

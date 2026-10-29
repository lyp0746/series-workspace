# -*- coding: utf-8 -*-
"""《同构的强度》——8 图 + 7 表；数据来自 data/motifs.py（单一来源）。"""
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
from data import motifs as M

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4, C5 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a", "#4f7a4f"

ROWS = M.rows()
S = M.stats()
STR = M.STRENGTHS
LAY = M.LAYERS
GRP = M.GROUPS


def save(fig, name):
    fig.savefig(ROOT / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


def tables():
    # 表 1：强度阶梯
    out = ["| 强度 | 定义 | 判据（答不出即降一档） | 条数 |", "|---|---|---|---|"]
    for s, d, c in [
        ("**严格同构**", "存在互逆的两个映射，复合回到单位", "能否写出 f 与 g，并验证 g∘f=id、f∘g=id？", ),
        ("**伴随／对偶**", "两个方向互相决定，但不必互逆", "能否说出「一边的变化由另一边的什么决定」？"),
        ("**函子式类同构**", "保持复合与单位，但丢掉了至少一项结构", "能否说出丢了哪一项，且举出一个它在 B 领域起作用的例子？"),
        ("**只是比喻**", "只在字面上相似，复合律不同或不成立", "能否举出一个「照它操作就会错」的动作？"),
    ]:
        n = S["strength"].get(s.strip("*").replace("／对偶", "").replace("/对偶", ""), None)
        if n is None:
            key = {"严格同构": "严格", "伴随/对偶": "伴随", "伴随／对偶": "伴随",
                   "函子式类同构": "函子", "只是比喻": "比喻"}[s.strip("*")]
            n = S["strength"].get(key, 0)
        out.append(f"| {s} | {d} | {c} | {n} |")
    (ROOT / "data" / "table_strength.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2：四十条总表
    out = ["| 编号 | 母题组 | 声明 | B 领域 | 对象 | 态射 | 复合律 | 强度 | 断裂层 | 负迁移 | 等级 |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["group"]} | {r["name"]} | {r["domain"]} | {r["obj"]} | {r["mor"]} | '
                   f'{r["comp"]} | {r["strength"]} | {r["layer"]} | {r["trans"]} | {r["grade"]} |')
    (ROOT / "data" / "table_motifs.md").write_text("\n".join(out), encoding="utf-8")
    with open(ROOT / "motifs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=M.FIELDS)
        w.writeheader(); w.writerows(ROWS)

    # 表 3：母题组 × 强度
    out = ["| 母题组 | 严格 | 伴随 | 函子 | 比喻 | 合计 | 降级率（比喻/合计） |", "|---|---|---|---|---|---|---|"]
    for g in GRP:
        v = [S["strength"].get("严格", 0)]
        row = [sum(1 for r in ROWS if r["group"] == g and r["strength"] == s) for s in STR]
        row = [sum(1 for r in ROWS if r["group"] == g and r["strength"] == s) for s in ["严格", "伴随", "函子", "比喻"]]
        tot = sum(row)
        out.append(f"| {g} | " + " | ".join(str(x) if x else "·" for x in row) +
                   f" | {tot} | {row[3]}/{tot} |")
    tot = [sum(1 for r in ROWS if r["strength"] == s) for s in ["严格", "伴随", "函子", "比喻"]]
    out.append("| **合计** | " + " | ".join(f"**{x}**" for x in tot) + f" | **{sum(tot)}** | {tot[3]}/{sum(tot)} |")
    (ROOT / "data" / "table_group_strength.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4：强度 × 断裂层
    out = ["| 强度 | 对象 | 态射 | 复合 | 等价 | 合计 |", "|---|---|---|---|---|---|"]
    for s in STR:
        row = [S["layer_by_strength"][s].get(l, 0) for l in LAY]
        out.append(f"| {s} | " + " | ".join(str(x) if x else "·" for x in row) + f" | {sum(row)} |")
    tot = [sum(S["layer_by_strength"][s].get(l, 0) for s in STR) for l in LAY]
    out.append("| **合计** | " + " | ".join(f"**{x}**" for x in tot) + f" | **{sum(tot)}** |")
    (ROOT / "data" / "table_layer.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5：强度 × 负迁移
    out = ["| 强度 | 负迁移（Y） | 条数 | 负迁移率 |", "|---|---|---|---|"]
    for s in ["严格", "伴随", "函子", "比喻"]:
        y, n = S["trans_by_strength"][s]
        out.append(f"| {s} | {y} | {n} | {y / n * 100:.0f}% |")
    (ROOT / "data" / "table_trans.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6：六核心对照
    out = ["| 核心 | 专著 | 在本文中的位置 | 关系 | 等级 |", "|---|---|---|---|---|"]
    for r in [("**看见**（主）", "《区分的语法》", "找同构＝跨领域划线：把两个东西划进同一个结构", "**扩展**：从「域内划线」到「跨域拉平」", "乙／B"),
              ("**记住**（主）", "《遗忘的边界》", "母题＝跨领域反复出现的压缩模式；压缩必有损", "**检验**：可分「可回溯」与「不可回溯」两类损失", "乙／B"),
              ("**讲述**（主）", "《诠释的权衡》", "同构强度＝给一条类比分配置信度", "**扩展**：四级强度阶梯可作为置信度刻度", "乙／B"),
              ("**跟上**", "《错位的时间》", "复合律检验＝时间结构上的匹配", "借用机制", "丙／C"),
              ("**选择**", "《选择的代价》", "每一次同构都是「保哪一项、让出哪一项」", "借用语言", "丙／C"),
              ("**临界**", "《涌现的临界》", "断裂点＝同构失效的门槛", "**检验**：断裂层分布支持「门槛」而非「连续退化」", "乙／B")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT / "data" / "table_six.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7：负迁移清单
    out = ["| 编号 | 声明 | B 领域 | 强度 | 照它操作会怎样错 |", "|---|---|---|---|---|"]
    for r in ROWS:
        if r["trans"] == "Y":
            out.append(f'| {r["id"]} | {r["name"]} | {r["domain"]} | {r["strength"]} | {r["probe"]} |')
    (ROOT / "data" / "table_negative.md").write_text("\n".join(out), encoding="utf-8")
    print("  tables: 7")


def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.55)

    box(.3, 4.6, 2.6, 1.0, "一个领域\n（现场、细节、例外）", "#f2efe6")
    box(3.6, 4.6, 2.8, 1.0, "四问压缩\n瓶颈·置换·可写·承担", "#dbe7f1")
    box(7.1, 4.6, 2.6, 1.0, "母题压缩\n对偶·泛性质·不变量", "#e6ecdf")
    box(3.6, 2.2, 2.8, 1.2, "可回溯的损失\n（留着回到案例的钩子：\nQ4 承担者、实例栏）", "#f7efe2", 7.8)
    box(7.1, 2.2, 2.6, 1.2, "不可回溯的损失\n（烧掉的细节：\n节奏、例外、制度）", "#f2e6e6", 7.8)
    ax.add_patch(FancyArrowPatch((2.95, 5.1), (3.55, 5.1), arrowstyle="-|>", mutation_scale=11, lw=1, color="#666"))
    ax.add_patch(FancyArrowPatch((6.45, 5.1), (7.05, 5.1), arrowstyle="-|>", mutation_scale=11, lw=1, color="#666"))
    ax.add_patch(FancyArrowPatch((5.0, 4.55), (5.0, 3.45), arrowstyle="-|>", mutation_scale=11, lw=1, color="#666"))
    ax.add_patch(FancyArrowPatch((8.4, 4.55), (8.4, 3.45), arrowstyle="-|>", mutation_scale=11, lw=1, color="#666"))
    ax.add_patch(FancyArrowPatch((5.0, 2.15), (6.9, 1.6), arrowstyle="-|>", mutation_scale=9, lw=.9, color="#999", ls="--"))
    ax.text(5.0, 1.35, "压缩越狠，右边越大、左边越小", fontsize=7.4, color="#666", ha="center")
    ax.text(.2, 5.95, "图 1　两种压缩，两级损失：可回溯的与不可回溯的", fontsize=9.8, fontweight="bold")
    ax.text(.2, .3, "注：母题的损失一般不可回溯——它换掉的是「对象是什么」，而不只是「细节多细」。",
            fontsize=7, color="#555")
    save(fig, "fig01_compress.png")


def fig02():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9),
                                 gridspec_kw={"width_ratios": [1.1, 1]})
    order = ["严格", "伴随", "函子", "比喻"]
    vals = [S["strength"][s] for s in order]
    a1.bar(order, vals, .55, color=[C1, C5, C2, C4], zorder=3)
    for i, v in enumerate(vals):
        a1.text(i, v + .2, str(v), ha="center", fontsize=9)
    a1.set_ylim(0, 15); a1.set_ylabel("条数")
    a1.set_title("(a) 强度分布：严格与函子各 12 条", fontsize=8.8, loc="left")

    bottom = np.zeros(len(GRP))
    for s, c in zip(order, [C1, C5, C2, C4]):
        v = np.array([sum(1 for r in ROWS if r["group"] == g and r["strength"] == s) for g in GRP])
        a2.bar(GRP, v, .55, bottom=bottom, label=s, color=c, zorder=3)
        bottom += v
    a2.set_ylim(0, 12); a2.legend(fontsize=7, frameon=False, ncol=2, loc="upper right")
    a2.set_title("(b) 母题组 × 强度：泛性质降级最多", fontsize=8.8, loc="left")
    fig.suptitle("图 2　四十条声明只落在四个价位上", fontsize=9.6, x=.02, ha="left", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, .93])
    save(fig, "fig02_strength.png")


def fig03():
    Mat = np.array([[sum(1 for r in ROWS if r["group"] == g and r["layer"] == l) for l in LAY] for g in GRP])
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    ax.imshow(Mat, cmap="Blues")
    ax.set_xticks(range(len(LAY))); ax.set_xticklabels(LAY, fontsize=9)
    ax.set_yticks(range(len(GRP))); ax.set_yticklabels(GRP, fontsize=9)
    for i in range(Mat.shape[0]):
        for j in range(Mat.shape[1]):
            if Mat[i, j]:
                ax.text(j, i, int(Mat[i, j]), ha="center", va="center", fontsize=9,
                        color="white" if Mat[i, j] >= 4 else "#222")
    ax.grid(False)
    ax.set_title("图 3　母题 × 断裂层：断裂集中在复合与等价", fontsize=9.2, loc="left")
    save(fig, "fig03_matrix.png")


def fig04():
    order = ["严格", "伴随", "函子", "比喻"]
    ys = [S["trans_by_strength"][s][0] / S["trans_by_strength"][s][1] * 100 for s in order]
    ns = [S["trans_by_strength"][s][1] for s in order]
    fig, ax = plt.subplots(figsize=(6.0, 2.9))
    ax.bar(order, ys, .5, color=[C1, C5, C2, C4], zorder=3)
    for i, (y, n) in enumerate(zip(ys, ns)):
        ax.text(i, y + 3, f"{y:.0f}%（{S['trans_by_strength'][order[i]][0]}/{n}）", ha="center", fontsize=8.6)
    ax.set_ylim(0, 100); ax.set_ylabel("负迁移率 %")
    ax.axhline(50, color="#bbb", ls=":", lw=.8)
    ax.set_title("图 4　最危险的不是比喻，是「像证明」的那两档", fontsize=9.4, loc="left")
    save(fig, "fig04_trans.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.0, 2.7))
    x = np.arange(len(LAY))
    ours = [S["layer"][l] for l in LAY]
    ax.bar(x - .18, ours, .34, label="本文：断裂实际发生在", color=C1, zorder=3)
    debate = [4, 8, 16, 12]  # 争论停在哪一层（示意，见 8.5）
    ax.bar(x + .18, debate, .34, label="争论通常停在哪层（示意）", color=C4, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(LAY, fontsize=9)
    ax.set_ylabel("条数"); ax.legend(fontsize=7.6, frameon=False)
    for i, v in enumerate(ours):
        ax.text(i - .18, v + .3, str(v), ha="center", fontsize=8)
    ax.set_title("图 5　断裂多在复合层，争论多在对象层", fontsize=9.4, loc="left")
    save(fig, "fig05_layer.png")


def fig06():
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    ax.plot([.6, 9.4], [1.2, 5.2], color="#c9c0ad", lw=2, zorder=1)
    pts = [("严格同构", "有 f 与 g，且 g(f(x))=x", 1.5, 1.55, C1),
           ("伴随／对偶", "两边互相决定，不必互逆", 3.9, 2.75, C5),
           ("函子式类同构", "保复合，丢一项结构", 6.3, 3.95, C2),
           ("只是比喻", "只像，复合律不同", 8.7, 5.15, C3)]
    for t, sub, x, y, c in pts:
        ax.scatter([x], [y], s=90, color=c, zorder=3, edgecolor="white", lw=1)
        ax.text(x, y + .45, t, ha="center", fontsize=9.2, fontweight="bold", color=c)
        ax.text(x, y - .55, sub, ha="center", fontsize=7.2, color="#555")
    ax.annotate("", xy=(9.2, 5.55), xytext=(1.1, 1.5),
                arrowprops=dict(arrowstyle="-|>", color="#999", lw=1.2, ls="--"))
    ax.text(2.4, 4.9, "强度下降方向：\n每降一档，必须多交代一件事",
            fontsize=7.6, color="#666", ha="left")
    ax.text(.2, 6.2, "图 6　强度阶梯：每一档的判据是不同的问句", fontsize=9.8, fontweight="bold")
    save(fig, "fig06_ladder.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.2, ec="#666", ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=.9, ls=ls))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.3, 1.3, 2.2, 1.1, "工作记忆\n状态机 + 最近 N 步", "#f2efe6", 7.6)
    box(2.8, 1.3, 2.2, 1.1, "程序性记忆\n技能（四问 Q3）", "#dbe7f1", 7.6)
    box(5.3, 1.3, 2.2, 1.1, "语义记忆\n领域知识（母题）", "#e6ecdf", 7.6)
    box(7.8, 1.3, 1.9, 1.1, "情景记忆\n偏好/失败三栏", "#f7efe2", 7.6)
    box(2.8, 4.2, 4.7, 1.1, "检索层：情境 → 母题 → 技能\n（本文给不出，只能指出它必须存在）",
        "#fff", 8.2, C3, "--")
    for x in (1.4, 3.9, 6.4, 8.75):
        ax.add_patch(FancyArrowPatch((x, 2.45), (x, 4.15), arrowstyle="-|>", mutation_scale=10,
                                     lw=.9, color="#999", ls=":"))
    ax.text(.2, 5.9, "图 7　三层记忆 + 两层抽象：缺的是检索层", fontsize=9.8, fontweight="bold")
    ax.text(.2, .55, "注：四问管程序性记忆的压缩，母题管语义记忆的组织；"
                     "「该用哪个抽象」不在这两层里，它在检索层。", fontsize=7, color="#555")
    save(fig, "fig07_memory.png")


def fig08():
    order = ["严格", "伴随", "函子", "比喻"]
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    x = np.arange(len(order))
    top = [S["strength"][s] for s in order]
    keep = [S["trans_by_strength"][s][1] - S["trans_by_strength"][s][0] for s in order]
    drop = [S["trans_by_strength"][s][0] for s in order]
    ax.bar(x, keep, .5, label="过探针（原档保留）", color=C1, zorder=3)
    ax.bar(x, drop, .5, bottom=keep, label="未过探针（负迁移风险）", color=C3, zorder=3)
    for i in range(len(order)):
        ax.text(i, keep[i] + drop[i] + .3, f"{keep[i]}+{drop[i]}", ha="center", fontsize=8.2)
    ax.set_xticks(x); ax.set_xticklabels(order, fontsize=9)
    ax.set_ylabel("条数"); ax.legend(fontsize=7.6, frameon=False, ncol=2)
    ax.set_title("图 8　自证：四十条声明过探针后的去向", fontsize=9.4, loc="left")
    save(fig, "fig08_self.png")


def main():
    print("tables...")
    tables()
    print("figures...")
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08):
        f()


if __name__ == "__main__":
    main()

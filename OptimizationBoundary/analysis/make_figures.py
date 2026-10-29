# -*- coding: utf-8 -*-
"""7 图 + 6 表；数据来自 data/opt_cases.py。"""
import csv, pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import opt_cases as O

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]; break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200, "font.size": 9,
                     "axes.titlesize": 9.6, "axes.labelsize": 9, "axes.edgecolor": "#444",
                     "axes.grid": True, "grid.color": "#e8e8e8", "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a"
ROWS = O.rows(); S = O.stats()
PRE = ["目标", "空间", "预算", "停止"]


def tables():
    out = ["| 前提 | 由哪个核心提供 | 缺了会怎样 | 本文案例数 |","|---|---|---|---|"]
    for name, core, fail, key in [("目标函数","讲述","把可计算指标当目标","目标"),
                                  ("搜索空间","看见","优化一个不存在的解","空间"),
                                  ("预算／时钟","记住、跟上","无限投入、错过窗口","预算"),
                                  ("停止规则","临界","局部最优当全局最优","停止")]:
        out.append(f"| **{name}** | {core} | {fail} | {S['by_premise'].get(key,0)} |")
    (ROOT/"data"/"table_premises.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 编号 | 案例 | 领域 | 被违反的前提 | 越界机制 | 后果 | 强度 | 等级 |","|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["case"]} | {r["domain"]} | {r["premise"]} | {r["mechanism"]} | {r["outcome"]} | {r["severity"]} | {r["grade"]} |')
    (ROOT/"data"/"table_cases.md").write_text("\n".join(out), encoding="utf-8")
    with open(ROOT/"cases.csv","w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=O.FIELDS); w.writeheader(); w.writerows(ROWS)

    outs = ["锁定","指标失真","反噬","无效"]
    out = ["| 前提 | 锁定 | 指标失真 | 反噬 | 无效 | 合计 |","|---|---|---|---|---|---|"]
    for p in PRE:
        row = [sum(1 for r in ROWS if r["premise"]==p and r["outcome"]==o) for o in outs]
        out.append(f"| {p} | " + " | ".join(str(v) if v else "·" for v in row) + f" | {sum(row)} |")
    tot = [sum(1 for r in ROWS if r["outcome"]==o) for o in outs]
    out.append("| **合计** | " + " | ".join(f"**{v}**" for v in tot) + f" | **{sum(tot)}** |")
    (ROOT/"data"/"table_premise_outcome.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 越界类型 | 检查项（一句话） | 本文实例 |","|---|---|---|"]
    for a,b,c in [("目标函数越界","这个指标是谁定的？换一个指标，行为会怎样变？","O05 O06 O07 O08 O09 O14 O15"),
                  ("搜索空间越界","解在不在可行域内？边界是由谁划的？","O01 O02 O03 O04 O13"),
                  ("预算越界","预算是硬的还是可以追加？追加的代价由谁付？","O19 O20"),
                  ("停止规则越界","达到什么条件就停？谁有权喊停？","O10 O11 O12 O16 O17")]:
        out.append(f"| {a} | {b} | {c} |")
    (ROOT/"data"/"table_failmodes.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 核心 | 专著 | 在优化中的位置 | 关系 | 等级 |","|---|---|---|---|---|"]
    for r in [("**讲述**（主）","《诠释的权衡》","给目标函数分配置信度；决定「哪个指标值得追」","**检验**：无讲述则目标失真","乙／B"),
              ("**临界**（主）","《涌现的临界》","提供停止规则；判定「何时该停」","**检验**：三标记在多数案例上不可判","乙／B"),
              ("看见","《区分的语法》","划定搜索空间（可行域）","借用语言","丙／C"),
              ("记住","《遗忘的边界》","预算中的「容量」一侧；局部最优的锁定","借用机制","丙／C"),
              ("跟上","《错位的时间》","预算中的「时钟」一侧；优化窗口","借用方向","丙／C"),
              ("选择","《选择的代价》","与优化的分工：取舍 vs 调参","**划界**（本文主要工作）","乙／B")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT/"data"/"table_six.md").write_text("\n".join(out), encoding="utf-8")


def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 4.2)); ax.set_xlim(0,10); ax.set_ylim(0,6.2); ax.axis("off")
    box = lambda x,y,w,h,t,fc,fs=8.4: (ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05,rounding_size=0.08",fc=fc,ec="#666",lw=.9)),
                                       ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,linespacing=1.5))
    box(4.0,2.7,2.4,1.1,"优化\n搜索—评估—停止","#f2efe6")
    box(4.0,4.8,2.4,.85,"目标函数\n← 讲述","#dbe7f1")
    box(.4,2.7,2.5,.95,"搜索空间\n← 看见","#e6ecdf")
    box(7.4,2.7,2.3,.95,"预算／时钟\n← 记住、跟上","#f7efe2")
    box(4.0,.6,2.4,.85,"停止规则\n← 临界","#f2e6e6")
    for a,b in [((5.2,4.8),(5.2,3.82)),((2.9,3.17),(3.98,3.17)),((7.4,3.17),(6.42,3.17)),((5.2,2.68),(5.2,1.47))]:
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=11,lw=1,color="#666"))
    ax.text(.2,5.95,"图 1　优化不是第七个核心，而是横切四个核心的循环",fontsize=9.8,fontweight="bold")
    ax.text(.2,.15,"注：四个前提各由一个核心提供；缺任一项，优化都会越界（表 1）。",fontsize=7,color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig01_loop.png",bbox_inches="tight"); plt.close(fig)


def fig02():
    ps = PRE; vals = [S["by_premise"].get(p,0) for p in ps]
    fig, ax = plt.subplots(figsize=(6.2,2.9))
    ax.bar(ps, vals, color=[C1,C2,C3,C4], width=.55, zorder=3)
    for i,v in enumerate(vals): ax.text(i, v+.12, str(v), ha="center", fontsize=9)
    ax.set_ylabel("案例数"); ax.set_ylim(0, max(vals)+1.5)
    ax.set_title("图 2　二十个越界案例的分布：目标函数最多，预算最少", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig02_premise.png",bbox_inches="tight"); plt.close(fig)


def fig03():
    outs = ["锁定","指标失真","反噬","无效"]
    M = np.array([[sum(1 for r in ROWS if r["premise"]==p and r["outcome"]==o) for o in outs] for p in PRE])
    fig, ax = plt.subplots(figsize=(5.8,2.9))
    ax.imshow(M, cmap="Reds")
    ax.set_xticks(range(len(outs))); ax.set_xticklabels(outs, fontsize=8.6)
    ax.set_yticks(range(len(PRE))); ax.set_yticklabels(PRE, fontsize=9)
    for i in range(len(PRE)):
        for j in range(len(outs)):
            if M[i,j]: ax.text(j,i,int(M[i,j]),ha="center",va="center",fontsize=9,
                               color="white" if M[i,j]>=3 else "#222")
    ax.grid(False); ax.set_title("图 3　前提 × 后果：目标越界多致指标失真，停止越界多致反噬", fontsize=9.2, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig03_matrix.png",bbox_inches="tight"); plt.close(fig)


def fig04():
    sev = {"重":3,"中":2,"轻":1}
    fig, ax = plt.subplots(figsize=(6.4,3.0))
    for i,p in enumerate(PRE):
        ys = [sev.get(r["severity"],2) for r in ROWS if r["premise"]==p and r["severity"] in sev]
        xs = [i + (j-(len(ys)-1)/2)*.06 for j in range(len(ys))]
        ax.scatter(xs, ys, s=30, color=[C1,C2,C3,C4][i], alpha=.85, zorder=3, edgecolor="white", lw=.5)
    ax.set_xticks(range(4)); ax.set_xticklabels(PRE, fontsize=9)
    ax.set_yticks([1,2,3]); ax.set_yticklabels(["轻","中","重"], fontsize=8.6)
    ax.set_ylabel("后果强度")
    ax.set_title("图 4　后果强度与前提：停止规则越界的后果最重", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig04_severity.png",bbox_inches="tight"); plt.close(fig)


def fig05():
    fig, ax = plt.subplots(figsize=(6.8,3.4)); ax.set_xlim(0,10); ax.set_ylim(0,4.6); ax.axis("off")
    ax.text(.2,4.3,"图 5　优化的四个越界出口（判据树）",fontsize=9.6,fontweight="bold")
    ax.add_patch(FancyBboxPatch((3.6,3.4),2.8,.6,boxstyle="round,pad=.04",fc="#dbe7f1",ec="#666"))
    ax.text(5,3.7,"开始优化",ha="center",va="center",fontsize=9)
    labels = ["目标由谁定？","解在可行域内吗？","预算硬吗？","什么时候停？"]
    outs = ["目标失真","锁定／无效","无限投入","反噬"]
    for i,(l,o) in enumerate(zip(labels,outs)):
        x = .3 + i*2.45
        ax.add_patch(FancyBboxPatch((x,2.0),2.2,.75,boxstyle="round,pad=.04",fc="#f7f7f4",ec="#bbb"))
        ax.text(x+1.1,2.38,l,ha="center",va="center",fontsize=8)
        ax.add_patch(FancyBboxPatch((x,1.0),2.2,.55,boxstyle="round,pad=.04",fc="#f2e6e6",ec="#bbb"))
        ax.text(x+1.1,1.28,o,ha="center",va="center",fontsize=8.4,color="#a8322d")
        ax.annotate("",xy=(x+1.1,2.02),xytext=(x+1.1,1.58),arrowprops=dict(arrowstyle="-|>",lw=.8,color="#777"))
        ax.annotate("",xy=(x+1.1,3.0),xytext=(x+1.1,3.38),arrowprops=dict(arrowstyle="-|>",lw=.8,color="#777"))
    ax.text(.2,.2,"判据：任何一项答不出，优化就已越界；四项都答得出，才谈得上调参。",fontsize=7.4,color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig05_tree.png",bbox_inches="tight"); plt.close(fig)


def fig06():
    fig, ax = plt.subplots(figsize=(6.8,3.2))
    cores = ["讲述","看见","记住","跟上","临界","选择"]
    vals  = [7,5,2,2,5,0]
    ax.barh(cores, vals, color=[C1,C2,C3,C4,C1,"#cccccc"], zorder=3)
    for i,v in enumerate(vals): ax.text(v+.1, i, str(v) if v else "划界", va="center", fontsize=8.4)
    ax.set_xlabel("对应案例数"); ax.invert_yaxis()
    ax.set_title("图 6　与六核心的接口：「选择」在优化里没有位置（它是另一层）", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig06_interface.png",bbox_inches="tight"); plt.close(fig)


def fig07():
    sts = ["成立","支持","部分","待检验","开放","证伪","撤回"]
    vals = [1,2,1,2,1,0,0]
    fig, ax = plt.subplots(figsize=(6.2,2.7))
    ax.bar(sts, vals, color=[C1,C1,C2,C4,C4,C3,"#6b2b26"], zorder=3)
    for i,v in enumerate(vals): ax.text(i, v+.08, str(v) if v else "0", ha="center", fontsize=8.6)
    ax.set_ylim(0,3); ax.set_ylabel("命题数")
    ax.set_title("图 7　本文自评：七条命题中两条支持、两条待检验、一条开放", fontsize=9.2, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig07_self.png",bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    tables(); fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07()
    print("figs:", sorted(p.name for p in ROOT.glob("fig0*.png")))
    print("stats:", S["n"], dict(S["by_premise"]))

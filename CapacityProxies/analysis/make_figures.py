# -*- coding: utf-8 -*-
"""7 图 + 6 表；数据来自 data/proxies.py。"""
import csv, pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import proxies as P

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]; break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200, "font.size": 9,
                     "axes.titlesize": 9.6, "axes.labelsize": 9, "axes.edgecolor": "#444",
                     "axes.grid": True, "grid.color": "#e8e8e8", "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3 = "#2f6f9f", "#b3701f", "#a8322d"


def tables():
    out = ["| 代理 | 容量（分子） | 压缩（分母或对照） | 遗忘（结果） | 数据来源 |","|---|---|---|---|---|"]
    for r in [("分期槽位","顶层边界数（1—10）","通货门占比","来源不再出现的门","分期篇 252 条边界"),
              ("编码槽位","驿铺条目数（13—44）","并镇与撤县","地名保留率","驿道篇六县"),
              ("标签槽位","日均新建量（134—1110）","星标门槛","合格率","生态篇四期")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT/"data"/"table_defs.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 槽位数 | 来源数 | 通货门占比（中位） |","|---|---|---|"]
    for lo,hi,n,med in P.SLOT_BINS: out.append(f"| {lo}—{hi} | {n} | {med:.2f} |")
    (ROOT/"data"/"table_bins.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 县 | 驿铺数 | 保留率 | 撤县年数 |","|---|---|---|---|"]
    for c,n,r,a in P.COUNTIES: out.append(f"| {c} | {n} | {r:.1f}% | {a if a is not None else '—'} |")
    (ROOT/"data"/"table_counties.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 期段 | 日均新建 | 合格率 |","|---|---|---|"]
    for p,n,r in P.PERIODS: out.append(f"| {p} | {n:.1f} | {r:.1f}% |")
    (ROOT/"data"/"table_periods.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 代理 | 结论 | 方向 | 统计量 | 备注 |","|---|---|---|---|---|"]
    for a,b,c,r,n in P.CONCLUSIONS: out.append(f"| {a} | {b} | {c} | r={r:.3f} | {n} |")
    (ROOT/"data"/"table_concl.md").write_text("\n".join(out), encoding="utf-8")

    out = ["| 核心 | 专著 | 在本文中的位置 | 关系 | 等级 |","|---|---|---|---|---|"]
    for r in [("**记住**（主）","《遗忘的边界》","容量端的三代理；压缩—遗忘的配对","**检验并修正**：容量≠保护","乙／B"),
              ("看见","《区分的语法》","槽位即划线的产物","借用语言","丙／C"),
              ("跟上","《错位的时间》","撤县年数＝制度时钟；与槽位混淆","借用","丙／C"),
              ("选择","《选择的代价》","槽位与压缩的取舍","借用语言","丙／C"),
              ("讲述","《诠释的权衡》","等级与结论强度的匹配","借用方法","乙／B"),
              ("临界","《涌现的临界》","槽位跃变是否为相变（判不可判）","检验","丙／C")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT/"data"/"table_six.md").write_text("\n".join(out), encoding="utf-8")


def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 3.6)); ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
    for i,(t,c) in enumerate([("容量\n（槽位数）","#dbe7f1"),("压缩\n（并镇／通货门）","#f7efe2"),("遗忘\n（保留率／合格率）","#f2e6e6")]):
        x = 1.2 + i*3.0
        ax.add_patch(FancyBboxPatch((x,2.4),2.4,1.0,boxstyle="round,pad=.05",fc=c,ec="#666"))
        ax.text(x+1.2,2.9,t,ha="center",va="center",fontsize=9,linespacing=1.5)
        if i<2:
            ax.add_patch(FancyArrowPatch((x+2.4,2.9),(x+3.0,2.9),arrowstyle="-|>",mutation_scale=11,lw=1,color="#666"))
    ax.text(1.2,1.85,"分期槽位：顶层边界数 → 通货门占比 → 门不再出现")
    ax.text(1.2,1.35,"编码槽位：驿铺条目数 → 并镇／撤县 → 地名保留率")
    ax.text(1.2,.85,"标签槽位：日均新建量 → 星标门槛 → 合格率")
    ax.text(.3,4.6,"图 1　三个代理共用一条链：容量 → 压缩 → 遗忘",fontsize=9.8,fontweight="bold")
    ax.text(.3,.25,"注：三个代理都不是容量本身，只是它的可见痕迹（正文 2.3）。",fontsize=7,color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig01_chain.png",bbox_inches="tight"); plt.close(fig)


def fig02():
    lo = [b[0] for b in P.SLOT_BINS]; med=[b[3] for b in P.SLOT_BINS]; ns=[b[2] for b in P.SLOT_BINS]
    fig, ax = plt.subplots(figsize=(6.4,3.1))
    ax.plot(range(len(med)), med, "o-", color=C1, lw=1.6, ms=7, zorder=3)
    for i,(m,n) in enumerate(zip(med,ns)):
        ax.text(i, m+.03, f"{m:.2f}\n(n={n})", ha="center", fontsize=7.6, color="#333")
    ax.set_xticks(range(len(med))); ax.set_xticklabels([f"{a}—{b}" for a,b in [(1,2),(3,4),(5,6),(7,20)]], fontsize=8.6)
    ax.set_xlabel("一部来源的顶层边界数（槽位）"); ax.set_ylabel("通货门占比（中位）")
    ax.set_ylim(0,.62)
    ax.set_title("图 2　分期槽位：槽位越多，越少依赖通货门（分箱单调）", fontsize=9.4, loc="left")
    ax.text(.98,.92,f"Pearson r={P.SLOT_R:.2f}（槽位≥2 的 51 部）", transform=ax.transAxes, ha="right", fontsize=7.6, color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig02_slots.png",bbox_inches="tight"); plt.close(fig)


def fig03():
    x=[c[1] for c in P.COUNTIES]; y=[c[2] for c in P.COUNTIES]
    fig, ax = plt.subplots(figsize=(6.4,3.2))
    ax.scatter(x, y, s=46, color=C2, zorder=3, edgecolor="white", lw=.6)
    for c,n,r,a in P.COUNTIES:
        ax.annotate(c, (n,r), xytext=(5,4), textcoords="offset points", fontsize=7.6)
    xs = np.linspace(min(x),max(x),10)
    k,b = np.polyfit(x,y,1); ax.plot(xs, k*xs+b, ls="--", lw=1, color="#999")
    ax.set_xlabel("驿铺条目数（槽位）"); ax.set_ylabel("地名保留率（%）")
    ax.set_title("图 3　编码槽位：槽位越多，保留率越低（与直觉相反）", fontsize=9.4, loc="left")
    ax.text(.98,.92,f"r={P.C_R:.2f}；与撤县年数 r={P.C_AGE_R4:.2f} 混淆", transform=ax.transAxes, ha="right", fontsize=7.4, color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig03_counties.png",bbox_inches="tight"); plt.close(fig)


def fig04():
    x=[p[1] for p in P.PERIODS]; y=[p[2] for p in P.PERIODS]
    fig, ax = plt.subplots(figsize=(6.4,3.0))
    ax.scatter(x, y, s=48, color=C3, zorder=3, edgecolor="white", lw=.6)
    for n,a,b in P.PERIODS: ax.annotate(n,(a,b),xytext=(6,-10),textcoords="offset points",fontsize=7.4)
    ax.set_xscale("log"); ax.set_xlabel("日均新建（对数）"); ax.set_ylabel("合格率（%）")
    ax.set_title("图 4　标签槽位：流入越大，合格率反而越高（n=4）", fontsize=9.4, loc="left")
    ax.text(.98,.92,f"r={P.T_R:.2f}；rho={P.T_RHO:.2f}", transform=ax.transAxes, ha="right", fontsize=7.4, color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig04_periods.png",bbox_inches="tight"); plt.close(fig)


def fig05():
    fig, ax = plt.subplots(figsize=(6.8,2.9))
    names=[c[0] for c in P.CONCLUSIONS]; rs=[c[3] for c in P.CONCLUSIONS]
    cols=[C1 if abs(r)<0.3 else (C2 if r<0 else C3) for r in rs]
    ax.barh(names, rs, color=cols, zorder=3)
    ax.axvline(0, color="#666", lw=.8)
    for i,r in enumerate(rs): ax.text(r + (0.02 if r>=0 else -0.02), i, f"{r:.2f}", va="center",
                                       ha="left" if r>=0 else "right", fontsize=8.4)
    ax.set_xlim(-1,1.1); ax.set_xlabel("相关系数（容量 → 遗忘 的方向）")
    ax.set_title("图 5　三个代理，三种结论：一弱支持、一混淆、一反向", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig05_verdict.png",bbox_inches="tight"); plt.close(fig)


def fig06():
    fig, ax = plt.subplots(figsize=(6.4,3.0))
    cores=["记住","看见","跟上","选择","讲述","临界"]; vals=[3,3,1,1,1,1]
    ax.barh(cores, vals, color=[C1,C1,"#b9c9d6","#b9c9d6","#b9c9d6","#b9c9d6"], zorder=3)
    ax.invert_yaxis(); ax.set_xlabel("被用到的次数")
    ax.set_title("图 6　与六核心的接口：主核是「记住」，其余是配角", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig06_interface.png",bbox_inches="tight"); plt.close(fig)


def fig07():
    sts=["成立","支持","部分","待检验","开放","证伪","撤回"]; vals=[0,1,1,2,2,1,0]
    fig, ax = plt.subplots(figsize=(6.2,2.7))
    ax.bar(sts, vals, color=[C1,C1,C2,"#9a9a9a","#9a9a9a",C3,"#6b2b26"], zorder=3)
    for i,v in enumerate(vals): ax.text(i, v+.06, str(v), ha="center", fontsize=8.6)
    ax.set_ylim(0,3); ax.set_ylabel("命题数")
    ax.set_title("图 7　本文自评：七条命题中一条被证伪、两条开放", fontsize=9.2, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig07_self.png",bbox_inches="tight"); plt.close(fig)


def table_gates():
    out = ["| 名次 | 门（年） | 累计覆盖边界数 |","|---|---|---|"]
    import csv, collections
    R = pathlib.Path(r"D:\0_Article\WorldPeriodization\data\schemes.csv")
    rows = list(csv.DictReader(open(R, encoding="utf-8-sig")))
    def y(r):
        try: return float(r["boundary_year"])
        except: return None
    part = [r for r in rows if r["level"]=="part" and y(r) is not None]
    cl = []
    for r in part:
        yy = y(r); placed = False
        for c in cl:
            if abs(c["y"]-yy) <= 10: c["n"] += 1; placed = True; break
        if not placed: cl.append({"y": yy, "n": 1})
    cl.sort(key=lambda c: -c["n"])
    cum = 0
    for i,c in enumerate(cl[:12], 1):
        cum += c["n"]
        out.append(f"| {i} | {int(c['y'])} | {cum} |")
    (ROOT/"data"/"table_gates.md").write_text("\n".join(out), encoding="utf-8")
    return cl

def fig08():
    import csv
    R = pathlib.Path(r"D:\0_Article\WorldPeriodization\data\schemes.csv")
    rows = list(csv.DictReader(open(R, encoding="utf-8-sig")))
    def y(r):
        try: return float(r["boundary_year"])
        except: return None
    part = [r for r in rows if r["level"]=="part" and y(r) is not None]
    cl = []
    for r in part:
        yy = y(r); placed = False
        for c in cl:
            if abs(c["y"]-yy) <= 10: c["n"] += 1; placed = True; break
        if not placed: cl.append({"y": yy, "n": 1})
    cl.sort(key=lambda c: -c["n"])
    ns = [c["n"] for c in cl]
    cum = np.cumsum(ns) / sum(ns)
    fig, ax = plt.subplots(figsize=(6.4,3.0))
    ax.plot(range(1, len(cum)+1), cum, color=C1, lw=1.6)
    ax.axhline(.734, color=C2, ls="--", lw=1)
    ax.text(len(cum)*.55, .76, "前十门 = 73.4%", fontsize=8, color=C2)
    ax.set_xlabel("门的名次（按出现频次）"); ax.set_ylabel("累计覆盖比例")
    ax.set_title("图 8　门的集中度：十个门覆盖七成边界，余下才是“私有门”", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig08_gates.png",bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    tables(); table_gates(); fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07(); fig08()
    print("figs:", sorted(p.name for p in ROOT.glob("fig0*.png")))

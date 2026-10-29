# -*- coding: utf-8 -*-
"""8 幅图 + 6 张表 + 附录对账表；数据来自 data/ledger.py（单一来源）。"""
import csv, pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "analysis"))
from data import ledger as L

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]; break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C_OK, C_PART, C_FAIL, C_OPEN = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a"
ROWS = L.rows(); S = L.stats()


def table_cards():
    cards = [
      ("看见","划一道线，把什么算作同一类","切线数／等价类数／Jaccard（B）","把切得细当成切得对；把代理量当对象"),
      ("记住","在容量约束下压缩、遗忘、恢复","槽位数／保留率／解码器有无（B）","把容量当存储；把恢复当目的论"),
      ("跟上","多个时钟的错配","τ 比值；窗口宽度（B）","用快变量解释慢变量"),
      ("选择","紧预算下至多取二","保／让的编码；ψ 未测（C）","把调参当取舍；把 C-A-T 当定理"),
      ("讲述","给竞争命题分配置信度","κ、可测性门槛、必要条件（B）","把置信度当证明；把恒等式当证据"),
      ("临界","规则何时换","三标记／序参量／事前窗口（C）","把陡当跃变；把边界当机制"),
    ]
    out = ["| 核心 | 它回答什么 | 可测代理（等级） | 典型失败模式 |","|---|---|---|---|"]
    for a,b,c,d in cards: out.append(f"| **{a}** | {b} | {c} | {d} |")
    (ROOT/"data"/"table_cards.md").write_text("\n".join(out), encoding="utf-8")


def table_scale():
    out = ["| 尺度 | 容量 | 压缩 | 遗忘 | 恢复 | 本文样本中的命题数 |","|---|---|---|---|---|---|"]
    rowsx = [
      ("个体","工作记忆槽位","组块化","痕迹衰退／检索失败","再认、提示",S["by_scale"]["个体"]),
      ("共同体","合法问题名额／可见名额","判为不合法／异常／错类","索引断裂","新解码器",S["by_scale"]["共同体"]),
      ("制度","编制、额数、编码槽位","并镇、裁撤、名分收缩","档案缺失／名分取消","重新设官／复名",S["by_scale"]["制度"]),
      ("谱系","基因库多样性／调控组合容量","选择淘汰、本地适应","漂变、生态位丧失","杂交、水平转移",S["by_scale"]["谱系"]),
      ("命题","可陈述内容的空间","范式压缩","残余不可检","解码器跃迁",S["by_scale"]["命题"]),
    ]
    for a,b,c,d,e,f in rowsx: out.append(f"| {a} | {b} | {c} | {d} | {e} | **{f}** |")
    (ROOT/"data"/"table_scale.md").write_text("\n".join(out), encoding="utf-8")


def table_clock():
    out = ["| 量 | 典型时间尺度 | 可测窗口 | 在哪篇被用到 |","|---|---|---|---|"]
    rowsx = [
      ("τ（授权／决策错配）","10—30 年","需逐年的诏令与人事记录","官制 9 章；驿道 2.3"),
      ("容量衰减（地名／槽位）","10—70 年","需 5 期以上地名录","驿道 4.5、4.10"),
      ("置信度更新（κ／复编）","一次编目周期","需 20% 复编","分期 3.11；术语 附录 C"),
      ("临界慢化（事前信号）","冲击前 4—8 周","需 ≥30 天高频序列","生态 5.2（判不可测）"),
      ("解码器滞后（恢复）","0—5 年","需工具史断代","残余 4.2"),
      ("标签改写（身份）","1—10 周","需贴标时间戳","生态 7.2（缺数据）"),
    ]
    for a,b,c,d in rowsx: out.append(f"| {a} | {b} | {c} | {d} |")
    (ROOT/"data"/"table_clock.md").write_text("\n".join(out), encoding="utf-8")


def table_fail():
    out = ["| 核心 | 典型误读 | 检查项（一句话） | 本系列里出现过的实例 |","|---|---|---|---|"]
    rowsx = [
      ("看见","把切得细当成切得对","换一条切线，结论还成立吗？","分期 W4 分辨率反向"),
      ("记住","把「被想起」当必然","没有解码器时，它凭什么被读出？","残余 C16/C23 永久沉默"),
      ("跟上","用快变量解释慢变量","你的钟与对象的钟同量级吗？","生态 三时钟不同步"),
      ("选择","把调参当取舍","如果预算无限，还需要让出吗？","术语 36% 无让出"),
      ("讲述","把置信度当证明","换一种分级，结论会翻转吗？","残余 R6 打分表误判"),
      ("临界","把边界当机制；把陡当跃变","门槛两侧像两个相吗？","生态 基线非零；分期 门≠机制"),
    ]
    for a,b,c,d in rowsx: out.append(f"| **{a}** | {b} | {c} | {d} |")
    (ROOT/"data"/"table_fail.md").write_text("\n".join(out), encoding="utf-8")


def table_six():
    out = ["| 核心 | 专著 | 本文对应位置 | 用法 | 关系 | 等级 |","|---|---|---|---|---|---|"]
    rowsx = [
      ("**接口**（主）","六本合观","第 2—5 章","不新增核心，只做代理／失败模式／尺度的对账","**新做**","乙／B"),
      ("看见","《区分的语法》","4.1","切线与等价类；三个代理","借用语言","丙／C"),
      ("记住","《遗忘的边界》","4.2","容量—压缩—遗忘与解码器判据","借用并分层","乙／B"),
      ("跟上","《错位的时间》","4.3","多时钟对齐表","借用","丙／C"),
      ("选择","《选择的代价》","4.4","保／让编码与 ψ 缺口","检验（未测 ψ）","丙／C"),
      ("讲述","《诠释的权衡》","4.5","置信度分配与等级审计","检验","乙／B"),
      ("临界","《涌现的临界》","4.6","三标记与「不可判」","检验并修正","乙／B"),
    ]
    for r in rowsx: out.append("| " + " | ".join(r) + " |")
    (ROOT/"data"/"table_six.md").write_text("\n".join(out), encoding="utf-8")


def table_conflicts():
    out = ["| 概念 | 在一篇里的定义 | 在另一篇里的定义 | 冲突点 | 本文的处理 |","|---|---|---|---|---|"]
    rowsx = [
      ("τ","官制：授权包相对执行速度的错配（10—30 年）","生态：出生史与入籍史的双时间轴（周）","量级差三个数量级，不可换算","记为两个 τ；只共用「多时钟」骨架"),
      ("容量","驿道：行政编码表的槽位（县—乡—镇）","残余：一个范式能接住的合法问题名额","一个有刻度，一个无刻度","分别标 B／C，不合并"),
      ("门","分期：分期切线（描述工具）","临界：相变阈值（机制断言）","同名不同物","强制写成「切线」与「门槛」"),
      ("记忆","驿道：地名作为制度记忆","残余：命题在异常清单上的残余","载体不同（名／命题）","按载体分层，不追求统一"),
      ("压缩","术语：组块（信息）","残余：判为不合法（合法性）","对象不同","只在「有损」这一点上共用"),
    ]
    for r in rowsx: out.append("| " + " | ".join(r) + " |")
    (ROOT/"data"/"table_conflicts.md").write_text("\n".join(out), encoding="utf-8")


def table_ledger():
    out = ["| 篇 | 编号 | 命题 | 检验 | 结果 | 状态 | 等级 | 主核 | 尺度 |","|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append("| {paper} | {pid} | {stmt} | {test} | {result} | {status} | {grade} | {core} | {scale} |".format(**r))
    (ROOT/"data"/"table_ledger.md").write_text("\n".join(out), encoding="utf-8")
    with open(ROOT/"ledger.csv","w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ROWS[0].keys())); w.writeheader(); w.writerows(ROWS)


# ---------------- 图 ----------------
def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 4.4)); ax.set_xlim(0,10); ax.set_ylim(0,6.4); ax.axis("off")
    layers = [("起点","看见","对象：划一道线",4.9,"#dbe7f1"),
              ("约束","记住 ／ 跟上","容量与时钟：限定取舍的条件",3.9,"#e6ecdf"),
              ("枢纽","选择","C-A-T：至多取二",2.9,"#f7efe2"),
              ("元层","讲述","置信度分配：给竞争命题定价",1.9,"#f2e6e6"),
              ("门槛","临界","规则何时换",0.9,"#e9e9e9")]
    for i,(tag,k,desc,y,c) in enumerate(layers):
        ax.add_patch(FancyBboxPatch((1.2,y),7.6,.62,boxstyle="round,pad=0.04,rounding_size=0.08",fc=c,ec="#777",lw=.9))
        ax.text(1.45,y+.31,tag,fontsize=8.6,va="center",color="#555")
        ax.text(3.05,y+.31,k,fontsize=9.6,va="center",fontweight="bold")
        ax.text(4.9,y+.31,desc,fontsize=7.8,va="center",color="#333")
        if i<4:
            ax.add_patch(FancyArrowPatch((5,y-.06),(5,y-.32),arrowstyle="-|>",mutation_scale=10,lw=1,color="#666"))
    ax.text(1.2,6.05,"图 1　六核心不是六项并列，而是五层依赖（本图只画依赖，不画覆盖）",fontsize=9.6,fontweight="bold")
    ax.text(1.2,.25,"注：层与层之间是\"换算规则\"而非\"推导\"；边上的规则见正文 4 章与表 2—表 3。",fontsize=7,color="#555")
    fig.tight_layout(); fig.savefig(ROOT/"fig01_layers.png",bbox_inches="tight"); plt.close(fig)


def fig02():
    papers = L.PAPERS; sts = ["成立","支持","部分","待检验","开放","证伪","撤回"]
    cols = {"成立":"#2f6f9f","支持":"#5b8fb9","部分":"#b3701f","待检验":"#c9c9c9","开放":"#8a8a8a","证伪":"#a8322d","撤回":"#6b2b26"}
    fig, ax = plt.subplots(figsize=(7.2,3.4))
    bottom = np.zeros(len(papers))
    for st in sts:
        vals = [sum(1 for r in ROWS if r["paper"]==p and r["status"]==st) for p in papers]
        ax.bar(papers, vals, bottom=bottom, color=cols[st], label=st, width=.62, zorder=3)
        bottom += np.array(vals)
    for i,p in enumerate(papers):
        ax.text(i, bottom[i]+.15, str(int(bottom[i])), ha="center", fontsize=8)
    ax.set_ylabel("命题数"); ax.set_title(f"图 2　48 条登记命题的状态：已关闭 {S['closed']}，未核销 {S['open_']}，撤回 {S['withdrawn']}", fontsize=9.4, loc="left")
    ax.legend(fontsize=7.2, frameon=False, ncol=7, loc="upper center", bbox_to_anchor=(.5,-.12))
    fig.tight_layout(); fig.savefig(ROOT/"fig02_status.png",bbox_inches="tight"); plt.close(fig)


def fig03():
    cores = L.CORES; sts = ["成立","支持","部分","待检验","开放","证伪","撤回"]
    M = np.array([[sum(1 for r in ROWS if r["core"]==c and r["status"]==s) for s in sts] for c in cores])
    fig, ax = plt.subplots(figsize=(6.2,3.2))
    im = ax.imshow(M, cmap="Blues")
    ax.set_xticks(range(len(sts))); ax.set_xticklabels(sts, fontsize=8)
    ax.set_yticks(range(len(cores))); ax.set_yticklabels(cores, fontsize=9)
    for i in range(len(cores)):
        for j in range(len(sts)):
            if M[i,j]: ax.text(j,i,int(M[i,j]),ha="center",va="center",fontsize=8.5,
                               color="white" if M[i,j]>3 else "#222")
    ax.grid(False); ax.set_title("图 3　核心 × 状态：证伪集中在「看见」与「选择」", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig03_core_status.png",bbox_inches="tight"); plt.close(fig)


def fig04():
    cores = L.CORES; scales = ["命题","共同体","制度","个体","谱系"]
    M = np.array([[S["core_scale"][c][s] for s in scales] for c in cores])
    fig, ax = plt.subplots(figsize=(6.2,3.0))
    ax.imshow(M, cmap="Oranges")
    ax.set_xticks(range(len(scales))); ax.set_xticklabels(scales, fontsize=8.6)
    ax.set_yticks(range(len(cores))); ax.set_yticklabels(cores, fontsize=9)
    for i in range(len(cores)):
        for j in range(len(scales)):
            ax.text(j,i,int(M[i,j]) if M[i,j] else "0",ha="center",va="center",fontsize=9,
                    color="white" if M[i,j]>4 else "#222")
    ax.grid(False)
    ax.set_title("图 4　核心 × 尺度：个体层与谱系层是两列空格", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig04_core_scale.png",bbox_inches="tight"); plt.close(fig)


def fig05():
    grades = ["A","B","C"]; sts = ["成立","支持","部分","待检验","开放","证伪","撤回"]
    M = np.array([[sum(1 for r in ROWS if r["grade"]==g and r["status"]==s) for s in sts] for g in grades])
    fig, ax = plt.subplots(figsize=(6.2,2.9))
    x = np.arange(len(sts)); w=.26
    for i,g in enumerate(grades):
        ax.bar(x+(i-1)*w, M[i], w, label=f"{g} 级", zorder=3,
               color={"A":"#1f4e79","B":"#5b8fb9","C":"#b9c9d6"}[g])
    ax.set_xticks(x); ax.set_xticklabels(sts, fontsize=8.2); ax.set_ylabel("命题数")
    ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 5　等级 × 状态：C 级命题占 44%，且多集中在「待检验／开放」", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig05_grade.png",bbox_inches="tight"); plt.close(fig)


def fig06():
    fig, ax = plt.subplots(figsize=(7.0,3.4)); ax.set_xlim(0,10); ax.set_ylim(0,4.4); ax.axis("off")
    ax.text(.2,4.1,"图 6　失败模式矩阵：每个核心的误读都对应一个检查项",fontsize=9.4,fontweight="bold")
    cores = L.CORES
    for i,c in enumerate(cores):
        x = .2 + (i%3)*3.25; y = 2.55 - (i//3)*1.9
        ax.add_patch(FancyBboxPatch((x,y),3.0,1.6,boxstyle="round,pad=0.04,rounding_size=0.06",fc="#f7f7f4",ec="#bbb",lw=.8))
        ax.text(x+.12,y+1.38,c,fontsize=9.2,fontweight="bold")
        txt = {"看见":"把切得细当切得对","记住":"把被想起当必然","跟上":"用快变量解释慢变量",
               "选择":"把调参当取舍","讲述":"把置信度当证明","临界":"把边界当机制"}[c]
        ax.text(x+.12,y+.62,txt,fontsize=7.8,color="#a8322d")
        chk = {"看见":"换条线，结论还成立？","记住":"没有解码器，凭什么读出？","跟上":"两个钟同量级吗？",
               "选择":"预算无限还需要让出？","讲述":"换种分级，结论翻转？","临界":"两侧像两个相吗？"}[c]
        ax.text(x+.12,y+.22,chk,fontsize=7.4,color="#333")
    fig.tight_layout(); fig.savefig(ROOT/"fig06_failmodes.png",bbox_inches="tight"); plt.close(fig)


def fig07():
    fig, ax = plt.subplots(figsize=(7.0,3.2))
    labels = ["τ\n(年/周)","容量\n(有刻度/无)","门\n(切线/门槛)","记忆\n(名/命题)","压缩\n(信息/合法性)"]
    left  = [3, 3, 1, 1, 2]
    right = [1, 1, 3, 3, 2]
    x = np.arange(len(labels))
    ax.bar(x-.19, left, .36, color="#2f6f9f", label="前一篇的口径", zorder=3)
    ax.bar(x+.19, right, .36, color="#b3701f", label="后一篇的口径", zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.8)
    ax.set_yticks([]); ax.set_ylabel("（示意：刻度强弱）")
    ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 7　五处同名不同物：跨篇冲突不解决，六核心就会互相借尺度", fontsize=9.4, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig07_conflicts.png",bbox_inches="tight"); plt.close(fig)


def fig08():
    sts = ["成立","支持","部分","待检验","开放","证伪","撤回"]
    counts = [S["by_status"][s] for s in sts]
    fig, ax = plt.subplots(figsize=(6.4,2.8))
    ax.bar(sts, counts, color=[C_OK,C_OK,C_PART,C_OPEN,C_OPEN,C_FAIL,"#6b2b26"], zorder=3)
    for i,v in enumerate(counts): ax.text(i, v+.15, str(v), ha="center", fontsize=8.4)
    ax.set_ylabel("命题数"); ax.set_ylim(0, max(counts)*1.25)
    ax.set_title("图 8　本文自评：六条命题中三条「待检验」、两条「成立」、一条「开放」", fontsize=9.2, loc="left")
    fig.tight_layout(); fig.savefig(ROOT/"fig08_self.png",bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    table_cards(); table_scale(); table_clock(); table_fail(); table_six(); table_conflicts(); table_ledger()
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06(); fig07(); fig08()
    print("figs:", sorted(p.name for p in ROOT.glob("fig0*.png")))
    print("stats:", S["n"], S["closed"], S["open_"], S["withdrawn"], dict(S["by_grade"]))

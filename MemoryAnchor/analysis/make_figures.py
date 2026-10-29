# -*- coding: utf-8 -*-
"""《记忆的锚点》——8 图 + 8 表；数据来自 data/schemes.py（单一来源）。"""
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
from data import schemes as S

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4, C5 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a", "#4f7a4f"

ROWS = S.rows()
ST = S.stats()


def save(fig, name):
    fig.savefig(ROOT / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


def tables():
    # 表 1 六变量
    out = ["| 变量 | 问什么 | 取值 | 判据 |", "|---|---|---|---|"]
    for a, b, c, d in [
        ("D1 残余粒度", "一条记忆存到多细", "全文／摘要／片段／字段", "存的是原文、概括、片段，还是可对账的字段（坐标、时间戳、控件）"),
        ("D2 硬日志锚点", "有没有非 LLM 写下的原始记录", "有／部分／无", "记录者不是模型，且可与重建结果逐条对账"),
        ("D3 线索维度", "一条残余能被几类线索唤起", "1–5（语义／时间／空间／人物／任务）", "数一数索引键的类别，不是数索引条数"),
        ("D4 重建者异构性", "谁来重建", "同源／同族／跨模型／无", "同源＝同一个模型；同族＝同架构不同提示；跨模型＝不同厂商或架构"),
        ("D5 裁判机制", "谁来定真伪", "无／自评／交叉／带锚裁决", "带锚＝裁决必须引用一条日志字段，否则只能标 C"),
        ("D6 主要失效", "它最先死在哪", "窗口满／摘要漂移／检索噪声／成本／幻觉／共识幻觉／人工瓶颈", "只记最先出现的那个，不记全部"),
    ]:
        out.append(f"| **{a}** | {b} | {c} | {d} |")
    (ROOT / "data" / "table_vars.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2 十二方案编码
    out = ["| 编号 | 方案 | 类型 | D1 粒度 | D2 锚点 | D3 线索 | D4 异构 | D5 裁判 | D6 失效 | 等级 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["id"]} | {r["name"]} | {r["kind"]} | {r["granular"]} | {r["anchor"]} | '
                   f'{r["cues"]} | {r["hetero"]} | {r["judge"]} | {r["failmode"]} | {r["grade"]} |')
    (ROOT / "data" / "table_schemes.md").write_text("\n".join(out), encoding="utf-8")
    with open(ROOT / "schemes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=S.FIELDS)
        w.writeheader(); w.writerows(ROWS)

    # 表 3 三件套覆盖
    out = ["| 方案 | 硬日志锚点 | 跨模型异构 | 带锚裁决 | 三件套 |", "|---|---|---|---|---|"]
    for r in ROWS:
        a = "●" if r["anchor"] == "有" else ("△" if r["anchor"] == "部分" else "○")
        h = "●" if r["hetero"] == "跨模型" else ("△" if r["hetero"] == "同族" else "○")
        j = "●" if r["judge"] == "带锚裁决" else ("△" if r["judge"] in ("交叉", "自评") else "○")
        n = sum(1 for x in (r["anchor"] == "有", r["hetero"] == "跨模型", r["judge"] == "带锚裁决") if x)
        out.append(f'| {r["id"]} {r["name"]} | {a} | {h} | {j} | {n}/3 |')
    (ROOT / "data" / "table_trio.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4 容量账（示意模型）
    out = ["| 策略 | 存什么 | 每条成本（token） | 1 万条占用 | 可唤起的信息（相对） | 前提 |", "|---|---|---|---|---|---|"]
    for a, b, c, d, e, f in [
        ("全量留存", "每条交互原文", "≈ 400", "≈ 400 万 token", "1.0×", "窗口／成本无上限（现实中不成立）"),
        ("摘要漂流", "每条压成摘要", "≈ 60", "≈ 60 万 token", "≈ 1.3×", "摘要不丢关键线索（现实中常不成立）"),
        ("情景唤起（本文）", "字段级残余 + 5 类线索 + 重建", "≈ 25（残余）＋索引 ≈ 8", "≈ 33 万 token", "≈ 1.8–3×", "锚点可用、重建可信（本文的核心假设）"),
    ]:
        out.append(f"| {a} | {b} | {c} | {d} | {e} | {f} |")
    out.append("\n> 表中「可唤起的信息（相对）」是**本文的示意估算**，不是测量；参数与算法见 5.4 与附录 D，"
               "任何读者可用自己的参数重算。这一列存在的意义不是给出倍数，而是指明「节省来自重建，不来自存储」。")
    (ROOT / "data" / "table_capacity.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5 死亡解剖
    out = ["| 症状 | 机制 | 本文的补丁 | 补丁也解决不了的 | 证据 |", "|---|---|---|---|---|"]
    for a, b, c, d, e in [
        ("第 3 天开始重复自己说过的话", "窗口满 → 早期内容被截断", "字段级残余 + 线索唤起（不靠窗口）", "线索本身缺失时无法唤起", "C（社区观察）"),
        ("第 4 天开始「认错人」", "摘要漂移：压缩时把两个用户混成一个", "摘要不再由生成模型独占，改由书记员字段对齐", "字段没覆盖的语义细节仍会漂", "C"),
        ("回复越来越像模板", "检索噪声：向量检索总返回最近的相似片段", "多线索粗筛 + 空间键（在哪一屏）", "索引成本上升，延迟增加", "C"),
        ("突然停更", "成本超支或账号处置", "无（这不是记忆问题）", "本文不处理", "C（推断）"),
        ("直播时对弹幕答非所问", "时效：重建耗时超过回复窗口", "低风险场景跳过投票，只做单路重建", "高分歧场景仍需人环，延迟不可消", "C"),
        ("重建出从未发生的事", "幻觉：无锚点的语义补全", "有锚才采信，无锚一律标 C", "锚点本身错了会一起错", "B（认知科学）"),
    ]:
        out.append(f"| {a} | {b} | {c} | {d} | {e} |")
    (ROOT / "data" / "table_death.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6 六核心
    out = ["| 核心 | 专著 | 在本架构里的位置 | 关系 | 等级 |", "|---|---|---|---|---|"]
    for r in [("**记住**（主）", "《遗忘的边界》", "容量—压缩—遗忘：存残余不存全量；索引是第二次压缩；淘汰是遗忘", "**检验**：多线索索引把「压缩率」与「可唤起量」解耦", "乙／B"),
              ("**讲述**（主）", "《诠释的权衡》", "裁判的置信度分配：有锚 A、半锚 B、无锚 C", "**扩展**：把置信度落到一条日志字段上", "乙／B"),
              ("**临界**（主）", "《涌现的临界》", "冲突阈值：分歧率超过 τ 则叫停或人环", "借用判据", "丙／C"),
              ("看见", "《区分的语法》", "索引即划线：五类线索＝五次划线", "借用语言", "丙／C"),
              ("跟上", "《错位的时间》", "重建耗时 vs 回复窗口；延迟以秒计的直播场景", "**检验**：投票机制在直播场景几乎不可用", "乙／B"),
              ("选择", "《选择的代价》", "用算力与索引空间换保真度；让出精确与延迟", "借用语言", "丙／C")]:
        out.append("| " + " | ".join(r) + " |")
    (ROOT / "data" / "table_six.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7 系列接口
    out = ["| 件 | 关系 | 一句话 |", "|---|---|---|"]
    for a, b, c in [
        ("《遗忘的边界》（卷三）", "**深化**", "把「容量—压缩—遗忘」落成一个可实现的索引—重建回路"),
        ("《线外的残余》（论文三）", "**执行**", "残余—解码器—可重建性：本文给出解码器的工程形态（线索 + 锚点）"),
        ("《区分的语法》（卷二）", "借用", "索引即划线；五类线索是五次划线"),
        ("《选择的代价》（卷五）", "借用", "保容量与可传递，让出精确与延迟"),
        ("《诠释的权衡》（卷六）", "**扩展**", "置信度分配到「锚点」这一格"),
        ("《涌现的临界》（卷七）", "借用", "分歧阈值 τ 与「不可判」"),
        ("《术语的账单》（论文一）", "**互证**", "「多数派背后是日志，模型投票背后没有日志」"),
        ("《领域的剖面》（论文十）", "**接口**", "四问里 Q3 可写性＝书记员能不能写下这条账"),
        ("《同构的强度》（论文十一）", "**互证**", "抖音→QQ 的「返回」负迁移，正是缺例外清单的函子档"),
        ("《六张账单的对账》（论文九）", "**登记**", "本文十条命题进它的「待测」与「失败模式」两格"),
    ]:
        out.append(f"| {a} | {b} | {c} |")
    (ROOT / "data" / "table_series.md").write_text("\n".join(out), encoding="utf-8")

    # 表 8 命题状态
    out = ["| 编号 | 命题 | 本文证据 | 状态 |", "|---|---|---|---|"]
    for a, b, c, d in [
        ("T1", "人类记忆是「残余＋多线索＋重建」", "认知科学四支文献一致（[13]–[17]）", "支持（B）"),
        ("T2", "情景唤起能在同一预算下提高可唤起量", "容量账示意模型（附录 D）", "**待测**（C）"),
        ("T3", "现有 11 个方案无一同时具备锚点／异构／带锚裁决", "十二方案编码（表 2、表 3）", "支持（B）"),
        ("T4", "同质多 Agent 投票会放大共模错误", "共模模型（图 4）与文献 [11]", "支持（B）"),
        ("T5", "投票不能决定真伪，只有残余能", "逻辑论证＋口诵传经的边界（7.2）", "支持（B）"),
        ("T6", "多数现有方案的死因是「窗口满／检索噪声」而非容量不足", "失效分布（表 3）", "部分（C，样本 12）"),
        ("T7", "直播类场景无法承受多路重建的延迟", "延迟估算（8.4）", "**待测**（C）"),
        ("T8", "裁判必须依赖非 LLM 日志，否则只是自评的变体", "十二方案中「带锚」者仅 2 例", "支持（B）"),
        ("T9", "该架构可把「几天就死」延长到「几周不死」", "无实验", "**撤回**"),
        ("T10", "三层架构是「记住」的架构落地，不是新核心", "六核心对照（表 6）自洽", "待检验（C）"),
    ]:
        out.append(f"| **{a}** | {b} | {c} | {d} |")
    (ROOT / "data" / "table_claims.md").write_text("\n".join(out), encoding="utf-8")
    print("  tables: 8")


def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.55)

    box(3.6, 4.55, 2.8, 1.1, "裁判 Judge\n带锚裁决 · A/B/C · 阈值 τ", "#f2e6e6")
    for i, x in enumerate((.35, 3.75, 7.15)):
        box(x, 2.65, 2.5, 1.15, ["回忆者 A\n时间线索", "回忆者 B\n空间线索", "回忆者 C\n人物线索"][i], "#dbe7f1", 7.9)
    box(.35, .55, 9.3, 1.15, "书记员 Clerk：字段级硬日志（时间戳 · 控件树 · 坐标 · 停留 · 动作 · 结果）\n"
                            "不由生成模型写，不参与回忆，只被对账", "#e6ecdf", 8.0)
    for x in (1.6, 5.0, 8.4):
        ax.add_patch(FancyArrowPatch((x, 2.6), (x, 1.75), arrowstyle="-|>", mutation_scale=10, lw=1, color="#888"))
        ax.add_patch(FancyArrowPatch((x, 3.85), (4.6, 4.5), arrowstyle="-|>", mutation_scale=10, lw=1, color="#888"))
    ax.add_patch(FancyArrowPatch((5.0, 1.75), (5.0, 2.6), arrowstyle="-|>", mutation_scale=10,
                                 lw=1.2, color=C2, ls="--"))
    ax.text(5.1, 2.15, "锚点复核", fontsize=7, color=C2)
    ax.text(.2, 5.95, "图 1　三层不是三个 Agent，是三种职能", fontsize=9.8, fontweight="bold")
    ax.text(.2, .15, "注：异构只在中层；底层与顶层如果也用同一个模型，就退化成「自问自答」。",
            fontsize=7, color="#555")
    save(fig, "fig01_stack.png")


def fig02():
    ids = [r["id"] for r in ROWS]
    cols = ["硬日志锚点", "跨模型异构", "带锚裁决"]
    M = np.array([[1 if r["anchor"] == "有" else (0.5 if r["anchor"] == "部分" else 0),
                   1 if r["hetero"] == "跨模型" else (0.5 if r["hetero"] == "同族" else 0),
                   1 if r["judge"] == "带锚裁决" else (0.5 if r["judge"] in ("交叉", "自评") else 0)]
                  for r in ROWS])
    fig, ax = plt.subplots(figsize=(4.6, 5.4))
    ax.imshow(M, cmap="Blues", vmin=0, vmax=1.6, aspect="auto")
    ax.set_xticks(range(3)); ax.set_xticklabels(cols, fontsize=8.6)
    ax.set_yticks(range(len(ids))); ax.set_yticklabels(ids, fontsize=7.4)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, {1: "●", .5: "△", 0: "○"}[M[i, j]], ha="center", va="center",
                    fontsize=8.5, color="white" if M[i, j] == 1 else "#333")
    ax.grid(False)
    ax.set_title("图 2　三件套覆盖：11 个现有方案没有一格同时为实心", fontsize=9.0, loc="left")
    save(fig, "fig02_trio.png")


def fig03():
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    labels = ["全量留存", "摘要漂流", "情景唤起"]
    store = [400, 60, 33]
    recall = [1.0, 1.3, 2.4]
    x = np.arange(3)
    ax.bar(x - .19, store, .36, label="每条占用（token，左轴）", color=C1, zorder=3)
    ax2 = ax.twinx()
    ax2.plot(x + .19, recall, "o-", color=C2, lw=1.8, ms=7, label="可唤起信息（相对，右轴）")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("每条占用 token"); ax2.set_ylabel("可唤起信息（相对）")
    ax2.set_ylim(0, 3.0); ax.set_ylim(0, 460)
    for i, (s, r) in enumerate(zip(store, recall)):
        ax.text(i - .19, s + 10, str(s), ha="center", fontsize=8)
        ax2.text(i + .19, r + .12, f"{r}×", ha="center", fontsize=8, color=C2)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.4, frameon=False, loc="upper right")
    ax.set_title("图 3　容量账（示意）：节省来自重建，不来自存储", fontsize=9.4, loc="left")
    save(fig, "fig03_capacity.png")


def fig04():
    """多数派错误率：n 取奇数以避免平票；ρ 为「全体共享同一次错误抽样」的概率。"""
    from math import comb
    n = np.array([1, 3, 5, 7, 9, 11])
    p_err = 0.2
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    for rho, c, lab in [(0.0, C1, "完全独立（ρ=0）"), (0.3, C2, "部分同源（ρ=0.3）"), (0.7, C5, "高度同源（ρ=0.7）")]:
        ys = []
        for k in n:
            tail = sum(comb(int(k), j) * p_err ** j * (1 - p_err) ** (int(k) - j)
                       for j in range(int(k) // 2 + 1, int(k) + 1))
            ys.append(rho * p_err + (1 - rho) * tail)
        ax.plot(n, ys, "o-", color=c, lw=1.6, ms=4.5, label=lab)
    ax.axhline(p_err, color="#bbb", ls=":", lw=.8)
    ax.text(1.1, p_err + .008, "单模型错误率 0.2", fontsize=7, color="#888")
    ax.set_xlabel("参与重建的独立模型数（奇数，避免平票）")
    ax.set_ylabel("多数派出错的概率")
    ax.set_ylim(0, .25); ax.set_xticks(n); ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 4　投票只在「独立」时才是防线：同源时它退化成一个模型", fontsize=9.2, loc="left")
    save(fig, "fig04_correlation.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.0); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.3, 3.4, 2.6, 1.1, "症状\n重复／认错人／模板化", "#f2efe6")
    box(3.5, 3.4, 3.0, 1.1, "机制\n窗口满 · 摘要漂移 · 检索噪声", "#f2e6e6")
    box(7.1, 3.4, 2.6, 1.1, "本文补丁\n字段残余 · 空间键 · 锚点", "#dbe7f1")
    box(.3, 1.2, 4.3, 1.1, "补丁也解决不了的\n线索缺失、账号处置、成本", "#fff", 7.8)
    box(5.2, 1.2, 4.5, 1.1, "仍必须人环的\n高风险动作（转账、公开发言）", "#fff", 7.8)
    for x in (1.6, 5.0, 8.4):
        ax.add_patch(FancyArrowPatch((x, 3.35), (x, 2.4), arrowstyle="-|>", mutation_scale=10, lw=.9, color="#999"))
    ax.text(.2, 4.8, "图 5　死亡解剖：症状不指向病因，机制才指向补丁", fontsize=9.6, fontweight="bold")
    save(fig, "fig05_death.png")


def fig06():
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis("off")

    def step(x, y, t, fc, fs=7.6):
        ax.add_patch(FancyBboxPatch((x, y), 1.7, .8, boxstyle="round,pad=0.04,rounding_size=0.07",
                                    fc=fc, ec="#666", lw=.8))
        ax.text(x + .85, y + .4, t, ha="center", va="center", fontsize=fs, linespacing=1.4)

    for i, t in enumerate(["用户提问", "向量检索", "拼接上下文", "生成回答"]):
        step(.2 + i * 1.95, 3.0, t, "#f2efe6")
        if i < 3:
            ax.add_patch(FancyArrowPatch((1.95 + i * 1.95, 3.4), (2.1 + i * 1.95, 3.4),
                                         arrowstyle="-|>", mutation_scale=9, lw=.9, color="#888"))
    for i, t in enumerate(["当前情境", "五类线索", "粗筛 + 精排", "多路重建", "带锚裁决", "行动/叫停"]):
        step(.2 + i * 1.62, .9, t, "#dbe7f1", 7.0)
        if i < 5:
            ax.add_patch(FancyArrowPatch((1.87 + i * 1.62, 1.3), (1.99 + i * 1.62, 1.3),
                                         arrowstyle="-|>", mutation_scale=9, lw=.9, color="#888"))
    ax.text(.2, 4.15, "图 6　query-driven（上）与 cue-driven（下）：后者由情境发起", fontsize=9.6, fontweight="bold")
    ax.text(.2, .25, "注：上排是「问什么查什么」，下排是「我在哪、刚做了什么、现在该想起什么」。",
            fontsize=7, color="#555")
    save(fig, "fig06_cue.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.3, 3.6, 3.0, 1.0, "看见\n索引＝划线（五类线索）", "#dbe7f1")
    box(3.6, 3.6, 3.0, 1.0, "记住\n残余＋压缩＋遗忘", "#e6ecdf")
    box(6.9, 3.6, 2.8, 1.0, "讲述\n裁判的 A/B/C", "#f2e6e6")
    box(.3, 1.4, 3.0, 1.0, "跟上\n重建耗时 vs 回复窗口", "#f7efe2")
    box(3.6, 1.4, 3.0, 1.0, "选择\n算力换保真", "#f7efe2")
    box(6.9, 1.4, 2.8, 1.0, "临界\n分歧阈值 τ", "#f2efe6")
    ax.text(.2, 5.2, "图 7　六核心在这套架构里的位置：三个主核、三个借用", fontsize=9.6, fontweight="bold")
    ax.text(.2, .7, "注：主核是「记住」「讲述」「临界」；「看见/跟上/选择」提供约束条件，不新增判据。",
            fontsize=7, color="#555")
    save(fig, "fig07_six.png")


def fig08():
    props = [("T1", "记忆＝残余＋线索＋重建", 1.0), ("T2", "同预算下唤起更多", .5),
             ("T3", "现有方案无一齐备三件套", 1.0), ("T4", "同源投票放大共模错误", 1.0),
             ("T5", "投票不能定真伪", 1.0), ("T6", "死因多为窗口/噪声", .75),
             ("T7", "直播不可承受多路重建", .5), ("T8", "裁判必须依赖非 LLM 日志", 1.0),
             ("T9", "能把「几天」延长到「几周」", 0.0), ("T10", "是「记住」的落地而非新核心", .5)]
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    ys = np.arange(len(props))[::-1]
    cols = {1.0: C1, .75: C2, .5: C4, 0.0: C3}
    ax.barh(ys, [p[2] for p in props], .55, color=[cols[p[2]] for p in props], zorder=3)
    for y, (i, t, v) in zip(ys, props):
        ax.text(-.02, y, f"{i} {t}", ha="right", va="center", fontsize=7.4)
        ax.text(max(v, 0) + .02, y, {1.0: "支持", .75: "部分", .5: "待测", 0.0: "撤回"}[v],
                va="center", fontsize=7.2, color=cols[v])
    ax.set_yticks([]); ax.set_xlim(0, 1.3); ax.set_xticks([0, .5, 1])
    ax.set_title("图 8　自证：十条命题里有一条被自己撤回", fontsize=9.4, loc="left")
    save(fig, "fig08_self.png")


def main():
    print("tables...")
    tables()
    print("figures...")
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08):
        f()


if __name__ == "__main__":
    main()

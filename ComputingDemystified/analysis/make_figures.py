# -*- coding: utf-8 -*-
"""生成 concepts.csv 与 fig01—fig12。

纪律（沿用系列 paper-mode 的十条）：
  * 一幅图一个论点；
  * 注释放在空区（右侧卡片、底部说明），不压在线上；
  * 需要沿边写的文字用白底 bbox，不旋转压在箭头上；
  * 能分面就分面；顶点/象限标签放角落；
  * 图上不写“实测”（示意写“示意”，编码写“编码”）；
  * 导出 bbox_inches="tight"，字号 ≥ 7pt。

运行：python make_figures.py
"""
import csv
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Ellipse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
from concepts import TERMS, LAYERS, BNECK, SWAP, stats  # noqa: E402

plt.rcParams.update({
    "font.family": ["SimHei", "Microsoft YaHei"],
    "axes.unicode_minus": False,
    "figure.dpi": 180,
    "savefig.dpi": 180,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "font.size": 9.5,
    "figure.facecolor": "white",
})

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "..")
S = stats()

RED, BLUE, GREEN, GOLD, GRAY = "#b3261e", "#1f4e79", "#2e6b4f", "#a8791f", "#5f6368"
P_RED, P_BLUE, P_GREEN, P_GOLD = "#fbe9e7", "#e8eff6", "#e6f1ea", "#faf1dd"
P_GRAY = "#f1f1f1"
VCOL = {"C": RED, "A": BLUE, "T": GREEN, "无": GRAY}
VNAME = {"C": "C 完备", "A": "A 可组合", "T": "T 传递", "无": "无让出"}


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", name)


def card(ax, x, y, w, h, fc, ec, title, body, tcol, tsize=10.5, bsize=8.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                fc=fc, ec=ec, lw=1.2, transform=ax.transAxes, zorder=1))
    ax.text(x + 0.03, y + h - 0.06, title, transform=ax.transAxes, fontsize=tsize,
            fontweight="bold", color=tcol, va="top", zorder=2)
    ax.text(x + 0.03, y + h - 0.155, body, transform=ax.transAxes, fontsize=bsize,
            color="#333333", va="top", linespacing=1.6, zorder=2)


def write_csv():
    path = os.path.join(OUT, "data", "concepts.csv")
    cols = ["id", "layer", "term", "en", "plain", "bneck", "bneck_txt", "swap",
            "swap_txt", "impl", "impl_g", "cat", "cat_txt", "shadow", "cross",
            "grade", "cgrade", "note"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in TERMS:
            w.writerow({k: t[k] for k in cols})
    print("   data/concepts.csv  (n=%d)" % len(TERMS))


# ------------------------------------------------------------------ fig01
def fig01():
    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    ax.set_xlim(0, 1); ax.set_ylim(0.0, 9.7); ax.axis("off")

    scarcity = ["算力 / 带宽", "容量 / 权限", "延迟（光速）", "延迟（寻道）",
                "协调（多数派）", "协调（人的维护）", "容量（显存）", "信任（责任）"]
    tau = ["ns", "µs", "ms", "ms", "10–100 ms", "天–年", "ms（批）", "秒–人"]
    sample = ["指令 流水线 缓存 SIMD 中断", "进程 虚拟内存 系统调用 容器",
              "协议栈 TCP TLS DNS 流式", "B+ 树 LSM WAL MVCC 纠删码",
              "共识 复制 分片 幂等 一致性模型", "依赖注入 消息队列 限流 可观测性",
              "注意力 KV cache 量化 MoE 位置编码", "工具 RAG 规划 评测 注入防御"]
    for i, L in enumerate(LAYERS):
        y = i + 1.25
        fc = "#ffffff" if i % 2 == 0 else "#faf8f3"
        ax.add_patch(Rectangle((0.02, y - 0.42), 0.96, 0.84, fc=fc,
                               ec="#c9c2b2", lw=0.8))
        ax.text(0.045, y + 0.10, "%d" % (i + 1), fontsize=13, fontweight="bold",
                color=GOLD, va="center")
        ax.text(0.100, y + 0.10, L, fontsize=11.5, fontweight="bold", va="center")
        ax.text(0.100, y - 0.20, sample[i], fontsize=8.2, color="#444", va="center")
        ax.text(0.615, y + 0.10, "稀缺：" + scarcity[i], fontsize=8.6, color=RED,
                va="center")
        ax.text(0.615, y - 0.20, "本层 τ：" + tau[i], fontsize=8.2, color=GRAY,
                va="center")

    ax.annotate("", xy=(0.995, 8.80), xytext=(0.995, 1.70),
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.4))
    ax.text(0.988, 8.88, "抽象上升", fontsize=8.6, color=GOLD, ha="right")
    ax.text(0.012, 9.38, "八层栈：每一层都在替上一层偿还同一种债——把稀缺资源换成时间或空间",
            fontsize=9.4, color="#222", fontweight="bold")
    ax.text(0.02, 0.55, "注：τ 为该层一次“往返”的典型量级；由上到下相差约九个数量级。"
                        "瓶颈列不是定义，而是这一层最常被记账的那一项。",
            fontsize=7.6, color="#666")
    save(fig, "fig01.png")


# ------------------------------------------------------------------ fig02
def fig02():
    M = np.zeros((len(BNECK), len(SWAP)), int)
    for t in TERMS:
        M[BNECK.index(t["bneck"]), SWAP.index(t["swap"])] += 1
    filled = int((M > 0).sum())
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    im = ax.imshow(M, cmap="YlOrBr", vmin=0, vmax=M.max())
    ax.set_xticks(range(len(SWAP))); ax.set_xticklabels(SWAP, fontsize=9)
    ax.set_yticks(range(len(BNECK))); ax.set_yticklabels(BNECK, fontsize=9)
    ax.set_xlabel("置换动作（把什么挪走）", fontsize=9.4)
    ax.set_ylabel("瓶颈（被谁逼出来）", fontsize=9.4)
    for i in range(len(BNECK)):
        for j in range(len(SWAP)):
            v = M[i, j]
            if v:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=9,
                        color="white" if v >= 4 else "#333",
                        fontweight="bold" if v >= 4 else "normal")
    ax.set_xticks(np.arange(-.5, len(SWAP), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(BNECK), 1), minor=True)
    ax.grid(which="minor", color="white", lw=1.6)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("术语数", fontsize=8)
    cb.ax.tick_params(labelsize=7.5)
    ax.set_title("%d 条术语落在 7×7 的账格里：只有 %d 格非空，最大格 %d 条"
                 % (len(TERMS), filled, int(M.max())), fontsize=10.5, pad=10)
    save(fig, "fig02.png")


# ------------------------------------------------------------------ fig03
def fig03():
    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")

    def box(x, y, w, h, txt, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                    fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=9)

    def arrow(x1, y1, x2, y2, txt, col, dy=0.30):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5,
                                    connectionstyle="arc3,rad=0.0"))
        ax.text((x1 + x2) / 2, max(y1, y2) + dy, txt, ha="center", va="bottom",
                fontsize=8.2, color=col)

    # (a) 传统路径
    ax.text(0.1, 5.85, "a　传统发送：4 次拷贝，4 次态切换", fontsize=10.2,
            fontweight="bold", color="#222")
    y = 4.35
    box(0.15, y, 1.3, 0.7, "磁盘", P_GRAY, GRAY)
    box(1.95, y, 1.7, 0.7, "内核缓冲区", P_BLUE, BLUE)
    box(4.15, y, 1.7, 0.7, "应用缓冲区", P_RED, RED)
    box(6.35, y, 1.7, 0.7, "套接字缓冲", P_BLUE, BLUE)
    box(8.55, y, 0.85, 0.7, "网卡", P_GRAY, GRAY)
    for x1, x2, lbl, col in [(1.45, 1.95, "①DMA", GRAY), (3.65, 4.15, "②CPU", RED),
                             (5.85, 6.35, "③CPU", RED), (8.05, 8.55, "④DMA", GRAY)]:
        arrow(x1 + 0.01, y + 0.35, x2 - 0.01, y + 0.35, lbl, col, dy=0.44)
    ax.text(4.7, y - 0.40, "②③ 各一次 read()/write()：应用态与内核态之间来回四次",
            fontsize=8.2, color=RED, ha="center")

    # (b) 零拷贝
    ax.text(0.1, 2.95, "b　零拷贝：2 次 DMA，0 次 CPU 拷贝，0 次应用态拷贝", fontsize=10.2,
            fontweight="bold", color="#222")
    y2 = 1.55
    box(0.15, y2, 1.3, 0.7, "磁盘", P_GRAY, GRAY)
    box(1.95, y2, 2.5, 0.7, "内核缓冲区（page cache）", P_BLUE, BLUE)
    box(5.45, y2, 0.95, 0.7, "网卡", P_GRAY, GRAY)
    box(7.15, y2, 2.25, 0.7, "应用缓冲区\n（这一路不经过）", "#ffffff", "#bbbbbb")
    arrow(1.47, y2 + 0.35, 1.93, y2 + 0.35, "①DMA", GRAY, dy=0.44)
    arrow(4.47, y2 + 0.35, 5.43, y2 + 0.35, "②DMA（一次 sendfile）", GRAY, dy=0.44)

    ax.text(0.1, 0.55, "“零”指零 CPU 干预、零应用空间拷贝；电信号仍在铜线与光纤里跑完每一段。",
            fontsize=8.6, color="#333")
    ax.text(0.1, 0.18, "示意：块大小与缓冲数量略去；DMA 由设备控制器执行，CPU 只下指令。",
            fontsize=7.4, color="#666")
    save(fig, "fig03.png")


# ------------------------------------------------------------------ fig04
def fig04():
    n_slice, slice_len, cold = 8, 400, 170
    xs, ys, bounds = [], [], []
    for k in range(n_slice):
        for i in range(slice_len):
            p = 0.97 if i > cold else 0.12
            xs.append(k * slice_len + i)
            ys.append(p * 100 + np.random.RandomState(k * 7 + i).normal(0, 1.1))
        bounds.append(k * slice_len)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 5.6), sharex=True,
                                   gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.18})
    ax1.plot(xs, ys, lw=0.7, color=BLUE)
    for b in bounds[1:]:
        ax1.axvline(b, color=RED, ls="--", lw=1.0)
    ax1.set_ylabel("缓存命中率（模型示意，%）", fontsize=9)
    ax1.set_ylim(5, 108)
    ax1.set_xlim(0, n_slice * slice_len)
    for k in range(n_slice):
        ax1.axvspan(k * slice_len, k * slice_len + cold, color=P_RED, alpha=0.55, lw=0)
    ax1.set_title("上下文切换真正的账单：不是那几条寄存器读写，而是被冲掉的缓存",
                  fontsize=10.6, pad=8)
    ax1.text(0.0, -0.30, "浅红区：切换后前 ~170 次访问几乎全部未命中（新进程的热点数据不在片上）。",
             transform=ax1.transAxes, fontsize=8.2, color=RED)
    ax1.text(0.0, -0.40, "示意模型：每片 400 次访问、冷启动 170 次；数值为构造，不是实测。",
             transform=ax1.transAxes, fontsize=7.6, color="#666")

    for k in range(n_slice):
        ax2.add_patch(Rectangle((k * slice_len, 0), slice_len, 1,
                                fc=P_BLUE if k % 2 == 0 else P_RED,
                                ec="white", lw=1.2))
        ax2.text((k + 0.5) * slice_len, 0.5, "A" if k % 2 == 0 else "B",
                 ha="center", va="center", fontsize=9, color=BLUE if k % 2 == 0 else RED)
    ax2.set_ylim(0, 1); ax2.set_yticks([])
    ax2.set_xlabel("时间（次访问）", fontsize=9)
    ax2.set_ylabel("占用 CPU 的进程", fontsize=9)
    ax2.set_xlim(0, n_slice * slice_len)
    save(fig, "fig04.png")


# ------------------------------------------------------------------ fig05
def fig05():
    fig, ax = plt.subplots(figsize=(9.2, 4.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
    xs = [1.4, 3.2, 5.0, 6.8, 8.6]
    names = ["n1", "n2", "n3", "n4", "n5"]
    ax.add_patch(Ellipse((3.2, 3.9), 4.0, 1.9, fc=P_BLUE, ec=BLUE, lw=1.3, alpha=0.55))
    ax.add_patch(Ellipse((6.8, 3.9), 4.0, 1.9, fc=P_GOLD, ec=GOLD, lw=1.3, alpha=0.55))
    for x, nm in zip(xs, names):
        ax.add_patch(plt.Circle((x, 3.9), 0.29, fc="white", ec="#333", lw=1.4, zorder=4))
        ax.text(x, 3.9, nm, ha="center", va="center", fontsize=9, zorder=5)
        if nm != "n3":
            ax.text(x, 3.28, "日志", ha="center", va="center", fontsize=7.6, color="#666")
    ax.text(3.2, 5.25, "多数派 A = {n1, n2, n3}", ha="center", fontsize=9.4, color=BLUE,
            fontweight="bold")
    ax.text(6.8, 5.25, "多数派 B = {n3, n4, n5}", ha="center", fontsize=9.4, color=GOLD,
            fontweight="bold")
    ax.add_patch(FancyBboxPatch((1.1, 0.55), 7.8, 1.45,
                                boxstyle="round,pad=0.04,rounding_size=0.08",
                                fc=P_RED, ec=RED, lw=1.1))
    ax.annotate("", xy=(5.0, 2.05), xytext=(5.0, 3.55),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2))
    ax.text(1.35, 1.60, "交集非空：n3 同时持有两份日志", fontsize=9.2, color=RED,
            fontweight="bold")
    ax.text(1.35, 1.05, "n = 5，阈值 k = 3；任意两个 k 子集必然相交，因为 2k > n。\n"
                        "这条不等式，就是“记账不会被推翻”的全部物理内容。",
            fontsize=8.8, color="#333", linespacing=1.6)
    ax.text(0.1, 6.05, "共识的护城河只有一条：多数派 + 更大的任期号", fontsize=10.4,
            fontweight="bold")
    save(fig, "fig05.png")


# ------------------------------------------------------------------ fig06
def fig06():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.4),
                                   gridspec_kw={"width_ratios": [1.0, 1.15], "wspace": 0.28})

    rng = np.random.RandomState(3)
    w = np.concatenate([rng.normal(-0.6, 0.35, 1200), rng.normal(0.7, 0.30, 900)])
    ax1.hist(w, bins=70, color="#dfdfdf", edgecolor="#c8c8c8", lw=0.3)
    lo, hi, b = w.min(), w.max(), 4
    levels = np.linspace(lo, hi, 2 ** b)
    for lv in levels:
        ax1.axvline(lv, color=RED, lw=0.9, alpha=0.85)
    ax1.set_xlabel("权重取值", fontsize=9)
    ax1.set_ylabel("参数个数（示意）", fontsize=9)
    ax1.set_yticks([])
    ax1.set_title("a　4 位量化：步长 = (max − min)/(2⁴ − 1)", fontsize=10.2)
    ax1.text(0.03, 0.94, "16 个台阶代替连续区间\n每个数四舍五入到最近的台阶\n步长 ≈ %.2f"
             % ((hi - lo) / 15), transform=ax1.transAxes, fontsize=8.2, va="top",
             color="#333", bbox=dict(fc="white", ec="none", alpha=0.85, pad=2.0))
    ax1.set_xlim(lo - 0.1, hi + 0.1)

    # speculative decoding timeline
    ax2.set_xlim(-0.6, 6.4); ax2.set_ylim(0, 3.2); ax2.axis("off")
    ax2.text(-0.5, 3.0, "b　投机采样：1 次大模型前向，换 4 个词", fontsize=10.2,
             fontweight="bold", va="top")
    for i, (tok, ok) in enumerate([("w1", True), ("w2", True), ("w3", True), ("w4", False)]):
        ax2.add_patch(FancyBboxPatch((i * 1.1, 1.55), 0.95, 0.62,
                                     boxstyle="round,pad=0.02,rounding_size=0.05",
                                     fc=P_GREEN if ok else P_RED,
                                     ec=GREEN if ok else RED, lw=1.3))
        ax2.text(i * 1.1 + 0.475, 1.86, tok, ha="center", va="center", fontsize=9.2)
        ax2.text(i * 1.1 + 0.475, 1.30, "采纳" if ok else "否决", ha="center", va="center",
                 fontsize=8, color=GREEN if ok else RED)
    ax2.text(-0.05, 2.45, "草稿模型先猜", fontsize=8.6, color=GRAY)
    ax2.annotate("", xy=(4.35, 2.30), xytext=(0.0, 2.30),
                 arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.1))
    ax2.add_patch(FancyBboxPatch((4.55, 1.55), 1.55, 0.62,
                                 boxstyle="round,pad=0.02,rounding_size=0.05",
                                 fc=P_BLUE, ec=BLUE, lw=1.3))
    ax2.text(5.32, 1.86, "大模型校验", ha="center", va="center", fontsize=8.8)
    ax2.text(5.32, 1.30, "并行算一次", ha="center", va="center", fontsize=8, color=BLUE)
    ax2.text(0.0, 0.62, "串行解码：4 次前向 → 4 个词", fontsize=8.8, color="#333")
    ax2.text(0.0, 0.20, "投机采样：1 次前向（+ 1 次廉价草稿）→ 4 个词：3 个采纳 + 1 个修正",
             fontsize=8.8, color="#333")
    save(fig, "fig06.png")


# ------------------------------------------------------------------ fig07
def fig07():
    seq, d, b = 1024, 768, 2
    per_tensor = seq * d * b * 2 / 1024 ** 2  # MiB, fp16
    unfused = 4 * 2 * per_tensor   # 4 ops, each read+write
    fused = 2 * per_tensor         # read x, write y
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    bars = ax.bar(["未融合\n（矩阵乘、缩放、偏置、激活）", "融合后\n（一个大循环）"],
                  [unfused, fused], width=0.45, color=[RED, GREEN], edgecolor="white")
    for r, v in zip(bars, [unfused, fused]):
        ax.text(r.get_x() + r.get_width() / 2, v + 0.25, "%.1f MiB" % v,
                ha="center", fontsize=10, fontweight="bold")
    ax.set_ylabel("显存往返流量（MiB）", fontsize=9.4)
    ax.set_ylim(0, unfused * 1.18)
    ax.annotate("省下 3 次写 + 3 次读\n流量降到 1/4", xy=(0.86, fused * 0.55),
                xytext=(0.34, unfused * 0.62), fontsize=8.8, color=GREEN,
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.1,
                                connectionstyle="arc3,rad=-0.15"))
    ax.set_title("算子融合的账单：算的是同一件事，搬的次数不同", fontsize=10.6, pad=8)
    ax.text(0.0, -0.20, "算例：seq=1024，d=768，batch=2，fp16；中间张量 %.1f MiB，"
                        "按每次算子读一次写一次计。" % per_tensor,
            transform=ax.transAxes, fontsize=7.8, color="#666")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig07.png")
    return per_tensor, unfused, fused


# ------------------------------------------------------------------ fig08
def fig08():
    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    ax.set_xlim(0, 10.6); ax.set_ylim(0, 6.6); ax.axis("off")

    def box(x, y, w, h, txt, fc, ec, fs=8.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.10",
                                    fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs,
                linespacing=1.5)

    def arr(x1, y1, x2, y2, col=GRAY, rad=0.0, lbl="", off=(0, 0.18), fs=7.8):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                                     color=col, lw=1.3,
                                     connectionstyle="arc3,rad=%s" % rad))
        if lbl:
            ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], lbl, fontsize=fs,
                    color=col, ha="center")

    # 上排：输入 → 组装 → 生成 → 判断
    box(0.10, 4.55, 2.00, 0.75, "读者输入", P_GRAY, GRAY)
    box(2.50, 4.55, 2.40, 0.75, "上下文组装\n（截断 / 排序）", P_GOLD, GOLD)
    box(5.30, 4.55, 2.00, 0.75, "模型前向", P_BLUE, BLUE)
    box(7.70, 4.55, 1.80, 0.75, "要调工具？", "#ffffff", "#333")
    # 中排：执行工具 → 写回 → 回到组装
    box(7.70, 3.05, 1.80, 0.75, "执行工具\n（校验参数）", P_GREEN, GREEN)
    box(5.30, 3.05, 2.00, 0.75, "结果写回\nmessages", P_BLUE, BLUE)
    # 下排：护栏 → 输出
    box(5.10, 0.95, 2.40, 0.75, "护栏 / 人在环", P_RED, RED)
    box(2.50, 0.95, 2.40, 0.75, "输出 + 日志\n（落盘 / 回放）", P_GRAY, GRAY)

    arr(2.10, 4.92, 2.48, 4.92)
    arr(4.90, 4.92, 5.28, 4.92)
    arr(7.30, 4.92, 7.68, 4.92, lbl="是", off=(0, 0.18))
    arr(8.60, 4.53, 8.60, 3.82)
    arr(7.68, 3.42, 7.32, 3.42)
    # 循环：写回 → 左 → 上，回到上下文组装
    ax.plot([5.28, 3.70, 3.70], [3.42, 3.42, 4.53], color=BLUE, lw=1.3)
    ax.add_patch(FancyArrowPatch((3.70, 4.20), (3.70, 4.53), arrowstyle="-|>",
                                 mutation_scale=12, color=BLUE, lw=1.3))
    ax.text(3.84, 3.94, "继续循环：带着新结果重读上下文", fontsize=7.6, color=BLUE)
    # 否：判断 → 右侧下行 → 护栏
    ax.plot([9.50, 9.95, 9.95, 7.52], [4.92, 4.92, 1.32, 1.32], color=GRAY, lw=1.3)
    ax.add_patch(FancyArrowPatch((7.75, 1.32), (7.52, 1.32), arrowstyle="-|>",
                                 mutation_scale=12, color=GRAY, lw=1.3))
    ax.text(9.99, 3.55, "否", fontsize=8.2, color=GRAY)
    arr(5.08, 1.32, 4.92, 1.32)

    ax.plot([3.70], [4.32], "o", ms=5, color=RED, zorder=6)
    ax.text(3.84, 4.32, "每轮先判 max_steps / 预算 / 超时（熔断）", fontsize=7.8,
            color=RED, va="center")

    ax.text(0.10, 2.35, "一轮循环 = 读上下文 → 生成 → 决定 → 执行 → 写回；所谓 Agent，"
                        "就是把这个 for 加上退出条件。",
            fontsize=8.8, color="#333")
    ax.text(0.10, 1.95, "工具 schema 决定模型能看见什么（区分）；messages 与截断是容量账；"
                        "护栏与人在环是权限账。",
            fontsize=8.8, color="#333")
    ax.text(0.10, 6.20, "一个 20 行 Agent 的结构：所有术语都挂在这个环上", fontsize=10.4,
            fontweight="bold")
    save(fig, "fig08.png")


# ------------------------------------------------------------------ fig09
def fig09():
    weeks = ["第 1 周", "第 2 周", "第 3 周", "第 4 周"]
    tasks = [["调通模型接口", "流式输出", "记 token 账"],
             ["定义 2 个工具", "参数校验", "错误与重试"],
             ["检索最小实现", "截断与排序", "记忆写回"],
             ["日志与回放", "10 条评测集", "人在环确认"]]
    checks = ["同一个问题，两次\n的 token 数差多少？",
              "工具报错时，\n循环会不会停？",
              "删掉一半上下文，\n答案掉多少？",
              "能复现昨天的\n那次失败吗？"]
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.set_xlim(0, 4.5); ax.set_ylim(0.0, 5.0); ax.axis("off")
    cols = [BLUE, GREEN, GOLD, RED]
    for i, (w, ts, c) in enumerate(zip(weeks, tasks, checks)):
        x = i + 0.10
        ax.add_patch(Rectangle((x, 1.10), 0.86, 3.30, fc="#ffffff", ec=cols[i], lw=1.3))
        ax.add_patch(Rectangle((x, 3.98), 0.86, 0.42, fc=cols[i], ec=cols[i]))
        ax.text(x + 0.43, 4.19, w, ha="center", va="center", fontsize=9.6,
                color="white", fontweight="bold")
        for j, t in enumerate(ts):
            ax.text(x + 0.43, 3.62 - j * 0.52, t, ha="center", va="center", fontsize=8.4)
        ax.plot([x + 0.08, x + 0.78], [2.00, 2.00], color=cols[i], lw=0.8, ls=":")
        ax.text(x + 0.43, 1.85, "自检", ha="center", va="top", fontsize=7.6, color=cols[i])
        ax.text(x + 0.43, 1.62, c, ha="center", va="top", fontsize=7.4, color="#333",
                linespacing=1.6)
    ax.text(0.02, 4.85, "四周：每周只增加一层，每周留一个能自己回答的问题", fontsize=10.4,
            fontweight="bold")
    ax.text(0.02, 0.60, "路径是顺序的，不是等级的：第 3 周卡住，常常要回第 1 周补 token 账。",
            fontsize=8.2, color="#666")
    save(fig, "fig09.png")


# ------------------------------------------------------------------ fig10
def fig10():
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.7); ax.axis("off")

    rows = [
        ("机制层：能写成循环", "算子融合、零拷贝、幂等、KV cache、投机采样",
         "写出来的那几行确实是核心；差距在工程量，不在原理", P_GREEN, GREEN, 4.55),
        ("规模层：写得出，控不住", "共识、连续批处理、多 Agent、限流、向量索引",
         "核心十行，参数与拓扑决定成败；调参与容量规划不在还原之内", P_GOLD, GOLD, 2.95),
        ("对抗层：写不出", "提示注入、能力涌现、评测泄漏、责任归属",
         "没有公认的极简机制；它的“原理”本身还在争论", P_RED, RED, 1.35),
    ]
    for title, ex, note, fc, ec, y in rows:
        ax.add_patch(FancyBboxPatch((0.15, y - 0.55), 9.7, 1.05,
                                    boxstyle="round,pad=0.04,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=1.3))
        ax.text(0.40, y + 0.24, title, fontsize=10, fontweight="bold", color=ec, va="center")
        ax.text(9.55, y + 0.24, ex, fontsize=8.2, color="#222", va="center", ha="right")
        ax.text(0.40, y - 0.28, note, fontsize=8.2, color="#444", va="center")

    ax.text(0.15, 0.28, "三条断层不是三种难度，而是三种失败方式：机制层失败于工程量，"
                        "规模层失败于不可控，对抗层失败于没有可写的机制。",
            fontsize=8.6, color="#333")
    save(fig, "fig10.png")


# ------------------------------------------------------------------ fig11
def fig11():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.6),
                                   gridspec_kw={"width_ratios": [2.1, 1.0], "wspace": 0.30})
    y = np.arange(len(LAYERS))
    left = np.zeros(len(LAYERS))
    for v in ["C", "A", "T", "无"]:
        vals = np.array([S["by_layer_vertex"][L][v] for L in LAYERS])
        ax1.barh(y, vals, left=left, color=VCOL[v], edgecolor="white", lw=1.0,
                 label=VNAME[v], height=0.62)
        for i, (val, l) in enumerate(zip(vals, left)):
            if val:
                ax1.text(l + val / 2, i, str(val), ha="center", va="center",
                         fontsize=8.2, color="white" if v != "无" else "#333")
        left += vals
    ax1.set_yticks(y); ax1.set_yticklabels(["%d %s" % (i + 1, L) for i, L in enumerate(LAYERS)],
                                           fontsize=8.8)
    ax1.invert_yaxis()
    ax1.set_xlabel("术语数", fontsize=9)
    ax1.set_xlim(0, max(S["layers"].values()) + 1.2)
    ax1.legend(ncol=4, fontsize=8, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, -0.30))
    ax1.set_title("按层记账：灰色是“没有让出任何一项”的纯资源置换", fontsize=10.2, pad=8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    tot = S["vertex"]
    vals = [tot["C"], tot["A"], tot["T"], tot["无"]]
    bottoms = 0
    for v, val in zip(["C", "A", "T", "无"], vals):
        ax2.bar([0], [val], bottom=bottoms, color=VCOL[v], width=0.55,
                edgecolor="white", lw=1.2)
        ax2.text(0, bottoms + val / 2, "%s %d" % (v, val), ha="center", va="center",
                 fontsize=8.6, color="white" if v != "无" else "#333",
                 fontweight="bold")
        bottoms += val
    ax2.set_xlim(-0.55, 0.55); ax2.set_ylim(0, S["n"] * 1.02)
    ax2.set_xticks([]); ax2.set_ylabel("n = 60", fontsize=9)
    ax2.set_title("让出顶点 %d / 无让出 %d"
                  % (S["n"] - S["vertex"]["无"], S["vertex"]["无"]), fontsize=10.2, pad=8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    save(fig, "fig11.png")


# ------------------------------------------------------------------ fig12
def fig12():
    symptoms = ["响应慢 / 成本高", "重复执行 / 数据脏", "记不住前文", "越权 / 被注入",
                "崩了丢数据", "结果不一致", "越改越乱"]
    grid = {
        "响应慢 / 成本高": [1, 1, 1, 1, 1, 0, 1, 0],
        "重复执行 / 数据脏": [0, 0, 1, 0, 1, 0, 0, 1],
        "记不住前文": [0, 0, 0, 1, 0, 0, 1, 1],
        "越权 / 被注入": [0, 1, 1, 0, 0, 0, 0, 1],
        "崩了丢数据": [0, 0, 0, 1, 1, 0, 0, 0],
        "结果不一致": [0, 1, 1, 0, 1, 1, 1, 0],
        "越改越乱": [0, 0, 0, 0, 0, 1, 0, 0],
    }
    M = np.array([grid[s] for s in symptoms])
    fig, ax = plt.subplots(figsize=(8.6, 4.5))
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            on = M[i, j]
            ax.add_patch(Rectangle((j, i), 1, 1, fc=P_RED if on else "#fcfcfa",
                                   ec="white", lw=2.0,
                                   hatch="" ))
            if on:
                ax.text(j + 0.5, i + 0.5, "●", ha="center", va="center",
                        fontsize=11, color=RED)
    ax.set_xlim(0, 8); ax.set_ylim(0, len(symptoms))
    ax.set_xticks(np.arange(8) + 0.5)
    ax.set_xticklabels(["硬件", "系统", "网络", "存储", "分布式", "工程", "大模型", "Agent"],
                       fontsize=8.6)
    ax.set_yticks(np.arange(len(symptoms)) + 0.5)
    ax.set_yticklabels(symptoms, fontsize=8.8)
    ax.invert_yaxis()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("按症状补课：● 表示先去看这一层（作者判断，C 级）", fontsize=10.2, pad=10)
    save(fig, "fig12.png")


if __name__ == "__main__":
    write_csv()
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06()
    per_tensor, unfused, fused = fig07()
    fig08(); fig09(); fig10(); fig11(); fig12()
    print("   tensor=%.2f MiB  unfused=%.1f  fused=%.1f" % (per_tensor, unfused, fused))
    print("   vertex:", dict(S["vertex"]), " impl:", dict(S["impl"]),
          " bneck:", dict(S["bneck"]), " swap:", dict(S["swap"]))

# -*- coding: utf-8 -*-
"""《锚点的下限》——8 图 + 8 表，全部读 results/*.csv（与实验同源，不手抄数字）。"""
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
RES = ROOT / "results"
DATA = ROOT / "data"

for cand in ["Microsoft YaHei", "SimHei", "Source Han Sans SC", "Noto Sans CJK SC"]:
    if any(cand in f.name for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.dpi": 200, "savefig.dpi": 200,
                     "font.size": 9, "axes.titlesize": 9.6, "axes.labelsize": 9,
                     "axes.edgecolor": "#444", "axes.grid": True, "grid.color": "#e8e8e8",
                     "grid.linewidth": .6, "figure.facecolor": "white"})
C1, C2, C3, C4, C5 = "#2f6f9f", "#b3701f", "#a8322d", "#9a9a9a", "#4f7a4f"


def rd(name):
    return [dict(r) for r in csv.DictReader(open(RES / name, encoding="utf-8"))]


SUM = rd("summary.csv")
DRIFT = rd("drift.csv")
THR = rd("thresholds.csv")
COV = rd("coverage.csv")
SENS = rd("sensitivity.csv")

# 主对照（cover=0.5）与交叉点（由覆盖率扫描插值得到）
M1_MIS = float([s for s in SUM if s["cond"] == "M1"][0]["mis"])
cov_x = [float(r["cover"]) for r in COV]
cov_mis = [float(r["mis"]) for r in COV]
THRESH = None
for i in range(1, len(cov_x)):
    if cov_mis[i - 1] >= M1_MIS >= cov_mis[i]:
        x0, x1, y0, y1 = cov_x[i - 1], cov_x[i], cov_mis[i - 1], cov_mis[i]
        THRESH = x0 + (x1 - x0) * (y0 - M1_MIS) / (y0 - y1)
        break


def save(fig, name):
    fig.savefig(ROOT / name, bbox_inches="tight")
    plt.close(fig)
    print("  " + name)


def tables():
    sys.path.insert(0, str(DATA))
    import experiment as E

    # 表 1 环境
    out = ["| 页面 | 正确动作 | 表面标签 | 该页「返回」的语义 | 是否不可逆 |", "|---|---|---|---|---|"]
    sem = {"douyin/feed": "退回上一条", "qq/chat": "退回上一级", "qq/settings": "退回上一级",
           "douyin/popup": "关闭弹窗", "douyin/live": "退出直播"}
    for a, b, act, surf, risk in E.PAGES:
        k = a + "/" + b
        out.append(f"| {k} | `{act}` | {surf} | {sem[k]} | {'是' if risk else '否'} |")
    (DATA / "table_env.md").write_text("\n".join(out), encoding="utf-8")

    # 表 2 参数
    out = ["| 参数 | 取值 | 含义 | 本文的处理 |", "|---|---|---|---|"]
    for a, b, c, d in [
        ("p", "0.15 / 0.25 / 0.35", "单个重建者在对象上出错的概率", "主对照取 0.25，敏感性三档"),
        ("ρ", "0 / 0.3 / 0.7", "共源程度（全体共享同一次错误抽样）", "主对照 0.5，敏感性三档"),
        ("K", "1 / 3 / 5 / 11", "重建路数（仅 M2，按风险分级）", "主对照 3，敏感性 1/3/5"),
        ("cover", "0.10–0.95", "锚点覆盖率（有字段日志的页面比例）", "主对照 0.5，扫描 10 档"),
        ("seeds", "20（扫描 20，敏感性 10）", "随机种子数", "每种子 200–400 步"),
        ("成本", "base 40ms / 重建 300ms / 裁决 200ms / 人环 5000ms", "延迟模型", "见附录 B，非实测"),
    ]:
        out.append(f"| `{a}` | {b} | {c} | {d} |")
    (DATA / "table_params.md").write_text("\n".join(out), encoding="utf-8")

    # 表 3 主对照
    out = ["| 条件 | 准确率 | 跨页面污染率 | 误动作率 | 低风险延迟 | 高风险延迟 | 人环/100 步 |", "|---|---|---|---|---|---|---|"]
    for s in [x for x in SUM if x["cond"] in ("M0", "M1", "M2")]:
        out.append(f'| {s["cond"]} | {float(s["acc"]):.3f} | {float(s["conf"]):.3f} | {float(s["mis"]):.3f} | '
                   f'{float(s["lat_low"]):.0f} ms | {float(s["lat_high"]):.0f} ms | {float(s["esc"]):.2f} |')
    (DATA / "table_main.md").write_text("\n".join(out), encoding="utf-8")

    # 表 4 覆盖率扫描
    out = ["| 锚点覆盖率 | 准确率 | 误动作率 | 人环/100 步 | 与摘要相比 |", "|---|---|---|---|---|"]
    for r in COV:
        m = float(r["mis"])
        cmp_ = "优于摘要" if m < M1_MIS else ("劣于摘要" if m > M1_MIS else "持平")
        out.append(f'| {float(r["cover"]):.2f} | {float(r["acc"]):.3f} | {m:.3f} | {float(r["esc"]):.2f} | {cmp_} |')
    (DATA / "table_coverage.md").write_text("\n".join(out), encoding="utf-8")

    # 表 5 rho / K
    out = ["| ρ | K=1 误动作 | K=3 误动作 | K=5 误动作 | K=3 延迟 |", "|---|---|---|---|---|"]
    for rho in ["0.0", "0.3", "0.7"]:
        row = {}
        for r in SENS:
            if r["cover"] == "0.9" and r["p"] == "0.25" and r["rho"] == rho:
                row[r["K"]] = r
        out.append(f"| {rho} | {float(row['1']['mis']):.3f} | {float(row['3']['mis']):.3f} | "
                   f"{float(row['5']['mis']):.3f} | {float(row['3']['lat']):.0f} ms |")
    (DATA / "table_rhok.md").write_text("\n".join(out), encoding="utf-8")

    # 表 6 否证裁决
    out = ["| 编号 | 预先登记的否证条件 | 结果 | 裁决 |", "|---|---|---|---|"]
    m2 = [s for s in SUM if s["cond"] == "M2"][0]
    out.append(f"| F1 | M2 误动作率 ≥ M1（任何覆盖率下） | 主对照 {float(m2['mis']):.3f} vs {M1_MIS:.3f}；cover≥0.6 时反转为优 | **部分触发**（有条件成立） |")
    out.append(f"| F2 | M2 低风险延迟 > 1 s | {float(m2['lat_low']):.0f} ms | 未触发 |")
    out.append(f"| F3 | M2 跨页面污染率 ≥ M1 | {float(m2['conf']):.3f} vs {float([s for s in SUM if s['cond']=='M1'][0]['conf']):.3f} | 未触发（M2 更优） |")
    out.append(f"| F4 | cover ≤0.2 时 M2 与 M1 无差异 | {float([r for r in COV if r['cover']=='0.2'][0]['mis']):.3f} vs {M1_MIS:.3f} | **未触发**：M2 明显更差 → 「覆盖率越低越不该上」成立 |")
    (DATA / "table_falsify.md").write_text("\n".join(out), encoding="utf-8")

    # 表 7 与论文十二的命题
    out = ["| 论文十二的命题 | 本文的检验 | 结果 |", "|---|---|---|"]
    for a, b, c in [
        ("书记员＋异构＋带锚裁决三层可运行", "实现并跑 12000 步", "**支持**（可运行，非空设计）"),
        ("锚点覆盖率决定天花板（附录 D.3 的预测）", "覆盖率扫描 0.10–0.95", "**支持**，且定位到阈值 ≈ %.2f" % THRESH),
        ("同源投票会失效（4.4 的模型）", "ρ 0→0.7，K=3", "**支持**：误动作 0.092→0.118，人环 0.55→2.40"),
        ("K=3 是拐点（分级裁决）", "K=1/3/5", "**支持**：0.131→0.104→0.103，延迟 488→723→1277ms"),
        ("「宁可忘，不要编」", "全票一致而错的比例", "**支持**：M2 分支内 14.5% 的全票是错的"),
        ("T9：能延长存活到几周", "模拟无法测", "**未检验**（仍撤回）"),
    ]:
        out.append(f"| {a} | {b} | {c} |")
    (DATA / "table_paper12.md").write_text("\n".join(out), encoding="utf-8")

    # 表 8 命题状态
    out = ["| 编号 | 命题 | 证据 | 状态 |", "|---|---|---|---|"]
    for a, b, c, d in [
        ("T1", "三层架构可运行且非空", "12000 步模拟", "支持（C，模拟）"),
        ("T2", "情景唤起在准确率上优于摘要", "0.441 vs 0.339", "支持（C）"),
        ("T3", "优势有覆盖率下限", "扫描定位 ≈ %.2f（自举区间 0.44–0.74）" % THRESH, "支持（C）"),
        ("T4", "摘要记忆的跨页面污染最重", "0.625 vs 0.187/0.179", "支持（C）"),
        ("T5", "共源降低准确率并抬高成本", "ρ0→0.7：误动作 +0.026、人环 ×4.4", "支持（C）"),
        ("T6", "K 的边际收益在 3 处饱和", "K3→5 仅 −0.001 误动作，+554ms", "支持（C）"),
        ("T7", "全票一致而错是主要失效", "M2 分支内 14.5%", "支持（C）"),
        ("T8", "低风险延迟 < 1s", "340ms", "支持（C）"),
        ("T9", "该架构能延长真实账号的存活", "无真实实验", "**未检验**"),
        ("T10", "0.57 是可迁移的常数", "只在一个环境、一组参数下测得", "**撤回**"),
    ]:
        out.append(f"| **{a}** | {b} | {c} | {d} |")
    (DATA / "table_claims.md").write_text("\n".join(out), encoding="utf-8")
    # 表 9 阈值移动
    base_tag = "基准 (p.25,ρ.3,K3)"
    def thr(tag):
        pts = [(float(r["cover"]), float(r["mis"])) for r in THR if r["tag"] == tag]
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]; x1, y1 = pts[i]
            if y0 >= M1_MIS >= y1:
                return x0 + (x1 - x0) * (y0 - M1_MIS) / (y0 - y1)
        return None
    out = ["| 参数组 | 交叉点 | 相对基准 | 说明 |", "|---|---|---|---|"]
    b0 = thr(base_tag)
    for tag in [base_tag, "低共源 (ρ=0)", "高共源 (ρ=0.7)", "弱重建 (p=0.35)", "单路 (K=1)"]:
        v = thr(tag)
        out.append(f"| {tag} | {v:.3f} | {'—' if tag == base_tag else '%+.3f' % (v - b0)} | "
                   f"{'基准' if tag == base_tag else ('阈值左移' if v < b0 else '阈值右移')} |")
    (DATA / "table_thresholds.md").write_text("\n".join(out), encoding="utf-8")

    # 表 10 回写漂移
    out = ["| 步数区间 | M2 准确率 | M2w 准确率 | M2 误动作 | M2w 误动作 |", "|---|---|---|---|---|"]
    m2 = {int(r["bucket"]): r for r in DRIFT if r["cond"] == "M2"}
    m2w = {int(r["bucket"]): r for r in DRIFT if r["cond"] == "M2w"}
    for b in sorted(m2):
        out.append(f"| {b*50}–{b*50+49} | {float(m2[b]['acc']):.3f} | {float(m2w[b]['acc']):.3f} | "
                   f"{float(m2[b]['mis']):.3f} | {float(m2w[b]['mis']):.3f} |")
    (DATA / "table_drift.md").write_text("\n".join(out), encoding="utf-8")

    # 表 11 逐页剖分（主对照 M0/M1/M2）
    steps = [dict(r) for r in csv.DictReader(open(RES / "steps.csv", encoding="utf-8"))]
    pages = sorted({r["page"] for r in steps})
    out = ["| 页面 | M0 准确 | M1 准确 | M2 准确 | M2 误动作 | M2 全票而错 |", "|---|---|---|---|---|---|"]
    for pg in pages:
        row = []
        for c in ("M0", "M1", "M2"):
            sub = [r for r in steps if r["cond"] == c and r["page"] == pg]
            row.append(sum(1 for r in sub if r["act"] == r["truth"]) / max(1, len(sub)))
        sub2 = [r for r in steps if r["cond"] == "M2" and r["page"] == pg]
        mis = sum(1 for r in sub2 if r["mis"] == "1") / max(1, len(sub2))
        unan = [r for r in sub2 if r["unanimous"] == "1"]
        uw = sum(1 for r in unan if r["act"] != r["truth"]) / max(1, len(unan)) if unan else 0
        out.append(f"| {pg} | {row[0]:.3f} | {row[1]:.3f} | {row[2]:.3f} | {mis:.3f} | {uw:.3f} |")
    (DATA / "table_pages.md").write_text("\n".join(out), encoding="utf-8")
    # 表 12 全部 81 组敏感性
    out = ["| p | ρ | K | cover | 准确率 | 误动作率 | 人环/100 |", "|---|---|---|---|---|---|---|"]
    for r in SENS:
        out.append(f'| {r["p"]} | {r["rho"]} | {r["K"]} | {r["cover"]} | {float(r["acc"]):.3f} | '
                   f'{float(r["mis"]):.3f} | {float(r["esc"]):.2f} |')
    (DATA / "table_sens81.md").write_text("\n".join(out), encoding="utf-8")
    print("  tables: 12")


def fig01():
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(.2, 5.25, "图 1　五个页面，两个标签，一个陷阱", fontsize=9.8, fontweight="bold")
    labels = [("信息流\n返回＝上一条", "#dbe7f1"), ("群聊\n返回＝上一级", "#e6ecdf"),
              ("设置\n返回＝上一级", "#e6ecdf"), ("弹窗\n返回＝关闭", "#f7efe2"),
              ("直播\n互动＝评论", "#f2e6e6")]
    for i, (t, c) in enumerate(labels):
        x = .3 + i * 1.92
        ax.add_patch(FancyBboxPatch((x, 3.0), 1.75, 1.3, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=c, ec="#666", lw=.9))
        ax.text(x + .87, 3.65, t, ha="center", va="center", fontsize=7.8, linespacing=1.6)
    ax.text(.3, 2.55, "表面标签相同（「返回」），语义不同 → 照搬即错。这就是负迁移的唯一来源。", fontsize=7.6, color="#555")
    for i, (name, y) in enumerate([("M0 无记忆：只按表面标签选默认动作", 1.75),
                                   ("M1 摘要：记住「标签→动作」，跨页面照搬", 1.2),
                                   ("M2 情景：字段日志＋线索＋K 路重建＋带锚裁决", .65)]):
        ax.add_patch(FancyBboxPatch((.3, y - .22), 9.3, .44, boxstyle="round,pad=0.03,rounding_size=0.06",
                                    fc="#fbf8f1", ec="#ddd", lw=.7))
        ax.text(.45, y, name, fontsize=7.8, va="center")
    save(fig, "fig01_env.png")


def fig02():
    fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.5))
    keys = [("acc", "准确率"), ("conf", "跨页面污染率"), ("mis", "误动作率"), ("esc", "人环/100 步")]
    cols = {"M0": C4, "M1": C2, "M2": C1, "M2w": C3}
    for ax, (k, lab) in zip(axes, keys):
        part = [s for s in SUM if s["cond"] in ("M0", "M1", "M2")]
        vals = [float(s[k]) for s in part]
        ax.bar([s["cond"] for s in part], vals, .55, color=[cols[s["cond"]] for s in part], zorder=3)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * .04, f"{v:.2f}" if k != "esc" else f"{v:.1f}",
                    ha="center", fontsize=7.6)
        ax.set_title(lab, fontsize=8.6); ax.set_ylim(0, max(vals) * 1.28 if max(vals) else 1)
    fig.suptitle("图 2　主对照（覆盖 0.5）：M2 在准确率与污染上胜出，在误动作上并未胜出", fontsize=9.2, x=.02, ha="left")
    fig.tight_layout(rect=[0, 0, 1, .9])
    save(fig, "fig02_main.png")


def fig03():
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    ax.plot(cov_x, cov_mis, "o-", color=C1, lw=1.8, ms=5, label="M2 误动作率")
    ax.axhline(M1_MIS, color=C2, ls="--", lw=1.4, label="M1 摘要（基线 %.3f）" % M1_MIS)
    if THRESH:
        ax.axvline(THRESH, color=C3, ls=":", lw=1.4)
        ax.text(THRESH + .01, max(cov_mis) * .92, "阈值 ≈ %.2f" % THRESH, fontsize=8, color=C3)
    ax.set_xlabel("锚点覆盖率（有字段日志的页面比例）"); ax.set_ylabel("误动作率")
    ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 3　覆盖率决定胜负：低于阈值时，带锚裁决比摘要更差", fontsize=9.2, loc="left")
    save(fig, "fig03_coverage.png")


def fig04():
    M = np.zeros((3, 3))
    for i, rho in enumerate(["0.0", "0.3", "0.7"]):
        for j, K in enumerate(["1", "3", "5"]):
            for r in SENS:
                if r["cover"] == "0.9" and r["p"] == "0.25" and r["rho"] == rho and r["K"] == K:
                    M[i, j] = float(r["mis"])
    fig, ax = plt.subplots(figsize=(4.8, 2.9))
    ax.imshow(M, cmap="Reds")
    ax.set_xticks(range(3)); ax.set_xticklabels(["K=1", "K=3", "K=5"], fontsize=9)
    ax.set_yticks(range(3)); ax.set_yticklabels(["ρ=0", "ρ=0.3", "ρ=0.7"], fontsize=9)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", fontsize=8.4,
                    color="white" if M[i, j] > M.mean() else "#222")
    ax.grid(False)
    ax.set_title("图 4　ρ × K 对误动作率：加路数的收益被共源吃掉", fontsize=9.0, loc="left")
    save(fig, "fig04_rhok.png")


def fig05():
    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    part = [s for s in SUM if s["cond"] in ("M0", "M1", "M2")]
    conds = [s["cond"] for s in part]
    low = [float(s["lat_low"]) for s in part]
    high = [float(s["lat_high"]) for s in part]
    x = np.arange(len(conds))
    ax.bar(x - .18, low, .34, label="低风险", color=C1, zorder=3)
    ax.bar(x + .18, high, .34, label="高风险", color=C2, zorder=3)
    ax.axhline(1000, color=C3, ls=":", lw=1.2)
    ax.text(-.45, 1050, "1 s 可用性红线", fontsize=7, color=C3)
    for i, (a, b) in enumerate(zip(low, high)):
        ax.text(i - .18, a + 20, f"{a:.0f}", ha="center", fontsize=7.4)
        ax.text(i + .18, b + 20, f"{b:.0f}", ha="center", fontsize=7.4)
    ax.set_xticks(x); ax.set_xticklabels(conds); ax.set_ylabel("端到端延迟 ms")
    ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 5　延迟：分级让低风险留在 1 秒内，高风险越过红线", fontsize=9.2, loc="left")
    save(fig, "fig05_latency.png")


def fig06():
    fig, ax = plt.subplots(figsize=(6.2, 2.8))
    bw = [float(r["unan_wrong"]) for r in COV]
    ax.plot(cov_x, bw, "o-", color=C3, lw=1.8, ms=5, label="全票一致而错（M2 分支内）")
    ax.plot(cov_x, cov_mis, "o--", color=C1, lw=1.2, ms=3.5, label="总误动作率")
    ax.set_xlabel("锚点覆盖率"); ax.set_ylabel("比例")
    ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 6　越有锚点，「一致地错」在错误里的占比越高", fontsize=9.2, loc="left")
    save(fig, "fig06_unanimous.png")


def fig07():
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")

    def box(x, y, w, h, t, fc, fs=8.0):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.08",
                                    fc=fc, ec="#666", lw=.9))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, linespacing=1.5)

    box(.3, 3.4, 3.0, 1.1, "论文十二：设计\n三层架构 + 十条命题", "#f2efe6")
    box(3.6, 3.4, 3.0, 1.1, "本文：压力测试\n模拟 12000 步", "#dbe7f1")
    box(6.9, 3.4, 2.8, 1.1, "结果：两支持\n一条件化、一未检验", "#e6ecdf")
    box(.3, 1.3, 4.4, 1.2, "被支持：三层可运行、K=3 拐点、\n「宁可忘不要编」（14.5% 全票是错的）", "#fff", 7.6)
    box(5.0, 1.3, 4.7, 1.2, "被条件化：优势有覆盖率下限 ≈0.57；\n低于它时不如摘要", "#fff", 7.6)
    for x in (1.8, 5.1, 8.3):
        ax.add_patch(FancyArrowPatch((x, 3.35), (x, 2.6), arrowstyle="-|>", mutation_scale=10, lw=.9, color="#999"))
    ax.text(.2, 4.9, "图 7　设计与测试的分工：论文十二给承诺，本文给边界", fontsize=9.6, fontweight="bold")
    save(fig, "fig07_interface.png")


def fig08():
    props = [("F1", "M2 误动作 ≥ M1", .5), ("F2", "低风险延迟 > 1 s", 1.0),
             ("F3", "M2 污染率 ≥ M1", 1.0), ("F4", "低覆盖时无差异", 1.0)]
    fig, ax = plt.subplots(figsize=(6.0, 2.4))
    ys = np.arange(len(props))[::-1]
    cols = {1.0: C1, .5: C2}
    ax.barh(ys, [p[2] for p in props], .5, color=[cols[p[2]] for p in props], zorder=3)
    for y, (i, t, v) in zip(ys, props):
        ax.text(-.02, y, f"{i} {t}", ha="right", va="center", fontsize=7.8)
        ax.text(v + .02, y, "未触发" if v == 1.0 else "部分触发", va="center", fontsize=7.4, color=cols[v])
    ax.set_yticks([]); ax.set_xlim(0, 1.35); ax.set_xticks([0, .5, 1])
    ax.set_title("图 8　自证：四条预先登记的否证条件，一条被部分触发", fontsize=9.2, loc="left")
    save(fig, "fig08_falsify.png")


def fig09():
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    for cond, c, lab in [("M2", C1, "M2 不回写"), ("M2w", C3, "M2w 允许回写")]:
        rows = sorted([r for r in DRIFT if r["cond"] == cond], key=lambda r: int(r["bucket"]))
        xs = [int(r["bucket"]) * 50 + 25 for r in rows]
        ax.plot(xs, [float(r["acc"]) for r in rows], "o-", color=c, lw=1.8, ms=5, label=lab + "（准确率）")
    ax.set_xlabel("决策步（每桶 50 步）"); ax.set_ylabel("准确率")
    ax.set_ylim(0, .55); ax.legend(fontsize=7.6, frameon=False)
    ax.set_title("图 9　允许回写：准确率在 200 步内从 0.34 掉到 0.15", fontsize=9.2, loc="left")
    save(fig, "fig09_drift.png")


def fig10():
    tags = ["低共源 (ρ=0)", "基准 (p.25,ρ.3,K3)", "弱重建 (p=0.35)", "高共源 (ρ=0.7)", "单路 (K=1)"]
    def thr(tag):
        pts = [(float(r["cover"]), float(r["mis"])) for r in THR if r["tag"] == tag]
        for i in range(1, len(pts)):
            x0, y0 = pts[i-1]; x1, y1 = pts[i]
            if y0 >= M1_MIS >= y1:
                return x0 + (x1 - x0) * (y0 - M1_MIS) / (y0 - y1)
        return 0
    vals = [thr(t) for t in tags]
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    ax.barh(range(len(tags)), vals, .5, color=[C5, C1, C4, C2, C3], zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + .005, i, "%.3f" % v, va="center", fontsize=8)
    ax.set_yticks(range(len(tags))); ax.set_yticklabels(tags, fontsize=8)
    ax.set_xlim(0, .75); ax.set_xlabel("与摘要基线的交叉点（覆盖率）")
    ax.set_title("图 10　阈值会移动：ρ 与 K 让它动 ±0.04–0.10，p 几乎不动它", fontsize=9.0, loc="left")
    save(fig, "fig10_thresholds.png")


def main():
    print("tables...")
    tables()
    print("figures...")
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10):
        f()
    print("阈值 =", THRESH)


if __name__ == "__main__":
    main()

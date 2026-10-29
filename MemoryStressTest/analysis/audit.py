# -*- coding: utf-8 -*-
"""校对脚本：核验《锚点的下限》正文与 results/*.csv 是否一致。"""
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
RES = ROOT / "results"
MD = ROOT / "锚点的下限_情景记忆的模拟对照实验.md"
TEXT = MD.read_text(encoding="utf-8")
issues = []


def bad(m):
    issues.append(m)


def rd(name):
    return [dict(r) for r in csv.DictReader(open(RES / name, encoding="utf-8"))]


SUM = {r["cond"]: r for r in rd("summary.csv")}
COV = rd("coverage.csv")
DRIFT = rd("drift.csv")

# 1 占位符
for ph in re.findall(r"<!--TABLE_[A-Z0-9_]+-->", TEXT):
    bad("占位符残留: " + ph)

# 2 图
figs = sorted(p.name for p in ROOT.glob("fig*.png"))
fig_refs = re.findall(r"!\[图 (\d+)\]", TEXT)
if len(set(fig_refs)) != len(figs):
    bad("图引用 %d 处 / 图片 %d 个: %s" % (len(set(fig_refs)), len(figs), figs))
for n in range(1, len(figs) + 1):
    if str(n) not in fig_refs:
        bad("图 %d 未在正文引用" % n)

# 3 表（1–13）
tab_refs = sorted(set(int(x) for x in re.findall(r"表 (\d+)", TEXT)))
if tab_refs != list(range(1, 14)):
    bad("表编号异常: %s" % tab_refs)

# 4 附录
for a in set(re.findall(r"附录 ([A-J]|D2|D3|D4|D5|D6|D7|D8|D9|F2)", TEXT)):
    if ("## 附录 %s" % a) not in TEXT:
        bad("引用不存在的附录: " + a)

# 5 禁用词
for w in ["必然", "不可避免", "注定", "死路", "无法消除"]:
    for m in re.finditer(w, TEXT):
        ctx = TEXT[max(0, m.start() - 16):m.start() + 16].replace("\n", " ")
        bad("宿命词「%s」: …%s…" % (w, ctx))

# 6 关键数字
def near(a, b, tol=1e-9):
    return abs(a - b) < tol

checks = [
    ("M2 准确率", float(SUM["M2"]["acc"]), 0.441),
    ("M1 准确率", float(SUM["M1"]["acc"]), 0.339),
    ("M0 误动作", float(SUM["M0"]["mis"]), 0.390),
    ("M1 污染", float(SUM["M1"]["conf"]), 0.625),
    ("M2 污染", float(SUM["M2"]["conf"]), 0.179),
    ("M2 误动作", float(SUM["M2"]["mis"]), 0.209),
    ("M2w 误动作", float(SUM["M2w"]["mis"]), 0.244),
]
for name, got, want in checks:
    if round(got, 3) != want:
        bad("%s 与正文不符: %.3f ≠ %.3f" % (name, got, want))

# 覆盖率单调性与交叉点
mis = [float(r["mis"]) for r in COV]
if mis != sorted(mis, reverse=True):
    # 允许一处平台（误差），仅提示
    drops = sum(1 for i in range(1, len(mis)) if mis[i] > mis[i - 1] + 1e-9)
    if drops:
        bad("覆盖率曲线不单调（上升 %d 处）" % drops)
if "0.569" not in TEXT and "0.57" not in TEXT:
    bad("正文未出现交叉点")

# 回写漂移：M2w 单调下滑
acc = [float(r["acc"]) for r in DRIFT if r["cond"] == "M2w"]
if acc != sorted(acc, reverse=True):
    bad("M2w 准确率轨迹非单调下降: %s" % acc)

# 7 必备块
for must in ["完成日期：2026-10-26", "李毅芃", "## 摘要", "## Abstract",
             "## 参考文献", "## 附录 A", "## 附录 I"]:
    if must not in TEXT:
        bad("缺少必备块: " + must)

# 8 预注册纪律：否证条件必须出现在结果之前
i_f = TEXT.index("F1")
i_r = TEXT.index("## 4 结果一")
if i_f > i_r:
    bad("否证条件出现在结果之后（违反预注册）")

print("A/B/C 标注 %d 次；图 %d、表 %d" % (len(re.findall(r"\b[ABC] 级", TEXT)), len(figs), len(tab_refs)))
print("\n== 统计 ==")
for c in ("M0", "M1", "M2", "M2w"):
    s = SUM[c]
    print("%-3s acc=%.3f conf=%.3f mis=%.3f esc=%.2f" % (c, float(s["acc"]), float(s["conf"]), float(s["mis"]), float(s["esc"])))
print("覆盖率 0.2/0.5/0.9 的误动作:", [round(float(r["mis"]), 3) for r in COV if r["cover"] in ("0.2", "0.5", "0.9")])

if issues:
    print("\n== 发现 %d 个问题 ==" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n校对通过：无占位符、图表与附录引用齐全、无宿命式表述、数字与结果一致、预注册顺序正确。")

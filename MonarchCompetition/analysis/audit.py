# -*- coding: utf-8 -*-
"""校对脚本：核验正文与数据/图表是否一致。

七类检查：
  1 占位符残留
  2 图引用与文件、编号连续
  3 表引用与编号连续
  4 附录交叉引用是否存在
  5 系列禁用词（宿命式结论）
  6 正文关键数字与 data/ 的统计是否一致
  7 元数据与必备块

用法：python analysis/audit.py
"""
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import prices as P
from data import vendors as V

MD = ROOT / "开明君主与两层竞争_执行方向与代价承担者.md"
TEXT = MD.read_text(encoding="utf-8")
S = P.S
issues = []


def bad(msg):
    issues.append(msg)


# 1 占位符
for ph in re.findall(r"<!--TABLE_[A-Z_]+-->", TEXT):
    bad("占位符残留: " + ph)

# 2 图
figs = sorted(p.name for p in ROOT.glob("fig*.png"))
refs = re.findall(r"!\[图 (\d+)\]", TEXT)
if len(set(refs)) != len(figs):
    bad("图引用数 %d 与图片数 %d 不符: %s" % (len(set(refs)), len(figs), figs))
for n in range(1, len(figs) + 1):
    if str(n) not in refs:
        bad("图 %d 未在正文引用" % n)

# 3 表
tabs = sorted(set(int(x) for x in re.findall(r"表 (\d+)", TEXT)))
if tabs != list(range(1, 9)):
    bad("表引用编号异常: %s" % tabs)

# 4 附录
for a in set(re.findall(r"附录 ([A-O])", TEXT)):
    if ("## 附录 %s" % a) not in TEXT:
        bad("引用不存在的附录: " + a)

# 5 禁用词
for w in ["必然", "不可避免", "注定", "死路", "无法消除", "永远不可能", "彻底摧毁"]:
    for m in re.finditer(w, TEXT):
        ctx = TEXT[max(0, m.start() - 20):m.start() + 20].replace("\n", " ")
        bad("宿命词「%s」: …%s…" % (w, ctx))

# 6 数字一致性
prem = [t["premium"] for t in S["tiers"] if t["premium"]]
checks = [
    ("438 个模型", S["n_models"] == 438),
    ("175 个", S["n_open"] == 175),
    ("294", S["n_rjs"] == 294),
    ("34.5", abs(S["rjs_med"] - 34.5) < .05),
    ("50.0", abs(S["rjs_closed"][1] - 50.0) < .05),
    ("18.9", abs(S["rjs_open"][1] - 18.9) < .05),
    ("$0.65", abs(S["out_open"][1] - 0.65) < .01),
    ("$4.46", abs(S["out_closed"][1] - 4.46) < .01),
    ("6.9", abs(S["out_ratio"] - 6.9) < .05),
    ("$6.00", abs(S["vintage_first"][1] - 6.00) < .01),
    ("$5.00", abs(S["vintage_last"][1] - 5.00) < .01),
    ("$0.60", abs(S["vintage_last"][0] - 0.60) < .01),
    ("21.3", abs(statistics.median(prem) - 21.3) < .05),
    ("6／9", len(prem) == 6),
    ("83.3", abs(max(prem) - 83.3) < .05),
    ("2.9", abs(min(prem) - 2.9) < .05),
    ("$12.6", abs(min(s[2] for s in V.SEATS) - 12.6) < .01),
    ("$200", max(s[2] for s in V.SEATS) == 200),
    ("0.53", abs(P.CF["ctx"][1] - 0.532) < .005),
    ("16.0", P.CF["quartile_all"][0][2] == 16.0),
    ("29.7", P.CF["quartile_all"][1][2] == 29.7),
    ("60.0", P.CF["quartile_all"][3][2] == 60.0),
    ("262K", P.CF["ctx_med"][0] == 262),
]
for s, ok in checks:
    if not ok:
        bad("数据与正文预期不符: " + s)

# 关键数字必须真的出现在正文里
for must in ["34.5", "18.9", "50.0", "21.3", "83.3", "2.9", "128.4", "0.5 万亿",
             "250 倍", "73%", "79%", "62%", "69%", "200", "$0.003", "$12.6", "$20"]:
    if must not in TEXT:
        bad("正文缺关键数字: " + must)

# 7 元数据
for must in ["完成日期：2026-10-28", "李毅芃", "## 摘要", "## Abstract",
             "## 参考文献", "## 附录 A", "## 附录 M", "## 附录 O", "## 13 自证"]:
    if must not in TEXT:
        bad("缺少必备块: " + must)

n_grade = len(re.findall(r"\b[ABC] 级", TEXT))
print("A/B/C 标注出现 %d 次" % n_grade)
print("\n== 统计 ==")
print("RJS 中位 %.1f（n=%d）；开放 %.1f vs 闭源 %.1f" %
      (S["rjs_med"], S["n_rjs"], S["rjs_open"][1], S["rjs_closed"][1]))
print("输出价 开放 %s 闭源 %s（%.1f 倍）" % (S["out_open"], S["out_closed"], S["out_ratio"]))
print("vintage %s → %s" % (S["vintage_first"], S["vintage_last"]))
print("双层 %d／9，溢价 %s 中位 %.1f" % (len(prem), sorted(prem), statistics.median(prem)))
print("T 分：", {v["lab"]: v["T"] for v in V.VENDORS})

if issues:
    print("\n== 发现 %d 个问题 ==" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n校对通过：无占位符、图表与附录引用齐全、无宿命式表述、数字与数据一致。")

# -*- coding: utf-8 -*-
"""校对脚本：核验《领域的剖面》正文与数据/图表是否一致。

检查五类问题：
  1. 占位符残留
  2. 图表引用与文件、索引是否对得上
  3. 章节/附录交叉引用是否存在
  4. 系列禁用词（宿命式结论）
  5. 正文数字与 data/domains.py 的统计是否一致

用法：python analysis/audit.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import domains as D

MD = ROOT / "领域的剖面_四个问题与二十个领域的审计.md"
SRC = MD
TEXT = SRC.read_text(encoding="utf-8")
S = D.stats()
issues = []


def bad(msg):
    issues.append(msg)


# 1 占位符
for ph in re.findall(r"<!--TABLE_[A-Z_]+-->", TEXT):
    bad("占位符残留: " + ph)

# 2 图
figs = sorted(p.name for p in ROOT.glob("fig*.png"))
fig_refs = re.findall(r"!\[图 (\d+)\]", TEXT)
if len(set(fig_refs)) != len(figs):
    bad("图引用数 %d 与图片数 %d 不符: %s" % (len(set(fig_refs)), len(figs), figs))
for n in range(1, len(figs) + 1):
    if str(n) not in fig_refs:
        bad("图 %d 未在正文引用" % n)

# 3 表
tab_refs = sorted(set(int(x) for x in re.findall(r"表 (\d+)", TEXT)))
if tab_refs != list(range(1, 9)):
    bad("表引用编号异常: %s" % tab_refs)

# 4 附录交叉引用
for a in set(re.findall(r"附录 ([A-M]|J2)", TEXT)):
    if ("## 附录 %s" % a) not in TEXT:
        bad("引用不存在的附录: " + a)

# 5 禁用词
for w in ["必然", "不可避免", "注定", "死路", "无法消除", "永远不可能"]:
    for m in re.finditer(w, TEXT):
        ctx = TEXT[max(0, m.start() - 18):m.start() + 18].replace("\n", " ")
        bad("宿命词「%s」: …%s…" % (w, ctx))

# 6 数字一致性
acts = S["actions"]
checks = [
    ("拆分 %d/20" % acts["拆分"], acts["拆分"] == 19),
    ("预计算 %d/20" % acts["预计算"], acts["预计算"] == 17),
    ("合并 %d/20" % acts["合并"], acts["合并"] == 2),
]
for s, ok in checks:
    if not ok:
        bad("数据与正文预期不符: " + s)
q3 = S["q3"]
if (q3["A"], q3["B"], q3["C"]) != (6, 13, 1):
    bad("可写性分布变了: %s" % dict(q3))
if S["swaps"] != 5:
    bad("改判数变了: %d" % S["swaps"])
visA = (S["cross"][("A", "在场")] + S["cross"][("A", "延迟")]) / 6 * 100
visB = (S["cross"][("B", "在场")] + S["cross"][("B", "延迟")]) / 13 * 100
if round(visA) != 67 or round(visB) != 31:
    bad("可见代价占比变了: %.1f / %.1f" % (visA, visB))
if S["q1a"].get("预算", 0) != 0:
    bad("预算主瓶颈数变了")
if S["q3"]["C"] != 1:
    bad("C 级领域数变了")

# 7 元数据一致性
for must in ["完成日期：2026-10-28", "李毅芃", "## 摘要", "## Abstract",
             "## 参考文献", "## 附录 A", "## 附录 L"]:
    if must not in TEXT:
        bad("缺少必备块: " + must)

# 8 等级标注密度
n_grade = len(re.findall(r"\b[ABC] 级", TEXT))
print("A/B/C 标注出现 %d 次" % n_grade)

print("\n== 统计 ==")
print("瓶颈主:", dict(S["q1a"]), " 次:", dict(S["q1b"]))
print("动作:", acts)
print("可写性:", dict(S["q3"]), " 承担者:", dict(S["q4"]), " 在场性:", dict(S["presence"]))
print("改判:", S["swaps"], S["swap_ids"])

if issues:
    print("\n== 发现 %d 个问题 ==" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n校对通过：无占位符、图表与附录引用齐全、无宿命式表述、数字与数据一致。")

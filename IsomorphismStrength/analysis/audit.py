# -*- coding: utf-8 -*-
"""校对脚本：核验《同构的强度》正文与 data/motifs.py 是否一致。"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import motifs as M

MD = ROOT / "同构的强度_对偶与泛性质与不变量与四十条断裂探针.md"
TEXT = MD.read_text(encoding="utf-8")
S = M.stats()
issues = []


def bad(m):
    issues.append(m)


# 1 占位符
for ph in re.findall(r"<!--TABLE_[A-Z_]+-->", TEXT):
    bad("占位符残留: " + ph)

# 2 图
figs = sorted(p.name for p in ROOT.glob("fig*.png"))
fig_refs = re.findall(r"!\[图 (\d+)\]", TEXT)
if len(set(fig_refs)) != len(figs):
    bad("图引用数 %d 与图片数 %d 不符" % (len(set(fig_refs)), len(figs)))
for n in range(1, len(figs) + 1):
    if str(n) not in fig_refs:
        bad("图 %d 未在正文引用" % n)

# 3 表
tab_refs = sorted(set(int(x) for x in re.findall(r"表 (\d+)", TEXT)))
if tab_refs != list(range(1, 9)):
    bad("表引用编号异常: %s" % tab_refs)

# 4 附录
for a in set(re.findall(r"附录 ([A-O]|J2)", TEXT)):
    if ("## 附录 %s" % a) not in TEXT:
        bad("引用不存在的附录: " + a)

# 5 禁用词
for w in ["必然", "不可避免", "注定", "死路", "无法消除"]:
    for m in re.finditer(w, TEXT):
        ctx = TEXT[max(0, m.start() - 18):m.start() + 18].replace("\n", " ")
        bad("宿命词「%s」: …%s…" % (w, ctx))

# 6 数字一致性
st = S["strength"]
if (st["严格"], st["伴随"], st["函子"], st["比喻"]) != (12, 5, 12, 11):
    bad("强度分布变了: %s" % dict(st))
lay = S["layer"]
if (lay["复合"], lay["等价"], lay["态射"], lay["对象"]) != (16, 12, 8, 4):
    bad("断裂层分布变了: %s" % dict(lay))
tb = S["trans_by_strength"]
rates = {k: round(v[0] / v[1] * 100) for k, v in tb.items()}
if (rates["严格"], rates["伴随"], rates["函子"], rates["比喻"]) != (17, 60, 50, 36):
    bad("负迁移率变了: %s" % rates)
if S["trans"]["Y"] != 15:
    bad("负迁移条数变了: %d" % S["trans"]["Y"])
group = S["group"]
if group["泛性质"] != 10:
    bad("母题组条数变了")
meta_share = sum(1 for r in M.rows() if r["group"] == "泛性质" and r["strength"] == "比喻")
if meta_share != 6:
    bad("泛性质比喻条数变了: %d" % meta_share)
strict_eq = sum(1 for r in M.rows() if r["strength"] == "严格" and r["layer"] == "等价")
if strict_eq != 11:
    bad("严格档等价层断裂数变了: %d" % strict_eq)

# 7 必备块
for must in ["完成日期：2026-10-28", "李毅芃", "## 摘要", "## Abstract",
             "## 参考文献", "## 附录 A", "## 附录 O"]:
    if must not in TEXT:
        bad("缺少必备块: " + must)

# 8 表 8 的九条降档必须与文本一致
for code in ["M04", "M06", "M09", "M16", "M24", "M29", "M31", "M36", "M39"]:
    if code not in TEXT:
        bad("表 8 中的降档条目缺失: " + code)

print("A/B/C 标注出现 %d 次" % len(re.findall(r"\b[ABC] 级", TEXT)))
print("\n== 统计 ==")
print("强度:", dict(st), " 断裂层:", dict(lay), " 负迁移:", dict(S["trans"]))
print("母题组:", dict(group), " 负迁移率:", rates)

if issues:
    print("\n== 发现 %d 个问题 ==" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n校对通过：无占位符、图表与附录引用齐全、无宿命式表述、数字与数据一致。")

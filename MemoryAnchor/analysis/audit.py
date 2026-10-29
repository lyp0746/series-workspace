# -*- coding: utf-8 -*-
"""校对脚本：核验《记忆的锚点》正文与 data/schemes.py 是否一致。"""
import pathlib
import re
import sys
from math import comb

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data import schemes as S

MD = ROOT / "记忆的锚点_情景唤起与异构重建与日志裁决.md"
TEXT = MD.read_text(encoding="utf-8")
ST = S.stats()
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
    bad("图引用 %d 处 / 图片 %d 个不匹配: %s" % (len(set(fig_refs)), len(figs), figs))
for n in range(1, len(figs) + 1):
    if str(n) not in fig_refs:
        bad("图 %d 未在正文引用" % n)

# 3 表
tab_refs = sorted(set(int(x) for x in re.findall(r"表 (\d+)", TEXT)))
if tab_refs != list(range(1, 9)):
    bad("表编号异常: %s" % tab_refs)

# 4 附录
for a in set(re.findall(r"附录 ([A-J]|D2|D3|D4|D5|D6|D7)", TEXT)):
    if ("## 附录 %s" % a) not in TEXT:
        bad("引用不存在的附录: " + a)

# 5 禁用词
for w in ["必然", "不可避免", "注定", "死路", "无法消除"]:
    for m in re.finditer(w, TEXT):
        ctx = TEXT[max(0, m.start() - 16):m.start() + 16].replace("\n", " ")
        bad("宿命词「%s」: …%s…" % (w, ctx))

# 6 数字一致性
if ST["anchor"]["有"] != 2 or ST["anchor"]["部分"] != 2:
    bad("锚点分布变了: %s" % dict(ST["anchor"]))
if round(ST["anchor"]["有"] + ST["anchor"]["部分"] * 0.5, 1) != 3.0:
    bad("锚点「折半后」不等于 3")
if ST["hetero"]["跨模型"] != 1:
    bad("跨模型异构数变了: %d" % ST["hetero"]["跨模型"])
if ST["judge"]["带锚裁决"] != 2:
    bad("带锚裁决数变了: %d" % ST["judge"]["带锚裁决"])
if ST["trio"] != 1:
    bad("三件套齐备数变了: %d" % ST["trio"])
if ST["fail"]["窗口满"] != 2:
    bad("窗口满例数变了: %d" % ST["fail"]["窗口满"])
if ST["fail"]["检索噪声"] != 3:
    bad("检索噪声例数变了: %d" % ST["fail"]["检索噪声"])
if ST["fail"]["摘要漂移"] != 2:
    bad("摘要漂移例数变了: %d" % ST["fail"]["摘要漂移"])
if ST["fail"]["共识幻觉"] != 1:
    bad("共识幻觉例数变了")

# 7 共模模型的三个数（p=0.2, n=11）
def tail(k, p=0.2):
    return sum(comb(k, j) * p ** j * (1 - p) ** (k - j) for j in range(k // 2 + 1, k + 1))


e0, e7 = tail(11, 0.2), 0.7 * 0.2 + 0.3 * tail(11, 0.2)
if f"{e0*100:.1f}%" != "1.2%":
    bad("ρ=0 的多数派错误率与正文不符: %.3f" % (e0 * 100))
if round(e7 * 100) != 14:
    bad("ρ=0.7 的多数派错误率与正文不符: %.1f%%" % (e7 * 100))

# 8 必备块
for must in ["完成日期：2026-10-26", "李毅芃", "## 摘要", "## Abstract",
             "## 参考文献", "## 附录 A", "## 附录 J"]:
    if must not in TEXT:
        bad("缺少必备块: " + must)

# 9 元数据一致性：标题里的三个关键词
if "记忆的锚点" not in TEXT.splitlines()[0]:
    bad("标题行异常")

print("A/B/C 标注出现 %d 次" % len(re.findall(r"\b[ABC] 级", TEXT)))
print("\n== 统计 ==")
print("锚点:", dict(ST["anchor"]), " 异构:", dict(ST["hetero"]), " 裁判:", dict(ST["judge"]))
print("失效:", dict(ST["fail"]), " 等级:", dict(ST["grade"]))
print("三件套:", ST["trio"], ST["trio_ids"], " 平均线索维度: %.2f" % ST["mean_cues"])
print("共模: ρ=0 → %.2f%%, ρ=0.7 → %.1f%%" % (e0 * 100, e7 * 100))

if issues:
    print("\n== 发现 %d 个问题 ==" % len(issues))
    for i in issues:
        print("  -", i)
    sys.exit(1)
print("\n校对通过：无占位符、图表与附录引用齐全、无宿命式表述、数字与数据一致。")

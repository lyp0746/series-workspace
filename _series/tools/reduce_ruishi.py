# -*- coding: utf-8 -*-
"""降低“如实/诚实”的修辞密度：保留具体动作（如实标注/写出/记录/报告），
把自我指涉的名词化用法换成可核对的实词。目标 ≤8 次/本。"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXED = [
    ("如实性", "可核对性"),
    ("如实度", "可核对程度"),
    ("“如实”的", "“可核对”的"),
    ("更如实", "更准确"),
    ("最如实", "最保守"),
    ("一种如实", "一种交代"),
    ("如实形态", "交代形态"),
    ("如实的代价", "标注的代价"),
    ("如实的边界", "边界"),
    ("如实的用法", "这一栏的用法"),
    ("如实的说法", "准确的说法"),
    ("如实的引用", "可核对的引用"),
    ("如实的书", "可信的书"),
    ("如实的框架", "可核对的框架"),
    ("如实的判断", "可核对的判断"),
    ("如实的观察", "可核对的观察"),
    ("如实的分级", "分级"),
    ("如实清单", "缺口清单"),
    ("如实的检验面", "可检验的面"),
    ("如实性的检验面", "可检验的面"),
    ("本书是否如实", "本书是否站得住"),
    ("本书的如实", "本书的可信"),
    ("本书确实如实", "本书确实站得住"),
    ("如实的记录", "记录"),
    ("如实的标注", "标注"),
    ("如实的地图", "准确的地图"),
    ("如实的位置", "真实的位置"),
    ("如实的一页", "可核对的一页"),
    ("如实地说出", "如实说出"),
    ("如实地", "准确地"),
]
KEEP = ("如实标注", "如实写出", "如实记录", "如实报告", "如实交代", "如实归因",
        "如实说出", "如实呈现", "如实登记", "如实统计")


def fix(p):
    s = open(p, encoding="utf-8").read()
    o = s
    for a, b in FIXED:
        s = s.replace(a, b)
    # 剩下的“如实的X”直接去掉形容词（X 不是具体动作时）
    s = re.sub(r"如实的(?=[\u4e00-\u9fff])", "", s)
    if s != o:
        open(p, "w", encoding="utf-8").write(s)
        return True
    return False


if __name__ == "__main__":
    n = 0
    for f in glob.glob(os.path.join(ROOT, "*/source/*.html")):
        n += fix(f)
    print("files changed:", n)
    for b in ["capacity-cascade", "distinction-evolution", "emergence-critical", "entropy-spiral",
              "impossibility-triangle", "interpretation-tradeoff", "knowledge-tradeoffs",
              "mind-forks", "hotspot-bills"]:
        s = "".join(open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(ROOT, b, "source", "*.html")))
        s = re.sub("<[^>]+>", "", s)
        print(f"{b:24s} 如实/诚实 = {len(re.findall('如实|诚实', s))}")

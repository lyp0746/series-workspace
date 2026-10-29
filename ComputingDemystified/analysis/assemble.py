# -*- coding: utf-8 -*-
"""把账本注入正文：source/paper.md → 术语的账单_从芯片到Agent的八十个计算机概念.md

占位符：
  <!--LAYER_TABLE_i-->   第 i 层的术语账本（i=1..8）
  <!--APPENDIX_A-->      六十条术语总表

表格与图、CSV 同源（data/concepts.py），避免正文与数据打架。
运行：python analysis/assemble.py
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(ROOT, "data"))
from concepts import TERMS, LAYERS, stats  # noqa: E402
from families import FAMILIES, audit  # noqa: E402

SRC = os.path.join(ROOT, "source", "paper.md")
OUT = os.path.join(ROOT, "术语的账单_从芯片到Agent的八十个计算机概念.md")

LAYER_CN = {
    1: "硬件与体系结构的术语账本",
    2: "操作系统的术语账本",
    3: "网络的术语账本",
    4: "存储的术语账本",
    5: "分布式的术语账本",
    6: "工程的术语账本",
    7: "大模型的术语账本",
    8: "Agent 的术语账本",
}


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def layer_table(i):
    L = LAYERS[i - 1]
    rows = [t for t in TERMS if t["layer"] == L]
    out = []
    out.append("| 术语（英） | 瓶颈→置换 | 最朴素实现 | Agent 影子 | 顶点·证据·概念 |")
    out.append("|---|---|---|---|---|")
    for t in rows:
        out.append("| %s（%s） | %s→%s | `%s` | %s | %s·%s·%s |" % (
            t["term"], t["en"], t["bneck"], t["swap"], cell(t["impl"]),
            cell(t["shadow"]), t["cat"], t["grade"], t["cgrade"]))
    out.append("")
    out.append("*表 %d　%s。实现一列是核心机制，不是完整实现；阴影一列是它在 Agent 里"
               "重演的位置。由 `concepts.csv` 生成。*" % (i + 3, LAYER_CN[i]))
    return "\n".join(out)


def appendix_a():
    out = ["| 层 | 术语 | 瓶颈→置换 | 核心实现 | 顶点·写·证 |",
           "|---|---|---|---|---|"]
    for t in TERMS:
        impl = t["impl"]
        if len(impl) > 30:
            impl = impl[:29] + "…"
        out.append("| %d | %s | %s→%s | `%s` | %s·%s·%s |" % (
            LAYERS.index(t["layer"]) + 1, t["term"], t["bneck"], t["swap"],
            cell(impl), t["cat"], t["impl_g"], t["grade"]))
    out.append("")
    out.append("*表 A1　%d 条术语总表。顶点列：C 完备 / A 可组合 / T 传递 / 无（纯资源置换）；"
               "写列：A 能写成可运行核心 / B 能写示意但工程量大 / C 写不出公认的极简核心；"
               "证：A/B/C 为证据等级，概念等级见 `concepts.csv` 的 cgrade 列。"
               "核心实现超过 30 字符的截断，全文见 CSV。由 `concepts.csv` 生成。*" % len(TERMS))
    return "\n".join(out)


def appendix_f():
    a = audit()
    if a["uncovered"] or a["missing_terms"] or a["orphans"]:
        raise SystemExit("家族覆盖核对未通过: %s" % a)
    out = ["| 层 | 机制家族 | 家族的定义 | 代表术语 | 条数 |",
           "|---|---|---|---|---|"]
    for layer, fam, defn, terms in FAMILIES:
        out.append("| %d | %s | %s | %s | %d |" % (
            LAYERS.index(layer) + 1, fam, defn, "、".join(terms), len(terms)))
    out.append("")
    out.append("*表 F1　%d 个机制家族与八十条术语的对应。每个家族至少一条代表，"
               "每条术语至少属于一个家族；由 `data/families.py` 自动核对（运行该文件可复现）。*"
               % len(FAMILIES))
    return "\n".join(out)


def main():
    text = open(SRC, encoding="utf-8").read()
    for i in range(1, 9):
        ph = "<!--LAYER_TABLE_%d-->" % i
        if ph not in text:
            raise SystemExit("missing placeholder: " + ph)
        text = text.replace(ph, layer_table(i))
    if "<!--APPENDIX_A-->" not in text:
        raise SystemExit("missing placeholder: <!--APPENDIX_A-->")
    text = text.replace("<!--APPENDIX_A-->", appendix_a())
    if "<!--APPENDIX_F-->" in text:
        text = text.replace("<!--APPENDIX_F-->", appendix_f())

    # 摘要里的数字由账本核对
    s = stats()
    assert s["n"] == len(TERMS) and s["n"] >= 80
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)

    chars = len(text)
    cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    print("   %s  (%s chars, %s CJK)" % (os.path.basename(OUT),
                                         format(chars, ","), format(cn, ",")))
    print("   vertex:", dict(s["vertex"]), " impl:", dict(s["impl"]))


if __name__ == "__main__":
    main()

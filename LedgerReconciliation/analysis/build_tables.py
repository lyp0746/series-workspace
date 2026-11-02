# -*- coding: utf-8 -*-
"""从 data/ledger.py 重新生成对账表（单一数据源）。

此前 table_bycore / table_bystatus / table_crosstab 停留在 48 条时代，
与正文 110/126 条不一致。本脚本把五张计数表全部重算，避免“正文改了、表没改”。
"""
import pathlib
import sys
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from data import ledger as L

D = BASE / "data"
ROWS = L.rows()
S = L.stats()


def write(name, lines):
    (D / name).write_text("\n".join(lines), encoding="utf-8")
    print("  " + name)


def main():
    # 1 逐条总表
    out = ["| 篇 | 编号 | 命题 | 检验 | 结果 | 状态 | 等级 | 主核 | 尺度 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        out.append(f'| {r["paper"]} | {r["pid"]} | {r["stmt"]} | {r["test"]} | {r["result"]} | '
                   f'{r["status"]} | {r["grade"]} | {r["core"]} | {r["scale"]} |')
    write("table_ledger.md", out)

    # 2 按核心重排
    out = ["| 核心 | 编号 | 命题 | 状态 | 等级 | 尺度 |", "|---|---|---|---|---|---|"]
    for c in L.CORES:
        for r in [x for x in ROWS if x["core"] == c]:
            out.append(f'| {c} | {r["paper"]}·{r["pid"]} | {r["stmt"]} | {r["status"]} | {r["grade"]} | {r["scale"]} |')
    write("table_bycore.md", out)

    # 3 按状态归组
    out = ["| 状态 | 命题（篇·编号） |", "|---|---|"]
    for st in L.STATUS:
        ids = [f'{r["paper"]}·{r["pid"]}' for r in ROWS if r["status"] == st]
        out.append(f'| **{st}**（{len(ids)} 条） | ' + "；".join(ids) + " |")
    write("table_bystatus.md", out)

    # 4 尺度计数
    out = ["| 尺度 | 容量 | 压缩 | 遗忘 | 恢复 | 本文样本中的命题数 |",
           "|---|---|---|---|---|---|"]
    desc = {
        "个体": ("工作记忆槽位", "组块化", "痕迹衰退／检索失败", "再认、提示"),
        "共同体": ("合法问题名额／可见名额", "判为不合法／异常／错类", "索引断裂", "新解码器"),
        "制度": ("编制、额数、编码槽位", "并镇、裁撤、名分收缩", "档案缺失／名分取消", "重新设官／复名"),
        "谱系": ("基因库多样性／调控组合容量", "选择淘汰、本地适应", "漂变、生态位丧失", "杂交、水平转移"),
        "命题": ("可陈述内容的空间", "范式压缩", "残余不可检", "解码器跃迁"),
    }
    for sc in ["个体", "共同体", "制度", "谱系", "命题"]:
        a, b, c, d = desc[sc]
        out.append(f'| {sc} | {a} | {b} | {c} | {d} | **{S["by_scale"].get(sc, 0)}** |')
    write("table_scale.md", out)

    # 5 篇 × 状态交叉表
    out = ["| 篇 | " + " | ".join(L.STATUS) + " | 合计 |",
           "|---|" + "---:|" * (len(L.STATUS) + 1)]
    for p in L.PAPERS:
        rs = [r for r in ROWS if r["paper"] == p]
        vals = [sum(1 for r in rs if r["status"] == st) for st in L.STATUS]
        out.append(f'| {L.TITLES[p]} | ' + " | ".join(str(v) if v else "·" for v in vals) + f' | {len(rs)} |')
    vals = [S["by_status"].get(st, 0) for st in L.STATUS]
    out.append("| **合计** | " + " | ".join(f"**{v}**" for v in vals) + f' | **{S["n"]}** |')
    write("table_crosstab.md", out)

    # 6 篇 × 状态（正文 4.11 用）
    out = ["| 篇 | 条数 | 成立 | 支持 | 部分 | 待检验 | 开放 | 证伪 | 撤回 |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for p in L.PAPERS:
        rs = [r for r in ROWS if r["paper"] == p]
        vals = [sum(1 for r in rs if r["status"] == st) for st in L.STATUS]
        out.append(f'| {L.TITLES[p]} | {len(rs)} | ' + " | ".join(str(v) if v else "·" for v in vals) + " |")
    out.append(f'| **合计** | **{S["n"]}** | ' + " | ".join(f'**{S["by_status"].get(st,0)}**' for st in L.STATUS) + " |")
    write("table_papers.md", out)

    print("rows", S["n"], "status", dict(S["by_status"]), "grade", dict(S["by_grade"]))


if __name__ == "__main__":
    main()

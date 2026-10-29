# -*- coding: utf-8 -*-
"""把生成的表注入 source/paper.md，输出正文 Markdown。

注入点：
  <!--TABLE2-->         表 2　三组传统（来源级／模板级）
  <!--TABLE5-->         表 8　来源清单（核心＋扩展）
  <!--TABLE9-->         表 9　可证伪登记
  <!--APPENDIX_TABLE--> 表 10　全部边界
"""
import csv
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "data"))
from schemes import SOURCE_NOTE  # noqa: E402

SRC = os.path.join(BASE, "source", "paper.md")
OUT = os.path.join(BASE, "门的数目_六十部世界史分期.md")
CSV = os.path.join(BASE, "data", "schemes.csv")
STATS = os.path.join(BASE, "data", "stats.json")

TRAD = [("european", "欧洲中心"), ("global", "全球史"), ("china", "中国教材")]
TRAD_CN = {"european": "欧洲中心", "global": "全球史", "china": "中国教材",
           "other": "补充（维基）", "premodern_europe": "前现代欧洲",
           "islamic": "伊斯兰", "african": "非洲", "south_asian": "南亚",
           "east_asian_premodern": "东亚（前现代）", "americas": "美洲"}
SCOPE_CN = {"world": "世界", "region": "区域", "nation": "国别"}
GENRE_CN = {"survey": "教材/通史", "reference": "工具书", "argument": "论证",
            "curriculum": "课程框架", "chronicle": "编年史",
            "sacred_history": "圣史", "treatise": "论说"}
LEVEL_CN = {"part": "顶层", "chapter": "章级"}
ERA_CN = {"ancient": "古代", "medieval": "中世纪", "early_modern": "近代早期",
          "modern": "近代", "contemporary": "当代", "sacred": "圣史"}
NAME_CN = {"event": "事件", "process": "过程", "space": "空间",
           "dynastic": "王朝", "sacred": "圣史", "era": "时代"}


def pct(x):
    return "%.0f%%" % (x * 100)


def table2(stats):
    W, T = stats["W2"], stats["W2T"]
    out = ["| 传统 | 来源数 | 边界数 | 顶层中位年 | 近代起点中位 | 1000—1225 | 1750±15 | 1640 | 1917 | 1500 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for t, cn in TRAD:
        d, d2 = W[t], T[t]
        cell = lambda k: "%s／%s" % (pct(d[k]), pct(d2[k]))  # noqa: E731
        out.append("| %s | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            cn, d["n"], d["n_b"], round(d["median_part"]),
            "—" if d["median_ms"] is None else "%d" % round(d["median_ms"]),
            cell("pre"), cell("late"), cell("y1640"), cell("y1917"), cell("y1500")))
    out.append("")
    out.append("*表 2　三组传统的边界位置。斜杠前为来源级比例，斜杠后为模板级比例；"
               "中国教材不含 3 部国别通史。Kruskal–Wallis H=%.1f，p=%.5f。*"
               % (W["kruskal"]["H"], W["kruskal"]["p"]))
    return "\n".join(out)


def table8(stats):
    src = stats["SOURCES"]
    rank = {"european": 0, "global": 1, "china": 2, "other": 3,
            "premodern_europe": 4, "islamic": 5, "african": 6,
            "east_asian_premodern": 7, "south_asian": 8, "americas": 9}
    items = sorted(src.items(), key=lambda kv: (rank[kv[1]["tradition"]],
                                                kv[1]["year_published"], kv[0]))
    out = ["| 来源 | 版次 | 传统 | 体裁·范围 | 顶层边界年 | 备注 |",
           "|---|---|---|---|---|---|"]
    for name, m in items:
        years = "、".join(str(y) for y in m["part"]) or "—"
        gr = "%s·%s" % (GENRE_CN.get(m["genre"], m["genre"]),
                        SCOPE_CN.get(m["scope"], m["scope"]))
        out.append("| %s | %d | %s | %s | %s | %s |" % (
            name, m["year_published"], TRAD_CN.get(m["tradition"], m["tradition"]),
            gr, years, SOURCE_NOTE.get(name, "")))
    out.append("")
    out.append("*表 8　来源清单（%d 部）。核心 46 部按传统、版次排序；扩展 14 部列于其后。"
               "顶层边界年为分析窗内的部／卷／单元级边界，章级边界见附录 D。*" % len(items))
    return "\n".join(out)


def table9():
    rows = [
        ("W1", "边界年集中在少数年份，机制是模板复制", "B／乙",
         "来源级前十 69.7%（零模型 10.1%）；模板级 75.0%（26.3%）", "成立"),
        ("W2", "三组传统在 1000—1225、1750、1640、1917 上不同", "B／乙",
         "64% 对 13%（p=0.008）；71% 对 7%（p=0.0005）；1640/1917 为中国教材专有", "成立"),
        ("W3", "组内分区距离小于组间", "B／乙",
         "ARI 0.651 对 0.508，Δ=0.143，p=0.0005；传统解释 R²=0.29", "成立（但效应中等）"),
        ("W4", "分辨率随范围上升：世界 > 区域 > 国别", "B／乙",
         "反向：世界 3.5 < 国别 3.7 < 区域 4.9（p=0.008）；旧口径 11.4 为跨度伪影", "失败"),
        ("W5", "1500 主断点：欧洲 >50%，全球 <30%", "B／乙",
         "73% 对 71%（p=1.0）；改为出现率／分量／排他性三量", "部分失败"),
        ("W6", "出版年漂移，方向由传统决定", "C／丙",
         "ρ=−0.01／−0.48／−0.41，均不显著；仅 AP 一例版本对照", "未获支持"),
        ("W7", "欧洲／中国贴事件年，全球史贴进程年", "B／乙",
         "82.8／69.1% 贴事件年；全球史 51.1% 贴进程年", "成立"),
        ("W8", "命名类型与年份标记同构；同切线多异名", "B／乙",
         "三组命名构成分离；668 对同切线中 63% 异名", "成立"),
        ("W9", "复编 κ≥0.7", "A／甲",
         "年份 1.00、时代 0.87、层级 0.53、整行 0.80", "部分失败（层级）"),
        ("W10", "边界年是现代教材体裁的变量", "B／乙（描述）",
         "14 部中 9 部印年（5 套纪年；全语料 6 套）；核心门与扩展语料仅 589 重合", "成立（描述层）"),
        ("R1", "交叉曲线是边际分布的恒等式", "A／甲",
         "587 对；R²=1.0000，最大残差 8.3×10⁻¹⁷", "成立（恒等式）"),
    ]
    out = ["| 编号 | 命题 | 预设等级 | 结果 | 状态 |", "|---|---|---|---|---|"]
    for r in rows:
        out.append("| %s | %s | %s | %s | %s |" % r)
    out.append("")
    out.append("*表 9　可证伪登记（W1—W10 与识别性结果 R1）。负面结果已在正文展开；"
               "任何一条被后续研究推翻时，只追加新行，不改旧行。*")
    return "\n".join(out)


def appendix():
    if not os.path.exists(CSV):
        return "（编码库为空：先跑 analysis/stats.py 与 analysis/make_figures.py）"
    with open(CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = ["| 来源 | 版次 | 传统 | 边界年 | 时期名 | 区域·时代·层级·命名 | 备注 |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        y = r["boundary_year"] if r["boundary_year"] not in ("None", "") else "NA"
        attr = "%s·%s·%s·%s" % (r["region"], ERA_CN.get(r["era"], r["era"]),
                                LEVEL_CN.get(r["level"], r["level"]),
                                NAME_CN.get(r["name_type"], r["name_type"]))
        out.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["source"], r["year_published"], TRAD_CN.get(r["tradition"], r["tradition"]),
            y, r["period_name"], attr, r["note"]))
    out.append("")
    out.append("*表 10　全部边界（%d 条，含分析窗外的公元前断点与扩展语料）。"
               "NA 表示来源未印出年份。由 `data/schemes.csv` 生成。*" % len(rows))
    return "\n".join(out)


def main():
    s = open(SRC, encoding="utf-8").read()
    stats = json.load(open(STATS, encoding="utf-8")) if os.path.exists(STATS) else None
    if stats:
        s = s.replace("<!--TABLE2-->", table2(stats))
        s = s.replace("<!--TABLE5-->", table8(stats))
    s = s.replace("<!--TABLE9-->", table9())
    s = s.replace("<!--APPENDIX_TABLE-->", appendix())
    open(OUT, "w", encoding="utf-8", newline="\n").write(s)
    print("wrote", OUT, len(s), "chars")


if __name__ == "__main__":
    main()

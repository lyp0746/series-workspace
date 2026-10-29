# -*- coding: utf-8 -*-
"""W8 复编：20% 来源的盲态二读（coder B）。

抽样：按来源在编码库中的顺序等距取 9/46（≈20%），覆盖三组传统与补充组。
复编者只使用 docs/codebook.md 与来源的目录标题，不看 coder A 的年份、era 与层级
（本文件独立于 schemes.py 书写；比对在 analysis/kappa.py 中做）。

自曝：复编由同一编码者在另一时段完成，不是独立第二人。κ 度量规则稳定性，
不度量人际一致性；真实的人际 κ 只会更低。

字段：source, boundary_year(A 轮用于对齐，不参与 B 的判定), 再编码结果
      year_b, era_b, level_b
"""

RECODE = [
    # ---- Spielvogel《西方文明史简编》第9版（7 条）
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=476,
         year_b=476, era_b="medieval", level_b="part"),
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1350,
         year_b=1350, era_b="early_modern", level_b="part"),
    # B 读法：宗教改革与文艺复兴同属一个部，不单列部级
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1517,
         year_b=1517, era_b="early_modern", level_b="chapter"),
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1648,
         year_b=1648, era_b="early_modern", level_b="chapter"),
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1789,
         year_b=1789, era_b="modern", level_b="part"),
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1914,
         year_b=1914, era_b="modern", level_b="part"),
    dict(source="Spielvogel《西方文明史简编》第9版", boundary_year=1945,
         year_b=1945, era_b="contemporary", level_b="part"),

    # ---- Palmer/Colton《现代世界史》第11版（5 条）
    dict(source="Palmer/Colton《现代世界史》第11版", boundary_year=1500,
         year_b=1500, era_b="early_modern", level_b="part"),
    # B 读法：1648 是部内一章（旧制度的起点在部标题，不在章）
    dict(source="Palmer/Colton《现代世界史》第11版", boundary_year=1648,
         year_b=1648, era_b="early_modern", level_b="chapter"),
    dict(source="Palmer/Colton《现代世界史》第11版", boundary_year=1789,
         year_b=1789, era_b="modern", level_b="part"),
    dict(source="Palmer/Colton《现代世界史》第11版", boundary_year=1914,
         year_b=1914, era_b="modern", level_b="part"),
    dict(source="Palmer/Colton《现代世界史》第11版", boundary_year=1945,
         year_b=1945, era_b="contemporary", level_b="part"),

    # ---- 《剑桥中世纪史》（2 条）
    dict(source="《剑桥中世纪史》", boundary_year=476,
         year_b=476, era_b="medieval", level_b="part"),
    # B 读法：1453 是中世纪卷的终点，按 R5「该边界开启的时期」应记 early_modern；
    # B 依书名判定为 medieval，构成一处 era 分歧。
    dict(source="《剑桥中世纪史》", boundary_year=1453,
         year_b=1453, era_b="medieval", level_b="part"),

    # ---- Bentley AHR 1996（2 条）
    dict(source="Bentley《世界史中的跨文化互动与分期》（AHR 1996）", boundary_year=1000,
         year_b=1000, era_b="medieval", level_b="part"),
    # B 读法：Bentley 主张 1500 之后为「现代世界体系」，记 modern
    dict(source="Bentley《世界史中的跨文化互动与分期》（AHR 1996）", boundary_year=1500,
         year_b=1500, era_b="modern", level_b="part"),

    # ---- Judge & Langdon《联系：世界史》第3版（4 条）
    dict(source="Judge & Langdon《联系：世界史》第3版", boundary_year=1000,
         year_b=1000, era_b="medieval", level_b="part"),
    dict(source="Judge & Langdon《联系：世界史》第3版", boundary_year=1500,
         year_b=1500, era_b="early_modern", level_b="part"),
    dict(source="Judge & Langdon《联系：世界史》第3版", boundary_year=1750,
         year_b=1750, era_b="modern", level_b="part"),
    dict(source="Judge & Langdon《联系：世界史》第3版", boundary_year=1914,
         year_b=1914, era_b="modern", level_b="part"),

    # ---- Osterhammel《世界的转型》（1 条）
    dict(source="Osterhammel《世界的转型》", boundary_year=1750,
         year_b=1750, era_b="modern", level_b="part"),

    # ---- 人教版《世界历史》九年级（6 条）
    dict(source="人教版《世界历史》九年级", boundary_year=1500,
         year_b=1500, era_b="early_modern", level_b="part"),
    dict(source="人教版《世界历史》九年级", boundary_year=1640,
         year_b=1640, era_b="modern", level_b="part"),
    # B 读法：1760 属「工业革命」单元内的一节，不单列顶层单元
    dict(source="人教版《世界历史》九年级", boundary_year=1760,
         year_b=1760, era_b="modern", level_b="chapter"),
    dict(source="人教版《世界历史》九年级", boundary_year=1914,
         year_b=1914, era_b="modern", level_b="part"),
    dict(source="人教版《世界历史》九年级", boundary_year=1917,
         year_b=1917, era_b="contemporary", level_b="part"),
    dict(source="人教版《世界历史》九年级", boundary_year=1945,
         year_b=1945, era_b="contemporary", level_b="part"),

    # ---- 苏联科学院《世界通史》十卷本（中译）（3 条）
    dict(source="苏联科学院《世界通史》十卷本（中译）", boundary_year=1640,
         year_b=1640, era_b="modern", level_b="part"),
    # B 读法：1789 是近代卷内的一章
    dict(source="苏联科学院《世界通史》十卷本（中译）", boundary_year=1789,
         year_b=1789, era_b="modern", level_b="chapter"),
    dict(source="苏联科学院《世界通史》十卷本（中译）", boundary_year=1917,
         year_b=1917, era_b="contemporary", level_b="part"),

    # ---- Wikipedia《Early modern period》（2 条）
    dict(source="Wikipedia《Early modern period》", boundary_year=1500,
         year_b=1500, era_b="early_modern", level_b="part"),
    # B 读法：该条目把 1800 记为近代早期的终点，按 R5 仍应是下一期的起点
    dict(source="Wikipedia《Early modern period》", boundary_year=1800,
         year_b=1800, era_b="early_modern", level_b="part"),
]

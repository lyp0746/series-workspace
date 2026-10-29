# -*- coding: utf-8 -*-
"""分期方案的编码库（唯一数据源）。

编码规则见 docs/codebook.md（先定后编，编码过程中未改规则）。

字段：
  source          来源简称（教材/通史/工具书/课程框架）
  year_published  实际使用的版次年份
  tradition       european / global / china / other
  scope           world / region / nation
  boundary_year   该来源明确写出的边界年；未写出就 None（记 NA），不推断
  period_name     该边界开启的时期名（照录来源的标签）
  region          欧洲 / 亚洲 / 非洲 / 全球 / 未注明
  era             该边界开启的时期所属：ancient / medieval / early_modern / modern / contemporary
  level           part（卷/编/部/课程单元/工具书分卷）/ chapter（章/节）
  note            并列、世纪、约、卷次、版次变更等
  coder           首轮 A；复编 B（见 data/recode_b.py）

编码依据：各来源公开的目录、分部/分卷标题、课程框架文件；只编码年份与时期名，
不复制原文。未逐页核对正文，因此全部行等级 B／C（见正文 2.2 与附录 C）。
"""
FIELDS = ["source", "year_published", "tradition", "scope", "genre", "series",
          "calendar", "explicit_year", "boundary_year", "period_name", "region",
          "era", "level", "name_type", "note", "coder"]

# ---------------------------------------------------------------- 来源定义
# 每个来源：元数据 + b=[(边界年, 时期名, 区域, era, level, note)]
# 边界年为 None 表示来源印出了该时期但未印年份（NA 行，不进统计）。

_S = []

# 体裁：survey 教材／通史；reference 工具书与多卷本；argument 单一断点论证；
# curriculum 课程框架；chronicle 编年史；sacred_history 圣史；treatise 论说
GENRE = {
    "Spielvogel《西方文明史简编》第9版": "survey",
    "McKay《西方社会史》第11版": "survey",
    "Coffin & Stacey《西方文明》第17版": "survey",
    "Kishlansky《西方文明》第7版": "survey",
    "Noble《西方文明：超越边界》第7版": "survey",
    "Perry《西方文明简史》第11版": "survey",
    "Palmer/Colton《现代世界史》第11版": "survey",
    "Roberts《企鹅世界史》第6版": "survey",
    "Britannica《欧洲史》条目": "reference",
    "Langer《世界史百科全书》第5版": "reference",
    "Acton《剑桥近代史》": "reference",
    "《剑桥中世纪史》": "reference",
    "Davies《欧洲史》": "survey",
    "Hobsbawm《年代四部曲》": "argument",
    "Spielvogel《世界史》第8版": "survey",
    "McNeill《世界史》第4版": "survey",
    "Bentley & Ziegler《传统与相遇》第6版": "survey",
    "Bentley《世界史中的跨文化互动与分期》（AHR 1996）": "argument",
    "Stavrianos《全球史》第7版": "survey",
    "Stearns《世界文明：全球视角》第7版": "survey",
    "Bulliet《大地与人民》第6版": "survey",
    "Spodek《世界的历史》第4版": "survey",
    "Judge & Langdon《联系：世界史》第3版": "survey",
    "AP 世界史：现代（课程框架）": "curriculum",
    "AP 世界史（2011 框架）": "curriculum",
    "《剑桥世界史》": "reference",
    "Pomeranz《大分流》": "argument",
    "Bayly《现代世界的诞生 1780—1914》": "argument",
    "Osterhammel《世界的转型》": "argument",
    "周一良、吴于廑《世界通史》": "survey",
    "吴于廑、齐世荣《世界史》六卷本": "survey",
    "刘宗绪《世界近代史》": "survey",
    "王斯德《世界现代史》": "survey",
    "《中外历史纲要（下）》人教版": "curriculum",
    "人教版《世界历史》九年级": "curriculum",
    "岳麓版《世界历史》九年级": "curriculum",
    "北师大版《世界历史》九年级": "curriculum",
    "华东师大版《世界历史》九年级": "curriculum",
    "《中国大百科全书·世界历史》": "reference",
    "苏联科学院《世界通史》十卷本（中译）": "reference",
    "范文澜《中国通史简编》": "survey",
    "钱穆《国史大纲》": "survey",
    "白寿彝《中国通史》": "survey",
    "Wikipedia《Periodization》": "reference",
    "Wikipedia《List of time periods》": "reference",
    "Wikipedia《Early modern period》": "reference",
}


def src(**kw):
    kw.setdefault("series", "core")
    kw.setdefault("calendar", "AD")
    kw.setdefault("explicit_year", True)
    kw.setdefault("genre", GENRE.get(kw.get("source"), "survey"))
    _S.append(kw)


# ============================================================ 欧洲中心传统
src(source="Spielvogel《西方文明史简编》第9版", year_published=2017,
    tradition="european", scope="region", source_note="五部分制；文艺复兴独立成部",
    b=[(476, "中世纪的开端", "欧洲", "medieval", "part", ""),
       (1350, "文艺复兴与宗教改革", "欧洲", "early_modern", "part", ""),
       (1517, "宗教改革", "欧洲", "early_modern", "chapter", "并列:1517/1520"),
       (1648, "三十年战争与主权国家", "欧洲", "early_modern", "chapter", ""),
       (1789, "法国大革命与近代政治", "欧洲", "modern", "part", ""),
       (1914, "两次世界大战", "欧洲", "modern", "part", ""),
       (1945, "冷战与当代欧洲", "欧洲", "contemporary", "part", "")])

src(source="McKay《西方社会史》第11版", year_published=2014,
    tradition="european", scope="region", source_note="章群按世纪切分，部按时代切分",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1350, "文艺复兴", "欧洲", "early_modern", "part", ""),
       (1517, "宗教改革", "欧洲", "early_modern", "chapter", ""),
       (1648, "近代国家的建构", "欧洲", "early_modern", "chapter", ""),
       (1789, "革命与近代政治", "欧洲", "modern", "part", ""),
       (1914, "世界大战时代", "欧洲", "modern", "part", ""),
       (1945, "战后欧洲", "欧洲", "contemporary", "part", "")])

src(source="Coffin & Stacey《西方文明》第17版", year_published=2017,
    tradition="european", scope="region", source_note="保留 1000 年作为内部断点",
    b=[(476, "中世纪早期", "欧洲", "medieval", "part", ""),
       (1000, "中世纪盛期", "欧洲", "medieval", "part", ""),
       (1348, "黑死病与危机", "欧洲", "medieval", "chapter", "约"),
       (1517, "宗教改革", "欧洲", "early_modern", "part", ""),
       (1648, "主权国家体系", "欧洲", "early_modern", "chapter", ""),
       (1789, "法国大革命", "欧洲", "modern", "part", ""),
       (1914, "第一次世界大战", "欧洲", "modern", "part", "")])

src(source="Kishlansky《西方文明》第7版", year_published=2010,
    tradition="european", scope="region", source_note="以 1453 开启近代",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "近代的开端", "欧洲", "early_modern", "part", "并列:1453/1492"),
       (1492, "海外扩张", "欧洲", "early_modern", "chapter", "并列:1453/1492"),
       (1517, "宗教改革", "欧洲", "early_modern", "chapter", ""),
       (1648, "威斯特伐利亚体系", "欧洲", "early_modern", "part", ""),
       (1789, "法国大革命", "欧洲", "modern", "part", ""),
       (1914, "世界大战", "欧洲", "modern", "part", "")])

src(source="Noble《西方文明：超越边界》第7版", year_published=2013,
    tradition="european", scope="region", source_note="1300 与 1500 分列两个部",
    b=[(476, "中世纪早期", "欧洲", "medieval", "part", ""),
       (1000, "中世纪盛期", "欧洲", "medieval", "part", ""),
       (1300, "文艺复兴", "欧洲", "early_modern", "part", "世纪"),
       (1500, "近代早期", "欧洲", "early_modern", "part", ""),
       (1648, "宗教战争之后", "欧洲", "early_modern", "chapter", ""),
       (1789, "革命时代", "欧洲", "modern", "part", ""),
       (1914, "20 世纪", "欧洲", "modern", "part", "")])

src(source="Perry《西方文明简史》第11版", year_published=2016,
    tradition="european", scope="region", source_note="1300 起为部级",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1300, "文艺复兴", "欧洲", "early_modern", "part", "世纪"),
       (1517, "宗教改革", "欧洲", "early_modern", "chapter", ""),
       (1648, "绝对主义与主权国家", "欧洲", "early_modern", "chapter", ""),
       (1789, "法国大革命", "欧洲", "modern", "part", ""),
       (1914, "世界大战", "欧洲", "modern", "part", ""),
       (1945, "当代", "欧洲", "contemporary", "part", "")])

src(source="Palmer/Colton《现代世界史》第11版", year_published=2013,
    tradition="european", scope="region", source_note="书名即现代世界，起点 1500",
    b=[(1500, "近代早期", "欧洲", "early_modern", "part", ""),
       (1648, "旧制度", "欧洲", "early_modern", "part", ""),
       (1789, "革命时代", "欧洲", "modern", "part", ""),
       (1914, "20 世纪", "欧洲", "modern", "part", ""),
       (1945, "战后", "欧洲", "contemporary", "part", "")])

src(source="Roberts《企鹅世界史》第6版", year_published=2014,
    tradition="european", scope="world", source_note="书名世界史；1500 起为欧洲时代",
    b=[(1500, "欧洲时代", "全球", "early_modern", "part", ""),
       (1750, "欧洲的世界霸权", "全球", "modern", "part", ""),
       (1914, "全球冲突", "全球", "modern", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

src(source="Britannica《欧洲史》条目", year_published=2020,
    tradition="european", scope="region", source_note="在线工具书条目",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "文艺复兴", "欧洲", "early_modern", "part", "并列:1453/1492"),
       (1492, "大航海", "欧洲", "early_modern", "chapter", "并列:1453/1492"),
       (1648, "旧制度", "欧洲", "early_modern", "part", ""),
       (1789, "革命与民族国家", "欧洲", "modern", "part", ""),
       (1914, "两次世界大战", "欧洲", "modern", "part", ""),
       (1945, "战后欧洲", "欧洲", "contemporary", "part", "")])

src(source="Langer《世界史百科全书》第5版", year_published=1972,
    tradition="european", scope="world", source_note="年表体工具书；分区按欧洲政治史",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "文艺复兴", "欧洲", "early_modern", "part", ""),
       (1492, "地理大发现", "全球", "early_modern", "chapter", ""),
       (1648, "威斯特伐利亚", "欧洲", "early_modern", "part", ""),
       (1789, "法国大革命", "欧洲", "modern", "part", ""),
       (1914, "第一次世界大战", "全球", "modern", "part", ""),
       (1945, "第二次世界大战之后", "全球", "contemporary", "part", "")])

src(source="Acton《剑桥近代史》", year_published=1902,
    tradition="european", scope="region", source_note="十四卷分卷制；卷名即边界",
    b=[(1450, "文艺复兴", "欧洲", "early_modern", "part", ""),
       (1517, "宗教改革", "欧洲", "early_modern", "part", ""),
       (1648, "三十年战争", "欧洲", "early_modern", "part", ""),
       (1789, "法国革命", "欧洲", "modern", "part", ""),
       (1815, "维也纳体系", "欧洲", "modern", "part", "")])

src(source="《剑桥中世纪史》", year_published=1911,
    tradition="european", scope="region", source_note="八卷；起讫即边界",
    b=[(476, "中世纪的开端", "欧洲", "medieval", "part", ""),
       (1453, "中世纪的终结", "欧洲", "early_modern", "part", "并列:1453/1494")])

src(source="Davies《欧洲史》", year_published=1996,
    tradition="european", scope="region", source_note="单卷区域通史",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "文艺复兴", "欧洲", "early_modern", "part", ""),
       (1517, "宗教改革", "欧洲", "early_modern", "chapter", ""),
       (1648, "旧制度", "欧洲", "early_modern", "part", ""),
       (1789, "革命时代", "欧洲", "modern", "part", ""),
       (1914, "20 世纪", "欧洲", "modern", "part", ""),
       (1945, "战后", "欧洲", "contemporary", "part", "")])

src(source="Hobsbawm《年代四部曲》", year_published=1962,
    tradition="european", scope="region", source_note="漫长的 19 世纪；丛书四卷即四个边界",
    b=[(1789, "革命的年代", "欧洲", "modern", "part", ""),
       (1848, "资本的年代", "欧洲", "modern", "part", ""),
       (1875, "帝国的年代", "欧洲", "modern", "part", ""),
       (1914, "极端的年代", "全球", "modern", "part", "")])

src(source="Spielvogel《世界史》第8版", year_published=2018,
    tradition="european", scope="world", source_note="书名世界史；主轴仍是西方文明",
    b=[(1500, "近代早期", "全球", "early_modern", "part", ""),
       (1800, "工业与帝国", "全球", "modern", "part", ""),
       (1914, "世界大战", "全球", "modern", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

# ============================================================ 全球史传统
src(source="McNeill《世界史》第4版", year_published=1999,
    tradition="global", scope="world", source_note="以欧亚网络与疾病—贸易带分期",
    b=[(1000, "欧亚复兴", "全球", "medieval", "part", ""),
       (1500, "西方的兴起", "全球", "early_modern", "part", ""),
       (1750, "工业突破", "全球", "modern", "part", ""),
       (1914, "全球冲突", "全球", "modern", "part", "")])

src(source="Bentley & Ziegler《传统与相遇》第6版", year_published=2015,
    tradition="global", scope="world", source_note="以跨文化互动为分期单位",
    b=[(500, "古典帝国的终结", "全球", "medieval", "part", ""),
       (1000, "跨区域网络的扩张", "全球", "medieval", "part", ""),
       (1500, "全球网络的成形", "全球", "early_modern", "part", ""),
       (1800, "工业与帝国", "全球", "modern", "part", ""),
       (1914, "全球冲突", "全球", "modern", "part", "")])

src(source="Bentley《世界史中的跨文化互动与分期》（AHR 1996）", year_published=1996,
    tradition="global", scope="world", source_note="论文；明确主张 1000 年为最大断点",
    b=[(1000, "跨文化互动的加速", "全球", "medieval", "part", ""),
       (1500, "全球体系的形成", "全球", "early_modern", "part", "")])

src(source="Stavrianos《全球史》第7版", year_published=1998,
    tradition="global", scope="world", source_note="以 1500 分为上下两编，但保留 1000 年内部断点",
    b=[(1000, "欧亚的复兴", "全球", "medieval", "part", ""),
       (1500, "西方的崛起", "全球", "early_modern", "part", ""),
       (1750, "工业革命", "全球", "modern", "part", ""),
       (1914, "全球战争", "全球", "modern", "part", "")])

src(source="Stearns《世界文明：全球视角》第7版", year_published=2015,
    tradition="global", scope="world", source_note="1450 与 1750 双断点",
    b=[(1000, "后古典时代", "全球", "medieval", "part", ""),
       (1450, "早期近代世界", "全球", "early_modern", "part", ""),
       (1750, "工业化的世界", "全球", "modern", "part", ""),
       (1914, "20 世纪", "全球", "modern", "part", "")])

src(source="Bulliet《大地与人民》第6版", year_published=2014,
    tradition="global", scope="world", source_note="环境—人口—技术为分期依据",
    b=[(1000, "半球网络", "全球", "medieval", "part", ""),
       (1500, "跨洋联系", "全球", "early_modern", "part", ""),
       (1750, "工业时代", "全球", "modern", "part", ""),
       (1914, "现代冲突", "全球", "modern", "part", "")])

src(source="Spodek《世界的历史》第4版", year_published=2010,
    tradition="global", scope="world", source_note="1900 作为 20 世纪起点",
    b=[(1000, "中世纪的世界", "全球", "medieval", "part", ""),
       (1500, "全球联系", "全球", "early_modern", "part", ""),
       (1750, "工业化", "全球", "modern", "part", ""),
       (1900, "20 世纪", "全球", "modern", "part", "")])

src(source="Judge & Langdon《联系：世界史》第3版", year_published=2016,
    tradition="global", scope="world", source_note="以连接为单位组织",
    b=[(1000, "区域联系的扩展", "全球", "medieval", "part", ""),
       (1500, "全球连接", "全球", "early_modern", "part", ""),
       (1750, "工业与帝国", "全球", "modern", "part", ""),
       (1914, "全球战争", "全球", "modern", "part", "")])

src(source="AP 世界史：现代（课程框架）", year_published=2019,
    tradition="global", scope="world", source_note="课程单元；行政规定而非史学论证",
    b=[(1200, "全球织毯", "全球", "medieval", "part", "课程单元"),
       (1450, "跨洋互联", "全球", "early_modern", "part", "课程单元"),
       (1750, "革命与工业", "全球", "modern", "part", "课程单元"),
       (1900, "全球冲突", "全球", "modern", "part", "课程单元")])

src(source="AP 世界史（2011 框架）", year_published=2011,
    tradition="global", scope="world", source_note="2019 年改版前框架；起点 600",
    b=[(600, "古典之后", "全球", "medieval", "part", "课程单元"),
       (1450, "全球网络", "全球", "early_modern", "part", "课程单元"),
       (1750, "工业与革命", "全球", "modern", "part", "课程单元"),
       (1914, "全球冲突", "全球", "modern", "part", "课程单元")])

src(source="《剑桥世界史》", year_published=2015,
    tradition="global", scope="world", source_note="九卷；卷目即边界",
    b=[(500, "帝国与网络", "全球", "medieval", "part", ""),
       (1400, "全球世界的建构", "全球", "early_modern", "part", "并列:1400/1500"),
       (1750, "生产、破坏与连接", "全球", "modern", "part", "")])

src(source="Pomeranz《大分流》", year_published=2000,
    tradition="global", scope="world", source_note="以 1800 为分流点；单一断点的论证性方案",
    b=[(1800, "大分流", "全球", "modern", "part", "")])

src(source="Bayly《现代世界的诞生 1780—1914》", year_published=2004,
    tradition="global", scope="world", source_note="以 1780 为现代起点；全球史论证",
    b=[(1780, "现代世界的诞生", "全球", "modern", "part", "")])

src(source="Osterhammel《世界的转型》", year_published=2014,
    tradition="global", scope="world", source_note="以 1750 前后为转型起点",
    b=[(1750, "转型的开始", "全球", "modern", "part", "约")])

# ============================================================ 中国教材传统
src(source="周一良、吴于廑《世界通史》", year_published=1962,
    tradition="china", scope="world", source_note="苏联体系；古代—近代以 1640 分",
    b=[(1640, "近代", "全球", "modern", "part", ""),
       (1917, "现代", "全球", "contemporary", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

src(source="吴于廑、齐世荣《世界史》六卷本", year_published=1994,
    tradition="china", scope="world", source_note="古代史编止于 1500；近代史编 1500—1900",
    b=[(1500, "近代", "全球", "early_modern", "part", ""),
       (1900, "现代", "全球", "modern", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

src(source="刘宗绪《世界近代史》", year_published=2011,
    tradition="china", scope="world", source_note="1640—1917 体系",
    b=[(1640, "近代", "全球", "modern", "part", ""),
       (1917, "现代", "全球", "contemporary", "part", "")])

src(source="王斯德《世界现代史》", year_published=1988,
    tradition="china", scope="world", source_note="1917—1945 体系",
    b=[(1917, "现代", "全球", "contemporary", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

src(source="《中外历史纲要（下）》人教版", year_published=2019,
    tradition="china", scope="world", source_note="高中必修；单元制，部分单元无年",
    b=[(1500, "走向整体的世界", "全球", "early_modern", "part", "世纪"),
       (1640, "资本主义制度的确立", "全球", "modern", "part", ""),
       (1760, "工业革命", "全球", "modern", "part", "年代"),
       (1914, "两次世界大战", "全球", "modern", "part", ""),
       (1917, "十月革命", "全球", "contemporary", "part", ""),
       (1945, "20 世纪下半叶", "全球", "contemporary", "part", ""),
       (1991, "当代世界", "全球", "contemporary", "part", "")])

src(source="人教版《世界历史》九年级", year_published=2018,
    tradition="china", scope="world", source_note="初中教材；1640 与 1917 为课标断点",
    b=[(1500, "步入近代", "全球", "early_modern", "part", "世纪"),
       (1640, "资产阶级革命", "全球", "modern", "part", ""),
       (1760, "工业革命", "全球", "modern", "part", "年代"),
       (1914, "第一次世界大战", "全球", "modern", "part", ""),
       (1917, "十月革命", "全球", "contemporary", "part", ""),
       (1945, "第二次世界大战", "全球", "contemporary", "part", "")])

src(source="岳麓版《世界历史》九年级", year_published=2015,
    tradition="china", scope="world", source_note="课标体系；近代起于 1640",
    b=[(1500, "近代的开端", "全球", "early_modern", "part", "世纪"),
       (1640, "英国革命", "全球", "modern", "part", ""),
       (1917, "十月革命", "全球", "contemporary", "part", ""),
       (1945, "战后世界", "全球", "contemporary", "part", "")])

src(source="北师大版《世界历史》九年级", year_published=2014,
    tradition="china", scope="world", source_note="课标体系",
    b=[(1500, "近代的开端", "全球", "early_modern", "part", "世纪"),
       (1640, "英国革命", "全球", "modern", "part", ""),
       (1917, "十月革命", "全球", "contemporary", "part", ""),
       (1945, "战后世界", "全球", "contemporary", "part", "")])

src(source="华东师大版《世界历史》九年级", year_published=2016,
    tradition="china", scope="world", source_note="课标体系",
    b=[(1500, "近代的开端", "全球", "early_modern", "part", "世纪"),
       (1640, "英国革命", "全球", "modern", "part", ""),
       (1917, "十月革命", "全球", "contemporary", "part", ""),
       (1945, "战后世界", "全球", "contemporary", "part", "")])

src(source="《中国大百科全书·世界历史》", year_published=1990,
    tradition="china", scope="world", source_note="工具书；兼收欧洲事件年与中国体系断点",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "文艺复兴", "欧洲", "early_modern", "part", ""),
       (1492, "地理大发现", "全球", "early_modern", "chapter", ""),
       (1640, "近代", "全球", "modern", "part", ""),
       (1917, "现代", "全球", "contemporary", "part", ""),
       (1945, "当代", "全球", "contemporary", "part", "")])

src(source="苏联科学院《世界通史》十卷本（中译）", year_published=1955,
    tradition="china", scope="world", source_note="中国教材体系的直接来源；1640—1917",
    b=[(1640, "近代", "全球", "modern", "part", ""),
       (1789, "法国革命", "欧洲", "modern", "part", ""),
       (1917, "现代", "全球", "contemporary", "part", "")])

src(source="范文澜《中国通史简编》", year_published=1949,
    tradition="china", scope="nation", source_note="国别通史；朝代断代，非世界史分期",
    b=[(-221, "上古", "亚洲", "ancient", "part", "公元前"),
       (589, "中古", "亚洲", "medieval", "part", ""),
       (960, "近古", "亚洲", "medieval", "part", ""),
       (1368, "近世", "亚洲", "medieval", "part", ""),
       (1644, "清", "亚洲", "medieval", "part", ""),
       (1840, "近代", "亚洲", "modern", "part", ""),
       (1911, "民国", "亚洲", "modern", "part", "")])

src(source="钱穆《国史大纲》", year_published=1940,
    tradition="china", scope="nation", source_note="国别通史；以 960 为近世起点",
    b=[(-221, "上古", "亚洲", "ancient", "part", "公元前"),
       (960, "近世", "亚洲", "medieval", "part", ""),
       (1911, "近代", "亚洲", "modern", "part", "")])

src(source="白寿彝《中国通史》", year_published=1999,
    tradition="china", scope="nation", source_note="国别通史；1840 与 1911 为断点",
    b=[(1840, "近代", "亚洲", "modern", "part", ""),
       (1911, "民国", "亚洲", "modern", "part", ""),
       (1949, "当代", "亚洲", "contemporary", "part", "")])

# ============================================================ 补充（仅用于敏感性）
src(source="Wikipedia《Periodization》", year_published=2024,
    tradition="other", scope="world", source_note="网络工具书，仅补充",
    b=[(1500, "近代早期", "全球", "early_modern", "part", ""),
       (1800, "现代", "全球", "modern", "part", "")])

src(source="Wikipedia《List of time periods》", year_published=2024,
    tradition="other", scope="world", source_note="网络工具书，仅补充",
    b=[(476, "中世纪", "欧洲", "medieval", "part", ""),
       (1453, "近代早期", "欧洲", "early_modern", "part", ""),
       (1492, "大航海", "全球", "early_modern", "chapter", ""),
       (1914, "现代", "全球", "modern", "part", "")])

src(source="Wikipedia《Early modern period》", year_published=2024,
    tradition="other", scope="world", source_note="网络工具书，仅补充",
    b=[(1500, "近代早期", "全球", "early_modern", "part", ""),
       (1800, "现代", "全球", "modern", "part", "")])


# ============================================================ 扩展语料（前现代与非欧洲）
# 规则：只编来源自己的时期切分；未印出绝对年份记 None（NA），不换算、不推断。
# explicit_year 记"来源是否印出年份（任何纪年）"；boundary_year 记换算后的公元年，
# 无法可靠换算者记 None 并在 note 说明。

src(source="伊西多尔《编年史》", year_published=615,
    tradition="premodern_europe", scope="world", genre="sacred_history",
    series="extended", calendar="AM", explicit_year=False,
    source_note="六时代；以世界纪年（AM）计，无绝对年",
    b=[(None, "第二时代（挪亚—亚伯拉罕）", "全球", "sacred", "part", "无年份"),
       (None, "第三时代（亚伯拉罕—大卫）", "全球", "sacred", "part", "无年份"),
       (None, "第四时代（大卫—巴比伦之囚）", "全球", "sacred", "part", "无年份"),
       (None, "第五时代（巴比伦之囚—基督）", "全球", "sacred", "part", "无年份"),
       (None, "第六时代（基督—当代）", "全球", "sacred", "part", "无年份")])

src(source="弗赖辛的奥托《编年史》", year_published=1146,
    tradition="premodern_europe", scope="world", genre="chronicle",
    series="extended", calendar="none", explicit_year=False,
    source_note="双城论；以帝国转移与王位更迭分段，不记年",
    b=[(None, "第一书：创世至罗马", "全球", "sacred", "part", "无年份"),
       (None, "第二书：帝国转移", "全球", "dynastic", "part", "无年份"),
       (None, "第三书：当代", "全球", "dynastic", "part", "无年份")])

src(source="伊本·赫勒敦《历史绪论》", year_published=1377,
    tradition="islamic", scope="world", genre="treatise",
    series="extended", calendar="none", explicit_year=False,
    source_note="王朝周期（三代约 120 年）；不记绝对年",
    b=[(None, "第一代：创业", "全球", "dynastic", "part", "周期，无绝对年"),
       (None, "第二代：守成", "全球", "dynastic", "part", "周期，无绝对年"),
       (None, "第三代：衰亡", "全球", "dynastic", "part", "周期，无绝对年")])

src(source="塔巴里《历代先知与帝王史》", year_published=915,
    tradition="islamic", scope="world", genre="chronicle",
    series="extended", calendar="AH", explicit_year=True,
    source_note="希吉拉纪年，按年编排，哈里发在位分段",
    b=[(622, "希吉拉", "全球", "event", "part", "AH 1"),
       (661, "伍麦叶王朝", "全球", "dynastic", "part", "AH 40"),
       (750, "阿拔斯革命", "全球", "event", "part", "AH 132"),
       (833, "马蒙之死", "全球", "event", "part", "AH 218"),
       (915, "当代", "全球", "era", "part", "AH 303")])

src(source="拉施特《史集》", year_published=1318,
    tradition="islamic", scope="world", genre="chronicle",
    series="extended", calendar="AH", explicit_year=True,
    source_note="世界史；蒙古—伊斯兰双轴，AH 纪年",
    b=[(622, "希吉拉", "全球", "event", "part", "AH 1"),
       (1258, "巴格达陷落", "全球", "event", "part", "AH 656"),
       (1318, "当代", "全球", "era", "part", "AH 718")])

src(source="萨阿迪《苏丹史》", year_published=1655,
    tradition="african", scope="region", genre="chronicle",
    series="extended", calendar="AH", explicit_year=True,
    source_note="桑海帝国编年；AH 纪年",
    b=[(1464, "桑尼·阿里", "非洲", "dynastic", "part", "AH 869"),
       (1493, "阿斯基亚王朝", "非洲", "dynastic", "part", "AH 899"),
       (1591, "摩洛哥征服", "非洲", "event", "part", "AH 999")])

src(source="《基尔瓦编年》", year_published=1520,
    tradition="african", scope="region", genre="chronicle",
    series="extended", calendar="mixed", explicit_year=True,
    source_note="设拉子王朝；AH 与公元混用，年代有争议",
    b=[(957, "设拉子王朝建立", "非洲", "dynastic", "part", "约"),
       (1331, "哈桑·伊本·苏莱曼", "非洲", "dynastic", "part", "约"),
       (1505, "葡萄牙人到来", "非洲", "event", "part", "约")])

src(source="司马迁《史记》", year_published=-91,
    tradition="east_asian_premodern", scope="nation", genre="chronicle",
    series="extended", calendar="reign", explicit_year=True,
    source_note="本纪／表；以王朝与帝王纪年分段",
    b=[(-221, "秦本纪", "亚洲", "dynastic", "part", "王朝纪年"),
       (-206, "汉本纪", "亚洲", "dynastic", "part", "王朝纪年"),
       (-141, "武帝", "亚洲", "dynastic", "part", "王朝纪年")])

src(source="司马光《资治通鉴》", year_published=1084,
    tradition="east_asian_premodern", scope="region", genre="chronicle",
    series="extended", calendar="reign", explicit_year=True,
    source_note="编年体；以王朝更替分段，年号纪年",
    b=[(-403, "战国", "亚洲", "dynastic", "part", "年号纪年"),
       (-221, "秦", "亚洲", "dynastic", "part", "年号纪年"),
       (220, "三国", "亚洲", "dynastic", "part", "年号纪年"),
       (265, "晋", "亚洲", "dynastic", "part", "年号纪年"),
       (317, "东晋", "亚洲", "dynastic", "part", "年号纪年"),
       (420, "南北朝", "亚洲", "dynastic", "part", "年号纪年"),
       (589, "隋", "亚洲", "dynastic", "part", "年号纪年"),
       (618, "唐", "亚洲", "dynastic", "part", "年号纪年"),
       (907, "五代", "亚洲", "dynastic", "part", "年号纪年"),
       (959, "宋", "亚洲", "dynastic", "part", "年号纪年")])

src(source="卡尔哈纳《王河》", year_published=1148,
    tradition="south_asian", scope="region", genre="chronicle",
    series="extended", calendar="laukika", explicit_year=True,
    source_note="八卷（taranga）；以王统分段，Laukika 纪年，未换算",
    b=[(None, "第一至三卷：远古诸王", "亚洲", "dynastic", "part", "Laukika 纪年未换算"),
       (None, "第四至六卷：克什米尔王统", "亚洲", "dynastic", "part", "Laukika 纪年未换算"),
       (None, "第七至八卷：当代", "亚洲", "dynastic", "part", "Laukika 纪年未换算")])

src(source="《摩奴法论》与往世书时轮", year_published=200,
    tradition="south_asian", scope="world", genre="sacred_history",
    series="extended", calendar="none", explicit_year=False,
    source_note="四时（yuga）循环；无绝对年",
    b=[(None, "圆满时", "全球", "sacred", "part", "无年份"),
       (None, "三分时", "全球", "sacred", "part", "无年份"),
       (None, "二分时", "全球", "sacred", "part", "无年份"),
       (None, "争斗时", "全球", "sacred", "part", "无年份")])

src(source="《波波尔·乌》", year_published=1550,
    tradition="americas", scope="world", genre="sacred_history",
    series="extended", calendar="none", explicit_year=False,
    source_note="创世与诸世代；无绝对年",
    b=[(None, "第一世代", "美洲", "sacred", "part", "无年份"),
       (None, "第二世代", "美洲", "sacred", "part", "无年份"),
       (None, "第三世代", "美洲", "sacred", "part", "无年份"),
       (None, "第四世代（今）", "美洲", "sacred", "part", "无年份")])

src(source="萨阿贡《佛罗伦萨抄本》", year_published=1577,
    tradition="americas", scope="region", genre="chronicle",
    series="extended", calendar="AD", explicit_year=True,
    source_note="第十二卷记征服；公元纪年与本土历并存",
    b=[(1519, "科尔特斯抵达", "美洲", "event", "part", ""),
       (1521, "特诺奇蒂特兰陷落", "美洲", "event", "part", ""),
       (1577, "成书", "美洲", "era", "part", "")])

src(source="瓜曼·波马《新编年史》", year_published=1615,
    tradition="americas", scope="region", genre="chronicle",
    series="extended", calendar="AD", explicit_year=True,
    source_note="安第斯世代与印加王统；公元纪年",
    b=[(1438, "帕查库特克", "美洲", "dynastic", "part", ""),
       (1532, "卡哈马卡", "美洲", "event", "part", ""),
       (1615, "当代", "美洲", "era", "part", "")])


# ---------------------------------------------------------------- 名称类型
# 六类：event 事件／process 过程／space 空间／dynastic 王朝／sacred 圣史／era 时代
# 判定按时期名的关键词，顺序即优先级；例外在此表内以 override 固定。
_NAME_RULES = [
    ("sacred", ("时代（", "世代", "圆满时", "三分时", "二分时", "争斗时", "先知",
                "基督", "佛陀", "创世", "始祖", "众神", "挪亚", "亚伯拉罕",
                "大卫", "巴比伦之囚", "洪水")),
    ("event", ("革命", "战争", "大战", "条约", "和约", "陷落", "灭亡", "起义",
               "独立", "发现", "改革", "会议", "统一", "征服", "抵达", "到来",
               "之死", "议会", "体系", "开幕", "冷战", "解体", "战后", "诞生", "冲突",
               "希吉拉", "卡哈马卡", "光复")),
    ("process", ("工业化", "工业", "网络", "扩张", "转型", "兴起", "崛起", "衰落",
                 "复兴", "增长", "分流", "连接", "互联", "互动", "定居", "农业",
                 "城市化", "殖民", "移民", "贸易", "积累", "形成", "成形", "建构",
                 "确立", "发展", "突破", "整体", "继承", "扩散")),
    ("dynastic", ("王朝", "帝国", "本纪", "苏丹", "哈里发", "可汗", "汗国",
                  "战国", "三国", "南北朝", "五代", "民国", "阿斯基亚", "设拉子",
                  "伍麦叶", "阿拔斯", "诸王", "代：")),
    ("era", ("当代", "世纪", "时代", "时期", "上古", "中古", "近世",
             "古代", "中世纪", "近代", "现代")),
    ("space", ("全球", "世界", "跨区域", "半球", "海洋", "大陆", "欧亚", "大西洋",
               "太平洋", "跨洋", "区域")),
]
_OVERRIDE = {
    ("瓜曼·波马《新编年史》", 1438): "dynastic",
    ("司马迁《史记》", -141): "dynastic",
    ("Spielvogel《西方文明史简编》第9版", 1500): "era",
    ("Palmer/Colton《现代世界史》第11版", 1500): "era",
    ("Bentley & Ziegler《传统与相遇》第6版", 1500): "space",
    ("《中外历史纲要（下）》人教版", 1500): "process",
    ("人教版《世界历史》九年级", 1500): "process",
}


def name_type(period_name, source=None, year=None):
    if source is not None and (source, year) in _OVERRIDE:
        return _OVERRIDE[(source, year)]
    for typ, keys in _NAME_RULES:
        if any(k in period_name for k in keys):
            return typ
    return "era"


# ---------------------------------------------------------------- 展开为行
SOURCE_NOTE = {s["source"]: s.get("source_note", "") for s in _S}
YEAR_PUB = {s["source"]: s["year_published"] for s in _S}
TRAD = {s["source"]: s["tradition"] for s in _S}
SCOPE = {s["source"]: s["scope"] for s in _S}

SCHEMES = []
for _s in _S:
    for (_y, _p, _r, _e, _l, _n) in _s["b"]:
        SCHEMES.append(dict(
            source=_s["source"], year_published=_s["year_published"],
            tradition=_s["tradition"], scope=_s["scope"],
            genre=_s.get("genre", "survey"), series=_s.get("series", "core"),
            calendar=_s.get("calendar", "AD"),
            explicit_year=_s.get("explicit_year", True),
            boundary_year=_y, period_name=_p, region=_r,
            era=_e, level=_l, name_type=name_type(_p, _s["source"], _y), note=_n, coder="A"))


def rows():
    return [{k: s.get(k) for k in FIELDS} for s in SCHEMES]


def sources():
    """来源级元数据（供表 2、图 1 排序、分辨率统计）。"""
    return [dict(source=s["source"], year_published=s["year_published"],
                 tradition=s["tradition"], scope=s["scope"],
                 genre=s.get("genre", "survey"), series=s.get("series", "core"),
                 calendar=s.get("calendar", "AD"),
                 explicit_year=s.get("explicit_year", True),
                 source_note=s.get("source_note", "")) for s in _S]


if __name__ == "__main__":
    print(len(SCHEMES), "boundaries from", len(_S), "sources")

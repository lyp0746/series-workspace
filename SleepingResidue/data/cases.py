# -*- coding: utf-8 -*-
"""延迟承认案例库（单一数据源）。

字段定义（编码规则见正文 3.3 节）：
  id            编号
  case          案例（人名/学说）
  claim         被埋没的那句命题（一句话）
  t_prop        提出年（负数=公元前）
  t_rev         重新被承认的年（"结果类别"为沉默时留空）
  decoder       使其重新可读的新工具/新理论
  t_dec         解码器可用年
  resid         残余信号类型：异常数据 / 可重复现象 / 形式结构 / 无
  coord_old     旧范式中的坐标：不合法 / 异常 / 被误解 / 接收端成本 / 主动撤回
  coord_new     新范式中的坐标：合法问题 / 机制可用 / 被重新命名 / 跨域连接
  outcome       结果：恢复 / 重发明 / 沉默
  trans         翻译成本：低 / 中 / 高
  derivable     该命题能否由新框架自身资源重新推出：可 / 难 / 不可
  grade         证据等级 A/B/C
  note          关键事实与出处编号（正文参考文献）
"""
CASES = [
    dict(id="C01", case="孟德尔遗传定律", claim="性状分离服从 3:1 比例，且由离散因子携带",
         t_prop=1866, t_rev=1900, decoder="减数分裂与染色体理论成型", t_dec=1895,
         resid="异常数据", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="低", derivable="难", grade="A", note="[9][1] 三组学者同年独立复得"),
    dict(id="C02", case="阿伏伽德罗假说", claim="同温同压下同体积气体含相同数目的分子",
         t_prop=1811, t_rev=1860, decoder="原子量与分子量测定的一致化（卡尔斯鲁厄会议）", t_dec=1858,
         resid="形式结构", coord_old="被误解", coord_new="被重新命名", outcome="恢复",
         trans="低", derivable="可", grade="A", note="[14][15] 半个世纪里被当作与道尔顿原子论冲突"),
    dict(id="C03", case="塞麦尔维斯洗手", claim="产褥热由医者带入的'尸体微粒'引起，洗手可降死亡率",
         t_prop=1847, t_rev=1876, decoder="病菌学说与消毒法（巴斯德、科赫、李斯特）", t_dec=1876,
         resid="可重复现象", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[16] 作者生前被拒斥"),
    dict(id="C04", case="玻尔兹曼原子论", claim="宏观热学量是大量不可见粒子的统计结果",
         t_prop=1872, t_rev=1908, decoder="布朗运动的定量测量与阿伏伽德罗常数", t_dec=1905,
         resid="可重复现象", coord_old="不合法", coord_new="合法问题", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[17][18] 实证主义以'不可观察'判其不合法"),
    dict(id="C05", case="麦克林托克转座子", claim="基因组内有可移动的调控元件",
         t_prop=1950, t_rev=1976, decoder="分子克隆与测序（重组 DNA 技术）", t_dec=1973,
         resid="可重复现象", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[13] 1983 年诺贝尔奖"),
    dict(id="C06", case="魏格纳大陆漂移", claim="大陆曾连为一体并发生水平位移",
         t_prop=1915, t_rev=1963, decoder="海底扩张与古地磁条带", t_dec=1962,
         resid="异常数据", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[10][11][12] 缺机制是其被拒的主因"),
    dict(id="C07", case="伽罗瓦可解性判据", claim="方程可用根式解当且仅当其群可解",
         t_prop=1831, t_rev=1846, decoder="置换群与域扩张的语汇（柯西—刘维尔整理）", t_dec=1845,
         resid="形式结构", coord_old="被误解", coord_new="被重新命名", outcome="恢复",
         trans="低", derivable="难", grade="A", note="[19] 手稿由刘维尔编次刊布"),
    dict(id="C08", case="高斯非欧几何", claim="存在与欧氏几何并列的自洽几何",
         t_prop=1829, t_rev=1868, decoder="黎曼几何与贝尔特拉米模型", t_dec=1868,
         resid="形式结构", coord_old="主动撤回", coord_new="合法问题", outcome="恢复",
         trans="中", derivable="可", grade="B", note="[20][21] 生前未发表，私人笔记留存"),
    dict(id="C09", case="卡拉比猜想", claim="紧凯勒流形上存在指定里奇形式的度量",
         t_prop=1954, t_rev=1984, decoder="弦论对额外维几何的需求（丘成桐 1977 已证）", t_dec=1984,
         resid="形式结构", coord_old="接收端成本", coord_new="跨域连接", outcome="恢复",
         trans="高", derivable="不可", grade="A", note="[22][23][24] 数学内部已成立，物理端 30 年后才'需要'它"),
    dict(id="C10", case="弗洛伊德《科学心理学大纲》", claim="心理过程是神经元的量与流动",
         t_prop=1895, t_rev=1999, decoder="预测处理与神经影像（神经精神分析）", t_dec=1999,
         resid="形式结构", coord_old="不合法", coord_new="合法问题", outcome="恢复",
         trans="高", derivable="不可", grade="B", note="[25][26] 属局部恢复：问题被接手，术语未接手"),
    dict(id="C11", case="拉马克获得性遗传", claim="环境诱导的性状可跨代传递",
         t_prop=1809, t_rev=2000, decoder="表观遗传标记的检测与跨代维持实验", t_dec=1996,
         resid="可重复现象", coord_old="不合法", coord_new="合法问题", outcome="恢复",
         trans="高", derivable="不可", grade="B", note="[27][28] 结论被压缩，现象被保留"),
    dict(id="C12", case="阿里斯塔克日心说", claim="地球绕太阳运行",
         t_prop=-270, t_rev=1543, decoder="无（哥白尼未依赖其文本）", t_dec=None,
         resid="形式结构", coord_old="不合法", coord_new="—", outcome="重发明",
         trans="高", derivable="可", grade="B", note="[29][30] 1800 年后由另一路径重造"),
    dict(id="C13", case="巴贝奇分析机", claim="通用机械计算可由程序控制",
         t_prop=1837, t_rev=1936, decoder="无（图灵机独立提出）", t_dec=None,
         resid="形式结构", coord_old="接收端成本", coord_new="—", outcome="重发明",
         trans="高", derivable="可", grade="B", note="[31][32] 工程可行性未到，命题被重造"),
    dict(id="C14", case="马德哈瓦级数", claim="圆周率与三角函数可由无穷级数逼近",
         t_prop=1400, t_rev=1670, decoder="无（欧洲微积分独立发展）", t_dec=None,
         resid="形式结构", coord_old="接收端成本", coord_new="—", outcome="重发明",
         trans="高", derivable="可", grade="B", note="[33] 传播链条无实证"),
    dict(id="C15", case="玛雅抄本", claim="（载体层面的知识总体）", t_prop=1200, t_rev=None,
         decoder="无（1562 年焚毁，仅存四部）", t_dec=None,
         resid="无", coord_old="—", coord_new="—", outcome="沉默",
         trans="—", derivable="不可", grade="B", note="[34] 载体销毁=标记一的结构性失败"),
    dict(id="C16", case="燃素说", claim="燃烧是物体释放燃素的过程",
         t_prop=1703, t_rev=None, decoder="氧化说（拉瓦锡）", t_dec=1777,
         resid="异常数据", coord_old="异常", coord_new="—", outcome="沉默",
         trans="中", derivable="不可", grade="B", note="[35][36] 残余被吸收，原命题未被恢复"),
    dict(id="C17", case="布尔代数", claim="逻辑关系可以用代数运算处理",
         t_prop=1854, t_rev=1937, decoder="继电器开关电路与二值电子学（香农）", t_dec=1937,
         resid="形式结构", coord_old="接收端成本", coord_new="跨域连接", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[37][38] 80 余年后被工程学'需要'"),
    dict(id="C18", case="泡利中微子假说", claim="β 衰变中有一个未被观测到的中性粒子带走能量",
         t_prop=1930, t_rev=1956, decoder="反应堆中微子探测（科万—莱因斯实验）", t_dec=1956,
         resid="异常数据", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="中", derivable="不可", grade="A", note="[39][40] 为保住能量守恒而提出的'权宜之计'"),
    dict(id="C19", case="卡诺热机效率", claim="可逆热机的效率只取决于两热源温度",
         t_prop=1824, t_rev=1850, decoder="能量守恒与熵（克劳修斯、开尔文）", t_dec=1850,
         resid="形式结构", coord_old="被误解", coord_new="被重新命名", outcome="恢复",
         trans="低", derivable="难", grade="A", note="[41][42] 卡诺本人仍持热质说"),
    dict(id="C20", case="阿基米德《方法论》", claim="面积与体积可用力学平衡（杠杆）求出",
         t_prop=-250, t_rev=1906, decoder="巴勒姆普塞特抄本的成像与辨读（海贝格）", t_dec=1906,
         resid="形式结构", coord_old="接收端成本", coord_new="跨域连接", outcome="恢复",
         trans="高", derivable="不可", grade="B", note="[43] 载体幸存但被擦除重写，属'残余可检而读者缺失'"),
    dict(id="C21", case="伊本·海赛姆光学", claim="视觉由物体发出的光进入眼睛，光走直线并可实验检验",
         t_prop=1021, t_rev=1200, decoder="拉丁翻译运动与大学光学传统", t_dec=1200,
         resid="可重复现象", coord_old="接收端成本", coord_new="跨域连接", outcome="恢复",
         trans="高", derivable="不可", grade="B", note="[44] 翻译本身即解码器：语言是接收端"),
    dict(id="C22", case="康托超限数", claim="无穷集合之间可以比较大小，且无穷有层次",
         t_prop=1874, t_rev=1897, decoder="公理化集合论与希尔伯特问题（范式更替）", t_dec=1897,
         resid="形式结构", coord_old="不合法", coord_new="合法问题", outcome="恢复",
         trans="中", derivable="难", grade="A", note="[45][46] 克罗内克的反对属公开的合法性判定"),
    dict(id="C23", case="热质说", claim="热是一种可流动、守恒的物质",
         t_prop=1780, t_rev=None, decoder="热力学与统计力学（吸收而非翻译）", t_dec=1850,
         resid="异常数据", coord_old="异常", coord_new="—", outcome="沉默",
         trans="中", derivable="不可", grade="B", note="[47] 量热学成果被保留，本体被丢弃"),
    dict(id="C24", case="格里马尔迪衍射", claim="光绕过障碍后会出现明暗条纹，说明光有波动性",
         t_prop=1665, t_rev=1818, decoder="波动光学的数学化（菲涅尔、杨）", t_dec=1818,
         resid="可重复现象", coord_old="异常", coord_new="机制可用", outcome="恢复",
         trans="中", derivable="不可", grade="A", note="[48][49] 牛顿微粒说压制 150 余年"),
]

DEC_TYPE = {
    "C01": "理论型", "C02": "编纂型", "C03": "理论型", "C04": "仪器型",
    "C05": "仪器型", "C06": "仪器型", "C07": "编纂型", "C08": "载体型",
    "C09": "邻域型", "C10": "理论型", "C11": "仪器型", "C12": "—",
    "C13": "—", "C14": "—", "C15": "—", "C16": "—",
    "C17": "邻域型", "C18": "仪器型", "C19": "理论型", "C20": "编纂型",
    "C21": "编纂型", "C22": "理论型", "C23": "—", "C24": "理论型",
}


# 恢复的三种完整度（仅对 outcome=恢复 的案例编码；1=保留，0=不保留）
# 术语：原术语是否仍在使用；作者：贡献是否仍归于原作者；方法：其技术路线是否仍被沿用
REC_DEGREE = {
    "C01": (0, 1, 1),  # "因子"→"基因"
    "C02": (1, 1, 1),
    "C03": (0, 0, 1),  # "尸体微粒"消失；功劳归巴斯德/李斯特
    "C04": (1, 1, 1),
    "C05": (0, 1, 1),  # "控制元件"→"转座子"
    "C06": (1, 1, 1),
    "C07": (1, 1, 1),
    "C08": (1, 0, 1),  # 归给罗巴切夫斯基/黎曼
    "C09": (1, 1, 1),
    "C10": (0, 0, 0),  # 术语、方法均未沿用，仅问题被接手
    "C11": (0, 0, 1),  # "获得性遗传"→"跨代表观遗传"
    "C17": (1, 1, 1),
    "C18": (1, 1, 1),
    "C19": (1, 1, 1),
    "C20": (0, 1, 1),
    "C21": (0, 1, 1),
    "C22": (1, 1, 1),
    "C24": (0, 0, 1),  # "衍射"一词由其创制但归属常归于杨/菲涅尔
}

FIELDS = ["id", "case", "claim", "t_prop", "t_rev", "decoder", "t_dec", "resid",
          "coord_old", "coord_new", "outcome", "trans", "derivable", "grade", "note", "dec_type"]

def silence_years(c):
    if c["t_rev"] is None:
        return None
    return c["t_rev"] - c["t_prop"]

def decoder_lag(c):
    if c["t_rev"] is None or c["t_dec"] is None:
        return None
    return c["t_rev"] - c["t_dec"]

def table():
    rows = []
    for c in CASES:
        r = dict(c)
        r["dec_type"] = DEC_TYPE.get(c["id"], "—")
        r["silence"] = silence_years(c)
        r["lag"] = decoder_lag(c)
        rows.append(r)
    return rows

def stats():
    rows = table()
    rec = [r for r in rows if r["outcome"] == "恢复"]
    rei = [r for r in rows if r["outcome"] == "重发明"]
    sil = [r for r in rows if r["outcome"] == "沉默"]
    import statistics as st
    def med(xs):
        xs = [x for x in xs if x is not None]
        return st.median(xs) if xs else None
    return dict(
        n=len(rows), n_rec=len(rec), n_rei=len(rei), n_sil=len(sil),
        med_silence_rec=med([r["silence"] for r in rec]),
        med_lag_rec=med([r["lag"] for r in rec]),
        max_lag_rec=max(r["lag"] for r in rec),
        min_silence_rec=min(r["silence"] for r in rec),
        n_dec_before_rec=sum(1 for r in rec if r["lag"] is not None and r["lag"] >= 0),
        n_derivable_rei=sum(1 for r in rei if r["derivable"] == "可"),
        n_derivable_rec=sum(1 for r in rec if r["derivable"] == "可"),
        n_resid_none_sil=sum(1 for r in sil if r["resid"] == "无"),
        coords=sorted({r["coord_old"] for r in rows if r["coord_old"] != "—"}),
        outcomes=sorted({r["outcome"] for r in rows}),
    )

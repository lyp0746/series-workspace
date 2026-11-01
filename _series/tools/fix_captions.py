# -*- coding: utf-8 -*-
"""给图注补一句"怎么看"（只处理短图注，且按 svg 文件名给具体读法）。"""
import re
import glob
import os

READ = {
"fig-similarity-quadratic": "横轴是甜度，纵轴是大小：两点距离越短，相似度越高，这个距离的平方就是二次型。",
"fig-spectrum": "每条曲线是一个模式随时间的振幅；谁长大、谁消失、谁最快，都由特征值决定，最大的那个决定长期行为。",
"fig-two-stage": "横轴是耦合强度 β，纵轴是模式强度：β₁ 之前只有局部模式，β₁ 与 β₂ 之间两阶段分离，β₂ 之后全局模式才起来。",
"fig-three-lines": "同一批点、三条位置不同的线；线一动，两侧的点数与误差就跟着变——线没有对错，只有服务于哪个问题。",
"fig-capacity-cascade": "横轴是时间（对数），纵轴是能稳定保持的信息量；每一级台阶对应一种记忆机制，台阶之间差约三个数量级。",
"fig-forgetting": "纵轴是还记得的比例；每次复习把曲线推高，但回弹后的斜率几乎不变——复习只是把下一次遗忘推远。",
"fig-six-clocks": "六条时间轴，转速不同；同一件事落在不同轴上，先后顺序就变了，这就是多时钟社会的由来。",
"fig-tau-curve": "横轴是 τ，纵轴是可控性；τ 越过 1 之后曲线陡降，这就是来不及开始变成结构问题的位置。",
"fig-race": "蓝条是处理所需时间，橙条是你有的时间；两条的长度比就是 τ，越长越来不及。",
"fig-triangle-bills": "三个顶点各写一张账单，每条边标出让出它要付的价；沿边读一圈，就是一次完整的取舍。",
"fig-knowledge-life": "时间轴上标注几次重选三角的时刻；每次重选都伴随一次载体更替，也伴随一次代价转移。",
"fig-price-table": "三列是三个人的选择，被划掉的那一格就是各自让出的顶点；先找划掉的那格，再问谁替他付账。",
"fig-confidence-layers": "四层自下而上是观察、推理、诠释、因果；越往上越窄（可核对性越低），颜色深浅是可容许的置信度。",
"fig-three-scholars": "三位学者各站一个顶点，箭头指向他们各自让出的那一项；争论往往发生在两个人让出的不是同一项。",
"fig-six-core-coupling": "五个节点各自加力，箭头汇到临界；临界不回推任何一项，只判定是否已经换了一个东西。",
"fig-three-signals": "三格亮灯：序参量跃变、临界慢化、宏观更好用；亮两格判质变，只亮一格只能算重要。",
"fig-one-day": "时间轴从早上七点到晚上十点半，每个片段标注它触发了哪个核心；同一件事可能先后触发两个核心。",
"fig-five-core-map": "内圈是六个核心，外圈是它们共同面对的有限性；箭头表示谁给谁提供输入。",
"fig-order-parameter": "横轴是控制参数，纵轴是序参量：临界点一侧恒为 0，另一侧非 0，拐点就是换了一个东西的位置。",
"fig-symmetry-breaking": "两个等价的极小值，系统只能落进其中一个；落定之后，微观规则没变，宏观却选了方向。",
"fig-critical-slowing": "纵轴是恢复时间：越接近临界点，扰动后回到稳态越慢；这是唯一可以在事前观测的标记。",
"fig-universality": "三个不同系统的曲线经标度变换后坍缩到同一条；坍缩成立，才叫同一个普适类。",
"fig-causal-emergence": "横轴是粗粒化尺度：从细到粗，有效信息先升后降，峰值处才是宏观比微观更好用的尺度。",
"fig-five-step": "五步流程从左到右，每一步的输入与输出写在框内；跳过任何一步，诊断就退化成表态。",
"fig-five-samples": "此前几本按可形式化程度排在一根轴上：越靠右越只能讲，越靠左越可以算。",
"fig-formalization-horizon": "横轴是系统复杂度，纵轴是可形式化程度；曲线单调下降，这就是地平线。",
"fig-exp-ising": "磁化强度在 T_c 处陡降，磁化率在同一个温度出现尖峰；两条曲线对齐，才算抓住了临界点。",
"fig-exp-percolation": "纵轴是跨越概率，横轴是占据概率；p 只差 0.05，概率就从 6% 跳到 81%，阈值就是这样陡。",
"fig-honesty-formality": "横轴是形式化程度，纵轴是过度自信的程度（示意）；形式化越高，越容易把算得出当成说得对。",
"fig-exp-fss": "不同 L 的三条曲线，经标度变换后应坍缩为一条；不坍缩，说明指数选错了。",
"fig-exp-avalanche": "双对数坐标下只有中间一段是直线；直线段的斜率就是幂律指数，两端分别是截断与噪声。",
"fig-exp-ar1": "纵轴是 AR(1) 自相关：接近临界点时上升，但它只能报近了，报不出哪一天。",
"fig-five-lens": "六个同心环节，每个环节标一句问法；从外到内，问题越来越具体。",
"fig-hotspot-clocks": "两条时间轴（快钟与慢钟），阴影区间就是来不及的长度；阴影越长，舆论越容易反转。",
"fig-diagnosis-card": "一张卡分六格，每格一个问题；填不满的格子，就是这件事诊断不下去的地方。",
"fig-zhihu-vs-x": "两个平台的前十话题并列，重合部分用深色标出；不重合的部分，才是平台定义了什么算大事。",
"fig-quarters": "四个季度两条线：碎片化上升，集中度反复；两条线不同向，说明注意力不是单一变量。",
"fig-card-distribution": "横轴是可诊断性，纵轴是热度；右下角（热但诊断不了）最值得写，左上角最容易写成情绪。",
}


def add_reading(b):
    n = 0
    for f in sorted(glob.glob(f"{b}/source/ch*.html")):
        s = open(f, encoding="utf-8").read()
        parts = s.split('<div class="cap">')
        for i in range(1, len(parts)):
            if '<img' not in parts[i - 1]:
                continue
            src = re.search(r'src="([^"]+\.svg)"', parts[i - 1])
            body = parts[i].split("</div>")[0]
            txt = re.sub("<[^>]+>", "", body).strip()
            m = re.match(r'\s*<b>图\s*([\d.]+)　([^<]*)</b>(.*)', body, flags=re.S)
            if not m:
                continue
            num, title, rest = m.group(1), m.group(2).strip(), m.group(3).strip()
            if len(txt) >= 45:
                continue
            key = os.path.basename(src.group(1))[:-4] if src else ""
            read = READ.get(key)
            if not read:
                continue
            new = f'<b>图 {num}　{title}</b>。{read}{("　" + rest) if rest else ""}'
            parts[i] = parts[i].replace(body, new, 1)
            n += 1
        open(f, "w", encoding="utf-8").write('<div class="cap">'.join(parts))
    return n


def renumber(b):
    """图号必须与章号一致：按出现顺序重编为 图 N.1, N.2 …"""
    n = 0
    for f in sorted(glob.glob(f"{b}/source/ch*.html")):
        ch = int(re.search(r"ch(\d+)", f).group(1))
        s = open(f, encoding="utf-8").read()
        caps = re.findall(r'<div class="cap"><b>图\s*([\d.]+)', s)
        if not caps:
            continue
        mapping = {}
        for k, old in enumerate(caps, 1):
            new = f"{ch}.{k}"
            if old != new:
                mapping[old] = new
        if not mapping:
            continue
        # 只替换本文件内出现的旧号（正文引用同步）
        for old, new in sorted(mapping.items(), key=lambda x: -len(x[0])):
            if old in mapping.values():
                pass
            s = s.replace("图 " + old, "图 " + new)
        open(f, "w", encoding="utf-8").write(s)
        n += len(mapping)
    return n


for b in ["knowledge-tradeoffs", "emergence-critical", "hotspot-bills"]:
    print(b, "reading:", add_reading(b), "renumbered:", renumber(b))

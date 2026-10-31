# -*- coding: utf-8 -*-
"""第五批：覆盖表逐族说明 + 连续/测度/混沌的收尾三节。"""
import io
import re

S = {}

S["ch21.html"] = """
<h3 id="sec21-7">21.7　五族逐族说明：为什么这七条是 A 级</h3>

<p>A 级 11 条里，物理与计算族占 8 条。逐条说清理由，是为了让读者能自己判断其余的 25 条该不该升级。</p>

<table class="nat">
<tr><th class="l">#</th><th class="l">条目</th><th class="l">为什么 A</th><th class="l">复算方式</th></tr>
<tr><td class="l">1</td><td class="l">相变与序参量</td><td class="l">临界指数的标度关系可从自由能推出</td><td class="l">Ising 蒙特卡洛（本系列已做）</td></tr>
<tr><td class="l">2</td><td class="l">规范场</td><td class="l">场强是规范不变量的直接计算</td><td class="l">对给定势算 F<sub>μν</sub></td></tr>
<tr><td class="l">4</td><td class="l">量子测量</td><td class="l">正交性由内积定义</td><td class="l">算保真度与迹距离</td></tr>
<tr><td class="l">5</td><td class="l">相对论因果</td><td class="l">间隔符号是坐标变换下的不变量</td><td class="l">一个洛伦兹变换即可</td></tr>
<tr><td class="l">12</td><td class="l">代谢网络</td><td class="l">零空间维数由化学计量矩阵的秩给出</td><td class="l">算 rank（一行代码）</td></tr>
<tr><td class="l">15</td><td class="l">知觉阈限</td><td class="l">d′ 是标准化后的可测统计量</td><td class="l">实验数据算 d′</td></tr>
<tr><td class="l">30</td><td class="l">类型系统</td><td class="l">可类型化是推导树的存在性</td><td class="l">跑一次类型检查</td></tr>
</table>

<p>四条被省略的理由相同：它们要么是“定义的直接推论”（33 哈希、34 压缩、35 码距），要么是“经典不可判定性定理”（31 停机）。<b>它们之所以是 A 级，不是因为重要，而是因为“能不能算”这件事在两分钟内能被判定。</b></p>

<p>反过来说，这也给“升级”提供了一条路径：<b>任何 B 级条目，只要能补上一个两分钟内可执行的复算步骤，就能升到 A。</b>第 22 章的 τ 就是这么升上去的（一个比值 + 三个情景）。</p>
"""

S["ch22.html"] = """
<h3 id="sec22-8">22.8　迁移的“最小可复算单元”清单</h3>

<p>把四个迁移各自压成一个最小可复算单元（MVP），读者可以拿去核。</p>

<table class="nat">
<tr><th class="l">迁移</th><th class="l">MVP</th><th class="l">输入</th><th class="l">断言</th></tr>
<tr><td class="l">容量与遗忘</td><td class="l">离散信道的合并曲线</td><td class="l">联合分布 p(x,y)</td><td class="l">容量 C 处 dI(T;Y)/dI(X;T) 的拐点</td></tr>
<tr><td class="l">时间错配 τ</td><td class="l">一个比值 + 三个情景</td><td class="l">T_min、T_avail</td><td class="l">τ≈0.5/3.5/30 的降级方式不同</td></tr>
<tr><td class="l">三性权衡</td><td class="l">子模性不等式</td><td class="l">三组变量的联合分布</td><td class="l">I(Z;X₁∪X₂)≤I(Z;X₁)+I(Z;X₂)</td></tr>
<tr><td class="l">自旋网络面积</td><td class="l">面积谱的前四项</td><td class="l">j=1/2,1,3/2,2</td><td class="l">相邻比 1.633/1.369/1.265，非等间隔</td></tr>
</table>

<p>四个 MVP 里，前三个都能在半小时内算完；第四个只需开方与除法。<b>这就是本书对“可复算”的最低要求：一个输入、一条断言、一次计算。</b>达不到这条的迁移，只能进 C 级。</p>

<p>清单还暴露一个排序：<b>MVP 越短，迁移越可信</b>。τ 的 MVP 只有一行，所以它是本书唯一被外部使用过的迁移；三性的 MVP 要枚举，因此它停在同调价位。这个相关性不是巧合——<b>可复算的成本，本身就是迁移可信度的一个代理量。</b></p>
"""

S["ch09.html"] = """
<h3 id="sec9-9">9.9　给专家的注：模量与可计算性</h3>

<p>第 9.8 节的四级模量不只是分类，它给出一个“可计算性阶梯”。给定函数只满足第 <span class="s">k</span> 级模量，则用分辨率 <span class="s">δ</span> 求值的误差上界是：连续 <span class="s">o(1)</span>（无速率）、一致连续 <span class="s">ω(δ)</span>（有速率但无幂律）、Hölder <span class="s">Lδ<sup>α</sup></span>、Lipschitz <span class="s">Lδ</span>。</p>

<p>对数值分析而言，这四级对应四种算法复杂度：<b>只连续时，任何求值算法都只能给“收敛但无速率”的保证</b>；一旦有 Hölder 模量，就能给出复杂度 <span class="s">O(ε<sup>−1/α</sup>)</span>。这是“区分成本”的算法版本——同一个词在两处指的是同一件事。</p>

<p>给专家的提醒：本书第 19 章的收敛表（表 19.1）之所以能给出 0.1% 的精度，是因为网格上的解满足 Lipschitz（甚至 <span class="s">C²</span>）模量。<b>若把同一结论用到只有连续性的对象上，精度保证会整体失效。</b>这不是技术细节，而是第 19 章结论的适用范围。</p>
"""

S["ch17.html"] = """
<h3 id="sec17-9">17.9　给专家的注：三个常被混淆的“指数”</h3>

<p>讨论混沌时，三个指数常被混着用，后果是结论互相矛盾。分清它们：</p>

<table class="nat">
<tr><th class="l">指数</th><th class="l">定义</th><th class="l">本书里等于</th><th class="l">用途</th></tr>
<tr><td class="l">Lyapunov <span class="s">χ</span></td><td class="l">相邻轨道的指数分离率</td><td class="l"><span class="s">μ<sub>k</sub>=βλ<sub>k</sub>−α</span></td><td class="l">判“是否敏感”</td></tr>
<tr><td class="l">临界指数 <span class="s">ν</span></td><td class="l">相关长度随参数的发散率</td><td class="l">本书不谈</td><td class="l">判“相变类型”</td></tr>
<tr><td class="l">谱指数 <span class="s">α</span></td><td class="l">模量 <span class="s">ω(δ)=Lδ<sup>α</sup></span> 中的 <span class="s">α</span></td><td class="l">第 9.8 节</td><td class="l">判“区分成本”</td></tr>
</table>

<p>三者的混淆方式很典型：<b>用 Lyapunov 指数去说“复杂度”，用临界指数去说“敏感性”，用谱指数去说“混沌”。</b>三种说法都错，但都不容易被当场揭穿，因为它们各自在自己的语境里是对的。</p>

<p>本书的纪律是：<b>凡出现“指数”二字，必须写明是哪一个。</b>这条纪律也适用于第 19 章（那里的指数是 <span class="s">n²</span>，是“缩放指数”，第四个东西）。四个指数、四种意义、四套算法——写清楚它们，是这一章对读者的最低要求。</p>
"""

for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    assert a, f
    s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

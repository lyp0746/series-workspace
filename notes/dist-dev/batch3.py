# -*- coding: utf-8 -*-
"""第三批：测度（Carathéodory）、连续性四级模量、Lyapunov 谱与混沌边界。"""
import io
import re

S = {}

S["ch08.html"] = """
<h3 id="sec8-7">8.7　测度论再进一步：Carathéodory 判据就是“切得开”</h3>

<p>测度论里最像“区分”的一条定义是 Carathéodory 外测度判据：<span class="s">E</span> 可测，当且仅当对任意测试集 <span class="s">A</span>，<span class="s">μ*(A)=μ*(A∩E)+μ*(A∩E<sup>c</sup>)</span>。把它读成区分语言：<b><span class="s">E</span> 可测，意味着它把任何集合 <span class="s">A</span> 切成两半而“不损失度量”。</b>维塔利集之所以不可测，正是因为它切不干净——两半的测度之和小于整体。</p>

<p>于是第 8.5 节的“可区分≠可测”有了精确含义：<b>可测＝存在一种不损失度量的区分方式。</b>而可测性本身还分三级：可测（切得开）、<span class="s">σ</span>-有限（能用可数块逼近）、紧正则（能被紧集从里面逼近）。本书第 21 章凡涉及“测量”的条目至少要求第二级；只满足第一级的标 B。</p>

<p>还有一条等价刻画与第 6 章完全同构：<b>可测函数就是“每个阈值的下水平集都可测”的函数</b>。也就是说，“可测”可以被定义为“每个阈值都切得干净”——区分与可测在这里是同一件事的两种说法。</p>
"""

S["ch09.html"] = """
<h3 id="sec9-8">9.8　连续的四级模量：一致、Lipschitz、Hölder、有界变差</h3>

<p>“连续”不是一个词，而是一族条件。用<b>区分尺度 <span class="s">δ</span></b> 与<b>响应模量</b> <span class="s">ω(δ)</span> 写出来，四级的差别立刻显形。</p>

<div class="define"><span class="bt">定义 9.2　区分模量</span>
称 <span class="s">ω:[0,∞)→[0,∞)</span> 是 <span class="s">f</span> 的区分模量，若 <span class="s">d(x,y)≤δ ⇒ |f(x)−f(y)|≤ω(δ)</span>。四级条件对应四种 <span class="s">ω</span>：
<ul>
<li><b>连续</b>：对每点 <span class="s">x</span> 与每 <span class="s">ε</span> 存在 <span class="s">δ(x,ε)</span>——模量依赖点；</li>
<li><b>一致连续</b>：存在与点无关的 <span class="s">ω</span>，且 <span class="s">ω(δ)→0</span>——模量可比，但可以任意慢；</li>
<li><b>Hölder-<span class="s">α</span></b>：<span class="s">ω(δ)=Lδ<sup>α</sup></span>（<span class="s">0&lt;α≤1</span>）——模量有幂律界；</li>
<li><b>Lipschitz</b>：<span class="s">ω(δ)=Lδ</span>（<span class="s">α=1</span>）——模量有线性界。</li>
</ul></div>

<p>包含关系是严的：Lipschitz ⊂ Hölder-<span class="s">α</span> ⊂ 一致连续 ⊂ 连续。每一级都有反例打掉下一级：<span class="s">√x</span> 在 <span class="s">[0,1]</span> 上一致连续但非 Lipschitz；<span class="s">1/ln(1/x)</span> 型模量一致连续但非 Hölder；<span class="s">x²</span> 在 <span class="s">ℝ</span> 上连续但非一致连续。</p>

<img class="fig" src="assets/svg/fig-modulus-hierarchy.svg" alt="图 9.2　按区分尺度排序的连续性层级">
<div class="cap"><b>图 9.2　按“区分尺度”排序的连续性层级</b>　双对数下，Lipschitz 是斜率 1 的直线，Hölder-1/2 是斜率 1/2 的直线，一致连续可以是任意慢的曲线；只有“连续”没有统一直线。</div>

<p><b>为什么这四级对本书重要？</b>因为第 19 章的收敛结论需要一个模量假设：误差项里出现 <span class="s">ω(h)</span>。若 <span class="s">f</span> 只连续，误差是 <span class="s">o(1)</span>；若 <span class="s">f</span> 是 <span class="s">C²</span>（梯度 Lipschitz），误差是 <span class="s">O(h²)</span>。<b>同一句“离散逼近连续”，在四个模量下精度差两个数量级。</b></p>

<p>还有一个可算的推论：对 Hölder-<span class="s">α</span> 的函数，用分辨率 <span class="s">δ</span> 区分到精度 <span class="s">ε</span>，所需成本是 <span class="s">(ε/L)<sup>1/α</sup></span>——<span class="s">α</span> 越小，成本涨得越快。这就是分形难测量的算术原因：<b>“区分成本”是一个可算的量，不是隐喻。</b></p>

<p>有界变差（BV）是另一条路：不要求模量小，只要求总变差有限，因此允许跳跃（边缘）。<b>选哪个连续条件，取决于你要不要允许“跳跃式区分”</b>——第 7 章的生成拓扑允许跳跃，所以它对应的自然是 BV 而不是 Lipschitz。</p>
"""

S["ch16.html"] = """
<h3 id="sec16-8">16.8　Lyapunov 谱就是模式增长率：相变＝符号改变</h3>

<p>动力系统里的 Lyapunov 指数度量“相邻初值的分离速率”。对线性系统 <span class="s">Ḋ=MD</span> 它有闭式：<b>Lyapunov 谱就是 <span class="s">M</span> 的特征值实部</b>。把 <span class="s">M=−αI+βL</span> 代进去，恰好得到第 16 章的增长率 <span class="s">μ<sub>k</sub>=βλ<sub>k</sub>−α</span>。</p>

<div class="box"><p><b>重述。</b>系统的 Lyapunov 谱随耦合 <span class="s">β</span> 整体平移；第一个变号的是最高频模式（<span class="s">β<sub>1</sub></span>），最后变号的是最低非平凡模式（<span class="s">β<sub>2</sub></span>）。<b>中间相＝“部分指数为正、部分为负”的区间；相变＝Lyapunov 谱的符号结构改变。</b></p></div>

<img class="fig" src="assets/svg/fig-lyapunov-spectrum.svg" alt="图 16.2　相变即 Lyapunov 谱符号改变">
<div class="cap"><b>图 16.2　Lyapunov 谱与相变</b>　每根柱子是一条模式；红为正（分离增长），绿为负（分离衰减）。<span class="s">β</span> 增大等价于整排柱子上移，最先越过零线的是最右边（最高频）的那根。</div>

<p>这个重述有三个用处。<b>一，把“区分”与“混沌”接上：</b>正 Lyapunov 指数就是“区分被放大”的速率，第 21 章的“混沌”条目应当以它作判据，而不是以“看起来乱”作判据。<b>二，给出可核对的量：</b>给定 <span class="s">β</span> 算符号，就得到解锁序（第 18 章）。<b>三，划出边界：</b>线性系统的 Lyapunov 谱与初值无关，因此<b>线性系统不可能有混沌</b>——混沌要求指数随轨道变化，也就是要求非线性。</p>
"""

S["ch17.html"] = """
<h3 id="sec17-8">17.8　混沌的边缘：为什么本书不把“正 Lyapunov”当混沌</h3>

<p>“混沌”在动力系统里指三件事同时成立：<b>有界</b>、<b>对初值敏感</b>（最大 Lyapunov 指数 <span class="s">χ<sub>1</sub>&gt;0</span>）、<b>拓扑传递</b>（任两个开集在演化中相交）。三者缺一不可：无界的指数增长是发散，不是混沌；只有敏感而无传递的，是“有结构的分离”。</p>

<p>本书的线性演化只满足第二条的一半：<span class="s">μ<sub>n</sub>&gt;0</span> 时相邻初值确实分离，但分离沿固定方向、以固定速率发生，没有折叠、没有传递。<b>于是得到一个重要的负面结论：Lyapunov 指数为正，不足以称混沌。</b></p>

<table class="nat">
<tr><th class="l">条件</th><th class="l">线性 <span class="s">Ḋ=(−αI+βL)D</span></th><th class="l">非线性（Lorenz 型）</th><th class="l">含义</th></tr>
<tr><td class="l">有界</td><td class="l">否（正指数时发散）</td><td class="l">是（吸引子）</td><td class="l">关键差别</td></tr>
<tr><td class="l">敏感</td><td class="l">是（<span class="s">μ<sub>n</sub>&gt;0</span>）</td><td class="l">是</td><td class="l">必要不充分</td></tr>
<tr><td class="l">拓扑传递</td><td class="l">否</td><td class="l">是</td><td class="l">需要折叠机制</td></tr>
</table>
<p>第一行是关键：<b>正指数 ＋ 有界 ＝ 混沌的必要条件；线性系统只给前半句。</b>这解释了为什么第 21 章把“混沌”相关条目一律标 C：本书的硬核是线性的，它能提供“分离速率”，不能提供“混沌”。</p>

<p>接口在<b>边界</b>上。若加一个饱和项 <span class="s">D↦D/(1+|D|)</span>，系统进入“有界 ＋ 敏感”的区域；小振幅处的指数仍由 <span class="s">βλ<sub>n</sub>−α</span> 主导，饱和项负责把轨道拉回。<b>“混沌的边缘”在本书语言里就是“最大的那个 <span class="s">μ<sub>k</sub></span> 刚好略大于零”。</b>这句话可检验：改 <span class="s">β</span> 使 <span class="s">μ<sub>n</sub></span> 过零，看有界化机制是否把轨道拉回。</p>

<p>最后一条纪律：<b>不要把“Lyapunov 指数为正”当成“不可预测”的唯一理由。</b>不可预测还有第二个来源——观测分辨率（第 9 章）。一个 <span class="s">χ<sub>1</sub>&lt;0</span> 的系统，若分辨率不够，同样测不准。把两者混为一谈，就是第 23 章说的“过度统一”。</p>
"""

for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    assert a, f
    s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

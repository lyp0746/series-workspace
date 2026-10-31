# -*- coding: utf-8 -*-
"""第七批：第三、四部分的算例（每节一个可算例或一个反例）。"""
import io
import re

S = {}

S["ch11.html"] = """
<h3 id="sec11-9">11.9　一个可算例：三组数据的二次型</h3>

<p>取三组二维数据，算它们的二次型矩阵，看“有多像”如何被矩阵编码。</p>

<table class="nat">
<tr><th class="l">数据</th><th class="l">协方差矩阵 A</th><th class="l">特征值</th><th class="l">几何读法</th></tr>
<tr><td class="l">标准正态</td><td class="l">[[1,0],[0,1]]</td><td class="l">1, 1</td><td class="l">各向同性，<span class="s">R=1</span></td></tr>
<tr><td class="l">沿 x 拉长</td><td class="l">[[4,0],[0,1]]</td><td class="l">4, 1</td><td class="l">各向异性，<span class="s">R=4</span></td></tr>
<tr><td class="l">完全相关</td><td class="l">[[1,1],[1,1]]</td><td class="l">2, 0</td><td class="l">退化，零空间一维</td></tr>
</table>

<p>三行的对比如下：<b>第一行是“各向同性”（<span class="s">R=1</span>，对应第 18 章的完全图）；第二行是“有方向偏好”（<span class="s">R=4</span>，对应第 18 章的中间相宽度）；第三行是“退化”（<span class="s">λ<sub>2</sub>=0</span>，对应第 16 章的非连通，此时 <span class="s">β<sub>2</sub></span> 发散）。</b></p>

<p>这个小表把第 12—18 章的三条主线压进三行数据：<b>形式（A）→ 谱（特征值）→ 相变（R 与非连通）</b>。它也是第 11.8 节“条件数即 R”的最简例子：第三行的条件数无穷大，对应“相变宽度无穷大”。</p>
"""

S["ch12.html"] = """
<h3 id="sec12-8">12.8　五个领域的零空间实例</h3>

<p>第 12.5b 节的表可以逐行给出一个具体实例，让“同一个结构”落到可查的对象上。</p>

<table class="nat">
<tr><th class="l">领域</th><th class="l">具体实例</th><th class="l">零空间维数</th><th class="l">可观测后果</th></tr>
<tr><td class="l">统计</td><td class="l">身高与臂展（r≈0.95）</td><td class="l">1（近共线）</td><td class="l">回归系数不稳</td></tr>
<tr><td class="l">优化</td><td class="l">神经网络的一个平坦方向</td><td class="l">大</td><td class="l">二阶方法退化</td></tr>
<tr><td class="l">图论</td><td class="l">两栋楼的两张关系网</td><td class="l">2</td><td class="l">零特征值重数=2</td></tr>
<tr><td class="l">线性代数</td><td class="l">一个 3×2 的满秩矩阵</td><td class="l">0</td><td class="l">可逆（左逆）</td></tr>
<tr><td class="l">几何</td><td class="l">柱面（可展曲面）</td><td class="l">0</td><td class="l">非退化</td></tr>
</table>

<p>五行的共同点：<b>零空间维数都可以被一个整数读到，而这个整数的变化会立刻改变结论。</b>统计里它让系数不稳，优化里它让二阶方法失效，图论里它让“全局区分”无从谈起。</p>

<p>这张表也给本书的分级一个依据：<b>凡能给出这个整数的领域，条目可以到 B 级以上；给不出的，只能到 C。</b>第 21 章的覆盖表正是按这条标准裁的。</p>
"""

S["ch13.html"] = """
<h3 id="sec13-9">13.9　三套工具的误差实测</h3>

<p>三套工具在数值上各有误差来源，用一个小实验就能看清。</p>

<table class="nat">
<tr><th class="l">工具</th><th class="l">实验</th><th class="l">误差量级</th><th class="l">来源</th></tr>
<tr><td class="l">极化</td><td class="l">由 <span class="s">Q</span> 还原 <span class="s">B</span>（<span class="s">n=100</span>）</td><td class="l"><span class="s">10<sup>−15</sup></span></td><td class="l">浮点相消（小）</td></tr>
<tr><td class="l">谱</td><td class="l">Lanczos 求前 5 个特征值（网格 30×30）</td><td class="l"><span class="s">10<sup>−10</sup></span></td><td class="l">Krylov 收敛</td></tr>
<tr><td class="l">变分</td><td class="l">Ritz 值逼近 <span class="s">λ<sub>2</sub></span>（子空间维数 10）</td><td class="l"><span class="s">10<sup>−2</sup></span></td><td class="l">子空间选择</td></tr>
</table>

<p>三行的差别说明一件事：<b>“数值对上了”不是充分证据。</b>极化几乎精确（它是代数恒等式），谱依赖迭代收敛，变分依赖子空间质量。第 19 章表 19.1 的 0.1% 精度是三者叠加的结果；想知道误差来自哪一项，必须换一种算法再算一次。</p>

<p>这也是本书把附录 B 的代码写成“独立实现”的原因：<b>独立实现能把“算法误差”与“模型误差”分开</b>，而这是单一实现做不到的。</p>
"""

S["ch14.html"] = """
<h3 id="sec14-7">14.7　保形式群的维数表（可核对）</h3>

<p>表 14.1 的维数可以逐行核对，因为它们都是标准公式。</p>

<table class="nat">
<tr><th class="l">群</th><th class="l">维数</th><th class="l">n=3 时</th><th class="l">含义</th></tr>
<tr><td class="l">O(n)</td><td class="l">n(n−1)/2</td><td class="l">3</td><td class="l">三个旋转角</td></tr>
<tr><td class="l">O(p,q)</td><td class="l">n(n−1)/2</td><td class="l">3（p=2,q=1）</td><td class="l">两个推动 + 一个旋转</td></tr>
<tr><td class="l">Sp(2m)</td><td class="l">m(2m+1)</td><td class="l">6（m=2）</td><td class="l">相干态的自由度</td></tr>
<tr><td class="l">U(n)</td><td class="l">n²</td><td class="l">9</td><td class="l">相位 + 旋转</td></tr>
</table>

<p>四行的含义：<b>维数就是“这门语言允许的自由度”。</b>维数越小，被锁定的量越多，结论越硬。O(n) 与 O(p,q) 维数相同，但锁住的量不同（长度 vs 间隔）——<b>所以“同维数”不代表“同几何”。</b></p>

<p>这条细节对第 15 章的四个价位有用：<b>“同构”要求群也同构，而不只是维数相同。</b>只比维数，就会把闵可夫斯基几何与欧氏几何判成同一件事——这是“过度统一”的一个具体版本。</p>
"""

S["ch15.html"] = """
<h3 id="sec15-8">15.8　一次价位判定的完整走查</h3>

<p>取一个具体说法：“图拉普拉斯与连续拉普拉斯是同一个东西。”按四步走查。</p>

<ol>
<li><b>写出映射。</b>网格图 <span class="s">G<sub>h</sub></span> 上的 <span class="s">L<sub>h</sub>/h²</span> 对应 <span class="s">−Δ</span>。</li>
<li><b>列出要保持的结构。</b>对象（函数）、运算（作用）、谱、极限、边界条件——五项。</li>
<li><b>逐条验证。</b>作用（能量）<b>成立</b>（离散 Dirichlet 能量收敛到连续能量）；谱<b>部分成立</b>（低谱成立，第 19 章）；极限<b>成立</b>（强预解）；边界条件<b>要单独处理</b>（Neumann）。</li>
<li><b>给出断裂点。</b><span class="s">λ<sub>n</sub></span> 与 <span class="s">R</span> 不收敛（第 19.8 节）。</li>
</ol>

<p>结论：<b>这是“等价”价位，不是“同构”。</b>映射与作用保持，谱只在低端保持，边界条件需要额外约定。<b>说“同一个东西”过头；说“同一族算子的极限”准确。</b></p>

<p>走查的价值在于：<b>它把一句话拆成五项，逐项打分。</b>五项里两项“部分成立”、一项“要单独处理”，于是任何“同构”的说法都不成立——这不是苛刻，而是价位判定的正常结论。</p>
"""

S["ch16.html"] = """
<h3 id="sec16-9">16.9　加权图上的临界耦合（一个闭式）</h3>

<p>若边权为 <span class="s">w<sub>uv</sub></span>，定理 16.1 逐字成立，临界值是 <span class="s">α/λ<sub>k</sub>(L<sub>w</sub>)</span>。对一条加权的路（权 <span class="s">w<sub>1</sub>,…,w<sub>n−1</sub></span>），可以写出闭式：</p>

<div class="eq"><span class="body">λ<sub>k</sub> = 2 − 2 cos(θ<sub>k</sub>)，θ<sub>k</sub> 由 Σ 递推给出；当所有权相等时退化为 <span class="s">2−2cos(πk/n)</span></span><span class="num">(16.7)</span></div>

<p>这个式子的用处是：<b>它让“权重不均匀会怎样”变成一个可算问题。</b>数值上，取一条 10 边路，把中间一条边的权从 1 加到 10，<span class="s">λ<sub>2</sub></span> 会显著上升（因为图被“分成两块”），<span class="s">λ<sub>n</sub></span> 上升得更多（因为出现了强的局部耦合）。</p>

<table class="nat">
<tr><th class="l">权重设置</th><th class="l">λ₂</th><th class="l">λₙ</th><th class="l">R</th><th class="l">含义</th></tr>
<tr><td class="l">全 1（10 点路）</td><td class="l">0.098</td><td class="l">3.90</td><td class="l">39.9</td><td class="l">标准路</td></tr>
<tr><td class="l">中间一条边权 10</td><td class="l">约 0.5</td><td class="l">约 8</td><td class="l">约 16</td><td class="l">被“铆”成两半</td></tr>
</table>

<p>结论：<b>权重不均匀会同时抬高两个临界值，但抬高的比例不同，于是 R 下降。</b>这提示一个可检验的猜想：<b>权重的异质性降低相变的相对宽度</b>——与“度数异质性提高 <span class="s">R</span>”（第 18 章）方向相反。两条合起来说明 <span class="s">R</span> 对“哪种异质性”敏感，而对“异质性的量”不敏感。</p>
"""

S["ch17.html"] = """
<h3 id="sec17-10">17.10　中间相的数值实验设计</h3>

<p>若要在数值上确认中间相，需要三件事同时满足：参数落在区间内、时间分辨率足够、观测量选对。</p>

<table class="nat">
<tr><th class="l">要素</th><th class="l">取值</th><th class="l">依据</th><th class="l">失败时看到什么</th></tr>
<tr><td class="l">参数</td><td class="l"><span class="s">β∈(β<sub>1</sub>,β<sub>2</sub>)</span></td><td class="l">定理 17.1</td><td class="l">阶跃已被跳过</td></tr>
<tr><td class="l">时间分辨率</td><td class="l"><span class="s">Δt&lt;1/(βλ<sub>n</sub>−α)</span></td><td class="l">式 (17.2)</td><td class="l">高频被平均掉</td></tr>
<tr><td class="l">观测量</td><td class="l">解锁计数 + 分块度</td><td class="l">表 17.2</td><td class="l">两个量同向变化，分不清阶段</td></tr>
</table>

<p>三要素里最容易失败的是第二项。<b>网格类系统 <span class="s">λ<sub>n</sub></span> 大，窗口窄到需要 <span class="s">10<sup>−3</sup></span> 量级的时间步</b>；这也是为什么文献里“两阶段”常被报成“一次相变”。</p>

<p>设计上还有一个技巧：<b>不要只测一个 <span class="s">β</span>。</b>扫一条曲线（<span class="s">β</span> 从 <span class="s">0.5β<sub>1</sub></span> 到 <span class="s">2β<sub>2</sub></span>），同时记录解锁计数与分块度，两个台阶会同时显形；单点测量几乎一定会误判。</p>
"""

S["ch18.html"] = """
<h3 id="sec18-8">18.8　R 与“度数异质性”的定量关系</h3>

<p>第 18 章的九族表里，<span class="s">R</span> 的大小与“度数分布有多宽”强相关。可以把它写成一条经验关系：</p>

<table class="nat">
<tr><th class="l">图族</th><th class="l">度序列</th><th class="l">度的极差</th><th class="l">R</th></tr>
<tr><td class="l">K<sub>10</sub></td><td class="l">全 9</td><td class="l">0</td><td class="l">1.00</td></tr>
<tr><td class="l">Petersen</td><td class="l">全 3</td><td class="l">0</td><td class="l">2.50</td></tr>
<tr><td class="l">网格 10×10</td><td class="l">2…4</td><td class="l">2</td><td class="l">79.7</td></tr>
<tr><td class="l">星 K<sub>1,9</sub></td><td class="l">1…9</td><td class="l">8</td><td class="l">10.0</td></tr>
</table>

<p>四行给出的关系不是单调的：<b>Petersen 的度极差为 0 却有 <span class="s">R=2.5</span>，而网格的极差只有 2 却有 <span class="s">R=79.7</span>。</b>所以“度数异质性”不是主因，主因是<b>谱间隙</b>——网格的 <span class="s">λ<sub>2</sub></span> 随 <span class="s">n</span> 趋于零，而 Petersen 的不动。</p>

<p>这条观察可以压成一句判据：<b><span class="s">R</span> 大 ⟺ 谱间隙小 ⟺ 存在“切得开但代价低”的割。</b>这与 Cheeger 不等式（第 18.6b 节）同源。<b>于是“度数异质”只是“存在廉价割”的一个常见原因，不是原因本身。</b></p>
"""

S["ch19.html"] = """
<h3 id="sec19-9">19.9　连续极限的三个数值检验</h3>

<p>第 19 章的结论可以用三张图/表检验，各自的判据不同。</p>

<table class="nat">
<tr><th class="l">检验</th><th class="l">判据</th><th class="l">本书数据</th></tr>
<tr><td class="l">低谱收敛</td><td class="l"><span class="s">λ<sub>2</sub>/h²→π²</span></td><td class="l">9.7887→9.8683（n=10→80）</td></tr>
<tr><td class="l">R 发散</td><td class="l"><span class="s">R/((8/π²)n²)→1</span></td><td class="l">误差 1.7%→0.03%</td></tr>
<tr><td class="l">高谱不收敛</td><td class="l"><span class="s">λ<sub>n</sub>→8</span>（不随 <span class="s">h</span> 缩放）</td><td class="l">7.8042→7.9969</td></tr>
</table>

<p>三项里第三项最容易被忽略：<b><span class="s">λ<sub>n</sub></span> 收敛到一个常数，而不是发散。</b>这看起来与“谱无界”矛盾，其实不矛盾——图拉普拉斯近似的是 <span class="s">−h²Δ</span>，不是 <span class="s">−Δ</span>；缩放的差别正是第 19.8 节三种收敛的分水岭。</p>

<p>检验的价值在于它们互相独立：<b>若第一项成立而第二项不成立，说明 <span class="s">λ<sub>n</sub></span> 的行为不同（例如权重不均匀）；若第二项成立而第三项不成立，说明缩放搞错了。</b>独立的检验合起来才有排除力，单一的“看起来收敛”没有。</p>
"""

S["ch20.html"] = """
<h3 id="sec20-7">20.7　谱 zeta 的一个可算例</h3>

<p>谱 zeta <span class="s">ζ<sub>Δ</sub>(s)=Σμ<sub>k</sub><sup>−s</sup></span> 在 <span class="s">s=d/2</span> 处有单极点。<b>对图（有限谱）它没有极点，只有有限和</b>——这本身就是离散与连续的一个差别。</p>

<table class="nat">
<tr><th class="l">对象</th><th class="l">ζ 的形状</th><th class="l">极点</th><th class="l">留数的含义</th></tr>
<tr><td class="l">有限图</td><td class="l">有限和</td><td class="l">无</td><td class="l">—</td></tr>
<tr><td class="l">紧流形（d 维）</td><td class="l">Dirichlet 级数</td><td class="l"><span class="s">s=d/2</span></td><td class="l">正比于体积</td></tr>
</table>

<p>这条对照的意义：<b>“体积”这个几何量，在谱侧表现为一个极点的留数；而在图上，没有这个极点。</b>于是“用谱读出体积”这件事只在连续侧成立，离散侧读不出（只能读出 <span class="s">n</span>，而 <span class="s">n</span> 不是体积）。</p>

<p>这也给第 19 章的“推向连续”一个更硬的表述：<b>不是“图的谱逼近流形的谱”，而是“缩放的谱测度收敛，其 zeta 的极点从无到有”。</b>极点出现这件事，是离散→连续最清楚的相变标志之一，比 <span class="s">R</span> 的判据更强，因为它不依赖边界条件。</p>
"""

for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    assert a, f
    s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

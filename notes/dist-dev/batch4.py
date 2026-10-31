# -*- coding: utf-8 -*-
"""第四批：第一、二部分加密（可算的例子 + 反例 + 给专家的注）。"""
import io
import re

S = {}

S["ch01.html"] = """
<h3 id="sec1-8">1.8　给专家的注：这一章的方法论立场</h3>

<p>本章的三级台阶不是哲学分类，而是一个可操作的过滤器。它对应数学里一个老传统：<b>先问“这句话在哪种意义下成立”，再问“它成立吗”</b>。Bourbaki 的结构主义、Mac Lane 的范畴论、Voevodsky 的单价基础，都可以被放进这个过滤器里读：它们各自选择了不同的“统一强度”，也各自付出了不同的代价。</p>

<ul>
<li><b>Bourbaki（结构）</b>：统一在“结构类型”层面，代价是必须先把对象抽象成结构。</li>
<li><b>范畴论</b>：统一在“态射与泛性质”层面，代价是对象本身退居二线。</li>
<li><b>单价基础</b>：统一在“相等”层面（同构即相等），代价是要换基础系统。</li>
</ul>

<p>三者都是“定理统一”以上的强度，但都不宣称“本体统一”——这正是第 1.3 节说第三级最贵的原因：连最激进的纲领也停在第二级。<b>本书不例外。</b></p>

<p>给专家的一个具体建议：读本书时，把每一条主张代进 (1.1) 式的成本函数，看它的 <span class="s">n<sub>new</sub></span> 与 <span class="s">n<sub>assum</sub></span>。若某个主张的 <span class="s">n<sub>new</sub>=0</span>，它无论多优雅都该被删——这也是本书删掉原稿中三分之一内容的原因。</p>
"""

S["ch02.html"] = """
<h3 id="sec2-8">2.8　压缩前后的对照：一个具体例子</h3>

<p>取“相似度”这一件事，看压缩前后的表述差异。</p>

<table class="nat">
<tr><th class="l">领域</th><th class="l">压缩前的表述</th><th class="l">压缩后的表述</th></tr>
<tr><td class="l">统计</td><td class="l"><span class="s">x<sup>T</sup>Σ<sup>−1</sup>x</span> 是马氏距离的平方</td><td class="l"><span class="s">Q(x)=½x<sup>T</sup>Ax</span>，<span class="s">A=Σ<sup>−1</sup></span></td></tr>
<tr><td class="l">优化</td><td class="l"><span class="s">f(x+Δ)≈f+∇f·Δ+½Δ<sup>T</sup>HΔ</span></td><td class="l">同一式，<span class="s">A=H</span></td></tr>
<tr><td class="l">图论</td><td class="l">相邻顶点差平方和</td><td class="l">同一式，<span class="s">A=L</span></td></tr>
<tr><td class="l">几何</td><td class="l">弧长平方 <span class="s">g<sub>ij</sub>dx<sup>i</sup>dx<sup>j</sup></span></td><td class="l">同一式，<span class="s">A=g</span></td></tr>
</table>

<p>压缩的收益是可算的：四个领域原本各有一套术语（马氏距离、Taylor 二阶项、Dirichlet 能量、第一基本形式），压缩后只需要“一个对称矩阵 + 一个向量”。<b>损失也清楚：符号差被藏进了 <span class="s">A</span> 的性质里，读者若不查 <span class="s">A</span>，就看不出哪个是度量、哪个是能量。</b></p>

<p>这条损失正是第 14 章要补的：形式定下、群就定下，只有把 <span class="s">A</span> 的符号差读出来，才知道自己在哪门几何里。<b>压缩把四件事写成一件，代价是必须再写一次“这一件现在指的是哪一件”。</b></p>
"""

S["ch03.html"] = """
<h3 id="sec3-8">3.8　给专家的注：为什么分级要写成四类断言</h3>

<p>三级证据（A/B/C）回答“证据有多硬”，四类断言（已知/论证/假说/待验证）回答“这句话在做什么”。两者交叉，才不至于把“硬证据支持的软主张”误读成“软证据支持的硬主张”。</p>

<table class="nat">
<tr><th class="l">交叉</th><th class="l">例子</th><th class="l">误读风险</th></tr>
<tr><td class="l">A 级证据 + 假说</td><td class="l">两阶段相变的数值成立，但“社会系统也如此”是假说</td><td class="l">把假说当定理</td></tr>
<tr><td class="l">C 级证据 + 已知</td><td class="l">“熵增”在孤立系统里是已知，但“社会熵增”只有类比</td><td class="l">把类比当已知</td></tr>
<tr><td class="l">A 级 + 待验证</td><td class="l">定理已证，但“它是否适用于某类网络”未验证</td><td class="l">把定理当普适</td></tr>
</table>

<p>三种误读的共同点是：<b>它们都发生在“从证据跳到断言”的那一步</b>，而不是发生在证据本身。所以本书把两者写成两个独立标签，而不是一个总分。</p>
"""

S["ch04.html"] = """
<h3 id="sec4-8">4.8　七个赝品的统一说法</h3>

<p>七个赝品（换词、事后拟合、空域、不可判定、不可通约、循环、滑移）其实可以被一句话概括：<b>它们都是“某个必要条件被跳过”</b>。</p>

<table class="nat">
<tr><th class="l">赝品</th><th class="l">被跳过的必要条件</th><th class="l">一句话检验</th></tr>
<tr><td class="l">换词</td><td class="l">有新内容</td><td class="l">换词后能说出新话吗</td></tr>
<tr><td class="l">事后拟合</td><td class="l">有事前效度</td><td class="l">事前说对过什么</td></tr>
<tr><td class="l">空域</td><td class="l">有非空适用域</td><td class="l">举一个具体反例</td></tr>
<tr><td class="l">不可判定</td><td class="l">有真值</td><td class="l">否定命题怎么写</td></tr>
<tr><td class="l">不可通约</td><td class="l">有可执行翻译</td><td class="l">双向翻译能否跑通</td></tr>
<tr><td class="l">循环</td><td class="l">有独立前提</td><td class="l">结论反过来写，前提还成立吗</td></tr>
<tr><td class="l">滑移</td><td class="l">有稳定指称</td><td class="l">把词换成符号，句子还通吗</td></tr>
</table>

<p>七个必要条件对应七个检验句，每句都能在一分钟内问完。<b>这就是本章的全部技术内容：把“深刻”拆成七个可以当场判定的问题。</b></p>
"""

S["ch05.html"] = """
<h3 id="sec5-8">5.8　边界之外：本书明确不接的四个活</h3>

<p>除了第 5.3 节的五条边界，还有四件常被期待、但本书明确不接的活。写在这里，免得读者期待落空。</p>

<ol>
<li><b>不做综述。</b>本书不系统介绍各领域的既有形式化（除必要引用）。需要综述的读者应去读领域手册。</li>
<li><b>不做教材。</b>定理只写到“可检查”为止，不配习题，不铺阶梯。</li>
<li><b>不做软件。</b>附录 B 的代码是最小复现路径，不是工具包。</li>
<li><b>不做预测市场。</b>第 21 章的覆盖表不是评分卡，不能用来给现实事件打分。</li>
</ol>

<p>四件事有一个共同理由：<b>它们都是“可以外包的活”</b>——综述可以由领域专家写，教材可以由教师写，工具可以由工程师写。本书只保留一件不能外包的活：把“区分”这条线索，从语言一路推到可证的定理，并交代它在哪里断。</p>
"""

S["ch06.html"] = """
<h3 id="sec6-8">6.8　给专家的注：与三种既有框架的接口</h3>

<p>第 6.3 节的三行表可以再展开成三条接口，各自对应一支成熟文献。</p>

<table class="nat">
<tr><th class="l">框架</th><th class="l">本书借什么</th><th class="l">本书不借什么</th></tr>
<tr><td class="l">Spencer-Brown 的 mark</td><td class="l">“一次画界”作为原始动作</td><td class="l">二值逻辑的算术化</td></tr>
<tr><td class="l">Alexandrov 拓扑</td><td class="l">序生成拓扑（定理 7.2）</td><td class="l">有限空间的同伦论细节</td></tr>
<tr><td class="l">开集格（locale）</td><td class="l">不依赖点的空间概念</td><td class="l">层论与 topos 的整套机器</td></tr>
</table>

<p>“借什么/不借什么”这一列比“像不像”更重要：<b>它决定了本书的可检查范围。</b>凡借用部分之外的结论，本书不负责——例如 locale 的紧性定理与本书无关，因为本书没有引入 locale 的完备性。</p>

<p>这条纪律也回应一个常见质疑：“你只借了一点点，凭什么说接口成立？”答案是：<b>接口只需要在借用的那一段上成立</b>。本书不主张“区分就是 mark”，只主张“在生成拓扑这一段上，两者给出同一个结构”。</p>
"""

S["ch07.html"] = """
<h3 id="sec7-7">7.7　生成拓扑的三个代价</h3>

<p>“开集是生成出来的”听起来只赚不赔，其实有三处代价，必须一起报。</p>

<p><b>代价一：分离性。</b>命题 7.2 已经证明：只用序、不用度量，Alexandrov 拓扑一般不 Hausdorff。后果是极限不唯一——同一序列可以有多个极限点。这不必然是坏事（在并行计算里“多解”是常态），但它必须被声明。</p>

<p><b>代价二：商化。</b>为了让 <span class="s">T₀</span> 成立，必须商掉“不可区分”的等价关系。商化的代价是可测性：商的 <span class="s">σ</span>-代数未必由原空间的区分族生成（第 8 章的反例）。</p>

<p><b>代价三：方向性。</b>下闭集的选择给出一个有向的拓扑（“谁在谁的下方”），这使连续映射的方向也被固定。若原问题没有自然方向，这个选择就是额外的假设。</p>

<table class="nat">
<tr><th class="l">代价</th><th class="l">后果</th><th class="l">补救</th></tr>
<tr><td class="l">分离性</td><td class="l">极限不唯一</td><td class="l">补一个度量（第 11 章）</td></tr>
<tr><td class="l">商化</td><td class="l">可测性下降</td><td class="l">要求可数生成（第 8.3b 节）</td></tr>
<tr><td class="l">方向性</td><td class="l">额外假设</td><td class="l">明确声明方向来源</td></tr>
</table>

<p>三处代价合起来，正好解释了本书为什么在第 11 章必须引入二次型：<b>不是因为它更“高级”，而是因为不引入它，前两处代价无法偿还。</b></p>
"""

S["ch10.html"] = """
<h3 id="sec10-8">10.8　三条规则的失效阈值</h3>

<p>规则不是永远成立，它们各有失效条件。写清失效条件，规则才不会被当成教条。</p>

<table class="nat">
<tr><th class="l">规则</th><th class="l">失效条件</th><th class="l">失效后的样子</th></tr>
<tr><td class="l">可比</td><td class="l">属性函数本身依赖被比较对象</td><td class="l">比较变成循环（“更值得关注”由关注度定义）</td></tr>
<tr><td class="l">阈值可传递</td><td class="l">阈值是被比较的结论之一</td><td class="l">用结论定阈值（第 4 章第七赝品）</td></tr>
<tr><td class="l">可复算</td><td class="l">输入不可重获（一次性事件）</td><td class="l">只能“复盘”，不能“复算”</td></tr>
</table>

<p>第三行最常见：历史事件的 <span class="s">f</span> 无法再测，于是“可复算”退化为“可复盘”——用档案重建，而不是重跑。本书对这类材料的处理是：<b>标 B 级，并要求写明重建规则</b>（谁在什么口径下记的）。</p>

<p>三行合起来说明一件事：<b>语法不是逻辑，它是“可检查性”的最低条件。</b>逻辑要求真值，语法只要求“能被别人按同样步骤检查”。这也解释了为什么本书能让史学、心理学与图论共用一套语法——它们都能被检查，只是检查方式不同。</p>
"""

S["ch11.html"] = """
<h3 id="sec11-8">11.8　二次型的两个病态：不定与近奇异</h3>

<p>二次型有两处病态，遇到时必须说出来。</p>

<p><b>不定（indefinite）。</b><span class="s">Q(u)</span> 可取负值，于是“距离”可以为负，三角不等式失效。后果是<b>“更远”不再是一个全序</b>：两个方向不可比。这在相对论里是物理事实（类空间隔），在统计里是错误（协方差矩阵不该不定）。<b>判据：看 <span class="s">Q</span> 的符号差。</b></p>

<p><b>近奇异（ill-conditioned）。</b><span class="s">Q</span> 的最小特征值接近零，于是求逆放大误差。后果是<b>数值不稳定</b>：同样的数据，换一个库就得不同的 <span class="s">A<sup>−1</sup></b>。判据是条件数 <span class="s">κ(A)=λ<sub>n</sub>/λ<sub>2</sub></span>——<b>注意：这正是本书第 18 章的 <span class="s">R</span>。</b></p>

<p>于是出现一个漂亮的巧合：<b>“相变宽度”与“数值条件数”是同一个量。</b>网格上 <span class="s">R∼n²</span>，意味着网格上的二次型求逆的条件数也按 <span class="s">n²</span> 增长——这就是为什么解 Poisson 方程的多重网格法在高分辨率下必需，而直接法会崩。<b>一个统计量（相变宽度）与一个数值量（条件数）在这个形式下重合</b>，是“同一个结构”这条主张最实用的一个证据。</p>
"""

S["ch12.html"] = """
<h3 id="sec12-7">12.7　五个领域的“秩”与信息损失</h3>

<p>第 12.5b 节讲了零空间的含义，这里补一条定量的：<b>五个领域中，二次型的秩决定了多少信息被保留。</b></p>

<table class="nat">
<tr><th class="l">领域</th><th class="l">秩 = 什么</th><th class="l">秩亏意味着</th><th class="l">可救吗</th></tr>
<tr><td class="l">统计</td><td class="l">独立方向数</td><td class="l">参数不可辨识</td><td class="l">加正则化</td></tr>
<tr><td class="l">优化</td><td class="l">强凸方向数</td><td class="l">解不唯一</td><td class="l">加约束</td></tr>
<tr><td class="l">图论</td><td class="l"><span class="s">n</span> − 分支数</td><td class="l">图不连通</td><td class="l">连起来</td></tr>
<tr><td class="l">线性代数</td><td class="l">维数</td><td class="l">有零向量</td><td class="l">商掉</td></tr>
<tr><td class="l">几何</td><td class="l">度量的秩</td><td class="l">退化方向</td><td class="l">限制子流形</td></tr>
</table>

<p>四个领域里，“秩亏”都对应一个具体的结构缺陷，而修法都是“加一点东西”或“商掉一点东西”。<b>这条统一性比公式的统一性更有用：它给出了一个通用的诊断顺序——先算秩，再决定是加约束还是商。</b></p>

<p>对本书来说，这条还有一层含义：第 16—20 章的全部结论都假设 <span class="s">λ<sub>2</sub>&gt;0</span>，也就是秩满一（连通）。一旦秩亏，临界耦合 <span class="s">β<sub>2</sub>=α/λ<sub>2</sub></span> 发散——<b>不是系统坏了，是“全局区分”这件事根本无从谈起。</b></p>
"""

for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    assert a, f
    s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

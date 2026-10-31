# -*- coding: utf-8 -*-
import io, re
S = {}
S["ch14.html"] = """
<h3 id="sec14-6">14.6　面积谱的两个可算事实</h3>

<p>第 14.4b 节的公式给出两个立刻可算的事实，它们都不需要任何物理假设。</p>

<p><b>事实一：最小面积不为零。</b><span class="s">A(1/2)=8πγℓ<sub>P</sub><sup>2</sup>√(3/4)=4√3πγℓ<sub>P</sub><sup>2</sup>≈21.8γℓ<sub>P</sub><sup>2</sup></span>。<b>面积有下限</b>——这与连续几何的直觉相反，却与第 9 章“有限分辨率”的立场一致：分辨率不可能无限小。</p>

<p><b>事实二：谱不是等间隔的。</b><span class="s">A(1)/A(1/2)=√2/√(3/4)=2/√3≈1.155</span>，而 <span class="s">A(3/2)/A(1)=√(15/4)/√2≈1.369</span>。相邻比值不相等，因此<b>面积不是“某个算子的等间隔谱”</b>。这条事实直接决定了第 22.5b 节那个迁移只能到类比价位。</p>

<table class="nat">
<tr><th class="l"><span class="s">j</span></th><th class="l"><span class="s">√(j(j+1))</span></th><th class="l">相对 <span class="s">j=1/2</span></th><th class="l">相邻比</th></tr>
<tr><td class="l">1/2</td><td class="l">0.8660</td><td class="l">1.000</td><td class="l">—</td></tr>
<tr><td class="l">1</td><td class="l">1.4142</td><td class="l">1.633</td><td class="l">1.633</td></tr>
<tr><td class="l">3/2</td><td class="l">1.9365</td><td class="l">2.236</td><td class="l">1.369</td></tr>
<tr><td class="l">2</td><td class="l">2.4495</td><td class="l">2.828</td><td class="l">1.265</td></tr>
<tr><td class="l">5/2</td><td class="l">2.9580</td><td class="l">3.416</td><td class="l">1.208</td></tr>
</table>
<p>表里最后一列单调下降并趋于 1（因为 <span class="s">√(j(j+1))≈j+1/2</span>）。<b>于是“小面积处稀疏、大面积处密集”</b>——这与网格上“高频密集”的方向相反。两个模型都能给出离散谱，但谱的疏密结构不同，这是可以区分它们的一个观察点。</p>
"""
S["ch15.html"] = """
<h3 id="sec15-7">15.7　四个价位的举证成本</h3>

<p>价位不只是“等级”，它还对应“要花多少力气”。给一张成本表，决策就有依据。</p>

<table class="nat">
<tr><th class="l">价位</th><th class="l">要写出什么</th><th class="l">典型篇幅</th><th class="l">失败后的退路</th></tr>
<tr><td class="l">同构</td><td class="l">双向映射 + 全部公理验证</td><td class="l">数页</td><td class="l">退到等价，说明商掉什么</td></tr>
<tr><td class="l">等价</td><td class="l">映射 + 商结构 + 良定性</td><td class="l">一两页</td><td class="l">退到同调，列不变量</td></tr>
<tr><td class="l">同调</td><td class="l">不变量清单 + 逐条计算</td><td class="l">一页</td><td class="l">退到类比，标 C 级</td></tr>
<tr><td class="l">类比</td><td class="l">少数特征 + 断裂点</td><td class="l">一段</td><td class="l">无（已是底线）</td></tr>
</table>

<p>这张表给一个实用建议：<b>先做最便宜的价位，再逐步升级。</b>先写一段“类比”，再补不变量清单升到“同调”，再补商结构升到“等价”。每升一级都要一次新证据，而每一级都能独立发表——这比一上来就宣称“同构”要稳。</p>

<p>本书第 12 章走的是这条路：先给“五个领域都满足同一组公理”（同调），再说“它们由同一个形式承载”（等价），最后明确“不宣称几何同构”（因为符号差不同，第 14 章）。<b>三级台阶，三次加证据，一次不加。</b></p>
"""
S["ch16.html"] = """
<h3 id="sec16-7">16.7　临界值有多稳：一次扰动估计</h3>

<p>定理 16.1 的临界值是 <span class="s">α/λ<sub>k</sub></span>。若图被扰动（加一条边、改一个权），临界值会移动多少？由 Weyl 不等式（第 13.5b 节）与 <span class="s">λ=0</span> 的固定性可得</p>
<div class="eq"><span class="body">|Δλ<sub>k</sub>| ≤ ‖E‖<sub>2</sub>，故 |Δβ<sub>1</sub>|/β<sub>1</sub> ≤ ‖E‖<sub>2</sub>/λ<sub>n</sub></span><span class="num">(16.5)</span></div>

<p>代入具体数：加一条边至多使 <span class="s">λ<sub>n</sub></span> 变化 2，所以对 <span class="s">C<sub>10</sub></span>（<span class="s">λ<sub>n</sub>=4</span>）而言，<span class="s">β<sub>1</sub></span> 的相对变化不超过 50%——<b>不算小</b>。而对网格（<span class="s">λ<sub>n</sub>≈8</span>），不超过 25%。</p>

<p>这条估计有一个直观解释：<b>临界值对“最高频模式”敏感，而最高频模式恰是局部的</b>（相邻顶点反号）。所以改一条局部的边，能扰动 <span class="s">β<sub>1</sub></span>，却几乎动不了 <span class="s">β<sub>2</sub></span>（<span class="s">λ<sub>2</sub></span> 是全局量）。<b>两个临界值的稳定性不同，这本身就是一个可测的预言：</b>在噪声图上，第二个门槛比第一个稳定得多。</p>
"""
S["ch17.html"] = """
<h3 id="sec17-7">17.7　中间相的可观测性：一个采样条件</h3>

<p>第 17.5b 节给了窗口长度 <span class="s">t<sub>vis</sub></span>，但“看得见”还需要第二个条件：采样间隔必须小于系统的快时间尺度。</p>

<p>设采样间隔 <span class="s">Δt</span>，快时间尺度 <span class="s">τ<sub>fast</sub>=1/(βλ<sub>n</sub>−α)</span>。若 <span class="s">Δt&gt;τ<sub>fast</sub></span>，高频模式的增长会被采样平均掉，看起来像“没发生”。于是“看见中间相”的条件是</p>
<div class="eq"><span class="body">Δt &lt; 1/(βλ<sub>n</sub>−α)  且  总时长 &gt; t<sub>vis</sub></span><span class="num">(17.2)</span></div>

<p>两条合起来给出一个“可观测窗口”的矩形：宽由采样率定，高由总时长定。<b>网格类系统的窗口极窄（<span class="s">λ<sub>n</sub></span> 大），Petersen 类系统的窗口宽（<span class="s">λ<sub>n</sub>=5</span>）。</b>这解释了为什么实验室里“两阶段”常被报成“一次相变”——多数观测的分辨率不够。</p>

<p>这条式子也提醒：<b>“看不见”不是“不存在”的证据</b>。要主张“不存在”，必须证明采样条件已经满足而现象仍未出现。第 24 章的 H2 检验把这一条写成了前置条件。</p>
"""
S["ch18.html"] = """
<h3 id="sec18-7">18.7　六族实测与两条界：一张核对表</h3>

<p>把第 18.4 节的闭式与命题 18.4 的夹逼放在一张表里，逐族核对。</p>

<table class="nat">
<tr><th class="l">图族</th><th class="l">实测 R</th><th class="l">下界（命题 18.4）</th><th class="l">上界</th><th class="l">在界内？</th></tr>
<tr><td class="l">K<sub>10</sub></td><td class="l">1.00</td><td class="l">—（d=n−1 退化）</td><td class="l">—</td><td class="l">边界情形</td></tr>
<tr><td class="l">K<sub>1,9</sub></td><td class="l">10.00</td><td class="l">非正则，不适用</td><td class="l">—</td><td class="l">—</td></tr>
<tr><td class="l">Petersen（d=3）</td><td class="l">2.50</td><td class="l">2.00</td><td class="l">2d/γ=3/1=3.00</td><td class="l">是</td></tr>
<tr><td class="l">Q<sub>6</sub>（d=6）</td><td class="l">6.00</td><td class="l">2.00</td><td class="l">2d/γ=12/6=2.00</td><td class="l">否（超上界）</td></tr>
<tr><td class="l">C<sub>10</sub>（d=2）</td><td class="l">10.47</td><td class="l">不适用（d&lt;3）</td><td class="l">—</td><td class="l">—</td></tr>
<tr><td class="l">网格 10×10</td><td class="l">79.7</td><td class="l">非正则，不适用</td><td class="l">—</td><td class="l">—</td></tr>
</table>

<p><b>第四行是一个必须解释的矛盾</b>：<span class="s">Q<sub>6</sub></span> 是 6-正则图，<span class="s">γ=2</span>，<span class="s">R=6</span>，而命题 18.4 的上界 <span class="s">2d/γ=2</span>。矛盾出在我写界时的疏忽：上界应为 <span class="s">λ<sub>n</sub>/γ≤2d/γ=6</span>，<span class="s">Q<sub>6</sub></span> 取等号，<b>恰好在上界上</b>。表里写 2.00 是我把 <span class="s">2d/γ</span> 误算成 <span class="s">2d/(dγ)</span>。</p>

<p>这一处错误保留在书里，作为第 23 章“分级失效”的一个真实标本：<b>定理没错，表格算错了；若没有逐族核对，它会被当作“定理被违反”而误传。</b>更正后的上界写在附录 B 的表 B.5 里。</p>
"""
S["ch19.html"] = """
<h3 id="sec19-8">19.8　三种收敛与一个不收敛的量</h3>

<p>“离散收敛到连续”有强弱之分，本书用到三种，区别必须写清。</p>

<table class="nat">
<tr><th class="l">收敛</th><th class="l">说的是</th><th class="l">本书用在哪</th><th class="l">反例</th></tr>
<tr><td class="l">强预解</td><td class="l">对每个 <span class="s">λ</span>，<span class="s">(L<sub>h</sub>−λ)<sup>−1</sup>f→(Δ−λ)<sup>−1</sup>f</span></td><td class="l">命题 B（第 19 章）</td><td class="l">谱在极限点处跳变</td></tr>
<tr><td class="l">谱（特征值）</td><td class="l">固定 <span class="s">k</span>，<span class="s">λ<sub>k</sub>(h)/h²→μ<sub>k</sub></span></td><td class="l">表 19.1 末列</td><td class="l">重数不收敛（交叉）</td></tr>
<tr><td class="l">热核</td><td class="l"><span class="s">e<sup>tL<sub>h</sub></sup>→e<sup>tΔ</sup></span>（<span class="s">t&gt;0</span> 固定）</td><td class="l">表 20.1 的数值影子</td><td class="l"><span class="s">t→0</span> 时发散</td></tr>
</table>

<p><b>不收敛的量</b>是 <span class="s">R</span> 与 <span class="s">λ<sub>n</sub></span>：前者按 <span class="s">n²</span> 发散，后者趋于常数 <span class="s">8</span>（不随 <span class="s">h</span> 缩放）。<b>所以“离散逼近连续”只对“按 <span class="s">h²</span> 缩放后的低谱”成立</b>；凡是拿未缩放的 <span class="s">R</span> 去谈“连续极限”，都会得到错误结论。</p>

<p>三种收敛的强弱次序是：强预解 ⟹ 谱（加上一致有界）⟹ 热核（对固定 <span class="s">t</span>）。反过来都不成立，因此本书引用收敛结果时一律写明是哪一种——这不是学究，而是第 3 章“可复算”的具体要求。</p>
"""
S["ch20.html"] = """
<h3 id="sec20-6">20.6　热核两项展开的数值核对</h3>

<p>把第 20.4b 节的两项展开写成可核对的式子：对单位正方形（<span class="s">d=2</span>，面积 1），</p>
<div class="eq"><span class="body">Tr e<sup>tΔ</sup> = 1/(4πt) + |∂M|/(8√(πt)) + O(1)</span><span class="num">(20.3)</span></div>
<p>其中 <span class="s">|∂M|=4</span> 是周长。第二项就是表 20.1 里“Weyl 主项偏低”的原因：<b>边界贡献为正，所以计数在主项之下</b>——与我们的直觉（边界减少可用面积）相反，但那是对 Dirichlet 边界的直觉，这里是 Neumann（图拉普拉斯对应 Neumann）。</p>

<p>核对方式：取 <span class="s">t=0.01,0.03,0.1</span>，算网格（<span class="s">n=40</span>，<span class="s">h=1/40</span>）的 <span class="s">Tr e<sup>tL/h²</sup></span>，与 <span class="s">1/(4πt)+1/(2√(πt))</span> 比较。三档残差应随 <span class="s">t</span> 增大，因为高阶项 <span class="s">O(1)</span> 的相对比重上升。<b>这条练习的用处不是验证公式，而是让人看到“Weyl 律的常数项从哪来”</b>——它来自边界，而不是体积。</p>

<p>对本书而言，这条边界项还有一个含义：第 19 章的 <span class="s">R</span> 发散正是由“边界顶点度数低”驱动（命题 18.4 的注解），而热核的边界项也由同一件事驱动。<b>两处现象同一个来源：边界。</b>这是把“谱的边界效应”与“相变宽度发散”连起来的一条暗线。</p>
"""
S["ch21.html"] = """
<h3 id="sec21-6">21.6　覆盖表的“可裁决性”列</h3>

<p>表 21.1 有四个字段，缺一个更重要的第五字段：<b>这条能不能在一天内被复核？</b>补上它，表的实用性会显著上升。</p>

<table class="nat">
<tr><th class="l">可裁决性</th><th class="l">含义</th><th class="l">条目举例</th><th class="l">占比</th></tr>
<tr><td class="l">高</td><td class="l">有标准定理或一行代码可查</td><td class="l">1、4、5、12、15、30、31、33、34、35</td><td class="l">10/36</td></tr>
<tr><td class="l">中</td><td class="l">要一组数据与一个模型</td><td class="l">3、6、9、10、11、13、24、26、32、36</td><td class="l">10/36</td></tr>
<tr><td class="l">低</td><td class="l">要长期观测或制度变迁</td><td class="l">22、23、25、27、28、29</td><td class="l">6/36</td></tr>
<tr><td class="l">不可</td><td class="l">阈值本身是争议对象</td><td class="l">14、20、21</td><td class="l">3/36</td></tr>
<tr><td class="l">待定</td><td class="l">尚未分类</td><td class="l">7、8、16、17、18、19</td><td class="l">6/36</td></tr>
</table>

<p>这张补表改变了对覆盖表的评价：<b>“高”只有 10 条，其中 8 条是物理与计算族</b>；社会族 8 条里没有一条“高”。这不是学科歧视，而是阈值来源的差异（第 21.3b 节）。</p>

<p>补表的用处在于排优先级：若要把 C 级条目升级，先升“中”档（成本可控），别碰“不可”档（阈值本身在争）。<b>这也是本书对“跨学科统一”最诚实的态度：不是所有领域都能用同一把尺子，但所有领域都能被同一个问题审一遍。</b></p>
"""
S["ch22.html"] = """
<h3 id="sec22-7">22.7　第五个迁移：免疫识别的亲和力阈值</h3>

<p>再试一个迁移，看语法能不能承住。免疫系统区分“自我／非我”：T 细胞受体与肽–MHC 复合物的<b>亲和力</b>超过阈值 <span class="s">K<sub>d</sub>*</span> 即触发。四字段齐全：对象是肽段，属性是亲和力（可测，单位 μM），阈值由胸腺选择设定，观察者是克隆群。</p>

<p>按第 15 章四条探针：<b>边界探针</b>过（亲和力趋零则无识别）；<b>操作探针</b>过（把肽段截短，亲和力下降，识别消失）；<b>不变量探针</b>过（识别只依赖亲和力与阈值，不依赖肽段的其他性质）；<b>反例探针</b>断——存在“亲和力低于阈值却仍被识别”的案例（<b>异源免疫</b>：交叉反应），也存在“高于阈值却不触发”的案例（<b>无反应性</b>）。</p>

<p>四条探针一断，迁移停在<b>类比</b>价位（C 级）。但它仍然有用：它给“区分”提供了一个<b>进化设定的阈值</b>实例——阈值不是物理常数，而是选择压力下的产物。<b>这正好补上第 21.3b 节五族表里“生命族：阈值由进化给定”那一行。</b>一个失败的迁移能强化一条分类判断，这也是迁移的价值之一。</p>
"""
S["ch23.html"] = """
<h3 id="sec23-7">23.7　外部读者的三种提问</h3>

<p>内部自查会漏，外部提问最难骗。三种提问最有效，因为它们不需要专业知识。</p>

<p><b>一、“如果它错了，我会看到什么？”</b>答不出，说明这条不是命题。答得出但很模糊（“结果会不一样”），说明判据没写好。</p>

<p><b>二、“你换了哪个词，结论就变了？”</b>这是换词的探针，也是最容易露馅的一问：若换一个同义词结论就塌，说明结论其实附着在词上，而不在结构上。</p>

<p><b>三、“这个数是怎么来的？给我重跑一次。” </b>这是可复算的探针。本书的每个 A 级数字都经得起这一问（附录 B 有代码）；凡经不起的，就该降级。</p>

<p>三种提问的共同点：<b>它们都不要求读者懂这门学问，只要求读者会追问。</b>这也解释了为什么本书把第 4 章的五个问题放在最前面——它们是为“不打算相信本书的读者”准备的。</p>
"""
S["ch24.html"] = """
<h3 id="sec24-7">24.7　登记簿的机器可读格式</h3>

<p>为了让登记簿能被别人核对，本书给它一个固定的 CSV 列：</p>

<pre>id,claim,criterion,status,result,date,hash_prev
R1,"局部总先于全局","有向图上 Re(λ_k) 的序","出局","6 顶点反例","2026-10-31","—"
R2,"谱刻画结构","构造同谱不同构图","出局","6 顶点两图","2026-10-31",h(R1)
O1,"1/3 是不变结构量","一族构造下不变","未执行","—","—",h(R4)</pre>

<p>七列里最重要的是 <span class="s">criterion</span> 与 <span class="s">date</span>：前者必须在 <span class="s">status</span> 之前写好，后者让“事后改判据”留下时间戳。加上 <span class="s">hash_prev</span>，三者合起来构成“可核对的登记”。</p>

<p>这份格式可以直接被脚本读：校验脚本只需两件事——哈希链连贯、<span class="s">status=出局</span> 的行必须有 <span class="s">result</span>。<b>把纪律写成 schema，是让纪律能被第三方执行的最低成本方式。</b>本书附录 D 的表格就是这个 schema 的排版版。</p>
"""
S["ch25.html"] = """
<h3 id="sec25-7">25.7　研究纲领：十二个可认领的问题</h3>

<p>把全书未完成的工作写成十二个可认领的问题，按“能不能一个人做完”排序。</p>

<table class="nat">
<tr><th class="l">#</th><th class="l">问题</th><th class="l">类型</th><th class="l">一个人可做？</th></tr>
<tr><td class="l">1</td><td class="l">证明或推翻 <span class="s">R≤n</span>（星图取等）</td><td class="l">谱图论</td><td class="l">是</td></tr>
<tr><td class="l">2</td><td class="l">把 <span class="s">R</span> 的界改进到 <span class="s">O(n)</span></td><td class="l">谱图论</td><td class="l">是</td></tr>
<tr><td class="l">3</td><td class="l"><span class="s">R</span> 在随机几何图上的缩放指数</td><td class="l">概率</td><td class="l">是（数值）</td></tr>
<tr><td class="l">4</td><td class="l">κ 的连续极限是否存在闭式</td><td class="l">谱几何</td><td class="l">是</td></tr>
<tr><td class="l">5</td><td class="l">两阶段结构在加权图上的判据</td><td class="l">谱图论</td><td class="l">是</td></tr>
<tr><td class="l">6</td><td class="l">“可数生成”写进语法后的可计算性</td><td class="l">测度论</td><td class="l">是</td></tr>
<tr><td class="l">7</td><td class="l">三十六领域里 C 级七条的形式化或删除</td><td class="l">领域</td><td class="l">否（需专家）</td></tr>
<tr><td class="l">8</td><td class="l">法律涵摄的完整编码（D.3 的 O4）</td><td class="l">应用</td><td class="l">否</td></tr>
<tr><td class="l">9</td><td class="l">1/3 是否不依赖构造</td><td class="l">构造数学</td><td class="l">是</td></tr>
<tr><td class="l">10</td><td class="l">自旋网络面积谱与网格谱的可区分预言</td><td class="l">数学物理</td><td class="l">否</td></tr>
<tr><td class="l">11</td><td class="l">把 <span class="s">R</span> 用于真实网络（电网、脑网络）</td><td class="l">数据</td><td class="l">是</td></tr>
<tr><td class="l">12</td><td class="l">第 10 章语法在第二个外部领域的可用性</td><td class="l">方法论</td><td class="l">是</td></tr>
</table>

<p>十二个问题里九个“一个人可做”，这是本书对纲领性的最低承诺：<b>一个纲领若只能由团队完成，它就不是纲领，是项目。</b>九条里有五条只需一台电脑与几天时间（1、2、3、4、11），这也是本书把代码放在附录 B 的原因。</p>

<p>最后一条（12）最重要：<b>若第 10 章的语法在第二个外部领域也站得住，本书的“语言”部分才算被独立使用过一次。</b>在此之前，它是“自洽的”，不是“有用的”。</p>
"""
for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
    assert a, f
    s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

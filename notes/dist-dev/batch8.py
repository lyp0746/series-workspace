# -*- coding: utf-8 -*-
"""第八批：覆盖表逐族（生命/认知）、失败复盘、登记实例、纲领接口、两条完整证明。"""
import io
import re

S = {}

S["ch21.html"] = """
<h3 id="sec21-8">21.8　生命与认知族：为什么只有两条到 A 级</h3>

<p>两族共 14 条，只有 12（代谢网络）与 15（知觉阈限）是 A 级。逐条说清“差在哪”。</p>

<table class="nat">
<tr><th class="l">#</th><th class="l">条目</th><th class="l">差在哪一步</th><th class="l">若补上什么可升 A</th></tr>
<tr><td class="l">8</td><td class="l">免疫识别</td><td class="l">亲和力阈值个体差异大</td><td class="l">一个标准化的体外测定</td></tr>
<tr><td class="l">9</td><td class="l">神经编码</td><td class="l">调谐曲线依赖电极与任务</td><td class="l">可复现的数据集（如公开电生理）</td></tr>
<tr><td class="l">10</td><td class="l">生态位</td><td class="l">竞争系数难独立测量</td><td class="l">受控微宇宙实验</td></tr>
<tr><td class="l">11</td><td class="l">进化谱系</td><td class="l">生殖隔离是连续量</td><td class="l">统一的操作定义</td></tr>
<tr><td class="l">13</td><td class="l">形态发生</td><td class="l">波长依赖参数，不依赖常数</td><td class="l">可测的扩散系数组合</td></tr>
<tr><td class="l">14</td><td class="l">微生物组</td><td class="l">“群落边界”没有唯一划分</td><td class="l">一个公认的划分算法</td></tr>
<tr><td class="l">16</td><td class="l">音位范畴</td><td class="l">边界随语言与语境移动</td><td class="l">跨语言的统一刺激集</td></tr>
<tr><td class="l">17</td><td class="l">概念范畴</td><td class="l">典型性评分是主观量</td><td class="l">行为学上的可复现范式</td></tr>
<tr><td class="l">18</td><td class="l">注意瓶颈</td><td class="l">容量依赖材料与练习</td><td class="l">标准化的 n-back 变体</td></tr>
<tr><td class="l">19</td><td class="l">记忆容量</td><td class="l">组块定义递归</td><td class="l">可操作的组块计数</td></tr>
<tr><td class="l">20</td><td class="l">价值判断</td><td class="l">效用不可独立测量</td><td class="l">显示偏好 + 可复现实验</td></tr>
<tr><td class="l">21</td><td class="l">可报告性</td><td class="l">报告阈值与判据混淆</td><td class="l">范式化的对比报告任务</td></tr>
</table>

<p>十二行的“差在哪一步”高度一致：<b>都是阈值或判据不唯一</b>，而不是结构不清楚。这与第 21.3b 节的五族表对齐——生命与认知族的阈值由进化或任务给定，因而可浮动。</p>

<p>这条观察对“纲领性”有帮助：<b>升级路径是清楚的（补一个标准化测量），只是每一条都要领域专家做。</b>本书能做的只有一件——把“缺什么”写清楚，而不是假装它们已经 A 级。</p>
"""

S["ch22.html"] = """
<h3 id="sec22-9">22.9　一次失败的迁移复盘：τ 用到高频交易</h3>

<p>把 <span class="s">τ=T<sub>min</sub>/T<sub>avail</sub></span> 迁移到高频交易，是本书试过并主动撤回的一次迁移。</p>

<p><b>四字段。</b>对象是两个报价-成交策略；属性是“从信号出现到下单完成的延迟”；阈值是“延迟是否小于对手的反应时间”；观察者是做市商。</p>

<p><b>探针结果。</b>边界探针过（延迟趋零则必成交）；操作探针<b>断</b>——把策略换成“撤单重报”之后，<span class="s">T<sub>min</sub></span> 的定义变了，因为“完成”指什么变了；不变量探针过（只依赖延迟差）；反例探针<b>断</b>——存在 <span class="s">τ&gt;1</span> 却盈利的策略（做市商的库存管理收益）。</p>

<p><b>结论：只到类比（C 级），且理由充分。</b>失败的根源是<b>“完成”这个动作在这个领域没有唯一含义</b>——成交、部分成交、撤单、排队，四种都可能算“完成”，于是 <span class="s">T<sub>min</sub></span> 不唯一。</p>

<p>这次复盘给第 15 章的探针表补了一条经验：<b>“操作探针”最能抓住失败的迁移，因为它检验“在那边做一次合法操作，翻译过来是否仍合法”。</b>凡是“动作语义不唯一”的领域，迁移都会在这一步断。</p>
"""

S["ch23.html"] = """
<h3 id="sec23-8">23.8　一次完整的失败复盘：把“1/3”当常数</h3>

<p>这是本书自己的一次越界，值得完整记录。</p>

<p><b>当时的说法。</b>在某些离散逼近里，连续极限与离散值之间留下一个约 1/3 的差额，于是被写成“离散与连续之间的 1/3 缺口”，并暗示它是一个普遍常数。</p>

<p><b>问题在哪。</b>按第 10 章的第二类语法错误（把阈值当对象）：<b>这个数依赖逼近方式</b>。换网格、换边界条件、换测度，差额随之变化。第 19 章给出了一个可判定的版本——不是关于 1/3，而是关于“两阶段宽度 <span class="s">R</span> 随分辨率的 <span class="s">n²</span> 增长”，那一条有闭式、有实测、有误差。</p>

<p><b>现在的处置。</b>1/3 保留在附录 D 的未执行项 O1 里，判据写明：“若能证明它在某一族构造下不变，则可升级；否则保持 C 级。”<b>没有删除，因为它是那次越界的证据；也没有升级，因为判据未执行。</b></p>

<p>三条教训：<b>（i）</b> 一个数若依赖构造，它就不是结构量；<b>（ii）</b> 把它写成常数是一种“定义滑移”（第 4 章第七赝品）；<b>（iii）</b> 撤回不必删除，登记即可——这也是 append-only 的用处。</p>
"""

S["ch24.html"] = """
<h3 id="sec24-8">24.8　一次完整的裁决实例</h3>

<p>取附录 D 的 R1，展示一次裁决的完整过程（从登记到出局）。</p>

<table class="nat">
<tr><th class="l">步骤</th><th class="l">内容</th><th class="l">时间</th></tr>
<tr><td class="l">登记</td><td class="l">命题：「局部总先于全局」；判据：「用 <span class="s">Re(λ<sub>k</sub>)</span> 排序，最高频是否总先变正」</td><td class="l">写作前</td></tr>
<tr><td class="l">执行</td><td class="l">构造 6 顶点有向图，算 <span class="s">Re(λ<sub>k</sub>)</span>；发现一个全局型模式先变正</td><td class="l">写作中</td></tr>
<tr><td class="l">裁决</td><td class="l">命题出局（限无向图）；定理 16.1 的前提补写「对称」</td><td class="l">写作中</td></tr>
<tr><td class="l">留痕</td><td class="l">附录 D 记 R1；第 16.5 节写入反例；正文前提加“对称”</td><td class="l">定稿</td></tr>
</table>

<p>四步里第三步最关键：<b>出局的不是定理，而是“定理的无条件表述”。</b>这正是分级与登记的用处——它让“部分错误”可以被精确表达，而不必二选一（要么全对，要么全错）。</p>

<p>这条实例也说明了为什么要“先写判据”：<b>如果先看到反例再写判据，很容易把判据写成“无向图上局部先增长”——于是什么也没学到。</b>判据先行，才有“出局”这一档。</p>
"""

S["ch25.html"] = """
<h3 id="sec25-8">25.8　与系列其他书的接口：一张对照表</h3>

<p>本书不是孤立的。与系列其他七本的接口如下，每一条都指向具体章节。</p>

<table class="nat">
<tr><th class="l">书</th><th class="l">本书给它的</th><th class="l">它给本书的</th></tr>
<tr><td class="l">只能选两样</td><td class="l">形式（第 12 章）与硬核（第 16—19 章）</td><td class="l">入口层的叙事与例子</td></tr>
<tr><td class="l">遗忘的边界</td><td class="l">压缩即区分合并（第 6.7 节）</td><td class="l">容量 \(C\) 与信息瓶颈的可测版本（第 22.2 节）</td></tr>
<tr><td class="l">错位的时间</td><td class="l">阈值与可观测窗口（第 17.7 节）</td><td class="l">τ 的定义与三个情景（第 22.3 节）</td></tr>
<tr><td class="l">选择的代价</td><td class="l">子模性与秩亏（第 12.7 节）</td><td class="l">三性权衡的同调价位（第 22.4 节）</td></tr>
<tr><td class="l">诠释的权衡</td><td class="l">分级与四类断言（第 3 章）</td><td class="l">置信度分配的领域检验</td></tr>
<tr><td class="l">涌现的临界</td><td class="l">临界＝谱符号改变（第 16.8 节）</td><td class="l">临界指数与尺度分析（第 21 章第 1 条）</td></tr>
<tr><td class="l">心灵的分岔</td><td class="l">“划线”的语法（第 10 章）</td><td class="l">心理学史的划线实例</td></tr>
</table>

<p>七行的共同结构是：<b>本书提供“形式”，其他书提供“材料”</b>。这个分工是刻意的——形式若由材料来检验，就必须能被材料单独引用；材料若由形式来统一，就必须接受形式的判据。</p>

<p>接口表也给读者一条捷径：<b>想验证本书，不必读全书，只需在你熟悉的那一本里找一个可复算的量，再回来看它在本书的哪一节被形式化。</b>找不到，就是本书的覆盖有缺口——这比任何自评都可靠。</p>
"""

S["ch18.html"] = """
<h3 id="sec18-9">18.9　一个待证的猜想：R ≤ n，且星图取等</h3>

<p>由表 18.1 可以提出一个自然的猜想。</p>

<div class="box"><p><b>猜想 18.5。</b>设 <span class="s">G</span> 是 <span class="s">n</span> 顶点的连通图，<span class="s">n≥2</span>。则 <span class="s">R(G)=λ<sub>n</sub>/λ<sub>2</sub> ≤ n</span>，等号由星图 <span class="s">K<sub>1,n−1</sub></span> 取到。</p></div>

<p><b>为什么猜它。</b>三点证据。其一，<span class="s">λ<sub>n</sub>≤n</span> 对全部 <span class="s">n≤7</span> 的连通图成立（可用 <code>networkx</code> 全图遍历验证，见附录 B）。其二，<span class="s">λ<sub>2</sub>≥1</span> 对所有非完全连通图成立吗？不成立（路图的 <span class="s">λ<sub>2</sub></span> 可以小于 1），所以 <span class="s">R≤n</span> 需要更强的论证。其三，星图给出 <span class="s">λ<sub>2</sub>=1</span>、<span class="s">λ<sub>n</sub>=n</span>，所以上界若成立必是锐的。</p>

<p><b>已知的部分。</b>由 Anderson–Morley 定理，<span class="s">λ<sub>n</sub>≤max<sub>(u,v)∈E</sub>(d<sub>u</sub>+d<sub>v</sub>)≤2Δ≤2(n−1)</span>。所以 <span class="s">R≤2(n−1)/λ<sub>2</sub></span>，当 <span class="s">λ<sub>2</sub>≥2</span> 时给出 <span class="s">R≤n−1&lt;n</span>。<b>于是猜想的关键情形只剩 <span class="s">λ<sub>2</sub>&lt;2</span>——也就是“瘦长”的图。</b></p>

<p>把猜想写成这样，它就成了一个可攻的具体问题（附录 D 的 O2）：<b>对 <span class="s">λ<sub>2</sub>&lt;2</span> 的连通图，证明 <span class="s">λ<sub>n</sub>≤nλ<sub>2</sub></span>。</b>这类“分段证明”的写法，是本书希望示范的：一个猜想若能被切成“已证的部分 + 待证的部分”，它就比一句口号有用。</p>
"""

S["appendix_a.html"] = """
<h3 id="seca9">A.9　定理 17.1 的完整证明</h3>

<p><b>定理 17.1。</b>设 <span class="s">G</span> 连通、<span class="s">n≥2</span>、<span class="s">α&gt;0</span>，<span class="s">β<sub>1</sub>=α/λ<sub>n</sub></span>、<span class="s">β<sub>2</sub>=α/λ<sub>2</sub></span>。则下列三条等价：(i) <span class="s">λ<sub>2</sub>&lt;λ<sub>n</sub></span>；(ii) <span class="s">β<sub>1</sub>&lt;β<sub>2</sub></span>；(iii) 存在开区间 <span class="s">I⊂(0,∞)</span>，使对任意 <span class="s">β∈I</span>，存在初值使 <span class="s">μ<sub>n</sub>&gt;0</span> 而所有 <span class="s">λ<sub>k</sub>≤λ<sub>2</sub></span> 的模式满足 <span class="s">μ<sub>k</sub>&lt;0</span>。</p>

<p><b>证明。</b>(i)⇒(ii)：由 <span class="s">α&gt;0</span> 与 <span class="s">λ<sub>2</sub>&lt;λ<sub>n</sub></span> 得 <span class="s">1/λ<sub>n</sub>&lt;1/λ<sub>2</sub></span>，两边乘 <span class="s">α</span> 即得。<br>
(ii)⇒(i)：反向同理（<span class="s">α&gt;0</span> 使乘法可逆）。<br>
(i)⇒(iii)：令 <span class="s">I=(α/λ<sub>n</sub>, α/λ<sub>2</sub>)</span>。由 (i)，<span class="s">I</span> 非空。取 <span class="s">β∈I</span>：则 <span class="s">β&gt;α/λ<sub>n</sub></span> 给出 <span class="s">μ<sub>n</sub>=βλ<sub>n</sub>−α&gt;0</span>；而 <span class="s">β&lt;α/λ<sub>2</sub></span> 给出 <span class="s">βλ<sub>2</sub>&lt;α</span>，由 <span class="s">λ<sub>k</sub>≤λ<sub>2</sub></span>（<span class="s">k≥2</span>）得 <span class="s">μ<sub>k</sub>&lt;0</span>；再由 <span class="s">λ<sub>1</sub>=0</span> 得 <span class="s">μ<sub>1</sub>=−α&lt;0</span>。取初值 <span class="s">D(0)=e<sub>n</sub></span> 即满足要求。<br>
(iii)⇒(i)：反证。设 <span class="s">λ<sub>2</sub>=λ<sub>n</sub></span>。则 <span class="s">β<sub>1</sub>=β<sub>2</sub></span>，区间 <span class="s">(β<sub>1</sub>,β<sub>2</sub>)</span> 为空。而对任意 <span class="s">β</span>：若 <span class="s">μ<sub>n</sub>&gt;0</span> 则 <span class="s">β&gt;α/λ<sub>n</sub>=α/λ<sub>2</sub></span>，于是 <span class="s">μ<sub>2</sub>=βλ<sub>2</sub>−α&gt;0</span>，与 (iii) 中 <span class="s">μ<sub>2</sub>&lt;0</span> 矛盾。故 (iii) 不成立。<span class="s">∎</span></p>

<p>证明只用了两件事：<b>特征值有序</b>与 <span class="s">α&gt;0</span>。这说明定理 17.1 的“两阶段”不是动力学的产物，而是<b>谱有序性的直接翻译</b>——动力学只是把它显影。</p>

<h3 id="seca10">A.10　定理 18.2 的完整证明</h3>

<p><b>定理 18.2。</b>设 <span class="s">G</span> 连通、<span class="s">n≥2</span>。则 <span class="s">λ<sub>2</sub>=λ<sub>n</sub></span> 当且仅当 <span class="s">G≅K<sub>n</sub></span>。</p>

<p><b>证明。</b>（⇐）<span class="s">K<sub>n</sub></span> 的拉普拉斯矩阵为 <span class="s">nI−J</span>，特征值为 <span class="s">0</span>（对应 <span class="s">𝟙</span>）与 <span class="s">n</span>（重数 <span class="s">n−1</span>），故 <span class="s">λ<sub>2</sub>=λ<sub>n</sub>=n</span>。</p>

<p>（⇒）设非零谱只有一个值 <span class="s">λ&gt;0</span>，重数 <span class="s">n−1</span>（连通性保证 <span class="s">λ<sub>2</sub>&gt;0</span>，故 <span class="s">λ<sub>1</sub>=0</span> 是单重根）。令 <span class="s">P=𝟙𝟙<sup>T</sup>/n</span> 为到 <span class="s">𝟙</span> 的投影。由谱分解，<span class="s">L</span> 在 <span class="s">𝟙<sup>⊥</sup></span> 上等于 <span class="s">λI</span>，在 <span class="s">𝟙</span> 上等于 0，故</p>

<div class="eq"><span class="body">L = λ(I−P) = λ(I − J/n)</span><span class="num">(A.1)</span></div>

<p>比较对角元：<span class="s">L<sub>vv</sub>=d<sub>v</sub>=λ(1−1/n)</span>，故所有顶点度数相同，记为 <span class="s">d</span>。比较非对角元：<span class="s">L<sub>vw</sub>=−A<sub>vw</sub>=−λ/n</span>，即 <span class="s">A<sub>vw</sub>=λ/n</span>。因 <span class="s">A<sub>vw</sub>∈{0,1}</span> 且连通图有边，存在 <span class="s">vw∈E</span>，于是 <span class="s">λ/n=1</span>，即 <span class="s">λ=n</span>。代回得 <span class="s">d=n(1−1/n)=n−1</span>，即每点与其余各点相邻，<span class="s">G≅K<sub>n</sub></span>。<span class="s">∎</span></p>

<p>证明中唯一“有技巧”的一步是由 <span class="s">A<sub>vw</sub>=λ/n</span> 得 <span class="s">λ=n</span>：<b>利用了邻接矩阵取值只有 0 与 1。</b>若换成加权图，这一步失效——加权图上 <span class="s">λ<sub>2</sub>=λ<sub>n</sub></span> 可以出现在非完全图上（例如完全图给每条边同一个权，仍等价；但给部分边不同权时，只要所有行和相同，仍可能成立）。<b>所以定理 18.2 的适用范围是“简单无权图”，这一点必须写进结论。</b></p>
"""

for f, add in S.items():
    s = io.open(f, encoding="utf-8").read()
    if f == "appendix_a.html":
        s = s.rstrip() + "\n\n" + add.strip() + "\n"
    else:
        a = re.search(r'<h3 id="sec\d+-ref">\d+　本章参考文献</h3>', s)
        assert a, f
        s = s[:a.start()] + add.strip() + "\n\n" + s[a.start():]
    io.open(f, "w", encoding="utf-8").write(s)
    print("ok", f, len(s))

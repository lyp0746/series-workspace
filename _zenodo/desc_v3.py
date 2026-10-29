# -*- coding: utf-8 -*-
"""五篇论文的 Zenodo 描述（中英双语，统一为「论文格式」）：

    中文摘要。 → 主要读数。 → 边界。 → Abstract (English). → Files.

生成的文本同时写入各仓库的 .zenodo.json 与 _zenodo/desc/<slug>.html，便于手动粘贴。
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
OUT = BASE / "_zenodo" / "desc"          # HTML 版（源码视图粘贴）
OUT_TXT = BASE / "_zenodo" / "desc_plain"   # 纯文本版（富文本编辑器直接粘贴）
OUT.mkdir(parents=True, exist_ok=True)
OUT_TXT.mkdir(parents=True, exist_ok=True)

D = {}

# ---------------------------------------------------------------- 第九篇
D["LedgerReconciliation"] = dict(
    title=("六张账单的对账：六核心的可测代理、失败模式与尺度边界 / "
           "Reconciling Six Ledgers: Proxies, Failure Modes and Scale Boundaries of the Six Cores"),
    version="2026-10-28", date="2026-10-28",
    paras=[
        ("中文摘要。",
         "本文不做综述，只做<b>对账</b>：把十四篇工作论文附录里的登记命题逐条抽出，按「篇—命题—检验—结果—状态—等级—核心—尺度」八列重编码，"
         "再做三件事——状态审计、等级审计、冲突审计。本版把登记簿从 <b>62 条扩到 110 条</b>，并入第十至十四篇的 48 条，"
         "<b>旧行一行未改</b>。结论是：六核心不是六个并列的词，而是「起点—约束—枢纽—元层—门槛」的五层结构；"
         "对账的作用不是让结论更强，而是让每个核心知道自己在哪里可测、在哪里失效、在哪里只能类比。"),
        ("主要读数。",
         "110 条中已核销 <b>76 条（69.1%）</b>、未核销 <b>27 条（24.5%）</b>、作者自己撤回 <b>7 条（6.4%）</b>；"
         "被自己数据打掉的（证伪 9 ＋ 撤回 7）共 <b>16 条，占 14.5%</b>。等级：<b>A 3／B 55／C 52</b>——"
         "九篇最想说的（临界、选择、容量）恰是等级最低的。尺度：命题 77、共同体 18、制度 14、<b>个体 0、谱系 1（且是反例）</b>，"
         "这是「记住」的容量端至今没有测量的结构原因。冲突：<b>七处同名不同物</b>——τ（年 vs 周）、容量（有刻度 vs 无刻度）、"
         "门（切线 vs 门槛）、记忆（名 vs 命题）、压缩（信息 vs 合法性），本版新增<b>便宜</b>（per token vs per capability）"
         "与<b>可传递性</b>（法律状态 vs 市场结构）。"),
        ("边界。",
         "对账不产生新证据，只改变可判断性；110 条是十四篇<b>已登记</b>的命题，不代表各篇的全部主张；"
         "状态的归一有判断成分，尤其「部分」与「支持」的界线；七处冲突的消解规则（按载体分层，不追求统一）是本文提出的，不是各篇作者的共识。"
         "本文另把自己六条命题也登记进同一张表，并以一条纪律收束：<b>以后每加一篇只登记、不补洞。</b>"),
        ("Abstract (English).",
         "This paper reconciles rather than reviews. All <b>110 registered propositions</b> in fourteen working papers are extracted and re-coded on eight columns "
         "(paper, id, claim, test, result, status, grade, core, scale) and audited three ways. Status: <b>76 closed (69.1%)</b>, 27 unclosed (24.5%), "
         "7 withdrawn (6.4%); 16 (14.5%) were killed by the authors' own data. Grade: <b>3 at A, 55 at B, 52 at C</b> — the cores the series most wants to claim "
         "(criticality, choice, capacity) carry the lowest grades. Scale: 77 at the proposition level, 18 at the community level, 14 at the institution level, "
         "<b>none at the individual level and one at the lineage level (a counter-example)</b>. Conflicts: <b>seven cases of \"same name, different object\"</b> — "
         "tau (years vs weeks), capacity (scaled vs unscaled), gate (periodisation cut vs critical threshold), memory (toponym vs proposition), compression "
         "(information vs legitimacy), and two new ones: <i>cheap</i> (per token vs per capability) and <i>transferability</i> (legal status vs market structure). "
         "The six cores are not six parallel words but a five-layer structure: starting point, constraint, hinge, meta-layer, threshold. The purpose of "
         "reconciliation is not to strengthen conclusions but to let every core know where it is measurable, where it fails, and where it is only analogical."),
        ("Files.",
         "论文（PDF 54 页 / HTML / Markdown / README）；8 幅图；<code>ledger.csv</code>（110 条 × 9 列）；<code>MANIFEST.txt</code>。"
         "全部计数由 <code>data/ledger.py</code> 重算，任何人可用自己的编码替换后重跑一次。"),
    ],
    notes="工作论文/预印本。第三版（2026-10-28，54 页，110 条，覆盖十四篇）。",
)

# ---------------------------------------------------------------- 第十一篇
D["IsomorphismStrength"] = dict(
    title=("同构的强度：对偶、泛性质、不变量与四十条断裂探针 / "
           "The Strength of Isomorphism: Motifs, Analogy, and Forty Fracture Probes"),
    version="2026-10-28", date="2026-10-28",
    paras=[
        ("中文摘要。",
         "本文给「两个领域像不像」定价。它提出一条四级强度阶梯——<b>严格／伴随／函子／比喻</b>——"
         "并要求每条跨域声明给出可观测的<b>断裂探针</b>：在哪个观察点上，这个「像」会断。四十条声明按五个母题组编码"
         "（对偶、泛性质、不变量、结构、过程），配四问式判据与负迁移登记。结论有一个不太舒服的形状："
         "<b>最危险的不是明说是比喻的那一档，而是看起来像证明的那两档。</b>"),
        ("主要读数。",
         "强度分布：严格 12、伴随 11、函子 12、比喻 5（四十条，<b>严格不到三分之一</b>）。断裂层：复合 16、等价 12、态射 8、对象 4——"
         "<b>七成断裂不在对象层</b>，而公共争论几乎全部停在对象层。负迁移共 15／40（38%），"
         "分档为 <b>严格 17%、伴随 60%、函子 50%、比喻 36%</b>：<b>负迁移率不随强度单调下降</b>。"
         "母题组的通货性有差异：泛性质跨域最弱（6／10 降为比喻）；而争论最激烈的那几条，恰恰落在伴随与函子两档。"
         "本版新增<b>附录 P（第四十一条声明）</b>：「人＝君主，agent＝臣民」——强度＝<b>比喻</b>、断裂层＝<b>复合</b>、负迁移＝Y；"
         "五条断裂探针（责任／继承／叛乱／启蒙／规模）里四条一碰就断：<b>一个不能叛乱的臣民不是臣民，是工具</b>。"
         "该声明<b>不计入四十条统计</b>，正文全部比例不变。"),
        ("边界。",
         "四级阶梯是判据，不是度量：它判「能不能写成复合律」，不能判「这个类比值多少」。四十条是一个<b>封闭集</b>，"
         "因此附录 P 的第四十一条只登记、不并入统计。本文最大的自我限制写在正文第 11 章：把本文自己的四十条声明也过一遍探针——"
         "能通过的那几条，都不是本文最想说的那几条。"),
        ("Abstract (English).",
         "This paper prices the claim that two fields resemble each other. It proposes a four-rung ladder — <b>strict, adjunction, functor, metaphor</b> — "
         "and requires every cross-domain declaration to supply an observable <b>fracture probe</b>: the point at which the resemblance breaks. Forty declarations "
         "are coded across five motif groups (duality, universal property, invariant, structure, process). Distribution: strict 12, adjunction 11, functor 12, "
         "metaphor 5 — <b>strict isomorphism covers under a third</b>. Fracture layer: composition 16, equivalence 12, morphism 8, object 4 — <b>seventy per cent of "
         "fractures are not at the object layer</b>, where almost all public argument sits. Negative transfer: 15 of 40 (38%), and it <b>does not fall monotonically "
         "with strength</b> (strict 17%, adjunction 60%, functor 50%, metaphor 36%): the dangerous rungs are the ones that look like proofs. This edition adds "
         "<b>Appendix P</b>, a forty-first declaration (\"the person is the sovereign, the agent the subject\"), coded at the metaphor rung with its fracture at the "
         "composition layer; four of its five probes cut immediately, because a subject that cannot rebel is a tool, not a subject. It is kept outside the closed "
         "set of forty, so every proportion in the main text is unchanged."),
        ("Files.",
         "论文（PDF 51 页 / HTML / Markdown / README）；8 幅图；<code>motifs.csv</code>（40 条声明 × 14 字段）；<code>MANIFEST.txt</code>。"),
    ],
    notes="工作论文/预印本。第二版（2026-10-28，51 页）：新增附录 P（第四十一条声明，不计入四十条统计）。",
)

# ---------------------------------------------------------------- 第十篇
D["DomainCrossSection"] = dict(
    title=("领域的剖面：四个问题、二十个领域与八十字段的审计 / "
           "The Cross-Section of Domains: Four Questions, Twenty Fields, and an Audit of Eighty Cells"),
    version="2026-10-28", date="2026-10-28",
    paras=[
        ("中文摘要。",
         "「把复杂领域压成几句话」是当代最流行的智力动作，也最容易退化成口头禅。本文把它固定成四条可判定的问题："
         "<b>Q1 瓶颈</b>（为哪项稀缺资源付账）、<b>Q2 置换</b>（让出了什么）、<b>Q3 可写性</b>（核心机制能否写成十行）、"
         "<b>Q4 承担者</b>（代价落在谁身上，他是否在场），并对二十个日常领域逐条编码，共 <b>80 个字段</b>，全部可复算。"
         "四问不是六核心之外的新框架，而是它的操作化压缩：Q1＝看见，Q2＝选择，Q3＝讲述＋临界，Q4＝讲述的扩展——置信度分配之外，再加一列<b>代价分配</b>。"),
        ("主要读数。",
         "瓶颈：协调 5／延迟 5／正确 4／容量 3／注意力 2／信任 1／<b>预算 0</b>——预算只是「次瓶颈的常客、主瓶颈的陌生人」。"
         "动作：拆分 19／20、预计算与复制各 17／20、试探 10、绕开 9、抽象 9、<b>合并只有 2／20</b>。"
         "可写性呈纺锤形：A 6／B 13／C 1（唯一的 C 是外交谈判）。把可写性与承担者的在场性交叉："
         "A 级 4／6（67%）、B 级 4／13（31%）、C 级 0／1（0%）——<b>越写不出核心的领域，代价越可能落在分散的、不在场的人身上</b>（只登记 C 级，拒绝 p 值）。"
         "主次瓶颈互换后 <b>5／20</b> 改判：四问是「在一个瓶颈假设下的读数」，不是判决书。"
         "本版新增<b>附录 M</b>：第十四篇补录 D21（agent 平台）后，D21 以<b>预算</b>为主瓶颈，<b>单例否证</b>本文 T3；"
         "而 D21 的可写性是 A、代价却落在不在场者，使 T5 在此域失效（<b>规则可写 ≠ 后果可写</b>），据此第十四篇给在场性加第五档「<b>在场而不知情</b>」。"),
        ("边界。",
         "全部字段是<b>规范读数</b>（de jure），依据公开规范、程序法与行业标准，不是现场观察；第 6 章列出六个「规范说了、行为没做」的落差。"
         "样本是目的抽样，偏向有规范文本的领域，街头摊贩与照护经济不在其中；编码由一人完成，没有第二编码者。"
         "九条命题中五条支持、两条部分、一条待检验、一条被本文自己撤回（T9：七个瓶颈类型不能穷举）。"),
        ("Abstract (English).",
         "Compressing a complex field into a few sentences is among the most popular intellectual moves of the age, and among the easiest to degrade into a "
         "catchphrase. This paper fixes the move into four checkable questions — <b>bottleneck</b> (which scarce resource is paid for), <b>substitution</b> (what is "
         "given up), <b>writability</b> (whether the core fits in ten lines), <b>bearer</b> (who ends up paying, and whether that party is present) — and codes "
         "twenty everyday fields on <b>eighty cells</b>. Bottlenecks: coordination 5, delay 5, correctness 4, capacity 3, attention 2, trust 1, <b>budget 0</b>. "
         "Actions: splitting in 19 of 20 fields, precomputation and replication 17 each, <b>merging only 2</b>. Writability is spindle-shaped (A 6 / B 13 / C 1); "
         "crossed with the bearer's presence it gives A 67%, B 31%, C 0% — <b>the less writable a field's core, the more likely the cost falls on the dispersed and "
         "the absent</b>, registered at grade C with no p-value. A swap test of primary and secondary bottlenecks changes the verdict in 5 of 20 fields. This second "
         "edition adds Appendix M: field D21 (agent platforms) pays primarily in budget, a <b>single-case falsification</b> of T3, and its high writability combined "
         "with an absent bearer suspends T5 — so a fifth presence grade, <i>present but uninformed</i>, is proposed there."),
        ("Files.",
         "论文（PDF 52 页 / HTML / Markdown / README）；8 幅图；<code>domains.csv</code>（20 领域 × 15 字段）；<code>MANIFEST.txt</code>。"),
    ],
    notes="工作论文/预印本。第二版（2026-10-28，52 页）：新增附录 M（两处跨篇相撞与登记）。数据与二十领域编码未变。",
)

# ---------------------------------------------------------------- 第十四篇
D["MonarchCompetition"] = dict(
    title=("开明君主与两层竞争：agent 价目表上的执行、方向与代价承担者 / "
           "The Enlightened Sovereign and Two-Tier Competition: Execution, Direction, and Who Pays on the Agent Price Sheet"),
    version="2026-10-28", date="2026-10-28",
    paras=[
        ("中文摘要。",
         "一个流行的说法是：有志气的人正在用 agent 扩张能力，这像启蒙思想家梦寐以求的「开明君主制」——人以理性和经验定方向，agent 负责实现；"
         "而当足够多的人这么做时，就会重演轴心时代的百家争鸣。这个说法有一个好直觉（执行权在扩散），也有一个未受检验的推论（红利会随之扩散）。"
         "本文把它拆成三个价目表能回答的问题：一次「新判断」比一次「重放」贵多少？执行单价真的在降吗？钱最后停在谁那一层？"
         "数据是四份公开快照：438 个模型的价目与托管读数、九个实验室的一手价目页与席位页、平台方每周发布的用量口径。"),
        ("主要读数。",
         "（1）<b>重放—判断价差</b>（RJS＝输出单价 ÷ 缓存读单价）在 294 个模型上的中位 <b>34.5 倍</b>；闭源 50、开放 19；"
         "自家价目页上 12—200 倍（DeepSeek 与 Claude Fable 5.1 均为 200），而多托管市场把同一批模型摊平到 19 倍——<b>重放被竞争压到底，判断由厂商自己写</b>。"
         "（2）<b>「执行变便宜」是同名不同物</b>：按同能力算降约 150 倍（单一来源）；按「当月进入市场的新模型标价中位」算，闭源 $6.00→$5.00、"
         "开放 $0.65→$0.60（不降）；且 Google 官方公告 Gemini 4 Argon 自 2026-12-01 起输出价 $10→$20。"
         "（3）<b>量与钱分离</b>：周 token 量 0.5 万亿→128.4 万亿（约 250 倍／20 个月），开放权重拿 62—79% 的 token，闭源仍拿 <b>73%</b> 的消费额。"
         "（4）<b>双层是常态</b>：9 家里 6 家同时经营「权重可下载、几十家可托管」的商品层与「只能在自己平台上用」的旗舰层，"
         "溢价 <b>2.9—83 倍</b>（中位 21.3）。"
         "（5）<b>席位不随执行降</b>：8 个公开价位 $12.6—$200；ChatGPT Plus 三年仍是 $20。"
         "（6）<b>低价的一半是数据</b>：首方最低价以训练权为对价，不训练的第三方托管约 2 倍价。"),
        ("边界（含三处自我打击）。",
         "其一，原假设「溢价来自不可传递性」被自己的数据否证：T 分与溢价无单调关系（T=4 的 OpenAI 83.3 倍，T=3 的月之暗面 2.9 倍），T8 登记为<b>否证</b>。"
         "其二，RJS 与上下文长度 ρ=0.53，按上下文四档分组后「闭源＞开放」只在两档成立，T2 降为<b>部分</b>。"
         "其三，「假竞争」这个词站不住——竞争是真的、只是分两层，改判为<b>两层竞争</b>。"
         "另有两条一般边界：数据只覆盖「通过第三方 API 使用模型」的市场，不含企业私有部署与消费端使用；全部价目是标价，不是实付价。"),
        ("Abstract (English).",
         "A popular claim holds that ambitious people are using agents to extend their own capacity, reviving the enlightened despotism that Enlightenment thinkers "
         "wished for, and that the Axial Age will repeat itself. The intuition (execution is being democratised) is sound; the inference (so are the returns) has not "
         "been tested. This paper asks three questions a price sheet can answer: how much more does a fresh judgement cost than a replay; is the unit price of "
         "execution actually falling; and on which tier does the money stop? Four public snapshots supply the data. Six results. (1) The <b>replay–judgement spread</b> "
         "(RJS = output price / cache-read price) has a median of <b>34.5x</b> across 294 models (closed 50x, open 19x), reaching 12–200x on first-party sheets while "
         "the multi-host market compresses the same models to 19x: replay is priced by competition, judgement by the vendor. (2) \"Execution is getting cheaper\" names "
         "two objects: capability-adjusted prices fell ~150x (single source), while the median list price of models entering the market fell only from $6.00 to $5.00 "
         "(closed) and $0.65 to $0.60 (open); Google schedules Gemini 4 Argon from $10 to $20 on 2026-12-01. (3) Volume and money separate: weekly tokens rose from "
         "0.5T to 128.4T, open weights hold 62–79% of tokens, and closed weights still take <b>73%</b> of spend. (4) Two tiers are the norm: six of nine labs sell both "
         "a self-hostable and a first-party-only tier, with premiums of <b>2.9–83x</b> (median 21.3x). (5) Seat prices do not follow execution prices down ($12.6–$200; "
         "ChatGPT Plus has been $20 for three years). (6) Half of a low price is data: first-party minimum prices are paid for with training rights, while no-train "
         "hosts charge about twice as much. Three self-inflicted wounds are reported: the transferability explanation of the premium is falsified by the paper's own "
         "data; RJS turns out to be largely a function of context length (rho = 0.53), demoting T2 to partial; and \"counterfeit competition\" is renamed "
         "\"two-tier competition\"."),
        ("Files.",
         "论文（PDF 51 页 / HTML / Markdown / README）；8 幅图；<code>MANIFEST.txt</code>。价格类数字由 <code>data/prices.py</code> 从同一份快照重算；"
         "原始页面快照（价目页、端点读数、许可证、平台周报）留在 GitHub 仓库，可逐个复核。"),
    ],
    notes="工作论文/预印本。系列第十四篇（测量篇）。51 页；数据快照 2026-10-26／27；十条命题：7 支持、1 部分、1 否证、1 单源。",
)

# ---------------------------------------------------------------- 第十三篇
D["MemoryStressTest"] = dict(
    title=("锚点的下限：情景记忆的模拟对照实验与 0.57 的覆盖率阈值 / "
           "The Floor of Anchoring: A Simulation Study of Episodic Memory and the 0.57 Coverage Threshold"),
    version="2026-10-26", date="2026-10-26",
    paras=[
        ("中文摘要。",
         "上一篇《记忆的锚点》提出三层记忆架构（书记员字段级硬日志／异构重建／带锚裁决），并把自己的关键命题 T9「能把几天延长到几周」撤回，因为没有实验。"
         "本文把那套架构实现成可复算的机制模拟，去回答一个更窄的问题：<b>它在什么条件下才比一张摘要更好？</b>"
         "配置：5 个页面 × 2 个表面标签（负迁移陷阱）× 4 个条件（M0 无记忆／M1 摘要／M2 情景／M2w 允许回写），"
         "12000 步主对照、80000 步覆盖率扫描、81 组敏感性，另有<b>四条预先登记的否证条件</b>。"),
        ("主要读数。",
         "（1）准确率：情景 <b>0.441</b> ＞ 摘要 0.339 ＞ 无记忆 0.000；但跨页面污染率是 <b>摘要 0.625</b>、无记忆 0.187、情景 0.179——"
         "<b>摘要是最危险的记忆</b>，污染是「无记忆」的 3.3 倍。（2）自我打击一条：情景在不可逆动作上并未胜过摘要（误动作 0.209 对 0.196），"
         "预注册的 <b>F1 部分触发</b>。（3）覆盖率扫描给出交叉点 <b>0.569</b>（自举 95% 区间 0.44—0.74）：低于它不如摘要，高于它才开始赢；"
         "换参数后阈值移动约 ±0.10，因此 <b>0.57 不是常数</b>。（4）允许重建回写（M2w）：200 步内准确率 0.338→0.151、误动作 0.209→0.273，"
         "而人环转介反而下降——<b>污染让系统更自信</b>，这是「重建不得回写账本」的量化版本。（5）相关 ρ 从 0 到 0.7：误动作 0.092→0.118、"
         "人环 0.55→2.40；集成规模 K 的收益在 <b>K=3 处饱和</b>（K=5 只再降 0.001，代价 +554 ms）。"
         "（6）参数 vs 覆盖率：把采样量提高到三倍，误动作只从 0.106 变到 0.110（几乎不动）；而覆盖率 0.5→0.9 让它 0.210→0.080（约 32 倍）——"
         "<b>补账本比换模型有效</b>。十条命题：八支持、一未检验（T9 仍撤回）、一撤回（T10：0.57 不可迁移）。"),
        ("边界。",
         "<b>这是机制模拟，不是 LLM 实验。</b>环境、日志、重建与裁决全部由代码定义，因此结论只对「这套机制」成立，不外推到真实模型；"
         "T9（能延长真实账号存活）仍为未检验。另有两处教训写在正文：一次失败的 M1 设计，一次参数误设；并附 ODD 九项自查与「如果重做会改哪三处」。"),
        ("Abstract (English).",
         "A recomputable mechanism simulation of the three-layer memory architecture proposed in the previous paper: five screens with two surface labels "
         "(a negative-transfer trap), four conditions (no memory / summary / episodic / episodic with write-back), 12,000 main steps, an 80,000-step coverage "
         "sweep, an 81-cell sensitivity grid, and <b>four preregistered falsification conditions</b>. This is a simulation of the mechanism, not an LLM experiment. "
         "Episodic recall reaches accuracy <b>0.441</b> against 0.339 for a summary and 0.000 for no memory, yet <b>does not beat the summary on irreversible-action "
         "errors</b> (0.209 vs 0.196), so the preregistered F1 is partially triggered. Cross-page contamination is <b>0.625 for the summary</b> — 3.3 times that of no "
         "memory — against 0.187 for no memory and 0.179 for episodic recall: <b>the summary is the most dangerous memory</b>. The coverage crossover is <b>0.569</b> "
         "(bootstrap 95% interval 0.44–0.74), and it moves by about ±0.10 when parameters change, so 0.57 is not a constant. Allowing reconstructions to be written "
         "back to the log halves accuracy within 200 steps while <i>reducing</i> human escalation: contamination makes the system more confident. Correlation rho from "
         "0 to 0.7 worsens both accuracy and cost; the ensemble gain saturates at K = 3; and raising coverage from 0.5 to 0.9 cuts the irreversible-action rate from "
         "0.210 to 0.080, far more than tripling the sample rate does — <b>improving the ledger beats upgrading the model</b>. Of ten propositions, eight are supported, "
         "one remains untested (T9 stays withdrawn) and one is withdrawn (T10: 0.57 is not transferable)."),
        ("Files.",
         "论文（PDF 51 页 / HTML / Markdown / README）；8 幅图；<code>explorer_sample.csv</code>（抽样轨迹）；<code>MANIFEST.txt</code>。"
         "主对照、覆盖率扫描与 81 组敏感性的参数、种子与脚本随仓库公开，可重跑。"),
    ],
    notes="工作论文/预印本。系列第十三篇（测试篇）。51 页；机制模拟而非 LLM 实验；四条预注册否证条件。",
)

# ---------------------------------------------------------------- 写出
def build(slug):
    d = D[slug]
    def para(lab, txt):
        gap = " " if txt[:1].isascii() and txt[:1].isalpha() else ""
        return "<p><b>%s</b>%s%s</p>\n" % (lab, gap, txt)
    body = "".join(para(lab, txt) for lab, txt in d["paras"])
    series = ("<p><b>系列 / Series。</b>同一作者的独立研究系列：九本书与十四篇工作论文。"
              "<b>系列入口与外部登记库：</b>https://github.com/lyp0746/knowledge-tradeoffs；"
              "源码与复现脚本：https://github.com/lyp0746</p>")
    return body, body + series


def plain(html):
    """HTML → 纯文本：段落变空行，去掉所有标签与行内代码。"""
    import re
    t = html.replace("</p>", "\n\n")
    for tag in ("b", "i", "code"):
        t = re.sub(r"<%s>(.*?)</%s>" % (tag, tag), r"\1", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip() + "\n"
    return t


if __name__ == "__main__":
    for slug in D:
        body, full = build(slug)
        (OUT / (slug + ".html")).write_text(full, encoding="utf-8")
        (OUT_TXT / (slug + ".txt")).write_text(plain(full), encoding="utf-8")
        p = BASE / slug / ".zenodo.json"
        meta = json.loads(p.read_text(encoding="utf-8"))
        meta["title"] = D[slug]["title"]
        meta["description"] = full
        meta["version"] = D[slug]["version"]
        meta["publication_date"] = D[slug]["date"]
        meta["notes"] = D[slug]["notes"]
        meta.setdefault("creators", [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}])
        meta.setdefault("license", "CC-BY-4.0")
        meta.setdefault("upload_type", "publication")
        meta.setdefault("publication_type", "preprint")
        meta.setdefault("language", "zho")
        meta.setdefault("access_right", "open")
        p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print("%-22s html %5d / txt %5d chars" % (slug, len(full), len(plain(full))))

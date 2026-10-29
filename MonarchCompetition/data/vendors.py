# -*- coding: utf-8 -*-
"""九个实验室的厂商级编码（单一数据源，人工编码 + 公开价目页快照）。

字段
----
lab             代码
name            中文／英文名
flag_model      旗舰层代表模型（该实验室闭源最贵一档）
com_model       商品层代表模型（该实验室可自托管、可多托管的一层）
premium         旗舰层 output 价 ÷ 商品层 output 价（倍数；单层者为 None）
open_weights    是否提供可下载权重：有／无
license         可得的最宽松许可证：MIT／Apache-2.0／受限（community/other）／无
T               可传递性 4 项布尔之和（0—4），见正文 3.5
seat            是否有面向使用者的席位（订阅）产品：有／无（只有 token）
seat_price      公开的席位价（美元／月，取最低档与最高档）
data_policy     首方 API 的数据政策：不用于训练／用于训练／未核实
grade           本行证据等级
refs            来源编号（见正文参考文献）

T 的四项
--------
T1 权重可下载（自托管可能）
T2 许可证允许商用与再分发（MIT／Apache-2.0 记 1；community/other 记 0）
T3 独立第三方托管商 ≥ 5（原厂与其签约超大规模云不计）
T4 首方付费 API 的输入不用于训练（或无数据回流）
"""

# 价格单位：美元／百万 token（output）。全部来自 data/prices.py 的同一份快照。
VENDORS = [
 dict(lab="openai", name="OpenAI", flag_model="GPT-6 Astra", com_model="gpt-oss-120b",
      flag_out=50.00, com_out=0.60, premium=83.3, open_weights="有", license="Apache-2.0",
      T=4, seat="有", seat_price="$20 — $200（Plus 至 Pro）", data_policy="不用于训练",
      grade="A", refs="[1][2][3][4][5]"),
 dict(lab="anthropic", name="Anthropic", flag_model="Claude Fable 5.1", com_model="—",
      flag_out=50.00, com_out=None, premium=None, open_weights="无", license="无",
      T=1, seat="有", seat_price="$30（Pro，月付）／$149.99 — $200（Max）／$20 座席 + 用量（Enterprise）",
      data_policy="不用于训练", grade="A", refs="[1][2][6]"),
 dict(lab="google", name="Google DeepMind", flag_model="Gemini 4 Argon", com_model="Gemma 4 31B",
      flag_out=10.00, com_out=0.40, premium=25.0, open_weights="有", license="Apache-2.0",
      T=4, seat="有", seat_price="未取（Gemini 订阅页为 JS 渲染，本轮未取到）", data_policy="付费 API 不用于训练",
      grade="B", refs="[1][2][3][16]"),
 dict(lab="deepseek", name="深度求索 DeepSeek", flag_model="—（无闭源旗舰）", com_model="DeepSeek V4.1 Flash",
      flag_out=None, com_out=0.42, premium=None, open_weights="有", license="MIT",
      T=3, seat="无", seat_price="无席位产品，只有按量计费与免费应用", data_policy="用于训练",
      grade="B", refs="[1][2][3][9][15]"),
 dict(lab="x-ai", name="xAI（Grok）", flag_model="Grok 4.7", com_model="—",
      flag_out=6.00, com_out=None, premium=None, open_weights="无", license="无",
      T=1, seat="有", seat_price="未取（grok.com 被 Cloudflare 拦截，价目页未取到）",
      data_policy="未核实", grade="C", refs="[1][2][17]"),
 dict(lab="moonshotai", name="月之暗面（Kimi）", flag_model="Kimi K3.1 Pro", com_model="Kimi K2.6",
      flag_out=10.00, com_out=3.41, premium=2.9, open_weights="有", license="受限（Modified MIT）",
      T=3, seat="有", seat_price="API 声明「无订阅计划」；会员与 Kimi Code 另计（价未取）",
      data_policy="未核实", grade="B", refs="[1][2][3][8][15]"),
 dict(lab="qwen", name="阿里（通义千问 Qwen）", flag_model="Qwen3.8 Max", com_model="Qwen3.8 Flash",
      flag_out=12.00, com_out=0.47, premium=25.5, open_weights="有", license="Apache-2.0",
      T=3, seat="有", seat_price="未取（千问 C 端会员价未在公开页取到）", data_policy="未核实",
      grade="B", refs="[1][2][3]"),
 dict(lab="z-ai", name="智谱（GLM）", flag_model="GLM-5.3 Prime", com_model="GLM-5.3-Flash",
      flag_out=8.80, com_out=0.50, premium=17.6, open_weights="有", license="MIT",
      T=4, seat="有", seat_price="$18／$80／$168（Lite／Pro／Max，年付 $12.6／$56／$117.6）",
      data_policy="不用于训练", grade="A", refs="[1][2][3][7]"),
 dict(lab="meta", name="Meta（Muse／Llama）", flag_model="Muse Wonder", com_model="Muse Glimmer 30B",
      flag_out=20.00, com_out=1.20, premium=16.7, open_weights="有", license="受限（Muse 须申请；Llama 社区协议）",
      T=4, seat="无", seat_price="无付费席位（Meta AI 免费）", data_policy="不用于训练",
      grade="B", refs="[1][2][3]"),
]

# 数据让渡矩阵：价格与数据政策的两两组合（正文 8.3）
DATA_MATRIX = [
 ("最低价 + 首方", "DeepSeek 首方 API：$0.14 输入／$0.28 输出（缓存后实测 $0.029）", "保留并用于训练", "B", "[15]"),
 ("最低价 + 第三方", "Fireworks／Together／DeepInfra 托管同权重：约 2 倍价格", "不用于训练", "B", "[15]"),
 ("高价 + 闭环", "Anthropic／OpenAI／Google 旗舰：$10—$50 输出", "付费 API 不用于训练", "A", "[4][6][16]"),
 ("零边际 + 自托管", "开放权重自建：只有算力成本，无单价", "不出域", "B", "[1][3]"),
]

# 席位价目（正文 8.1）：只登记取到的数，取不到的写明取不到
SEATS = [
 ("OpenAI", "ChatGPT Plus", 20, "月付", "官方帮助中心（更新于取数前一周）", "A", "[5]"),
 ("OpenAI", "ChatGPT Pro", 200, "月付", "与 Plus 同级页并列，取数本轮未逐项复核", "C", "[5]"),
 ("Anthropic", "Claude Pro", 30, "月付（年付 $25，$300 预付）", "官方价目页", "A", "[6]"),
 ("Anthropic", "Claude Max", 149.99, "月起（最高至 $200）", "官方价目页", "A", "[6]"),
 ("Anthropic", "Enterprise", 20, "座席／月 + API 用量", "官方价目页", "A", "[6]"),
 ("智谱 GLM", "Coding Plan Lite", 12.6, "月（年付；月付 $18）", "官方订阅页", "A", "[7]"),
 ("智谱 GLM", "Coding Plan Pro", 56, "月（年付；月付 $80）", "官方订阅页", "A", "[7]"),
 ("智谱 GLM", "Coding Plan Max", 117.6, "月（年付；月付 $168）", "官方订阅页", "A", "[7]"),
]

# 执行层与席位层的关键读数（正文 8.2 用的对照）
EXEC_ANCHORS = [
 ("Gemini 4 Argon 输出价（2026-11-30 前）", 10.00, "官方价目页", "A", "[16]"),
 ("Gemini 4 Argon 输出价（2026-12-01 起）", 20.00, "官方价目页：同一模型公告涨价 2 倍", "A", "[16]"),
 ("Claude Fable 5.1 输出价", 50.00, "价目快照", "A", "[1]"),
 ("GPT-6 Astra 输出价", 50.00, "官方价目页", "A", "[4]"),
 ("DeepSeek V4.1 Flash 输出价", 0.42, "价目快照", "A", "[1]"),
 ("同能力溢价（DeepSeek V4 Flash 对 GPT-5.5 级输出价）", 150.0,
  "OpenRouter 官方博文给出的「约 150 倍更便宜」", "B", "[15]"),
]


# 市场读数（量／钱分离）：OpenRouter Inferred 周报，2026 年 9 月第二周
MARKET = dict(
    token_week_2025_01=0.5,      # 万亿 token／周，2025-01-13 当周
    token_week_2026_09=128.4,    # 万亿 token／周，2026-09-14 当周
    token_growth=250,            # 倍，官方口径「约 250 倍／20 个月」
    spend_closed=73,             # 闭源权重模型占平台消费的比例（%），2026-09 第二周
    spend_closed_2025_01=89,     # 同上，2025-01-05 当周
    token_open_peak=79,          # 开放权重模型的 token 份额峰值（%），2026-07 初
    token_open_floor=62,         # 峰值之后维持的下限（%）
    token_chinese=69,            # 中国实验室占平台 token 的比例（%）
    token_restofworld_now=2,     # 美中之外实验室的 token 份额（%），现
    token_restofworld_2025=12,   # 同上，2025 年初
    startup_deepseek_now=40,     # 美国创业公司中使用 DeepSeek 的比例（%）
    startup_deepseek_jan=13,     # 同上，2026-01
    agent_vs_human=7,            # agentic 密钥的 token 量相对人类密钥的倍数
    agent_cache_share=90,        # agentic token 中缓存前缀的占比（%），2026-09
    agent_output_share=1,        # agentic token 中输出与推理的占比（%）
    human_output_share=12,       # 人类 token 中输出与推理的占比（%）
    new_models_per_day=1.3,      # 日均上新模型数
    new_models_per_month=40,     # 月均上新模型数
    refs="[10][11][12]",
)


# 官方（一手）价目表上的重放—判断价差：取该实验室旗舰模型在自家价目页上的
# output 价 ÷ cache-read 价。与市场读数（data/prices.py）并列，正文 4.2 用。
OFFICIAL_RJS = [
 ("openai", "GPT-6 Astra", 50.0, "$50.00 ÷ $1.00", "A", "[4]"),
 ("anthropic", "Claude Fable 5.1", 200.0, "缓存读为输出的 1/200", "B", "[12]"),
 ("anthropic", "Claude Sonnet 5.5", 100.0,
  "$10.00 ÷ $0.10（快照 10-26）；周报 10-08 的读数为 50（缓存读 $0.20）", "B", "[1][12]"),
 ("google", "Gemini 4 Argon", 100.0, "$10.00 ÷ $0.10", "A", "[16]"),
 ("deepseek", "DeepSeek V4.1 Flash", 200.0, "$0.60 ÷ $0.003（谷时）", "A", "[9]"),
 ("x-ai", "Grok 4.7", 12.0, "$6.00 ÷ $0.50", "B", "[1]"),
 ("moonshotai", "Kimi K3.1 Pro", 50.0, "$10.00 ÷ $0.20", "B", "[1]"),
 ("qwen", "Qwen3.8 Max", 24.0, "$12.00 ÷ $0.50", "B", "[1]"),
 ("meta", "Muse Wonder", 100.0, "$20.00 ÷ $0.20", "B", "[1]"),
]


def by_lab():
    return {v["lab"]: v for v in VENDORS}


if __name__ == "__main__":
    for v in VENDORS:
        print("%-11s T=%d 溢价=%-6s 权重=%s 许可=%-28s 席位=%s"
              % (v["lab"], v["T"], v["premium"], v["open_weights"], v["license"], v["seat_price"][:26]))
    ts = [v["T"] for v in VENDORS]
    prem = [v["premium"] for v in VENDORS if v["premium"]]
    print("\nT 分分布：", {t: ts.count(t) for t in sorted(set(ts))})
    import statistics
    print("双层实验室 %d／%d；溢价 %s，中位 %.1f" % (len(prem), len(VENDORS), sorted(prem),
                                                statistics.median(prem)))

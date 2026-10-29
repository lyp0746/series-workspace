# -*- coding: utf-8 -*-
"""十二个记忆方案的六变量编码库（单一数据源）。

字段
----
id        编号 S01–S12
name      方案名
kind      类型：检索／分层／架构／关联／窗口／摘要／提案／人工
granular   D1 残余粒度：全文／摘要／片段／字段／无
anchor     D2 硬日志锚点：有／部分／无
cues       D3 线索维度数（1–6：语义、时间、空间、人物、任务、效价）
hetero     D4 重建者异构性：同源／同族／跨模型／无
judge      D5 裁判机制：无／自评／交叉／带锚裁决
failmode   D6 主要失效：窗口满／摘要漂移／检索噪声／成本／幻觉／人工瓶颈／无
grade     证据等级 A／B／C
refs      参考文献编号
note      一句话

编码规则见正文 3.1–3.3：D1–D5 各给三档以上，D6 只记「最先出现的那个」。
"""

SCHEMES = [
 ("S01", "RAG（检索增强生成）", "检索", "片段", "无", 1, "无", "无", "检索噪声", "A", "[2]",
  "单一语义索引；检索到的是原文片段，没有情景线索"),
 ("S02", "Generative Agents 记忆流", "架构", "片段", "部分", 3, "同源", "自评", "检索噪声", "B", "[3]",
  "记忆流 + 新近度/重要性/相关度三因子；有重要性标签但无空间键"),
 ("S03", "MemGPT（分页式上下文）", "分层", "摘要", "无", 2, "同源", "自评", "摘要漂移", "B", "[4]",
  "把上下文当操作系统，热/冷分层；压缩由同一个模型做，故漂移同源"),
 ("S04", "CoALA 认知架构", "架构", "片段", "无", 3, "同源", "无", "无（是框架）", "B", "[5]",
  "工作/情节/语义/程序四类记忆的**分类学**，不规定实现"),
 ("S05", "知识图谱记忆", "关联", "字段", "部分", 4, "无", "无", "检索噪声", "B", "[6]",
  "实体—关系—实体；结构强、但重建要靠模板，缺情景"),
 ("S06", "现代 Hopfield 关联记忆", "关联", "字段", "无", 1, "无", "无", "幻觉", "A", "[7][8]",
  "内容寻址的吸引子；能容错但要靠数学结构，不是靠日志"),
 ("S07", "KV cache / 长上下文窗口", "窗口", "全文", "无", 1, "无", "无", "窗口满", "A", "[9]",
  "不压缩、只堆窗口；窗口一满就「死」，成本随长度平方增长"),
 ("S08", "滚动摘要式长期记忆", "摘要", "摘要", "无", 1, "同源", "无", "摘要漂移", "C", "[10]",
  "每次把对话压成摘要再接着聊；错误会被下一次摘要固化"),
 ("S09", "Transformer 注意力即检索", "关联", "全文", "无", 1, "无", "无", "窗口满", "A", "[1]",
  "注意力本身是内容寻址，但它是「一次性」的，不跨会话"),
 ("S10", "同质多 Agent 投票（初版设想）", "架构", "片段", "无", 2, "同源", "交叉", "共识幻觉", "C", "[11]",
  "十几个同源 Agent 各背一遍再投票；共模故障会投出同一个错误"),
 ("S11", "人环记忆（人工复核）", "人工", "片段", "有", 3, "无", "带锚裁决", "人工瓶颈", "B", "[12]",
  "由人做锚点与裁决；准，但不可扩展，延迟以小时计"),
 ("S12", "本文提案（书记员＋异构回忆者＋裁判）", "提案", "字段", "有", 5, "跨模型", "带锚裁决", "待测", "C", "本文",
  "硬日志锚点 + 跨模型异构重建 + 带锚裁决；未做实验，见附录 D"),
]

FIELDS = ["id", "name", "kind", "granular", "anchor", "cues", "hetero", "judge",
          "failmode", "grade", "refs", "note"]

GRANULAR = ["全文", "摘要", "片段", "字段", "无"]
ANCHOR = ["有", "部分", "无"]
HETERO = ["跨模型", "同族", "同源", "无"]
JUDGE = ["带锚裁决", "交叉", "自评", "无"]
FAIL = ["窗口满", "摘要漂移", "检索噪声", "成本", "幻觉", "共识幻觉", "人工瓶颈", "无（是框架）", "待测"]


def rows():
    return [dict(zip(FIELDS, s)) for s in SCHEMES]


def stats():
    import collections
    rs = rows()
    trio = [r for r in rs if r["anchor"] == "有" and r["hetero"] == "跨模型" and r["judge"] == "带锚裁决"]
    return dict(
        n=len(rs),
        anchor=collections.Counter(r["anchor"] for r in rs),
        hetero=collections.Counter(r["hetero"] for r in rs),
        judge=collections.Counter(r["judge"] for r in rs),
        fail=collections.Counter(r["failmode"] for r in rs),
        grade=collections.Counter(r["grade"] for r in rs),
        cues={r["id"]: r["cues"] for r in rs},
        mean_cues=sum(r["cues"] for r in rs) / len(rs),
        trio=len(trio),
        trio_ids=[r["id"] for r in trio],
    )


if __name__ == "__main__":
    s = stats()
    print("n =", s["n"])
    for k in ("anchor", "hetero", "judge", "fail", "grade"):
        print(k, dict(s[k]))
    print("线索维度:", s["cues"], "均值 %.2f" % s["mean_cues"])
    print("三件套齐备:", s["trio"], s["trio_ids"])

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《六张账单的对账》结构整改 v2（谨慎版）。

1. 折叠重复的空壳节标题（`## 2 理论框架` ×2）；
2. 新增「7 第十四篇：开明君主的十条命题与两处相撞」——ledger.csv 里已有 10 条，
   正文此前 0 次提及；
3. 「9 六篇导读」原本排在全部附录之后 → 移回正文（成为第 10 章）；
4. 术语与符号移出附录序列（参考文献之后），附录重排为 A–F；
5. 图表索引、术语英译 出附录（内容归档到 _series/registry/）；
6. 修正「110 条」与「62 条」并存、以及「八本书与六篇工作论文」的陈旧计数。

用法：  python fix_ledger2.py [--apply]
        （不带 --apply 时只打印结构，不动文件）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "LedgerReconciliation", "source", "paper.md")

NEW_SEC = """## 7 第十四篇：开明君主的十条命题与两处相撞

第十四篇《开明君主与两层竞争》是这套系列里唯一一篇**用价目表说话**的论文。它的问题来自一句玩笑：人是不是 agent 的"开明君主"。作者没有停在比喻上，而是把它压成三个价目表能回答的问题——执行有多便宜、方向有多贵、代价落在谁身上。总账必须收进它，理由不是补全，而是它给"选择"这一端第一次装上了**价格刻度**。

### 7.1 先把大词降到比喻档

第十四篇做的第一件事是自降一档：它明确写着，人＝君主、agent＝臣民属于**比喻档**，断裂在复合层（"君主"预设单一意志，而真实系统里"谁在下令"本身就在争）。降到比喻档之后，剩下的才可测：重放—判断价差（RJS＝输出价 ÷ 缓存读价）、执行价格的三种口径、量与钱的分离、双层溢价、席位价，以及"低价的一半是数据"。

这一步的方法论意义大于它的结论：**同一个大词，先说清自己是哪个价位，再说话**。本文第 5 章把七处"同名不同物"归到载体分层；第十四篇的做法是给"档位"也标一个载体——比喻档不许承担读数档的推论。

### 7.2 六条读数与三条自我打击

登记在 `ledger.csv` 的"两层"组共 10 条（T1—T10）。其中最硬的六条是：

1. **重放—判断价差中位 34.5 倍**（294 个模型；闭源 50、开放 19；官方价目页 12—200 倍，多托管市场把同一批模型摊平到 19 倍）。B 级：口径公开、可复算，但样本是目录快照，不是成交价。
2. **"执行变便宜"是同名不同物**：按同能力算降约 150 倍（单源）；按"当月新模型标价中位"算，闭源 6.00→5.00 美元、开放 0.65→0.60 美元，实际不降。这就是第 5 章"便宜（per token vs per capability）"那一处冲突的原始现场。
3. **量与钱分离**：周 token 量从 0.5 万亿到 128.4 万亿（250 倍／20 个月），开放权重占 62—79% 的 token，闭源占 73% 的消费额。
4. **双层是常态**：9 家里 6 家同时经营可自托管层与独占层，溢价 2.9—83 倍（中位 21.3）。
5. **席位不随执行降**：8 个公开价位 12.6—200 美元；ChatGPT Plus 三年仍是 20 美元。
6. **低价的一半是数据**：首方最低价以训练权为对价，不训练托管约 2 倍价。

真正该写进总账的不是这六条，而是**三条自我打击**：T8 被自己的数据否证（溢价与"T 分"无单调关系，作者从"支持"改判"撤回"）；"假竞争"改判为"两层竞争"（原假设是市场没有竞争，数据给的是竞争发生在不同层）；"开明君主"只能是比喻档。这三条与 4.11 节"为什么只有两个 A 级"是同一件事的两面：**这套框架最可信的部分，是它删掉自己结论的那部分**。

### 7.3 两处相撞：一处在预算，一处在比喻

**第一处，预算也可以当主瓶颈。** 第十篇《领域的剖面》的 T3 说"预算从来不是主瓶颈"（0/20 主、2/20 次）。第十四篇的 D21 编码里，**预算就是主瓶颈**——不是钱少，而是这一层不能自托管，只能按价目付费。这是一个单例否证：全称命题只需一条反例。第十篇据此新增附录 M，把 T3 从"成立"降为"被单例否证"，并给"在场性"补了第五档"在场而不知情"。

**第二处，比喻的重量。** 第十一篇《同构的强度》的四级阶梯（严格／伴随／函子／比喻）在"人＝君主"上落到最低一档，断裂在复合层。这与第 5 章处理七处冲突的方式一致：不把它抬成函子，而是标价——它能承载多少推论，就在哪一档收住。

### 7.4 它给"选择"补了什么，又留下什么

在此之前，"选择"的测量最薄：9 条命题里 8 条是判据型，只有 1 条带数。第十四篇补的不是一条新命题，而是一根**价格轴**：同一批模型在不同层、不同上下文、不同训练权条款下，价格差 2.9—83 倍。于是"选择"第一次可以问一个可算的问题——**你为可组合性多付了多少**。

代价要写明：价目表是目录价不是成交价；快照是两周内的读数不是趋势；九家样本不构成市场全景。因此本章结论一律不超过 B 级，且每条都带"何时不成立"。这是本文对"冷峻"的定义：数可以硬，话必须软。

"""

DIST_NEW = (
    "110 条的分布是：分期 11、官制 9、术语 9、领域 9、同构 9、锚点 10、下限 10、两层 10、"
    "生态 7、残余 7、容量 7、优化 7、驿道 5、总账 6。篇际数量差两倍，这本身是一个发现："
    "**登记密度与论文的\"自证强度\"相关**——分期篇有 11 条（因为它做了恒等式识别性与 κ 检验），"
    "驿道篇只有 5 条（因为它的多数数字是重建值，不宜写成命题）；新并入的六篇各在 9—10 条之间，"
    "说明它们的作者已经学会把主张切成可证伪的小句。")

OLD_DIST = (
    "110 条的分布是：官制 9、驿道 5、术语 9、分期 11、生态 7、残余 7、容量 7、优化 7。"
    "篇际数量差三倍，这本身是一个发现：**登记密度与论文的\"自证强度\"相关**——分期篇有 11 条"
    "（因为它做了恒等式识别性与 κ 检验），驿道篇只有 5 条（因为它的多数数字是重建值，不宜写成命题）。")

OLD_SERIES = ("系列现有八本书与六篇工作论文。本文不新增对象，只对六篇做对账；它与八本书的关系是\"借用语言\"，"
              "与六篇的关系是\"二次编码\"。若有第七篇（容量代理）、第八篇（优化边界），它们应把命题登记进本表，使对账持续。")
NEW_SERIES = ("系列现有九本书与十四篇工作论文（本文首版时为八本与六篇；旧口径保留在附录 D 的旧行里，不改写）。"
              "本文不新增对象，只做对账：它与九本书的关系是\"借用语言\"，与十四篇的关系是\"二次编码\"。"
              "新论文只要把命题登记进本表，对账就能继续——这正是 append-only 的意思。")


def split_blocks(t):
    parts = re.split(r"(?m)^## ", t)
    head = parts[0]
    blocks = []
    for p in parts[1:]:
        h, _, b = p.partition("\n")
        blocks.append([h.strip(), b])
    return head, blocks


def main():
    apply = "--apply" in sys.argv
    t = open(P, encoding="utf-8").read()
    head, blocks = split_blocks(t)

    # 1) 折叠同号空壳
    dedup = []
    for h, b in blocks:
        m = re.match(r"^(\d+)[\s　]", h)
        pm = re.match(r"^(\d+)[\s　]", dedup[-1][0]) if dedup else None
        if m and pm and m.group(1) == pm.group(1):
            if not dedup[-1][1].strip():
                dedup[-1] = [h, b]        # 空壳在前：用有内容的替换
                continue
            if not b.strip():
                continue                  # 空壳在后：丢弃
        dedup.append([h, b])
    blocks = dedup

    def take(frag):
        for i, (h, b) in enumerate(blocks):
            if frag in h:
                return blocks.pop(i)
        return None

    # 2) 取出附录件
    a_table = take("六十二条命题的对账总表")
    a_conf = take("七处同名不同物的清单")
    a_cards = take("六张卡")
    a_reg = take("本文六条命题的登记")
    a_idx = take("图表索引")          # 出附录（归档）
    a_term = take("术语与符号")
    a_rel = take("与其他十四件的关系")
    a_annot = take("逐条评注")
    a_manual = take("对账操作手册")
    a_bycore1 = take("按核心重排的同一批命题")
    a_bystatus = take("按状态归组")
    a_bycore2 = take("按核心重排：110 条")
    a_cross = take("篇 × 状态交叉表")
    a_excerpt = take("六篇登记簿的原文摘录")
    a_check = take("对账检查表")
    a_enidx = take("110 条命题的英文索引")
    take("附录K")                      # 空壳
    a_trad = take("与四套")
    a_ten = take("对账的十个常见反对")
    a_en = take("术语英译")            # 出附录（归档）
    a_use = take("六条最小可引用句")
    s_read = take("六篇导读")
    s_notes = take("附注")
    s_ref = take("参考文献")

    body = [b for b in blocks if re.match(r"^(\d+|摘要|Abstract)", b[0])]

    # 3) 插入新的第 7 章
    out = []
    inserted = False
    for h, b in body:
        if re.match(r"^7[\s　]", h) and not inserted:
            _, nb = split_blocks(NEW_SEC)
            out.append([nb[0][0], nb[0][1]])
            inserted = True
        out.append([h, b])

    # 4) 正文重编号 1..10（讨论 7→8、结论 8→9、导读 9→10）
    n = 0
    for blk in out:
        m = re.match(r"^(\d+)[\s　]+(.+)$", blk[0])
        if not m:
            continue
        old, title = m.group(1), m.group(2)
        n += 1
        blk[0] = f"{n} {title}"
        blk[1] = re.sub(rf"(?m)^### {old}\.(\d+)", lambda mm: f"### {n}.{mm.group(1)}", blk[1])
        blk[1] = re.sub(rf"(?<![\d.]){old}\.(\d+)(\s*[节表图])",
                        lambda mm: f"{n}.{mm.group(1)}{mm.group(2)}", blk[1])
        blk[1] = re.sub(rf"第\s*{old}\s*章", f"第{n}章", blk[1])

    # 导读归位为第 10 章
    s_read[0] = "10 六篇导读：对账之后重读一遍"

    # 5) 计数修正
    for blk in out + [s_ref, s_notes, a_term]:
        if blk[1]:
            blk[1] = blk[1].replace(OLD_SERIES, NEW_SERIES).replace(OLD_DIST, DIST_NEW)
    if a_term[1]:
        a_term[1] = a_term[1].replace(OLD_SERIES, NEW_SERIES)

    # 6) 组装
    def sec(title, part):
        return [title, (part[1] if part else "").strip()]

    term = ["术语与符号", a_term[1].strip() + "\n\n### 与其他十四件的关系\n\n" + a_rel[1].strip()]
    apxA = sec("附录 A　110 条对账总表与六张卡",
               None)  # 占位，下面拼
    apxA[1] = "\n\n".join([
        "### 110 条的对账总表\n\n" + a_table[1].strip(),
        "### 六张卡\n\n" + a_cards[1].strip(),
        "### 按状态归组：110 条的七种处境\n\n" + a_bystatus[1].strip(),
        "### 按核心重排：110 条的另一种视图\n\n" + a_bycore2[1].strip(),
        "### 篇 × 状态交叉表\n\n" + a_cross[1].strip(),
        "### 110 条命题的英文索引\n\n" + a_enidx[1].strip(),
    ])
    apxC = ["附录 C　对账操作手册与检查表", "\n\n".join([
        a_manual[1].strip(),
        "### 按核心重排的同一批命题\n\n" + a_bycore1[1].strip(),
        "### 对账检查表（可打印一页）\n\n" + a_check[1].strip(),
        "### 与四套\"登记\"传统的对照\n\n" + a_trad[1].strip(),
    ])]
    apxD = ["附录 D　可证伪登记簿（append-only）", "\n\n".join([
        "### 本文六条命题的登记\n\n" + a_reg[1].strip(),
        "### 六篇登记簿的原文摘录\n\n" + a_excerpt[1].strip(),
    ])]
    apxF = ["附录 F　十个常见反对与用法示例", "\n\n".join([
        a_ten[1].strip(),
        "### 六条最小可引用句的用法示例\n\n" + a_use[1].strip(),
    ])]

    final = out + [s_read, s_ref, term,
                   apxA,
                   ["附录 B　七处同名不同物", a_conf[1].strip()],
                   apxC,
                   apxD,
                   ["附录 E　逐条评注（按篇）", a_annot[1].strip()],
                   apxF,
                   s_notes]

    def emit(h, b):
        b = (b or "").strip()
        return f"## {h}\n\n{b}\n\n" if b else f"## {h}\n\n"

    txt = head + "".join(emit(h, b) for h, b in final)
    print("正文节:", [h[:14] for h, _ in final if re.match(r"^\d", h)])
    print("附录:", [h[:12] for h, _ in final if h.startswith("附录")])
    print("归档:", [x[0] for x in (a_idx, a_en) if x])
    if apply:
        open(P, "w", encoding="utf-8").write(txt)
        reg = os.path.join(ROOT, "_series", "registry")
        os.makedirs(reg, exist_ok=True)
        with open(os.path.join(reg, "appendix_archive.md"), "a", encoding="utf-8") as f:
            for x in (a_idx, a_en):
                if x:
                    f.write(f"\n\n<!-- from LedgerReconciliation: {x[0]} -->\n{x[1].strip()}\n")
        print("已写入", P)
    return 0


if __name__ == "__main__":
    sys.exit(main())

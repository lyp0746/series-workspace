#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把论文里"结论之后又加的节"收回讨论，并统一节数（spec §3：12–16 节）。"""
import io, re, sys

def blocks(t):
    parts = re.split(r"(?m)^## ", t)
    head = parts[0]
    bl = []
    for p in parts[1:]:
        h, _, b = p.partition("\n")
        bl.append([h.strip(), b])
    return head, bl

def demote(text):
    """## 段内部：### → ####，保留原有层级"""
    return re.sub(r"(?m)^### ", "#### ", text)

def rebuild(path, keep_titles, absorb_into, drop_tail_after=None):
    t = io.open(path, encoding="utf-8").read()
    head, bl = blocks(t)
    keep, absorb, tail = [], [], []
    mode = "keep"
    for h, b in bl:
        title = re.sub(r"^\d+[\s　]+", "", h)
        if h.startswith("参考文献") or h.startswith("附录") or h.startswith("附注"):
            tail.append([h, b]); mode = "tail"; continue
        if mode == "tail":
            tail.append([h, b]); continue
        if title in keep_titles:
            keep.append([h, b])
        else:
            absorb.append([h, b])
    # 找到 absorb_into 的位置
    idx = next(i for i, (h, _) in enumerate(keep)
               if re.sub(r"^\d+[\s　]+", "", h) == absorb_into)
    add = "\n".join(f"### {re.sub(r'^\d+[\s　]+', '', h)}\n\n{demote(b).strip()}\n"
                    for h, b in absorb)
    keep[idx][1] = keep[idx][1].rstrip() + "\n\n" + add + "\n"
    # 重编号
    n = 0
    for i, (h, b) in enumerate(keep):
        n += 1
        title = re.sub(r"^\d+[\s　]+", "", h)
        keep[i][0] = f"{n} {title}"
    out = head + "".join(f"## {h}\n{b}\n" for h, b in keep + tail)
    io.open(path, "w", encoding="utf-8").write(out)
    return len(keep), len(absorb)

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "capacity":
        k, a = rebuild("CapacityProxies/source/paper.md",
            ["引言", "框架：容量、压缩、遗忘的可数版本", "数据与方法",
             "结果一：分期槽位（支持，但弱）", "结果二：编码槽位（不可判）",
             "结果三：标签槽位（反向）", "结果四：三个代理的交叉验证",
             "结果五：一次失败的重编码", "讨论",
             "三个代理的联合测量协议", "与价格轴的接口：容量能不能被定价", "结论"],
            "讨论")
        print("capacity:", k, "节，吸收", a)
    elif which == "optimization":
        k, a = rebuild("OptimizationBoundary/source/paper.md",
            ["引言", "理论框架：四个前提，四个提供者", "数据与方法", "结果",
             "与六核心的接口", "结果二：四个越界案例的深度复核",
             "与优化话语的对话", "反例章：进化不是优化", "讨论", "结论"],
            "讨论")
        print("optimization:", k, "节，吸收", a)

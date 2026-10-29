#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把生成的表注入正文：source/paper.template.md → source/paper.md。

表、图、交互页与附录都由同一份 data/counts.json 生成；
正文里的 <!--TABLE_xxx--> 与 {{N_QUERIES}} 是唯一允许的"手写以外的内容"入口。
"""
import json, pathlib, collections

BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "被点燃的生态_两个社区与三个标记.md"

def rd(p):
    return p.read_text(encoding="utf-8").strip()

def load():
    return json.loads((DATA / "counts.json").read_text(encoding="utf-8"))

def table_a1(rows):
    """查询协议表：类别 / 模板 / 条数。条数由 counts.json 现算，不手抄。"""
    n = collections.Counter()
    for r in rows:
        k = r["key"]
        if k.startswith("dsh|day|"):      n["日尺度"] += 1
        elif k.startswith("lad|"):        n["星标阶梯"] += 1
        elif k.startswith("ret|"):        n["存活率"] += 1
        elif k.startswith("skills|"):     n["主序列 · agent-skills"] += 1
        elif k.startswith("dsh|"):        n["主序列 · dsh-plugin"] += 1
        elif k.startswith("meta|"):       n["元层探针"] += 1
        elif k.startswith("topic"):       n["星标榜（前 50）"] += 1
        elif k.startswith("overlap|"):    n["交集"] += 1
        else:                             n["其他"] += 1
    tpl = {
        "主序列 · dsh-plugin": "`topic:dsh-plugin created:<起>..<止>` × 三档 `stars:>=k fork:false`",
        "主序列 · agent-skills": "`topic:agent-skills created:<起>..<止>` × 两档 `stars:>=k fork:false`",
        "日尺度": "`topic:dsh-plugin created:2026-08-06..2026-08-24`（逐日）",
        "星标阶梯": "`… stars:>=1` / `stars:>=1000`",
        "存活率": "`<队列> pushed:>=2026-10-16`，及 `+ stars:>=10`",
        "交集": "`topic:dsh-plugin topic:agent-skills`",
        "元层探针": "`… awesome in:name`、`… marketplace OR store OR registry in:name`",
        "星标榜（前 50）": "`sort=stars&per_page=50`",
        "其他": "回溯贴标探针（`created:<概念之前>`、`stars:>=100`）",
    }
    order = list(tpl.keys())
    out = ["| 类别 | 查询串模板 | 条数 |", "|---|---|---|"]
    total = 0
    for k in order:
        if not n[k]:
            continue
        out.append(f"| {k} | {tpl[k]} | {n[k]} |")
        total += n[k]
    out.append(f"| **合计** | — | **{total}** |")
    return "\n".join(out), total

def main():
    rows = load()
    a1, total = table_a1(rows)
    tpl = (SRC / "paper.md").read_text(encoding="utf-8")
    subs = {
        "<!--TABLE_DSH-->": rd(DATA / "table_dsh.md"),
        "<!--TABLE_SKILLS-->": rd(DATA / "table_skills.md"),
        "<!--TABLE_RETENTION-->": rd(DATA / "table_retention.md"),
        "<!--TABLE_LADDER-->": rd(DATA / "table_ladder.md"),
        "<!--TABLE_TOP50-->": rd(DATA / "table_top50.md"),
        "<!--TABLE_A1-->": a1,
        "<!--TABLE_A2Q-->": rd(DATA / "table_a2_queries.md"),
        "<!--TABLE_MATRIX-->": rd(DATA / "table_matrix.md"),
        "<!--TABLE_C1-->": rd(DATA / "table_c1.md"),
        "<!--TABLE_D1-->": rd(DATA / "table_d1.md"),
        "{{N_QUERIES}}": str(total),
    }
    for k, v in subs.items():
        assert k in tpl, f"缺占位符 {k}"
        tpl = tpl.replace(k, v)
    assert "<!--TABLE_" not in tpl and "{{" not in tpl, "仍有未替换的占位符"
    OUT.write_text(tpl, encoding="utf-8")
    print(f"{OUT.name}: {len(tpl)} chars, {total} queries")

if __name__ == "__main__":
    main()

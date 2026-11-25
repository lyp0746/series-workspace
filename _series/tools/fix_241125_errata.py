# -*- coding: utf-8 -*-
"""勘误：2025-11-25 一轮（Gemini 复核清单 + 人工核实补充）。

只做"文本级定点替换"，不动内容、不动正文论证。三条纪律：
  1. 白名单文件：只改源码与合集的输入副本；release/ 与 versions/ 是已发布快照，不改。
  2. 每一条都写清"旧串 → 新串"，跑完打印逐行变更；可反查、可回滚。
  3. 幂等：同一个脚本跑两遍，第二遍不产生任何改动。

用法：
    python _series/tools/fix_241125_errata.py --dry-run   # 只看会改什么
    python _series/tools/fix_241125_errata.py             # 落盘
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG = []

# ---------------------------------------------------------------- 1 通用替换
# 每项：(说明, 旧串, 新串)
# 注：Gemini 报的「**“部分”用得多** 未渲染」不是源码错误——用现行 markdown 库重排
# 这一句能正常加粗，`_build-print.html` 里的字面量是 11-15 那版旧渲染器的产物。不动源。
GLOBAL_FIXES = [
    ("「系列第本系列工作论文」是抹旧序号留下的病句", "系列第本系列", "本系列"),
    ("论文二曾用名《门的数目》，统一为现名", "《门的数目》", "《谁在切时间轴》"),
    ("「前此前几本」多打一个「前」", "前此前几本", "此前几本"),
]

# ---------------------------------------------------------------- 2 编号迁移
# 合集把《六张账单的对账》从旧第九篇移到最后作第十五篇，于是旧十—十五整体前移一位。
# 1—8 篇编号未变，只需重编 9—15。逐文件显式声明，避免跨文件误伤。
RENUMBER = {
    # 旧 14 = 开明君主 → 新 13
    "DomainCrossSection": {"第十四篇": "第十三篇"},
    "IsomorphismStrength": {"第十四篇": "第十三篇"},
    "OptimizationBoundary": {"第十四篇": "第十三篇"},
    "CapacityProxies": {"第十四篇": "第十三篇"},
    # 旧 9 = 六张账单 → 新 15；旧 10 = 领域剖面 → 新 9；旧 11 = 同构 → 新 10
    "MonarchCompetition": {"第十篇": "第九篇", "第十一篇": "第十篇",
                           "第九篇": "第十五篇", "前九篇": "前十四篇"},
    "LedgerReconciliation": {"第十篇": "第九篇", "第十一篇": "第十篇",
                             "第十四篇": "第十三篇", "第十五篇": "第十四篇",
                             "第十四、十五篇": "第十三、十四篇",
                             "第七至十四篇": "第七至十三篇"},
}

# ---------------------------------------------------------------- 3 单点替换
POINT_FIXES = [
    # 《粗码》目录与公开元数据：正文早已是三十九章，只有目录短标题与 Zenodo 描述残留
    ("resolution-grain/build_book.py",
     "路线图：八部分，三十八章", "路线图：八部分，三十九章"),
    ("resolution-grain/.zenodo.json",
     "八部分三十八章", "八部分三十九章"),
    ("resolution-grain/.zenodo.json",
     "thirty-eight chapters", "thirty-nine chapters"),
    # 合集总序：方法部（七—十三）的括注漏了「九」且出现两个「十三」
    ("合集/build_collection.py",
     "'把四问操作化（十）、给跨域类比定价（十一）、把「记住」落成架构（十二）、再把那套架构压测到边界（十三）、'",
     "'把四问操作化（九）、给跨域类比定价（十）、把「记住」落成架构（十一）、再把那套架构压测到边界（十二）、'"),
    ("合集/build_collection.py",
     "它已把十—十五的 58 条与本文自己的 6 条并账",
     "它已把九—十四的 58 条与本文自己的 6 条并账"),
    ("合集/build_collection.py",
     "# 分部：九卷 / 实证论文（一—六）/ 方法论文（七、八、十—十三）/ 阶段总账（九）",
     "# 分部：九卷 / 实证论文（一—六）/ 方法论文（七—十三）/ 阶段总账（十五）"),
]


# ---------------------------------------------------------------- 工具
def walk_targets():
    """产出 (path, 适用规则) 列表。白名单按文件角色决定。"""
    targets = []

    def add(path, rules):
        if os.path.exists(path):
            targets.append((path, rules))

    base = ROOT
    for d, mapping in RENUMBER.items():
        src = os.path.join(base, d, "source", "paper.md")
        add(src, mapping)
        # 合集的输入副本（<中文名>.md / .html）同步，否则重建合集时又被覆盖回去
        for fn in os.listdir(os.path.join(base, d)):
            if fn.endswith(".md") or fn.endswith(".html"):
                add(os.path.join(base, d, fn), mapping)

    glob_rules = {old: new for _, old, new in GLOBAL_FIXES}
    # 论文正文（含 source）
    for d in os.listdir(base):
        pdir = os.path.join(base, d)
        if not os.path.isdir(pdir) or d.startswith(("_", ".", "合集")):
            continue
        for root, dirs, files in os.walk(pdir):
            dirs[:] = [x for x in dirs
                       if x not in {"release", "versions", "archive", ".git", "node_modules"}]
            for fn in files:
                if fn.endswith((".md", ".html")):
                    add(os.path.join(root, fn), glob_rules)
    # 合集自身
    add(os.path.join(base, "合集", "build_collection.py"), glob_rules)
    return targets


def apply_text(text, rules, where):
    """两遍替换：先落占位符，避免 第十篇→第九篇 又被 第九篇→第十五篇 二次命中。"""
    changed = False
    marks = {}
    for i, (old, new) in enumerate(rules.items()):
        if old in text:
            key = f"\x00{i}\x00"
            while key in text or key in marks.values():
                key += "\x00"
            n = text.count(old)
            text = text.replace(old, key)
            marks[key] = new
            LOG.append((where, old, new, n))
            changed = True
    for key, new in marks.items():
        text = text.replace(key, new)
    return text, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = walk_targets()
    touched = 0

    for path, rules in targets:
        try:
            raw = io.open(path, encoding="utf-8").read()
        except Exception:
            continue
        text = raw

        rel = os.path.relpath(path, ROOT)
        text, _ = apply_text(text, rules, rel)

        if text != raw:
            touched += 1
            if not args.dry_run:
                io.open(path, "w", encoding="utf-8").write(text)

    # 单点替换
    for rel, old, new in POINT_FIXES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print(f"[跳过] 缺文件 {rel}")
            continue
        raw = io.open(p, encoding="utf-8").read()
        if old not in raw:
            print(f"[无匹配] {rel}: {old[:24]}")
            continue
        n = raw.count(old)
        if not args.dry_run:
            io.open(p, "w", encoding="utf-8").write(raw.replace(old, new))
        LOG.append((rel, old, new, n))
        touched += 1

    print(f"\n{'[dry-run] ' if args.dry_run else ''}改动 {touched} 个文件 / {len(LOG)} 条规则命中\n")
    for where, old, new, n in LOG:
        print(f"  {where}\n    ×{n}  {old!r} → {new!r}")


if __name__ == "__main__":
    main()

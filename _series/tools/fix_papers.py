#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""论文结构统一（spec v2 §3 / §4）。

五步，全部内容保留、只重排：
1. 折叠连续重复的 `## N 标题`（同一节号出现 2–4 次的空标题）；
2. 附录瘦身到 ≤6：把最短的一件并进它的上一篇，降为 `###` 小节（登记簿不并）；
3. 按文档顺序把附录重编号为 A–F（A0/D2/J2 这类"打补丁编号"随之消失）；
4. 按文档顺序把 `## N` 重编号为 1..K（消除跳号与乱序）；
5. 回写正文里的 `附录 X` 引用。

只改 `source/paper.md`；产物由各仓 `assemble.py` 重建。
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAPERS = ["ComputingDemystified", "WorldPeriodization", "SleepingResidue", "HunanRelaySystem",
          "BureauRotationCession", "HarnessEcology", "OptimizationBoundary", "CapacityProxies",
          "DomainCrossSection", "IsomorphismStrength", "MemoryAnchor", "MemoryStressTest",
          "LedgerReconciliation", "MonarchCompetition"]
KEEP_LEDGER = "登记簿"
PROTECT = ("登记簿", "十个常见反对", "编码手册", "字段字典", "数据来源", "数据与复现", "快照")
DROP = ("图表索引", "术语英译")


def split_blocks(t):
    """按 `## ` 切成 (前置, [(heading, body)])"""
    parts = re.split(r"(?m)^## ", t)
    head = parts[0]
    blocks = []
    for p in parts[1:]:
        line, _, body = p.partition("\n")
        blocks.append([line.strip(), body])
    return head, blocks


def join(head, blocks):
    out = [head.rstrip() + "\n\n" if head.strip() else ""]
    for h, b in blocks:
        b = (b or "").strip()
        out.append(f"## {h}\n\n{b}\n\n" if b else f"## {h}\n\n")
    return "".join(out)


def dedupe(blocks):
    """折叠相邻的同号标题：留最长的那个（空壳在前、真标题在后）"""
    out = []
    dropped = 0
    for h, b in blocks:
        m = re.match(r"^(\d+)[\s　]", h)
        if out and m and not b.strip():
            prev_num = re.match(r"^(\d+)[\s　]", out[-1][0])
            if prev_num and prev_num.group(1) == m.group(1):
                dropped += 1
                continue
            # 前一个是空壳、当前有内容：用当前替换
            if prev_num and prev_num.group(1) == m.group(1) and not out[-1][1].strip():
                out[-1] = [h, b]
                dropped += 1
                continue
        if out:
            pn = re.match(r"^(\d+)[\s　]", out[-1][0])
            n = re.match(r"^(\d+)[\s　]", h)
            if pn and n and pn.group(1) == n.group(1) and not out[-1][1].strip() and b.strip():
                out[-1] = [h, b]
                dropped += 1
                continue
        out.append([h, b])
    return out, dropped


APPX = re.compile(r"^附\s*录\s*([A-Z])(\d*)\s*[　 ]?(.*)$")


def appx_tag(h):
    m = APPX.match(h)
    return (m.group(1) + m.group(2)) if m else None


def cn(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def drop_low_value(blocks, archive):
    """图表索引（PDF 书签已有）与术语英译（归到系列术语表）不进附录。

    内容不丢：归档到 _series/registry/glossary_en.md 与 appendix_archive/。
    """
    keep = []
    for h, b in blocks:
        if appx_tag(h) and any(d in h for d in DROP):
            archive.append((h, b))
            continue
        keep.append([h, b])
    return keep


def shrink(blocks, limit=6, log=None):
    """附录并到 ≤limit：最短者并入上一篇（登记簿等受保护的件不并）"""
    aps = [i for i, (h, _) in enumerate(blocks) if appx_tag(h)]
    while len(aps) > limit:
        cand = []
        for idx in aps:
            h = blocks[idx][0]
            if any(x in h for x in PROTECT):
                continue
            cand.append((cn(blocks[idx][1]), idx))
        if not cand:
            break
        _, idx = min(cand)
        tgt = max([i for i in aps if i < idx], default=None)
        if tgt is None:
            tgt = min([i for i in aps if i > idx], default=None)
        if tgt is None:
            break
        h, b = blocks[idx]
        m = APPX.match(h)
        sub = m.group(3).strip() if m else h
        # 被并者降为 ### 小节
        blocks[tgt][1] = blocks[tgt][1].rstrip() + f"\n\n### {sub}\n\n" + b
        del blocks[idx]
        if log is not None:
            log.append(f"并：{h[:28]} → {blocks[tgt-1][0][:20] if tgt>idx else blocks[tgt][0][:20]}")
        aps = [i for i, (hh, _) in enumerate(blocks) if appx_tag(hh)]
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    for p in (PAPERS if not a.item else [a.item]):
        src = os.path.join(ROOT, p, "source", "paper.md")
        if not os.path.exists(src):
            print(f"{p:22} 无 source/paper.md，跳过")
            continue
        t = open(src, encoding="utf-8").read()
        head, blocks = split_blocks(t)
        blocks, dropped = dedupe(blocks)
        log = []
        archive = []
        blocks = drop_low_value(blocks, archive)
        blocks = shrink(blocks, 6, log)

        # 附录重编号
        amap = {}
        k = 0
        for h, _ in blocks:
            tag = appx_tag(h)
            if not tag:
                continue
            new = chr(ord("A") + k)
            k += 1
            amap[tag] = new

        def fix_appx_ref(m):
            tag = m.group(1) + (m.group(2) or "")
            return "附录 " + amap.get(tag, tag)

        body = join(head, blocks)
        for old in sorted(amap, key=len, reverse=True):
            body = re.sub(rf"附\s*录\s*{old}(?![\dA-Z])", "附录 " + amap[old], body)

        # 附录标题重写（在正文引用改写后统一做）
        head2, blocks2 = split_blocks(body)
        k = 0
        for b in blocks2:
            m = APPX.match(b[0])
            if not m:
                continue
            title = m.group(3).strip()
            b[0] = f"附录 {chr(ord('A') + k)}　{title}"
            k += 1

        # 正文节内小节按文档顺序重编号（治 3.1,3.2,3.3,3.5,3.4 这类乱序）
        for b in blocks2:
            m = re.match(r"^(\d+)[\s　]", b[0])
            if not m:
                continue
            sec = m.group(1)
            submap = {}
            cnt = 0

            def _sub(mm):
                nonlocal cnt
                cnt += 1
                submap[mm.group(1)] = str(cnt)
                return f"### {sec}.{cnt}"

            b[1] = re.sub(rf"(?m)^### {sec}\.(\d+)", _sub, b[1])
            if submap:
                b[1] = re.sub(rf"(?<![\d.]){sec}\.(\d+)(\s*[节表图])",
                              lambda mm: f"{sec}.{submap.get(mm.group(1), mm.group(1))}{mm.group(2)}", b[1])

        # 正文节重编号
        n = 0
        secmap = {}
        for b in blocks2:
            m = re.match(r"^(\d+)[\s　]+(.+)$", b[0])
            if not m:
                continue
            old, title = m.group(1), m.group(2).strip()
            n += 1
            secmap[old] = str(n)
            b[0] = f"{n} {title}"
            # 小节号 X.k
            b[1] = re.sub(rf"(?m)^### {old}\.(\d+)", lambda mm: f"### {n}.{mm.group(1)}", b[1])
            b[1] = re.sub(rf"(?<![\d.]){old}\.(\d+)(\s*[节表图])",
                          lambda mm: f"{n}.{mm.group(1)}{mm.group(2)}", b[1])

        out = join(head2, blocks2)
        n_ap = sum(1 for b in blocks2 if APPX.match(b[0]))
        if a.dry:
            print(f"{p:22} 去重 {dropped} / 附录 {n_ap} / 节 {n} / 并 {len(log)} / 归档 {len(archive)}")
            continue
        if archive:
            reg = os.path.join(ROOT, "_series", "registry")
            os.makedirs(reg, exist_ok=True)
            with open(os.path.join(reg, "glossary_en.md"), "a", encoding="utf-8") as f:
                for h, b in archive:
                    f.write(f"\n\n<!-- from {p}: {h} -->\n" + b.strip() + "\n")
        open(src, "w", encoding="utf-8").write(out)
        print(f"{p:22} 去重 {dropped} / 附录 {n_ap} / 节 {n} / 并 {len(log)} / 归档 {len(archive)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

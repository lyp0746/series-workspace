# -*- coding: utf-8 -*-
"""把每件的「结构化地图」投递到三处：仓内 assets/（已在生成时写好）、release/、文集。

一源三投，一次生成，一处对账：
  源   书   <repo>/interactive/<repo>-explorer.html（结构地图）
          <repo>/interactive/<repo>-reader.html（阅读页）
       论文 <repo>/interactive/<原名>.html   （保留各自图表的原始文件，不搬走）
       粗码 <repo>/assets/knowledge-map.html
       合集 合集/合集-explorer.html
  投 1 <repo>/release/<repo>-explorer.html      （书的 release.sh 里已加 copy 行）
  投 2 C:\\Users\\16103\\Downloads\\李毅芃作品集\\_可视化\\<repo>-explorer.html
  对账 文集/_可视化/MANIFEST.txt（字节数＋SHA256 前 16 位）

用法：  "$PY" _series/tools/publish_viz.py [--check]
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DROP = r"C:\Users\16103\Downloads\李毅芃作品集\_可视化"   # 注意：Windows 路径，不是 /mnt/c

BOOKS = ["knowledge-tradeoffs", "capacity-cascade", "emergence-critical", "entropy-spiral",
         "interpretation-tradeoff", "impossibility-triangle", "distinction-evolution",
         "mind-forks", "hotspot-bills"]

# 论文：源文件（各自仓 interactive/ 下的原名）；5 篇用的是 section 名
PAPERS = [
    ("ComputingDemystified", "term-explorer.html"),
    ("WorldPeriodization", "periodization-explorer.html"),
    ("SleepingResidue", "sleeping-residue-explorer.html"),
    ("HunanRelaySystem", "hunan-explorer.html"),
    ("BureauRotationCession", "control-explorer.html"),
    ("HarnessEcology", "harness-explorer.html"),
    ("OptimizationBoundary", "optimization-boundary-explorer.html"),
    ("CapacityProxies", "capacity-proxies-explorer.html"),
    ("DomainCrossSection", "domains.html"),
    ("IsomorphismStrength", "motifs.html"),
    ("MemoryAnchor", "schemes.html"),
    ("MemoryStressTest", "steps.html"),
    ("MonarchCompetition", "monarch-competition-explorer.html"),
    ("SeamLedger", "seams.html"),
    ("LedgerReconciliation", "ledger-reconciliation-explorer.html"),
]

GRAIN = ("resolution-grain", "assets/knowledge-map.html")
COLL = ("合集", "合集-explorer.html")


def sha16(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()[:16]


def items():
    out = []
    for b in BOOKS:
        out.append((b, f"interactive/{b}-explorer.html", f"{b}-explorer.html"))
        out.append((b, f"interactive/{b}-reader.html", f"{b}-reader.html"))
    for repo, fn in PAPERS:
        out.append((repo, f"interactive/{fn}", f"{repo}-explorer.html"))
    out.append((GRAIN[0], GRAIN[1], f"{GRAIN[0]}-explorer.html"))
    out.append((COLL[0], COLL[1], f"{COLL[0]}-explorer.html"))
    return out


def main(argv):
    check = "--check" in argv
    os.makedirs(DROP, exist_ok=True)
    rows, missing = [], []
    for repo, rel, name in items():
        src = os.path.join(ROOT, repo, rel)
        if not os.path.exists(src):
            missing.append(f"{repo}/{rel}")
            continue
        rel_dir = os.path.join(ROOT, repo, "release")
        rel_dst = os.path.join(rel_dir, name)
        drop_dst = os.path.join(DROP, name)
        if not check:
            os.makedirs(rel_dir, exist_ok=True)
            shutil.copy2(src, rel_dst)
            shutil.copy2(src, drop_dst)
        rows.append((name, os.path.getsize(src) / 1024, sha16(src)))
    if not check:
        with open(os.path.join(DROP, "MANIFEST.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# 可视化对账单（2026-11-26）\n")
            fh.write("# 文件\tKB\tSHA256 前 16 位\n")
            for name, kb, h in sorted(rows):
                fh.write(f"{name}\t{kb:.0f}\t{h}\n")
        with open(os.path.join(ROOT, "_series", "tools", "viz-manifest.txt"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("# 可视化源与哈希（2026-11-26）；三处同源，改一处跑一次 publish_viz.py\n")
            for name, kb, h in sorted(rows):
                fh.write(f"{name}\t{kb:.0f}\t{h}\n")
    total = sum(kb for _, kb, _ in rows)
    print(f"{len(rows)} 件投放{'(检查模式，未写盘)' if check else ''}；合计 {total / 1024:.1f} MB")
    if missing:
        print("缺源：", *missing, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

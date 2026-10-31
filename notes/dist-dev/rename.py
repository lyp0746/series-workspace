# -*- coding: utf-8 -*-
"""更名：《区分的语言》→《区分的语言》，并按新内容重写副题。

原则：
  * 本仓（distinction-evolution）的源文件、题名文件全部更新；
  * 其余仓只改 source/ 与题名文件（CITATION/README/docs），不动 output/release（下次构建生效）；
  * 概念 DOI 不变；旧名以「旧名《区分的语言》」形式在 CHANGELOG 留痕。
"""
import io
import os
import re

ROOT = r"D:\0_Article"
OLD, NEW = "区分的语言", "区分的语言"

TITLE = "区分的语言"
SUBTITLE = "区分如何生成空间、形式与谱——七条定理、三十六个领域与一次连续极限"
TITLE_EN = "The Language of Distinction"
SUBTITLE_EN = ("How Distinctions Generate Space, Form and Spectrum: "
               "Seven Theorems, Thirty-Six Domains, and One Continuum Limit")

# 1) 本仓 book.json
p = os.path.join(ROOT, "distinction-evolution", "source", "book.json")
import json
b = json.load(io.open(p, encoding="utf-8"))
b["title"] = TITLE
b["subtitle"] = SUBTITLE
b["title_en"] = TITLE_EN
b["subtitle_en"] = SUBTITLE_EN
io.open(p, "w", encoding="utf-8").write(json.dumps(b, ensure_ascii=False, indent=2) + "\n")
print("book.json 已更新")

# 2) 本仓 CITATION.cff：题名行 + 摘要首句
p = os.path.join(ROOT, "distinction-evolution", "CITATION.cff")
s = io.open(p, encoding="utf-8").read()
s = re.sub(r'^title: ".*"$',
           'title: "%s：%s / %s: %s"' % (TITLE, SUBTITLE, TITLE_EN, SUBTITLE_EN),
           s, count=1, flags=re.M)
s = s.replace("本著作提出“区分的语言”这一语言规范", "本著作提出“区分的语言”这一语言规范")
s = s.replace("（旧名《区分的语言》）", "")
io.open(p, "w", encoding="utf-8").write(s)
print("CITATION.cff 已更新")

# 3) 全库把旧名替换为新名（只改 source/docs/题名文件）
EXT = (".html", ".md", ".cff", ".json", ".py", ".txt")
SKIP_DIR = ("output", "release", "node_modules", ".git", "__pycache__", "assets")
changed = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIR]
    for f in files:
        if not f.endswith(EXT):
            continue
        p = os.path.join(base, f)
        if os.path.getsize(p) > 2_000_000:
            continue
        try:
            s = io.open(p, encoding="utf-8").read()
        except Exception:
            continue
        if OLD in s:
            io.open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
            changed.append(os.path.relpath(p, ROOT))
print("替换文件数：", len(changed))
for c in changed[:12]:
    print("  ", c)

# 4) README 标题行
p = os.path.join(ROOT, "distinction-evolution", "README.md")
s = io.open(p, encoding="utf-8").read()
s = re.sub(r"^# .*$", "# %s" % TITLE, s, count=1, flags=re.M)
s = re.sub(r"^> .*$", "> %s" % SUBTITLE, s, count=1, flags=re.M)
io.open(p, "w", encoding="utf-8").write(s)
print("README 已更新")

# 5) inventory.tsv（系列元数据单一来源）
p = os.path.join(ROOT, "inventory.tsv")
if os.path.exists(p):
    s = io.open(p, encoding="utf-8").read()
    s = s.replace("区分的语言：五个领域，同一个二次型 / The Grammar of Distinction: Fi",
                  "%s：%s / %s: How Distinctions Gen" % (TITLE, SUBTITLE[:20], TITLE_EN))
    io.open(p, "w", encoding="utf-8").write(s)
    print("inventory.tsv 已更新")

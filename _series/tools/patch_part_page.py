#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""一次性补丁：让 9 本书都渲染「部分扉页导语 + 部分小结」（spec v2 §1）。

幂等：已打过的文件跳过。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["knowledge-tradeoffs", "distinction-evolution", "capacity-cascade", "entropy-spiral",
         "impossibility-triangle", "interpretation-tradeoff", "emergence-critical",
         "hotspot-bills", "mind-forks"]

FUNCS = '''

def _part_para(text):
    """部分导语/小结正文：按空行拆段，逐段包 <p>。"""
    text = (text or "").strip()
    if not text:
        return ""
    out = []
    for seg in re.split(r"\\n\\s*\\n", text):
        seg = " ".join(seg.split())
        if seg:
            out.append(f"<p>{seg}</p>")
    return "\\n".join(out)


def build_part_page(part):
    """部分扉页：标题 + 导语。

    导语回答三件事：上一部分留下了什么、这一部分怎么推进、让出了什么。
    数据来自 parts.json 的 `intro`，缺省回退 `desc`（避免旧数据空着）。
    """
    title = part["part"]
    intro = part.get("intro") or part.get("desc") or ""
    return (f'<div class="part-page">'
            f'<h1 class="part-title">{title}</h1>'
            f'<div class="part-intro">{_part_para(intro)}</div>'
            f'</div>')


def build_part_summary(part):
    """部分小结：最硬的一条、它依赖的假设、下一部分为什么从这里开始。"""
    sm = part.get("summary") or ""
    if not sm.strip():
        return ""
    return (f'<div class="part-summary"><span class="bt">本部分小结</span>'
            f'{_part_para(sm)}</div>')

'''

CSS = '''
/* ---- 部分扉页 / 部分小结（spec v2 §1） ---- */
.part-page { break-before: page; }
.part-intro {
  max-width: 132mm; margin: 7mm auto 0;
  font-size: 10.5pt; line-height: 1.9; color: #2b2b2b; text-align: justify;
}
.part-intro p { margin: 0 0 .55em; text-indent: 2em; }
.part-summary {
  max-width: 132mm; margin: 8mm auto 2mm; padding: 4.5mm 6mm;
  border-top: 1px solid #d8cbb0; border-bottom: 1px solid #d8cbb0;
  background: #fbf9f4; font-size: 10pt; line-height: 1.8;
}
.part-summary .bt {
  display: block; font-weight: 700; letter-spacing: 1px;
  margin-bottom: .35em; color: #8a6d2f;
}
.part-summary p { margin: 0 0 .45em; text-indent: 2em; }
'''

OLD = '''    for part in parts:
        n_before = len(blocks)
        for ch in part.get("chapters", []):
            if ch.get("written") and ch.get("file"):
                f = os.path.join(SOURCE, ch["file"])
                if os.path.exists(f):
                    if len(blocks) == n_before:  # 部分扉页只加一次
                        blocks.append(f'<h1 class="part-title">{part["part"]}</h1>')
                    with open(f, encoding="utf-8") as fh:
                        body = fh.read()
                    blocks.append(f'<div id="ch{ch["no"]}">{body}</div>')
                    written.append(ch["no"])
'''

NEW = '''    for part in parts:
        if not any(c.get("written") and c.get("file") for c in part.get("chapters", [])):
            continue
        blocks.append(build_part_page(part))
        for ch in part.get("chapters", []):
            if ch.get("written") and ch.get("file"):
                f = os.path.join(SOURCE, ch["file"])
                if os.path.exists(f):
                    with open(f, encoding="utf-8") as fh:
                        body = fh.read()
                    blocks.append(f'<div id="ch{ch["no"]}">{body}</div>')
                    written.append(ch["no"])
        blocks.append(build_part_summary(part))
'''


def patch(path):
    with open(path, encoding="utf-8", newline="") as f:
        t = f.read()
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    if "build_part_page" in t:
        return "skip"
    if OLD not in t:
        return "MISS"
    t = t.replace(OLD, NEW, 1)
    m = re.search(r"\ndef build\(book, parts, ereader=False\):", t)
    if not m:
        m = re.search(r"\ndef build\(", t)
    if not m:
        return "NOBUILD"
    t = t[:m.start()] + FUNCS + t[m.start():]
    if crlf:
        t = t.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(t)
    return "ok"


def patch_css(path):
    if not os.path.exists(path):
        return "missing"
    with open(path, encoding="utf-8", newline="") as f:
        t = f.read()
    if ".part-intro" in t:
        return "skip"
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n") + CSS
    if crlf:
        t = t.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(t)
    return "ok"


def main():
    for b in BOOKS:
        r1 = patch(os.path.join(ROOT, b, "build_book.py"))
        r2 = patch_css(os.path.join(ROOT, b, "assets", "css", "book.css"))
        r3 = patch_css(os.path.join(ROOT, b, "assets", "css", "paper.css"))
        print(f"{b:24} build={r1:6} book.css={r2:8} paper.css={r3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

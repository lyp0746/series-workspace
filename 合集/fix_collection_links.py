#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为合集目录页补内部链接：按目录行末页码生成 LINK_GOTO。"""
import re, sys, os
import pymupdf


def fix(path):
    doc = pymupdf.open(path)
    # 预索引：每页前 300 字，供无页码目录回退查找
    texts = [doc[i].get_text()[:600] for i in range(len(doc))]
    added = 0
    for pno in range(len(doc)):
        page = doc[pno]
        txt = page.get_text()
        if "总目录" not in txt and "本卷目录" not in txt:
            continue
        words = page.get_text("words")
        words = sorted(words, key=lambda w: (w[1], w[0]))
        rows = []
        cur = []
        for w in words:
            if not cur or abs(w[1] - cur[0][1]) < 4.0:
                cur.append(w)
            else:
                rows.append(cur); cur = [w]
        if cur:
            rows.append(cur)
        for row in rows:
            row = sorted(row, key=lambda w: w[0])
            s = " ".join(w[4] for w in row).strip()
            m = re.match(r"^(.*?)\s+(\d{1,4})$", s)
            if m:
                label, num = m.group(1).strip(".·… "), int(m.group(2))
            else:
                label, num = s.strip(".·… "), None
            if len(label) < 3:
                continue
            if not re.match(r"^(卷[一二三四五六七八九十]+|论文[一二三四五六七八九十]+|第\s*\d+\s*章|附\s*录)", label):
                continue
            # 目录行左侧的文字块（排除页码本身）
            body = [w for w in row if not re.fullmatch(r"\d{1,4}", w[4])]
            if not body:
                continue
            x0 = min(w[0] for w in body); y0 = min(w[1] for w in body)
            x1 = max(w[2] for w in body); y1 = max(w[3] for w in body)
            target = None
            if num and 1 <= num <= len(doc):
                target = num - 1
            else:
                probe = label[:18]
                for j in range(pno + 3, len(doc)):
                    if probe and probe in texts[j]:
                        target = j
                        break
            if target is None:
                continue
            page.insert_link({"kind": pymupdf.LINK_GOTO,
                              "from": pymupdf.Rect(x0, y0, x1, y1),
                              "page": target, "to": pymupdf.Point(0, 0)})
            added += 1
    tmp = path + ".links.pdf"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, path)
    print(path, "links added", added)

if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix(p)

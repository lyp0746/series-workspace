#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按分组重建一章：把旧小节合并成新小节，保留正文，去掉重复标题与重复导语。

用法：python _series/tools/regroup_chapter.py <chapter.html> <spec.json>
spec: [{"title": "新标题", "ids": ["sec25-1", ...], "prefix": "可选过渡句"}, ...]
未列入任何组的正文（章首、旧 lead）保留在最前；列入组的 h3 全部删除。
"""
import json, re, sys

H3 = re.compile(r'<h3([^>]*)>(.*?)</h3>', re.S)


def plain(h):
    return re.sub(r"<[^>]+>", "", h).strip()


def main():
    path, spec_path = sys.argv[1], sys.argv[2]
    t = open(path, encoding="utf-8").read()
    spec = json.load(open(spec_path, encoding="utf-8"))
    heads = list(H3.finditer(t))
    intro = t[:heads[0].start()] if heads else t
    secs = {}
    order = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(t)
        mid = re.search(r'id="([^"]+)"', m.group(1))
        sid = mid.group(1) if mid else f"anon{i}"
        body = t[m.end():end]
        # 去掉正文里重复的“本章/本节边界”式段落头（保留内容）
        secs[sid] = (plain(m.group(2)), body)
        order.append(sid)
    used = set()
    out = [intro.rstrip()]
    for g in spec:
        chunks = []
        for sid in g["ids"]:
            if sid not in secs:
                print(f"  !! missing {sid}")
                continue
            used.add(sid)
            body = secs[sid][1].strip()
            if body:
                chunks.append(body)
        num = g.get("num")
        title = f'{num}　{g["title"]}' if num else g["title"]
        out.append(f'<h3 id="sec{num.replace(".", "-") if num else "x"}">{title}</h3>')
        if g.get("prefix"):
            out.append(f'<p>{g["prefix"]}</p>')
        out.extend(chunks)
    # 未列入组的节（除章首）原样保留在末尾之前
    rest = [sid for sid in order if sid not in used]
    for sid in rest:
        title, body = secs[sid]
        out.append(f"<h3>{title}</h3>")
        out.append(body.strip())
    text = "\n\n".join(x for x in out if x)
    open(path, "w", encoding="utf-8").write(text + "\n")
    print(f"regrouped {path}: {len(heads)} -> {len(spec) + len(rest)} sections")


if __name__ == "__main__":
    main()

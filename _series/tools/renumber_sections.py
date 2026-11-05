#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""节号归一：删掉 a/b/c 补丁号，按文档顺序重排 N.M，并同步 parts.json 与交叉引用。

用法：
    python _series/tools/renumber_sections.py <repo> [--write]
默认 dry-run，只打印映射；--write 才落盘。
"""
from __future__ import annotations
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3 = re.compile(r'<h3([^>]*)>(.*?)</h3>', re.S)
LABEL = re.compile(r'^(\d+)[.．](\d+)([a-z]?)[　\s]')


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    open(p, "w", encoding="utf-8").write(s)


def plain(h):
    return re.sub(r"<[^>]+>", "", h).strip()


def main():
    repo = sys.argv[1]
    do_write = "--write" in sys.argv
    src = os.path.join(ROOT, repo, "source")
    files = sorted(f for f in os.listdir(src) if re.fullmatch(r"ch\d+\.html", f))
    mapping = {}          # (ch, oldlabel) -> newlabel
    new_by_file = {}
    for f in files:
        ch = int(re.search(r"\d+", f).group())
        t = read(os.path.join(src, f))
        heads = list(H3.finditer(t))
        k = 0
        repl = []
        for m in heads:
            txt = plain(m.group(2))
            lm = LABEL.match(txt)
            if not lm:
                continue
            k += 1
            old = f"{lm.group(1)}.{lm.group(2)}{lm.group(3)}"
            new = f"{ch}.{k}"
            mapping[(ch, old)] = new
            rest = txt[lm.end():]
            repl.append((m, old, new, rest))
        new_by_file[f] = (t, repl)
        print(f"{f}: {len(repl)} sections")
    # 打印映射中的补丁号
    patched = [(k, v) for k, v in mapping.items() if k[1][-1].isalpha()]
    for (ch, old), new in patched:
        print(f"  {ch}: {old} -> {new}")

    def remap_refs(text, chapter=None, letters_only=False):
        # 只替换明确的“节”引用，以及字母补丁号（字母号不会与图表号混淆）
        def one(m):
            a, b, l = m.group(1), m.group(2), m.group(3)
            old = f"{a}.{b}{l}"
            new = mapping.get((int(a), old))
            return m.group(0).replace(old, new) if new else m.group(0)

        text = re.sub(r"(第\s*)(\d{1,2})[.．](\d{1,2})([a-z]?)(\s*节)",
                      lambda m: m.group(1) + (mapping.get((int(m.group(2)), f"{m.group(2)}.{m.group(3)}{m.group(4)}"), f"{m.group(2)}.{m.group(3)}{m.group(4)}")) + m.group(5), text)
        text = re.sub(r"(?<![\d.])(\d{1,2})[.．](\d{1,2})([a-z])(?![\d.])", one, text)
        return text

    if not do_write:
        return
    # 章节文件：先重写 h3，再改引用
    for f, (t, repl) in new_by_file.items():
        ch = int(re.search(r"\d+", f).group())
        for m, old, new, rest in sorted(repl, key=lambda x: -x[0].start()):
            a, b = old.split(".")
            na, nb = new.split(".")
            head = m.group(2)
            # 标题里的号
            head2 = LABEL.sub(f"{na}.{nb}　", head, count=1)
            # id
            attr = m.group(1)
            attr2 = re.sub(r'id="sec\d+-\d+[a-z]?"', f'id="sec{na}-{nb}"', attr)
            t = t[:m.start()] + f"<h3{attr2}>{head2}</h3>" + t[m.end():]
        t = remap_refs(t)
        write(os.path.join(src, f), t)
    # 其它文件
    for f in sorted(os.listdir(src)):
        if not f.endswith(".html") or f in new_by_file:
            continue
        p = os.path.join(src, f)
        t = read(p)
        t2 = remap_refs(t)
        if t2 != t:
            write(p, t2)
    # parts.json：从 h3 重建 sections
    pj = os.path.join(src, "parts.json")
    if os.path.exists(pj):
        data = json.loads(read(pj))
        for part in data:
            for c in part.get("chapters", []):
                f = c.get("file")
                if not f or f not in new_by_file:
                    continue
                t = read(os.path.join(src, f))
                secs = []
                for m in H3.finditer(t):
                    txt = plain(m.group(2))
                    if re.match(r"^附\s*录", txt):
                        continue
                    secs.append(txt)
                c["sections"] = secs
        write(pj, json.dumps(data, ensure_ascii=False, indent=1))
    print("written")


if __name__ == "__main__":
    main()

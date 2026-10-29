# -*- coding: utf-8 -*-
"""把生成的表注入正文：source/paper.md → 线外的残余_延迟承认的三种机制.md

表、图、附录与 cases.csv 同源（data/cases.py）。
"""
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "线外的残余_延迟承认的三种机制.md"

def rd(p):
    return p.read_text(encoding="utf-8").strip()

def main():
    tpl = (SRC / "paper.md").read_text(encoding="utf-8")
    subs = {
        "<!--TABLE_CASES-->": rd(DATA / "table_cases.md"),
        "<!--TABLE_GROUPS-->": rd(DATA / "table_groups.md"),
        "<!--TABLE_COORDS-->": rd(DATA / "table_coords.md"),
        "<!--TABLE_MARKS-->": rd(DATA / "table_marks.md"),
        "<!--TABLE_DEC-->": rd(DATA / "table_dec.md"),
        "<!--TABLE_DEGREE-->": rd(DATA / "table_degree.md"),
        "<!--TABLE_A1J-->": rd(DATA / "table_time.md"),
        "<!--TABLE_A1-->": rd(DATA / "table_a1.md"),
        "<!--TABLE_A2-->": rd(DATA / "table_a2.md"),
    }
    for k, v in subs.items():
        assert k in tpl, f"缺占位符 {k}"
        tpl = tpl.replace(k, v)
    assert "<!--TABLE_" not in tpl, "仍有未替换的占位符"
    OUT.write_text(tpl, encoding="utf-8")
    print(f"{OUT.name}: {len(tpl)} chars")

if __name__ == "__main__":
    main()

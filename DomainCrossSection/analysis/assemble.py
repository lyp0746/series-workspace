# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "领域的剖面_四个问题与二十个领域的审计.md"


def rd(p):
    return p.read_text(encoding="utf-8").strip()


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_FOUR-->": rd(DATA / "table_four.md"),
                 "<!--TABLE_DOMAINS-->": rd(DATA / "table_domains.md"),
                 "<!--TABLE_BOTTLENECK-->": rd(DATA / "table_bottleneck.md"),
                 "<!--TABLE_ACTIONS-->": rd(DATA / "table_actions.md"),
                 "<!--TABLE_CROSS-->": rd(DATA / "table_cross.md"),
                 "<!--TABLE_SWAP-->": rd(DATA / "table_swap.md"),
                 "<!--TABLE_SIX-->": rd(DATA / "table_six.md"),
                 "<!--TABLE_BASIS-->": rd(DATA / "table_basis.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t))


if __name__ == "__main__":
    main()

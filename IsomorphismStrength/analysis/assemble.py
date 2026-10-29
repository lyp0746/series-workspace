# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "同构的强度_对偶与泛性质与不变量与四十条断裂探针.md"


def rd(p):
    return p.read_text(encoding="utf-8").strip()


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_MOTIFS-->": rd(DATA / "table_motifs.md"),
                 "<!--TABLE_GROUP_STRENGTH-->": rd(DATA / "table_group_strength.md"),
                 "<!--TABLE_LAYER-->": rd(DATA / "table_layer.md"),
                 "<!--TABLE_TRANS-->": rd(DATA / "table_trans.md"),
                 "<!--TABLE_SIX-->": rd(DATA / "table_six.md"),
                 "<!--TABLE_NEGATIVE-->": rd(DATA / "table_negative.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE/"source", BASE/"data"
OUT = BASE/"优化的边界_四前提与越界的二十个案例.md"
def rd(p): return p.read_text(encoding="utf-8").strip()
def main():
    t = (SRC/"paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_PREMISES-->": rd(DATA/"table_premises.md"),
                 "<!--TABLE_SIX-->": rd(DATA/"table_six.md"),
                 "<!--TABLE_PREMISE_OUTCOME-->": rd(DATA/"table_premise_outcome.md"),
                 "<!--TABLE_FAILMODES-->": rd(DATA/"table_failmodes.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8"); print(OUT.name, len(t))
if __name__ == "__main__": main()

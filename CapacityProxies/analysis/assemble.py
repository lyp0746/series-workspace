# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE/"source", BASE/"data"
OUT = BASE/"容量的三个代理_分期槽位与编码槽位与标签槽位.md"
def rd(p): return p.read_text(encoding="utf-8").strip()
def main():
    t = (SRC/"paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_DEFS-->": rd(DATA/"table_defs.md"),
                 "<!--TABLE_BINS-->": rd(DATA/"table_bins.md"),
                 "<!--TABLE_COUNTIES-->": rd(DATA/"table_counties.md"),
                 "<!--TABLE_PERIODS-->": rd(DATA/"table_periods.md"),
                 "<!--TABLE_CONCL-->": rd(DATA/"table_concl.md"),
                 "<!--TABLE_SIX-->": rd(DATA/"table_six.md"),
                 "<!--TABLE_GATES-->": rd(DATA/"table_gates.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8"); print(OUT.name, len(t))
if __name__ == "__main__": main()

# -*- coding: utf-8 -*-
"""表注入：source/paper.md → 六张账单的对账_六核心的可测代理与尺度边界.md"""
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE/"source", BASE/"data"
OUT = BASE/"六张账单的对账_六核心的可测代理与尺度边界.md"
def rd(p): return p.read_text(encoding="utf-8").strip()
def main():
    t = (SRC/"paper.md").read_text(encoding="utf-8")
    for k, v in {
      "<!--TABLE_SCALE-->": rd(DATA/"table_scale.md"),
      "<!--TABLE_CLOCK-->": rd(DATA/"table_clock.md"),
      "<!--TABLE_FAIL-->": rd(DATA/"table_fail.md"),
      "<!--TABLE_SIX-->": rd(DATA/"table_six.md"),
      "<!--TABLE_LEDGER-->": rd(DATA/"table_ledger.md"),
      "<!--TABLE_CONFLICTS-->": rd(DATA/"table_conflicts.md"),
      "<!--TABLE_CARDS-->": rd(DATA/"table_cards.md"),
      "<!--TABLE_BYSTATUS-->": rd(DATA/"table_bystatus.md"),
      "<!--TABLE_BYCORE-->": rd(DATA/"table_bycore.md"),
      "<!--TABLE_CROSSTAB-->": rd(DATA/"table_crosstab.md"),
    }.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t))
if __name__ == "__main__": main()

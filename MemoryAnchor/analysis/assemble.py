# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "记忆的锚点_情景唤起与异构重建与日志裁决.md"


def rd(p):
    return p.read_text(encoding="utf-8").strip()


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_VARS-->": rd(DATA / "table_vars.md"),
                 "<!--TABLE_SCHEMES-->": rd(DATA / "table_schemes.md"),
                 "<!--TABLE_TRIO-->": rd(DATA / "table_trio.md"),
                 "<!--TABLE_CAPACITY-->": rd(DATA / "table_capacity.md"),
                 "<!--TABLE_DEATH-->": rd(DATA / "table_death.md"),
                 "<!--TABLE_SIX-->": rd(DATA / "table_six.md"),
                 "<!--TABLE_SERIES-->": rd(DATA / "table_series.md"),
                 "<!--TABLE_CLAIMS-->": rd(DATA / "table_claims.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t))


if __name__ == "__main__":
    main()

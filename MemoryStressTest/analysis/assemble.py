# -*- coding: utf-8 -*-
import pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "锚点的下限_情景记忆的模拟对照实验.md"


def rd(p):
    return p.read_text(encoding="utf-8").strip()


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    for k, v in {"<!--TABLE_ENV-->": rd(DATA / "table_env.md"),
                 "<!--TABLE_PARAMS-->": rd(DATA / "table_params.md"),
                 "<!--TABLE_MAIN-->": rd(DATA / "table_main.md"),
                 "<!--TABLE_COVERAGE-->": rd(DATA / "table_coverage.md"),
                 "<!--TABLE_RHOK-->": rd(DATA / "table_rhok.md"),
                 "<!--TABLE_FALSIFY-->": rd(DATA / "table_falsify.md"),
                 "<!--TABLE_PAPER12-->": rd(DATA / "table_paper12.md"),
                 "<!--TABLE_CLAIMS-->": rd(DATA / "table_claims.md"),
                 "<!--TABLE_PAGES-->": rd(DATA / "table_pages.md"),
                 "<!--TABLE_THRESHOLDS-->": rd(DATA / "table_thresholds.md"),
                 "<!--TABLE_DRIFT-->": rd(DATA / "table_drift.md"),
                 "<!--TABLE_SENS81-->": rd(DATA / "table_sens81.md"),
                 "<!--TABLE_LEVELS-->": rd(DATA / "table_levels.md")}.items():
        assert k in t, k
        t = t.replace(k, v)
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t))


if __name__ == "__main__":
    main()

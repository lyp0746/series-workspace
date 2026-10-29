# -*- coding: utf-8 -*-
"""把 8 张表填进 source/paper.md，产出可直接排版的 Markdown。"""
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "开明君主与两层竞争_执行方向与代价承担者.md"

MAP = {
    "<!--TABLE_FOUR-->": "table_four.md",
    "<!--TABLE_VENDORS-->": "table_vendors.md",
    "<!--TABLE_RJS-->": "table_rjs.md",
    "<!--TABLE_MODELS-->": "table_models.md",
    "<!--TABLE_TIER-->": "table_tier.md",
    "<!--TABLE_SEATS-->": "table_seats.md",
    "<!--TABLE_DATA-->": "table_data.md",
    "<!--TABLE_CLAIMS-->": "table_claims.md",
}


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    for k, f in MAP.items():
        assert k in t, k
        t = t.replace(k, (DATA / f).read_text(encoding="utf-8").strip())
    assert "<!--TABLE_" not in t
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t), "chars")


if __name__ == "__main__":
    main()

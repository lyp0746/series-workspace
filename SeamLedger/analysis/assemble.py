# -*- coding: utf-8 -*-
"""把 data/ 生成的表与 assets/figures 的图注入 source/paper.md，输出发布用 Markdown。"""
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
SRC, DATA = BASE / "source", BASE / "data"
OUT = BASE / "接缝不在奇点_量子力学与广义相对论的三十道裂缝.md"

FIGS = {
    "FIG01": ("fig01_seams.png", "图 1　“根本矛盾”不是一种东西，而是四种不同的接缝"),
    "FIG02": ("fig02_types.png", "图 2　三十条账目里，逻辑矛盾只占 13%"),
    "FIG03": ("fig03_core_type.png", "图 3　六核心 × 四种接缝：没有哪个核心只对一种冲突负责"),
    "FIG04": ("fig04_scale_meas.png", "图 4　尺度越靠近普朗克/宇宙，越不可直接测量"),
    "FIG05": ("fig05_timeline.png", "图 5　四种接缝在不同年代累积：定理边界最早，记账冲突最晚"),
    "FIG06": ("fig06_coverage.png", "图 6　六个候选纲领的“声称覆盖”：没有一个超过 60%"),
    "FIG07": ("fig07_grade_status.png", "图 7　A 级只出现在“已测/已证定理”，解释与开放几乎全是 C"),
    "FIG08": ("fig08_self.png", "图 8　自证：十条命题里三条成立、两条部分、一条被自己证伪"),
}


def rd(p):
    return p.read_text(encoding="utf-8").strip()


def main():
    t = (SRC / "paper.md").read_text(encoding="utf-8")
    tables = {
        "TABLE_PROPS": "table_props.md",
        "TABLE_TYPES": "table_types.md",
        "TABLE_CORES": "table_cores.md",
        "TABLE_SCALES": "table_scales.md",
        "TABLE_GRADE_STATUS": "table_grade_status.md",
        "TABLE_SENSITIVITY": "table_sensitivity.md",
        "TABLE_NOGO": "table_nogo.md",
        "TABLE_CANDIDATES": "table_candidates.md",
        "TABLE_SELF": "table_self.md",
        "TABLE_SIX": "table_six.md",
        "TABLE_THIRTY": "table_thirty.md",
    }
    for k, v in tables.items():
        tag = f"<!--{k}-->"
        if tag in t:
            t = t.replace(tag, rd(DATA / v))
    for k, (fn, cap) in FIGS.items():
        tag = f"<!--{k}-->"
        if tag in t:
            block = f"![{cap}](assets/figures/{fn})\n\n*{cap}*\n"
            t = t.replace(tag, block)
    assert "<!--TABLE_" not in t, "还有未注入的表"
    assert "<!--FIG" not in t, "还有未注入的图"
    OUT.write_text(t, encoding="utf-8")
    print(OUT.name, len(t), "chars")


if __name__ == "__main__":
    main()

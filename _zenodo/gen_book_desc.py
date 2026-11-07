# -*- coding: utf-8 -*-
"""Generate consistent 2026-11-07 book descriptions from each book's book.json.

Outputs: _zenodo/desc/<slug>.html and updates <slug>/.zenodo.json description/date/title.
This keeps the first paragraph `<p><b>中文摘要。</b>` and the seven Chinese + seven English sections.
"""
import json, re, pathlib
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOKS = ["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
         "impossibility-triangle","interpretation-tradeoff","emergence-critical","mind-forks","hotspot-bills"]

def strip_html(s):
    return re.sub(r"<[^>]+>", "", s).strip()

def counts(slug):
    src = ROOT/slug/"source"
    parts = json.load(open(src/"parts.json", encoding="utf-8"))
    nparts = len(parts); nch = sum(len(p["chapters"]) for p in parts)
    figs = 0
    for f in src.glob("ch*.html"):
        figs += len(re.findall(r"<img", f.read_text(encoding="utf-8")))
    apx = sorted(f for f in src.glob("appendix_*.html"))
    letters = "A–" + chr(64+len(apx)) if apx else "无"
    pdf = ROOT/slug/"output"/"book.pdf"
    pages = len(PdfReader(pdf).pages) if pdf.exists() else 0
    return nparts, nch, pages, figs, len(apx), letters

def main():
    out = ROOT/"_zenodo"/"desc"; out.mkdir(exist_ok=True)
    for slug in BOOKS:
        bj = json.load(open(ROOT/slug/"source"/"book.json", encoding="utf-8"))
        z = json.load(open(ROOT/slug/".zenodo.json", encoding="utf-8"))
        nparts, nch, pages, figs, napx, letters = counts(slug)
        abstract = strip_html(bj.get("abstract",""))
        title = bj["title"]; sub = bj["subtitle"]; ten = bj.get("title_en", title); sen = bj.get("subtitle_en", sub)
        zh = (f"<p><b>中文摘要。</b>{abstract}</p>\n"
              f"<p><b>核心主张。</b>{sub}。本书不把「{title}」写成一本无所不包的概论，而是把一个问题做深：一个有限的东西，怎样一边保持结构，一边还能变化。</p>\n"
              f"<p><b>结构与证据。</b>{nparts} 部分、{nch} 章、{pages} 页、附录 {letters}、{figs} 幅图；每章保留证据分级（A/B/C 与甲/乙/丙）与可证伪登记，失败与撤回写在正文，不放进脚注。</p>\n"
              f"<p><b>版本状态（2026-11-07）。</b>本版为当前编排：书名与副题统一，版式与页码统一，附录收束为 A–F；以概念 DOI 归档，版本 DOI 指向 2026-11-07 这一版。</p>\n"
              f"<p><b>诚实纪律。</b>结论强度不超过证据强度；能算的给出数，不能算的写明「判不了」；每一条硬约束都写清谁在承担代价，以及这条限制使什么成为可能。</p>\n"
              f"<p><b>边界。</b>本书给坐标与判据，不给判决；它不替代领域专家的材料，也不把类比写成定理。具体边界见各章末与附录的登记簿。</p>\n"
              f"<p><b>版本信息。</b>2026-11-07，{pages} 页，{nch} 章，附录 {letters}；内容 CC BY 4.0，代码 MIT。</p>\n"
              f"<p><b>Abstract.</b> {ten}: {sen}. The book does not attempt an all-encompassing survey; it works one problem through: how does something finite keep its structure while still being able to change? It is organised in {nparts} parts and {nch} chapters, with appendices {letters} and {figs} figures; every chapter keeps its evidence grades (A/B/C) and falsifiability register, and reports failures and retractions in the body.</p>\n"
              f"<p><b>Core thesis.</b> {sen}. The book offers coordinates and criteria, not verdicts.</p>\n"
              f"<p><b>Structure and evidence.</b> {nparts} parts, {nch} chapters, {pages} pages, appendices {letters}, {figs} figures. The apparatus is open: data, scripts and registers are in the repository; the prose keeps a single visible grade per claim rather than hedging every clause.</p>\n"
              f"<p><b>This edition (2026-11-07).</b> Title and subtitle unified; layout and folios unified; appendices consolidated to A–F; residual DOI, series-count and typographic errors corrected; the concept DOI is stable and the version DOI points to this edition.</p>\n"
              f"<p><b>Discipline.</b> Conclusion strength does not exceed evidence strength; what can be computed is computed, what cannot is marked as undecidable; every hard constraint names who pays for it and what it makes possible.</p>\n"
              f"<p><b>Boundaries.</b> The book gives coordinates and criteria, not verdicts; it does not replace field expertise, and it does not dress an analogy as a theorem. See the chapter ends and the register appendices for specific limits.</p>\n"
              f"<p><b>Edition.</b> 2026-11-07, {pages} pages, {nch} chapters, appendices {letters}; content CC BY 4.0, code MIT.</p>")
        (out/f"{slug}.html").write_text(zh, encoding="utf-8")
        z["description"] = zh
        z["title"] = f"{title}：{sub} / {ten}: {sen}"
        z["publication_date"] = "2026-11-07"
        z["version"] = "2026-11-07"
        z["notes"] = f"学术专著/读本。2026-11-07，{pages} 页，{nch} 章，附录 {letters}。"
        (ROOT/slug/".zenodo.json").write_text(json.dumps(z, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(slug, pages, nch, letters, len(zh))

if __name__ == "__main__":
    main()

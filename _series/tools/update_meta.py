# -*- coding: utf-8 -*-
"""统一 23 件的 Zenodo 元信息：日期 2026-10-30、版本 DOI／概念 DOI、仓库链接。

权威来源：各仓 CITATION.cff 已有的 DOI + _zenodo/registry.json（覆盖书与 10–19 篇）。
"""
import io, re, os, json, glob

DATE = "2026-10-30"
BOOKS = ["entropy-spiral","capacity-cascade","distinction-evolution","impossibility-triangle",
         "interpretation-tradeoff","emergence-critical","knowledge-tradeoffs","mind-forks","hotspot-bills"]
reg = json.load(io.open("_zenodo/registry.json", encoding="utf-8"))
REG = {w["slug"]: w for w in reg["works"]}

def get(t, key):
    m = re.search(rf"^{key}:\s*(.+)$", t, re.M)
    return m.group(1).strip().strip('"') if m else None

def set_field(t, key, val, after=None):
    line = f'{key}: {val}'
    if re.search(rf"^{key}:.*$", t, re.M):
        return re.sub(rf"^{key}:.*$", line, t, count=1, flags=re.M)
    if after and re.search(rf"^{after}:.*$", t, re.M):
        return re.sub(rf"(^{after}:.*$)", r"\1\n" + line, t, count=1, flags=re.M)
    return t.rstrip() + "\n" + line + "\n"

rows = []
for d in sorted(os.listdir(".")):
    cff = os.path.join(d, "CITATION.cff")
    if not os.path.isdir(d) or not os.path.exists(cff):
        continue
    t = io.open(cff, encoding="utf-8").read()
    slug = d
    r = REG.get(slug, {})
    doi = r.get("最新版本DOI") or get(t, "doi")
    cdoi = r.get("概念DOI") or get(t, "concept-doi")
    is_book = slug in BOOKS or get(t, "type") == "book"
    repo = f"https://github.com/lyp0746/{slug}" if is_book else None
    t = set_field(t, "date-released", DATE, after="authors")
    t = set_field(t, "version", f'"{DATE}"', after="date-released")
    if doi:   t = set_field(t, "doi", doi, after="version")
    if cdoi:  t = set_field(t, "concept-doi", cdoi, after="doi")
    if repo:
        t = set_field(t, "repository-code", f'"{repo}"', after="concept-doi")
    if doi:   t = set_field(t, "url", f'"https://doi.org/{doi}"', after="repository-code")
    io.open(cff, "w", encoding="utf-8").write(t)
    rows.append((slug, "书" if is_book else "论文", doi or "—", cdoi or "—", repo or "（无仓库）"))

print(f"{'slug':24}{'类':4}{'版本DOI':30}{'概念DOI':30}仓库")
for r in rows:
    print(f"{r[0]:24}{r[1]:4}{r[2]:30}{r[3]:30}{r[4]}")
print("共", len(rows), "件")

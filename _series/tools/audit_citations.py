# -*- coding: utf-8 -*-
"""文献抽样核对（Tier-2）：对四本书的章末文献做确定性抽样，
用 Crossref 查存在性，比较标题与年份，输出可复核的清单。
"""
import glob
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = ["distinction-evolution", "capacity-cascade", "entropy-spiral", "impossibility-triangle"]
UA = {"User-Agent": "series-citation-audit/1.0 (mailto:1610369302@qq.com)"}
OUT = os.path.join(ROOT, "_series", "review", "CITATION-AUDIT.md")


def entries():
    for b in BOOKS:
        for f in sorted(glob.glob(os.path.join(ROOT, b, "source", "ch*.html"))):
            s = open(f, encoding="utf-8").read()
            for m in re.finditer(r'<div class="refs">(.*?)</div>', s, flags=re.S):
                for p in re.findall(r"<p>(.*?)</p>", m.group(1), flags=re.S):
                    p = p.strip()
                    if not p or "refh" in p:
                        continue
                    yield (b, p)


def parse(html):
    plain = re.sub("<[^>]+>", "", html).strip()
    plain = plain.replace("★ ", "")
    y = re.search(r"\((19\d{2}|20\d{2})[a-z]?\)", plain)
    year = int(y.group(1)) if y else None
    title = plain
    if year:
        title = re.sub(r"^.*?\((19\d{2}|20\d{2})[a-z]?\)\.?\s*", "", title)
    # 取到第一个“句号+空格+大写”为止（副标题用冒号，不受影响）
    m2 = re.search(r"\.\s+(?=[A-Z(])", title)
    if m2:
        title = title[:m2.start()]
    title = title.strip(" .，,;；")
    name = re.match(r"([^.,，。（(]{1,24})", plain)
    return year, re.sub(r"\s+", " ", title)[:180], (name.group(1).strip() if name else "")


def toks(s):
    return set(re.findall(r"[a-z0-9]{3,}", s.lower()))


def query(title):
    """OpenAlex 优先（书与章节覆盖好），失败再退 Crossref。"""
    try:
        url = ("https://api.openalex.org/works?per-page=3&select=title,publication_year,doi&search="
               + urllib.parse.quote(title[:180]))
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            j = json.load(r)
        out = []
        for w in j.get("results", []):
            out.append({"title": [w.get("title") or ""], "issued": {"date-parts": [[w.get("publication_year")]]},
                        "DOI": (w.get("doi") or "").replace("https://doi.org/", "")})
        if out:
            return out
    except Exception:
        pass
    url = ("https://api.crossref.org/works?rows=3&select=title,issued,author,DOI,container-title&query.bibliographic="
           + urllib.parse.quote(title[:160]))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["message"]["items"]


def main():
    rows = []
    for b, html in entries():
        y, title, name = parse(html)
        if not y or len(toks(title)) < 3:
            continue
        rows.append({"book": b, "html": html, "year": y, "title": title, "name": name})
    # 分层抽样：每本书等距取 9 条
    sample = []
    for b in BOOKS:
        rb = [r for r in rows if r["book"] == b]
        step = max(1, len(rb) // 9)
        sample += rb[::step][:9]
    out = ["# 文献抽样核对（Tier-2）", "",
           f"对象：四本章末文献共 {len(rows)} 条可核对条目；确定性抽样（每 3 条取 1）{len(sample)} 条，"
           "用 OpenAlex／Crossref 查存在性，比较标题词集与年份。", "",
           "判定：**命中**=标题词集重合 ≥0.6 且年份差 ≤1；**存疑**=命中但年份差 >1；**未命中**=前三条都不重合。", "",
           "| # | 书 | 作者 | 年 | 标题（截断） | 判定 | 命中记录 |", "|---|---|---|---|---|---|---|"]
    stat = {"命中": 0, "存疑": 0, "未命中": 0}
    detail = []
    for i, r in enumerate(sample, 1):
        try:
            items = query(r["title"])
        except Exception as e:
            stat["未命中"] += 1
            out.append(f"| {i} | {r['book']} | {r['name']} | {r['year']} | {r['title'][:52]} | 查询失败 | {type(e).__name__} |")
            continue
        best, bs = None, 0
        for it in items:
            t = " ".join(it.get("title") or [])
            a, b2 = toks(r["title"]), toks(t)
            if not a or not b2:
                continue
            s = len(a & b2) / len(a | b2)
            if s > bs:
                best, bs = it, s
        if not best or bs < 0.6:
            stat["未命中"] += 1
            out.append(f"| {i} | {r['book']} | {r['name']} | {r['year']} | {r['title'][:52]} | 未命中 | — |")
            detail.append((r, None, bs))
            continue
        iy = (best.get("issued", {}).get("date-parts") or [[None]])[0][0]
        dy = abs((iy or 0) - r["year"])
        verdict = "命中" if dy <= 1 else "存疑"
        stat[verdict] += 1
        doi = best.get("DOI", "")
        out.append(f"| {i} | {r['book']} | {r['name']} | {r['year']} | {r['title'][:52]} | {verdict} | "
                   f"[{doi}](https://doi.org/{doi}) · {iy} |")
        detail.append((r, best, bs))
        time.sleep(0.3)
    out += ["", f"**结果：命中 {stat['命中']} / 存疑 {stat['存疑']} / 未命中 {stat['未命中']}（共 {len(sample)} 条）**", "",
            "未命中不等于伪造：中文著作、旧书、报告与工作论文不一定进 Crossref。存疑项（年份差 >1）优先人工复核。", "",
            "## 未命中明细", ""]
    for r, best, bs in detail:
        if best is None:
            out.append(f"- {r['book']}｜{r['name']}（{r['year']}）｜{r['title'][:110]}")
    out += ["", "## 复核方式", "",
            "每行给出 DOI 与返回年份；点开 DOI 即可对照作者、刊名、卷页。脚本：`_series/tools/audit_citations.py`。"]
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote", OUT, stat, "sample", len(sample))


if __name__ == "__main__":
    main()

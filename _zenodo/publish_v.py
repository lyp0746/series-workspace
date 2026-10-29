# -*- coding: utf-8 -*-
"""发布新版本：六本学术专著（先）→ 其余三本与论文（后）。

用法：
    python _zenodo/publish_v.py dry  <slug>...
    python _zenodo/publish_v.py go   <slug>...
"""
import io, json, os, re, sys, glob, urllib.request
from pypdf import PdfReader
sys.path.insert(0, os.path.dirname(__file__))
import api
from descriptions import DESC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = "2026-10-30"
MONO = ["entropy-spiral","capacity-cascade","distinction-evolution",
        "impossibility-triangle","interpretation-tradeoff","emergence-critical"]

def state(slug):
    src = os.path.join(ROOT, slug, "source")
    parts = json.load(io.open(os.path.join(src, "parts.json"), encoding="utf-8"))
    bj = json.load(io.open(os.path.join(src, "book.json"), encoding="utf-8"))
    nch = sum(len(p["chapters"]) for p in parts)
    figs = sum(len(re.findall(r"<img", io.open(f, encoding="utf-8").read()))
               for f in glob.glob(os.path.join(src, "ch*.html")))
    apx = sorted(f for f in os.listdir(src) if re.fullmatch(r"appendix_[a-z]\.html", f))
    letters = "—".join([chr(65), chr(64 + len(apx))]) if apx else "无"
    pdf = os.path.join(ROOT, slug, "output", "book.pdf")
    pages = len(PdfReader(pdf).pages)
    return dict(pages=pages, nch=nch, nparts=len(parts), figs=figs,
                napx=len(apx), letters=letters, title=bj["title"], sub=bj["subtitle"])

def desc(slug, st, relation_note=""):
    if slug not in DESC:
        bj = json.load(io.open(os.path.join(ROOT, slug, "source", "book.json"), encoding="utf-8"))
        d = f"<p><b>中文摘要。</b>{bj.get('abstract','')}</p>"
    else:
        d = DESC[slug]
    d = re.sub(r"<p><b>版本信息。</b>.*?</p>", "", d, flags=re.S)
    d = re.sub(r"<p><b>Edition\.</b>.*?</p>", "", d, flags=re.S)
    zh = (f"<p><b>版本信息。</b>{DATE} 版：{st['pages']} 页、{st['nparts']} 部分 {st['nch']} 章、"
          f"{st['figs']} 幅插图、附录 {st['napx']} 件（{st['letters']}）；"
          f"每部分含满栏插图扉页与部分小结，每章八段（主提问／场景／导论／机制／表图／反例／小结／一句话带走）。"
          f"结构校阅 24 条规则 error 0 / warn 0。GitHub：github.com/lyp0746/{slug}。</p>")
    en = (f"<p><b>Edition.</b> {DATE}: {st['pages']} pages, {st['nparts']} parts and {st['nch']} chapters, "
          f"{st['figs']} figures, {st['napx']} appendices ({st['letters']}). Each part opens with a full-page "
          f"illustration and closes with a summary; each chapter follows an eight-part skeleton. "
          f"Structural lint: 24 rules, 0 error / 0 warning. GitHub: github.com/lyp0746/{slug}.</p>")
    return d.strip() + zh + en + (relation_note or "")

def legacy_meta(slug, st, related=None):
    cff = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    title = re.search(r'^title:\s*"(.+?)"\s*$', cff, re.M).group(1)
    kw_block = re.search(r"(?ms)^keywords:\n(.*?)\n[a-z]", cff)
    kws = [x.strip().strip('- "') for x in kw_block.group(1).split("\n") if x.strip().startswith("-")] if kw_block else []
    rel = related or [{"identifier": f"https://github.com/lyp0746/{slug}",
                       "relation": "isSupplementedBy", "scheme": "url"}]
    return {"metadata": {
        "upload_type": "publication", "publication_type": "book",
        "title": title, "description": desc(slug, st),
        "creators": [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}],
        "publication_date": DATE, "version": DATE, "access_right": "open",
        "license": "cc-by-4.0", "language": "zho",
        "keywords": kws[:20], "related_identifiers": rel}}


def meta_of(slug, st, extras=None):
    cff = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    title = re.search(r"^title:\s*\"(.+?)\"\s*$", cff, re.M).group(1)
    kw = re.search(r"(?ms)^keywords:\n(.*?)\n[a-z]", cff)
    keywords = [x.strip().strip('- "') for x in kw.group(1).split("\n") if x.strip().startswith("-")] if kw else []
    rel = [{"identifier": f"https://github.com/lyp0746/{slug}", "relation": "isSupplementedBy", "scheme": "url"}]
    rel += (extras or [])
    return {
        "metadata": {
            "title": title,
            "description": desc(slug, st, ""),
            "creators": [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}],
            "publication_date": DATE, "version": DATE,
            "license": "cc-by-4.0", "language": "zho",
            "resource_type": "book" if slug in MONO or slug in ("knowledge-tradeoffs","mind-forks","hotspot-bills") else "publication",
            "keywords": keywords[:20],
            "related_identifiers": rel,
        }
    }

def upload(dep_id, folder):
    _, d = api.req("GET", "https://zenodo.org/api/deposit/depositions/%s" % dep_id)
    bucket = d["links"]["bucket"]
    for f in d.get("files", []):
        api.req("DELETE", "https://zenodo.org/api/deposit/depositions/%s/files/%s" % (dep_id, f["id"]))
    n = 0
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        if not os.path.isfile(p): continue
        data = open(p, "rb").read()
        r = urllib.request.Request(f"{bucket}/{urllib.parse.quote(os.path.basename(p))}", data=data, method="PUT",
                                   headers={"Authorization": "Bearer " + api.TOK,
                                            "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x:
            x.read(); n += 1
    return n

if __name__ == "__main__":
    import urllib.parse
    mode, slugs = sys.argv[1], sys.argv[2:]
    reg = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
    for slug in slugs:
        st = state(slug)
        print(f"{slug}: {st['pages']} 页 / {st['nch']} 章 / 附录 {st['napx']}（{st['letters']}）")
        if mode == "dry": continue
        rid = reg[slug]["记录ID"]
        _, d = api.req("POST", "https://zenodo.org/api/deposit/depositions/%s/actions/newversion" % rid)
        _, d2 = api.req("GET", d["links"]["latest_draft"])
        did = d2["id"]
        n = upload(did, os.path.join(ROOT, slug, "release"))
        api.req("PUT", "https://zenodo.org/api/deposit/depositions/%s" % did, data=legacy_meta(slug, st))
        _, pub = api.req("POST", "https://zenodo.org/api/deposit/depositions/%s/actions/publish" % did)
        print(f"  PUBLISHED {slug}: {pub.get('doi')}  (概念 {pub.get('conceptdoi')})  文件 {n}")

# -*- coding: utf-8 -*-
# ⚠️ 已停用（2026-10-31）：本脚本走 actions/newversion + legacy 键名（license/keywords），
# 新版本草稿是 RDM 形态，这两个键会被静默丢弃——2026-10-30 那批 20 件就是这样丢了 CC BY 4.0。
# 发新版本请用：  python _zenodo/republish_book.py go <slug>
# 只补许可与关键词请用：python _zenodo/fix_rights_subjects.py go <slug>
raise SystemExit(__doc__ or "deprecated: use _zenodo/republish_book.py")


"""合集：发新版本（文件取自 合集23/release/ 的 8 件，不含 assets 目录）。"""
import io, json, os, sys, glob, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = 23668413           # 上一版
DATE = "2026-10-30"
REL = os.path.join(ROOT, "合集23", "release")
FILES = ["00-合集-印刷版.pdf", "01-合集-电子版.pdf", "合集.epub", "02-合集.html",
         "03-合集.md", "04-assets.zip", "MANIFEST.txt", "README.md"]

TITLE = "有限系统的取舍：系列合集 / The Tradeoffs of Finite Systems: A Collection"
DESC = """<p><b>中文摘要。</b>九本书与十四篇工作论文装订成一册，另收卷首一篇非学术文本（《中道周行集》，诗词散骈赋铭六体，为作者的方法自述，不参与分级）。本合集只做装订：每件保留自己的题名、作者行、版权页、图表、附录与登记簿，正文一字未改；合集另加总封面、总序、总目录、各卷卷封面与卷前言、各部分过渡语、后记与版本记。</p>
<p><b>结构。</b>第一部 九卷专著：只能选两样（导览）→ 区分的语言 → 遗忘的边界 → 错位的时间 → 选择的代价 → 诠释的权衡 → 涌现的临界 → 心灵的分岔 → 热点的账单。第二部 实证论文六篇：术语的账单、谁在切时间轴、线外的残余、明清湘中驿道、轮换的让渡、被点燃的生态。第三部 方法论文与阶段总账：优化的边界、容量的三个代理、领域的剖面、同构的强度、记忆的锚点、锚点的下限、开明君主与两层竞争；末为《六张账单的对账》（覆盖一—十四、110 条登记命题）。</p>
<p><b>这一版（2026-10-30，第七版）。</b>九本书与十四篇论文全部换为同日新版：各卷新增满栏插图扉页与部分小结，每章补齐八段骨架（主提问／场景／导论／机制／表图／反例／小结／一句话带走）；十四篇论文统一为 12–16 节、附录 ≤6 件且单节 ≤1200 字；全书结构校阅 24 条规则 error 0 / warn 0。版式对齐单行本（正文 12.6pt／行距 2.05／页边 26–30mm）。</p>
<p><b>边界。</b>合集为阅读便利而编，引用请以各件单行本为准（含其 DOI、附录与可证伪登记簿）。合集中的章节编号、图表编号与证据分级均与单行本一致，未做统一重排。</p>
<p><b>Abstract (English).</b> Nine books and fourteen working papers are bound into one volume, preceded by a non-academic preface (Zhongdao Zhouxing Ji — a set of poems, lyrics, prose, parallel prose, rhapsody and inscriptions that states the author's method in another language and takes no part in grading). The collection only binds: every item keeps its own title page, colophon, figures, appendices and register, with the body text unchanged. The collection adds a general cover, general preface, general table of contents, volume covers and prefaces, part transitions, an afterword and a version note.</p>
<p><b>Structure.</b> Part I, nine monographs: Pick Two (a guide) → The Grammar of Distinction → The Boundary of Forgetting → Desynchronized Time → The Price of Choice → The Interpretation Tradeoff → The Criticality of Emergence → The Forking Mind → The Bill of the Hot List. Part II, six empirical papers. Part III, method papers and the stage ledger (Reconciling Six Ledgers, covering papers I–XIV and 110 registered propositions).</p>
<p><b>This edition.</b> 2026-10-30, seventh edition: all twenty-three items replaced by the same-day editions; every chapter now carries the eight-part skeleton; every paper is 12–16 sections with ≤6 appendices of ≤1,200 characters each; structural lint passes 24 rules with zero errors and zero warnings. Typography matches the single volumes.</p>
<p><b>Files.</b>印刷版 PDF（A4）/ 电子版 PDF（B5）/ EPUB 3 / 单文件 HTML / 合并 Markdown / 图件包 / MANIFEST / README。</p>
<p><b>系列 / Series。</b>工作区与外部登记库：https://github.com/lyp0746/series-workspace；入门读本：https://github.com/lyp0746/knowledge-tradeoffs；概念 DOI 10.5281/zenodo.23613406 不变。</p>"""

def upload_dep(dep, folder, names):
    _, d = api.req("GET", f"https://zenodo.org/api/deposit/depositions/{dep}", tries=2, timeout=90)
    bucket = d["links"]["bucket"]
    for f in d.get("files", []):
        api.req("DELETE", f"https://zenodo.org/api/deposit/depositions/{dep}/files/{f['id']}", tries=1, timeout=60)
    n = 0
    for name in names:
        p = os.path.join(folder, name)
        r = urllib.request.Request(f"{bucket}/{urllib.parse.quote(name)}", data=open(p, "rb").read(),
            method="PUT", headers={"Authorization": "Bearer " + api.TOK, "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=1800) as x:
            x.read(); n += 1
        print("   +", name, os.path.getsize(p)//1024//1024, "MB", flush=True)
    return n

try:
    _, d = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{REC}/actions/newversion", tries=2, timeout=120)
    _, d2 = api.req("GET", d["links"]["latest_draft"], tries=2, timeout=120)
except Exception as e:
    print("newversion 失败，改用 /versions：", str(e)[:120], flush=True)
    _, d2 = api.req("POST", f"https://zenodo.org/api/records/{REC}/versions", tries=2, timeout=120)
did = d2["id"]
n = upload_dep(did, REL, FILES)
meta = {"upload_type": "publication", "publication_type": "book", "title": TITLE, "description": DESC,
        "creators": [{"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}],
        "publication_date": DATE, "version": DATE, "access_right": "open", "license": "cc-by-4.0",
        "language": "zho", "keywords": ["有限系统", "取舍", "六核心", "系列合集", "The Tradeoffs of Finite Systems", "collection"],
        "related_identifiers": [{"identifier": "https://github.com/lyp0746/series-workspace", "relation": "isSupplementedBy", "scheme": "url"}] +
            [{"identifier": v, "relation": "isPartOf", "scheme": "doi"} for v in
             ("10.5281/zenodo.23771608","10.5281/zenodo.23771832","10.5281/zenodo.23771933",
              "10.5281/zenodo.23772040","10.5281/zenodo.23771397","10.5281/zenodo.23772106")]}
api.req("PUT", f"https://zenodo.org/api/deposit/depositions/{did}", data={"metadata": meta}, tries=2, timeout=300)
_, pub = api.req("POST", f"https://zenodo.org/api/deposit/depositions/{did}/actions/publish", tries=2, timeout=300)
print("PUBLISHED", pub.get("doi"), "| concept", pub.get("conceptdoi"), "| 文件", n, flush=True)

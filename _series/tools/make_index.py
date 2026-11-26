# -*- coding: utf-8 -*-
"""总导览：把 26 件放进一张 2D 卡片墙（不做 3D——二维能读清就不用 3D）。
数据全部现场读：各仓 interactive/*.html 是否存在、体积；论文总账 126 条；粗码 39 章。"""
import glob, io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOOKS = [("knowledge-tradeoffs","只能选两样","通俗读本"),("capacity-cascade","遗忘的边界","学术专著"),
         ("emergence-critical","涌现的临界","学术专著"),("entropy-spiral","错位的时间","学术专著"),
         ("interpretation-tradeoff","诠释的权衡","学术专著"),("impossibility-triangle","选择的代价","学术专著"),
         ("distinction-evolution","区分的语言","学术专著"),("mind-forks","心灵的分岔","通俗读本"),
         ("hotspot-bills","热点的账单","通俗读本")]
PAPERS = [("ComputingDemystified","术语的账单"),("WorldPeriodization","谁在切时间轴"),
          ("SleepingResidue","线外的残余"),("HunanRelaySystem","明清湘中驿道"),
          ("BureauRotationCession","轮换的让渡"),("HarnessEcology","被点燃的生态"),
          ("OptimizationBoundary","优化的边界"),("CapacityProxies","容量的三个代理"),
          ("DomainCrossSection","领域的剖面"),("IsomorphismStrength","同构的强度"),
          ("MemoryAnchor","记忆的锚点"),("MemoryStressTest","锚点的下限"),
          ("MonarchCompetition","开明君主与两层竞争"),("SeamLedger","接缝不在奇点"),
          ("LedgerReconciliation","六张账单的对账")]
TRI = {"knowledge-tradeoffs","impossibility-triangle"}

def kb(p):
    return os.path.getsize(p)//1024 if os.path.exists(p) else 0

def card(repo, title, kind, note):
    rd = os.path.join(ROOT, repo, "interactive", f"{repo}-reader.html")
    ex = os.path.join(ROOT, repo, "interactive", f"{repo}-explorer.html")
    if repo == "resolution-grain":
        ex = os.path.join(ROOT, repo, "assets", "knowledge-map.html")
    btns = []
    if os.path.exists(rd): btns.append(f'<a class="b1" href="{repo}-reader.html">阅读页 →</a>')
    if os.path.exists(ex): btns.append(f'<a class="b2" href="{repo}-explorer.html">结构/台账 →</a>')
    sb = '<span class="tag tri">含复算沙盘</span>' if repo in TRI or repo=="resolution-grain" else ""
    return (f'<div class="card" data-k="{kind}"><div class="k">{kind}</div>'
            f'<h3>{title}</h3><div class="m">{note}　·　{max(kb(rd),0)} KB {sb}</div>'
            f'<div class="acts">{"".join(btns)}</div></div>')

def main():
    rows = []
    for repo,title,kind in BOOKS:
        n = len(glob.glob(os.path.join(ROOT,repo,"source","ch*.html")))
        rows.append(card(repo,title,kind,f"{n} 章"))
    for repo,title in PAPERS:
        rows.append(card(repo,title,"工作论文","总账对账"))
    rows.append(card("resolution-grain","粗码","集大成","39 章 · 8 部 · 25 行登记 + 27 条否证线"))
    rows.append('<div class="card" data-k="合集"><div class="k">合集</div><h3>二十四件合集</h3>'
                '<div class="m">9 卷 + 15 篇 · 印刷/电子/EPUB</div>'
                '<div class="acts"><a class="b2" href="合集-explorer.html">结构地图 →</a></div></div>')
    css = """
:root{--ink:#1f3b57;--alt:#b5651d;--line:#e2dccd;--paper:#fbfaf7;--wash:#faf8f3}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:#1c1c1c;
font:15px/1.7 "Noto Sans SC","Microsoft YaHei",sans-serif}
header{padding:34px 30px 10px}h1{font-size:26px;margin:0 0 6px;color:var(--ink)}
.sub{color:#6b6255;font-size:13px;max-width:900px;line-height:1.8}
.stat{display:flex;gap:10px;flex-wrap:wrap;padding:16px 30px 4px}
.stat div{background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px 14px}
.stat b{display:block;font-size:20px;color:var(--ink)}
.stat span{font-size:11.5px;color:#8c8c8c}
h2{font-size:15px;color:var(--ink);margin:26px 30px 8px}
.wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;padding:0 30px 30px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.card .k{font-size:11px;color:var(--alt);letter-spacing:.08em}
.card h3{margin:4px 0 6px;font-size:16px;color:#1c1c1c}
.card .m{font-size:11.5px;color:#8c8c8c;line-height:1.7}
.acts{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap}
.acts a{font-size:12px;padding:6px 11px;border-radius:999px;text-decoration:none}
.b1{background:var(--ink);color:#fff}.b2{background:var(--wash);color:var(--ink);border:1px solid var(--line)}
.tag{margin-left:6px;font-size:10.5px;padding:1px 6px;border-radius:8px}
.tag.tri{background:#fdf6ec;color:#8a4f14;border:1px solid #e8d4b4}
.help{margin:0 30px;border:1px solid var(--line);border-radius:12px;background:#fff;padding:14px 18px;font-size:13px;color:#4a463d}
.help b{color:var(--ink)}
footer{margin:26px 30px 50px;border:1px solid var(--line);border-radius:12px;background:var(--wash);
padding:14px 18px;font-size:12.5px;color:#4a463d;line-height:1.9}
footer code{background:#fff;border:1px solid var(--line);border-radius:4px;padding:0 4px}
"""
    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>有限系统的取舍 · 全集入口</title>
<style>{css}</style></head><body>
<header><h1>有限系统的取舍 · 全集入口</h1>
<div class="sub">九本专著、十五篇工作论文、《粗码》、二十四件合集——每一件都有两个入口：<b>阅读页</b>（三档＋章末审问卡）与
<b>结构地图/台账</b>（章际引用、附录原表）。全部离线单文件，断网可开。</div></header>
<div class="stat">
 <div><b>25</b><span>件作品（9 书 + 15 论文 + 粗码）</span></div>
 <div><b>126</b><span>论文总账登记的命题</span></div>
 <div><b>25 + 27</b><span>粗码登记行 + 否证线</span></div>
 <div><b>3</b><span>含确定性复算沙盘的件</span></div>
 <div><b>0</b><span>外部依赖 / 服务器 / API</span></div>
</div>
<h2>九本专著</h2><div class="wall">{"".join(rows[:9])}</div>
<h2>十五篇工作论文</h2><div class="wall">{"".join(rows[9:24])}</div>
<h2>《粗码》与《合集》</h2><div class="wall">{"".join(rows[24:])}</div>
<div class="help"><b>三句话说明这套装置。</b>
① 每件阅读页顶部三个档：<b>骨架</b>（只留标题与高亮框，5 分钟刷结构）／<b>阅读</b>（正文全显，表与证据折叠）／<b>全展</b>（全部展开，可用 Ctrl+F 搜全书表格）。
② 三类验证装置：<b>确定性复算沙盘</b>（卷一、选择的代价、粗码——页内按钮可当场把书里的数算出来）／<b>CSV 原表台账</b>（十五篇论文，读 <code>data/</code>）／<b>附录否证对账</b>（书的附录原表，按表号可搜）。
③ 每章末尾一张<b>审问卡</b>：带走一句／打脸条件／证据封顶／动手——四行都是原文摘录；右上角一键复制，粘到自己的 AI 里当严苛伴读。</div>
<footer><b>读法与边界</b><br>
生成脚本：<code>_series/tools/make_reader.py</code>（阅读页）· <code>make_atlas.py</code>（结构地图）· <code>make_index.py</code>（本页）；快照 {SNAP}。<br>
<br>· 这套装置只做**取用**，不做**判断**：所有等级、结论、否证线都是原文，本页一个字未重写。<br>
· 沙盘是说明性装置（C 级）：演示式子怎么动，不预测任何具体行业或结果。<br>
· 折叠与骨架只改"看见多少"，不改"书里写了什么"；任何被收起的内容，在「全展」里都在。</footer>
</body></html>"""
    out = os.path.join(r"C:\\Users\\16103\\Downloads\\李毅芃作品集\\_可视化", "index.html")
    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    print("index.html", len(html)//1024, "KB ->", out)

SNAP = "2026-11-26"
if __name__ == "__main__":
    main()

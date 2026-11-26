# -*- coding: utf-8 -*-
"""为一件作品生成单文件「结构化地图」（零依赖 3D，视觉语言与《粗码》knowledge-map 同源）。

同一份引擎，三种输入：
  book 模式   九本书：章际引用 3D 螺旋 ＋ 部×部 3D 柱阵 ＋ 附录台账
  grain 模式  《粗码》：同上（复用已发布的 knowledge-map 数据源）
  coll 模式   合集：25 件 3D 螺旋（阅读顺序即轨道）＋ 部×部 3D 柱阵 ＋ 总表

铁律（与全系列一致）：
  1) 同源：只读 source/*.json、source/*.html、data/*（不手填任何数字）；
  2) 只摆字段：位置＝真实字段（书序／篇序／部），大小＝度数或序，颜色＝部或体裁；
  3) 每张图带「不能主张什么」；等级写在页脚，不写在每句话上。

用法：
  "$PY" _series/tools/make_atlas.py knowledge-tradeoffs ...
  "$PY" _series/tools/make_atlas.py --all
  "$PY" _series/tools/make_atlas.py --coll
产出：
  <repo>/assets/<slug>-explorer.html        （书：assets/；合集：合集/）
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAP = "2026-11-26"

BOOKS = ["knowledge-tradeoffs", "capacity-cascade", "emergence-critical", "entropy-spiral",
         "interpretation-tradeoff", "impossibility-triangle", "distinction-evolution",
         "mind-forks", "hotspot-bills"]

# 部色带：从墨蓝到赭石的六级，压低饱和度，避免七个颜色互抢
PALETTE = ["#1f3b57", "#2f5677", "#4a7ba6", "#8fa8bd", "#b5651d", "#c08a4e", "#9c6b3f"]

TAG = re.compile(r"<[^>]+>")


def txt(s: str) -> str:
    s = TAG.sub("", s)
    s = html.unescape(s).replace("\u3000", " ")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- 一本书的数据
def load_parts(repo: str):
    d = json.load(open(os.path.join(ROOT, repo, "source", "parts.json"), encoding="utf-8"))
    parts, chapters = [], []
    for pi, part in enumerate(d):
        pname = txt(part.get("part", "")) or f"第{pi + 1}部分"
        chs = []
        for c in part.get("chapters", []):
            ch = {"no": int(c["no"]), "title": txt(c.get("title", "")),
                  "file": c.get("file", ""), "part": pi, "partName": pname,
                  "written": bool(c.get("written", True)),
                  "sections": [txt(s) for s in c.get("sections", [])]}
            chs.append(ch["no"]); chapters.append(ch)
        parts.append({"i": pi, "name": pname, "desc": txt(part.get("desc", "")), "chapters": chs})
    chapters.sort(key=lambda c: c["no"])
    return parts, chapters


def load_edges(repo: str, chapters):
    """章际交叉引用：正文里指向别章的「第N章」与「§N.M」。"""
    idx = {c["no"]: c for c in chapters}
    out = {}
    for c in chapters:
        p = os.path.join(ROOT, repo, "source", c["file"])
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        targets = set()
        for m in re.finditer(r"第\s?(\d+)\s?章", t):
            n = int(m.group(1))
            if n in idx and n != c["no"]:
                targets.add(n)
        for m in re.finditer(r"§\s?(\d+)\.(\d+)", t):
            n = int(m.group(1))
            if n in idx and n != c["no"]:
                targets.add(n)
        for n in targets:
            out[(c["no"], n)] = out.get((c["no"], n), 0) + 1
        c["out"] = len(targets)
    indeg = {c["no"]: 0 for c in chapters}
    for (a, b) in out:
        indeg[b] += 1
    for c in chapters:
        c["deg"] = indeg[c["no"]] + c["out"]
        c["indeg"] = indeg[c["no"]]
    edges = [{"a": a, "b": b, "w": w,
              "cross": idx[a]["part"] != idx[b]["part"]} for (a, b), w in out.items()]
    edges.sort(key=lambda e: (-e["w"], e["a"], e["b"]))
    return edges, sum(out.values())


def load_tables(repo: str):
    """全部带 caption 的表：编号、标题、所在章/附录、表头、行。"""
    out = []
    src = os.path.join(ROOT, repo, "source")
    for fn in sorted(os.listdir(src)):
        if not fn.endswith(".html"):
            continue
        t = open(os.path.join(src, fn), encoding="utf-8").read()
        where = chapter_label(fn)
        for m in re.finditer(r"<table[^>]*>(.*?)</table>", t, re.S):
            block = m.group(1)
            cap = re.search(r"<caption[^>]*>(.*?)</caption>", block, re.S)
            if not cap:
                continue
            caption = txt(cap.group(1))
            num = re.match(r"(表\s?[A-Z]?[\d.]+)", caption)
            head = []
            th = re.search(r"<thead>(.*?)</thead>", block, re.S)
            if th:
                head = [txt(x) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", th.group(1))]
            body = re.search(r"<tbody>(.*?)</tbody>", block, re.S)
            rows = []
            if body:
                for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body.group(1), re.S):
                    cells = [txt(x) for x in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr)]
                    if any(cells):
                        rows.append(cells)
            out.append({"n": num.group(1).replace(" ", "") if num else "",
                        "cap": re.sub(r"^表\s?[A-Z]?[\d.]+\s*", "", caption),
                        "where": where, "head": head, "rows": rows})
    return out


def chapter_label(fn: str) -> str:
    m = re.match(r"ch(\d+)\.html", fn)
    if m:
        return f"第{int(m.group(1))}章"
    m = re.match(r"appendix_([a-f])\.html", fn)
    if m:
        return f"附录 {m.group(1).upper()}"
    m = re.match(r"front_(\w+)\.html", fn)
    if m:
        return "前言/前置"
    m = re.match(r"back_(\w+)\.html", fn)
    if m:
        return "后置"
    return fn


def load_figs(repo: str):
    """SVG 内联成缩略图（单文件可带走）；PNG 只列清单（体积太大）。"""
    import base64
    import glob as _glob
    a = os.path.join(ROOT, repo, "assets")
    svg, budget = [], 3.2 * 1024 * 1024
    import xml.etree.ElementTree as _ET
    for p in sorted(_glob.glob(os.path.join(a, "svg", "*.svg"))):
        raw = open(p, "rb").read()
        try:
            _ET.fromstring(raw)     # 只内联合法 XML：浏览器 <img> 按严格 XML 解析
        except Exception:
            svg.append({"n": os.path.basename(p), "d": None, "b": len(raw),
                        "bad": True})
            continue
        if len(raw) > 220 * 1024 or budget - len(raw) * 1.34 < 0:
            svg.append({"n": os.path.basename(p), "d": None, "b": len(raw)})
            continue
        budget -= len(raw) * 1.34
        svg.append({"n": os.path.basename(p),
                    "d": "data:image/svg+xml;base64," + base64.b64encode(raw).decode(),
                    "b": len(raw)})
    png = [{"n": os.path.basename(p), "b": os.path.getsize(p)}
           for p in sorted(_glob.glob(os.path.join(a, "charts", "*.png")))]
    return svg, png


def book_payload(repo: str):
    parts, chapters = load_parts(repo)
    edges, mentions = load_edges(repo, chapters)
    tables = load_tables(repo)
    svg, png = load_figs(repo)
    title = book_title(repo)
    n_unwritten = sum(1 for c in chapters if not c.get("written", True))
    payload = {
        "mode": "book",
        "slug": repo, "title": title["title"], "sub": title["sub"],
        "parts": parts,
        "nodes": [{"no": c["no"], "t": c["title"], "p": c["part"], "d": c["deg"],
                   "i": c["indeg"], "o": c["out"],
                   "s": [s.split("　")[0] if "　" in s else s for s in c["sections"]][:20],
                   "secs": len(c["sections"])} for c in chapters],
        "edges": edges,
        "tables": tables,
        "figs": {"svg": svg, "png": png},
        "meta": {"chapters": len(chapters), "parts": len(parts), "edges": len(edges),
                 "mentions": mentions, "pairs": len(edges),
                 "tables": len(tables), "svg": len(svg), "png": len(png),
                 "svg_inline": sum(1 for x in svg if x["d"]),
                 "sections": sum(len(c["sections"]) for c in chapters),
                 "unwritten": n_unwritten},
    }
    return payload


def book_title(repo: str):
    """书名/副题：优先 source/book.json，其次 合集 的 VOLUMES。"""
    p = os.path.join(ROOT, repo, "source", "book.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf-8"))
            return {"title": d.get("title", repo), "sub": d.get("subtitle", "")}
        except Exception:
            pass
    v = collection_meta()
    for m in v:
        if m["repo"] == repo:
            return {"title": m["title"], "sub": m["sub"]}
    return {"title": repo, "sub": ""}


# ---------------------------------------------------------------- 合集
def collection_meta():
    """从 合集/build_collection.py 直接读元数据（唯一来源，不另抄一份）。"""
    p = os.path.join(ROOT, "合集", "build_collection.py")
    src = open(p, encoding="utf-8").read()
    vols = []
    blk = re.search(r"VOLUMES = \[(.*?)\n\]", src, re.S).group(1)
    for m in re.finditer(r'\("([\w\-.]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]*)",\s*"([^"]*)"', blk):
        vols.append({"repo": m.group(1), "no": m.group(2), "title": m.group(3),
                     "sub": m.group(4), "one": m.group(5), "kind": "书"})
    papers = []
    blk = re.search(r"PAPERS = \[(.*?)\n\]", src, re.S).group(1)
    for m in re.finditer(r'\("([\w\-.]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)"', blk):
        papers.append({"repo": m.group(1), "no": m.group(2), "title": m.group(3),
                       "sub": m.group(4), "core": m.group(5), "kind": m.group(6),
                       "md": m.group(7), "doi": m.group(8)})
    return vols + papers


def coll_payload():
    items = collection_meta()
    # 四部：九卷 / 实证（一—六）/ 方法（七—十三）/ 跨域十四 / 总账十五
    parts = [
        {"i": 0, "name": "第一部　九卷（专著）", "chapters": []},
        {"i": 1, "name": "第二部　实证（一—六）", "chapters": []},
        {"i": 2, "name": "第三部　方法（七—十三）", "chapters": []},
        {"i": 3, "name": "第四部　跨域（十四）与阶段总账（十五）", "chapters": []},
    ]
    nodes = []
    for k, it in enumerate(items):
        if it["kind"] == "书":
            pi = 0
        elif it["kind"] == "实证":
            pi = 1
        elif it["kind"] == "方法":
            pi = 2
        else:
            pi = 3
        parts[pi]["chapters"].append(k)
        nodes.append({"no": k + 1, "t": it["title"], "sub": it["sub"], "p": pi,
                      "k": it["kind"], "label": it["no"],
                      "core": it.get("core", ""), "doi": it.get("doi", ""),
                      "d": 1, "i": 0, "o": 0, "secs": 0, "s": []})
    # 轨道＝阅读顺序；边＝同部相邻（只画阅读链，不造假引用）
    edges = [{"a": k + 1, "b": k + 2, "w": 1, "cross": nodes[k]["p"] != nodes[k + 1]["p"]}
             for k in range(len(nodes) - 1)]
    tables = []
    total_secs = 0
    for it in items:
        p = os.path.join(ROOT, it["repo"])
        if it["kind"] == "书":
            _, chs = load_parts(it["repo"])
            total_secs += sum(len(c["sections"]) for c in chs)
        else:
            md = os.path.join(p, "source", "paper.md")
            if os.path.exists(md):
                total_secs += len(re.findall(r"^##\s", open(md, encoding="utf-8").read(), re.M))
    return {
        "mode": "coll", "slug": "合集", "title": "有限系统的取舍", "sub": "九卷与十五篇：二十四件的位置",
        "parts": parts, "nodes": nodes, "edges": edges, "tables": tables,
        "figs": {"svg": [], "png": []},
        "meta": {"chapters": len(nodes), "parts": len(parts), "edges": len(edges),
                 "mentions": len(edges), "pairs": len(edges),
                 "tables": 0, "svg": 0, "png": 0, "sections": total_secs, "unwritten": 0},
    }


# ---------------------------------------------------------------- 页面
CSS = """
:root{--ink:#1f3b57;--alt:#b5651d;--grey:#8c8c8c;--line:#e2dccd;--wash:#faf8f3;
      --paper:#fbfaf7;--card:#ffffff;--faint:#6b6255}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:#1c1c1c;
  font:14px/1.65 "Noto Sans SC","Microsoft YaHei",-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased}
header{padding:26px 30px 6px}
h1{font-size:21px;margin:0 0 5px;font-weight:600;color:var(--ink);letter-spacing:.2px}
h1 small{font-weight:400;color:var(--faint);font-size:14px;margin-left:8px}
.sub{color:var(--faint);font-size:12.5px;max-width:1000px;line-height:1.75}
.cards{display:flex;gap:10px;flex-wrap:wrap;padding:14px 30px 4px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:9px 14px;min-width:104px}
.card .k{font-size:11px;color:var(--grey);letter-spacing:.06em}
.card .v{font-size:20px;font-weight:600;color:var(--ink);
  font-variant-numeric:tabular-nums;margin-top:1px}
.card .v small{font-size:11.5px;font-weight:400;color:var(--grey);margin-left:3px}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:14px 30px 8px}
.bar button{font:12.5px/1 inherit;padding:7px 13px;border:1px solid var(--line);
  background:#fff;color:#3d3d3d;border-radius:999px;cursor:pointer;transition:.15s}
.bar button:hover{border-color:#c9c0a9}
.bar button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.bar .sep{width:1px;height:18px;background:var(--line);margin:0 6px}
.bar .hint{color:var(--grey);font-size:12px}
.bar .jump{font:12.5px/1 inherit;padding:7px 13px;color:#fff;background:var(--alt);
  border-radius:999px;text-decoration:none;white-space:nowrap}
.bar .jump:hover{filter:brightness(1.08)}
main{padding:0 30px 10px}
.view{display:none} .view.on{display:block}
.stage{display:grid;grid-template-columns:minmax(0,1fr) 232px;gap:16px;align-items:start}
canvas{width:100%;height:620px;display:block;background:#fff;border:1px solid var(--line);
  border-radius:14px;cursor:grab;touch-action:none;
  box-shadow:0 1px 2px rgba(31,59,87,.04),0 8px 24px rgba(31,59,87,.04)}
canvas:active{cursor:grabbing}
aside{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 15px;
  font-size:12.5px;color:#3d3d3d;position:sticky;top:14px}
aside h3{margin:0 0 8px;font-size:12px;letter-spacing:.1em;color:var(--grey);font-weight:600}
.lg{display:flex;align-items:center;gap:7px;margin:5px 0;cursor:pointer;border-radius:6px;padding:2px 4px}
.lg:hover{background:var(--wash)}
.lg i{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
.lg b{font-weight:500}
.lg span{color:var(--grey);margin-left:auto;font-variant-numeric:tabular-nums}
.foot{margin:16px 30px 40px;border:1px solid var(--line);border-radius:12px;background:var(--wash);
  padding:14px 18px;font-size:12.5px;color:#4a463d;line-height:1.85}
.foot b{color:var(--ink)}
.foot .lb{font-size:11px;letter-spacing:.1em;color:var(--grey);text-transform:uppercase;
  display:block;margin:8px 0 2px}
.tip{position:fixed;pointer-events:none;background:#fff;border:1px solid var(--line);
  border-radius:9px;padding:9px 12px;font-size:12.5px;box-shadow:0 8px 26px rgba(31,59,87,.14);
  opacity:0;transition:opacity .12s;max-width:300px;z-index:9;line-height:1.7}
.tip b{color:var(--ink)} .tip em{color:var(--alt);font-style:normal}
.tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0 0 12px}
input[type=search],select{padding:7px 10px;border:1px solid var(--line);border-radius:8px;
  background:#fff;font:12.5px/1 inherit;font-family:inherit}
input[type=search]{min-width:280px}
.ledger{display:grid;grid-template-columns:330px minmax(0,1fr);gap:14px;align-items:start}
.list{background:#fff;border:1px solid var(--line);border-radius:12px;max-height:620px;overflow:auto}
.list .row{padding:8px 12px;border-bottom:1px solid #f0ece1;cursor:pointer;font-size:12.5px}
.list .row:hover{background:var(--wash)} .list .row.on{background:#f6efe0}
.list .row .n{color:var(--alt);font-variant-numeric:tabular-nums;margin-right:7px;font-weight:600}
.list .row .w{color:var(--grey);font-size:11px;margin-left:6px}
.panel{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;
  max-height:620px;overflow:auto}
.panel h2{font-size:15px;margin:0 0 2px;color:var(--ink);font-weight:600}
.panel .meta{color:var(--grey);font-size:11.5px;margin-bottom:10px}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{padding:7px 9px;border-bottom:1px solid #f0ece1;text-align:left;vertical-align:top}
th{background:var(--wash);position:sticky;top:0;color:var(--ink);font-weight:600}
.figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(196px,1fr));gap:10px}
.figs .thumb{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px;
  display:flex;flex-direction:column;gap:5px;overflow:hidden}
.figs .thumb img{width:100%;height:118px;object-fit:contain;background:#fff}
.figs .thumb .cap{font-size:10.5px;color:var(--grey);text-align:center;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.figs .tiny{border-style:dashed;color:#6b6255;font-size:11px;padding:7px 9px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
@media (max-width:980px){.stage,.ledger{grid-template-columns:1fr}aside{position:static}
  canvas{height:460px}}
"""

JS = r"""
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const TIP=$('#tip');
const M=DATA.meta, PARTS=DATA.parts, NODES=DATA.nodes, EDGES=DATA.edges;
let FILTER='all', FILTERV='all';
const PCOL=PARTS.map((p,i)=>PAL[i%PAL.length]);
const MAXD=Math.max(1,...NODES.map(n=>n.d));
const crossOK=e=>e.cross;
function label(n){return DATA.mode==='coll'?n.label:'第'+n.no+'章'}

/* ---------------- 3D 基础：旋转 → 透视 → 自适应取景 ---------------- */
function rot(p,cam){
  const cy=Math.cos(cam.yaw),sy=Math.sin(cam.yaw);
  const x=p[0]*cy-p[2]*sy, z0=p[0]*sy+p[2]*cy;
  const cp=Math.cos(cam.pitch),sp=Math.sin(cam.pitch);
  return [x, p[1]*cp-z0*sp, p[1]*sp+z0*cp];
}
function persp(v){
  /* f 必须远大于场景尺寸（网格可到 ±2.6），否则近处除零、远处爆炸 */
  const f=6.4, d=Math.max(1.2, v[2]+f), k=f/d;
  return [v[0]*k, v[1]*k, v[2]];
}
/* 给定一组 3D 点，算出把全部点框进画布的变换；zoom 是读者的缩放 */
function framing(pts3,cam,W,H,zoom,pad){
  const P=pts3.map(p=>persp(rot(p,cam)));
  let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  P.forEach(p=>{x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);
                y0=Math.min(y0,p[1]);y1=Math.max(y1,p[1]);});
  const w=Math.max(0.001,x1-x0), h=Math.max(0.001,y1-y0);
  const s=Math.min((W-pad*2)/w,(H-pad*2)/h)*zoom;
  const ox=W/2-(x0+x1)/2*s, oy=H/2+(y0+y1)/2*s;
  return v=>[v[0]*s+ox, -v[1]*s+oy, v[2]];
}
"""

# 后续 JS 片段分开写，避免超长字符串里手工找括号
JS_SPIRAL = r"""
/* ---------------- 视图一：3D 螺旋（章际引用） ---------------- */
let cam={yaw:-0.55,pitch:0.46,zoom:1,spin:true,drag:false,px:0,py:0,hover:null};
const cv=$('#cv-spiral'), cx=cv.getContext('2d');
function buildGeo(){
  const N=NODES.length, TURN=19;            /* 一圈约 19 章：与《粗码》那张图同一口径 */
  const R=1.05, HGT=1.30;
  NODES.forEach((n,i)=>{
    const th=2*Math.PI*i/TURN;
    const y=-(i/Math.max(1,N-1)-.5)*HGT;
    n.p3=[Math.cos(th)*R, y, Math.sin(th)*R];
  });
}
function resize(c){
  const r=c.getBoundingClientRect(), dpr=Math.min(2,devicePixelRatio||1);
  c.width=Math.round(r.width*dpr); c.height=Math.round(r.height*dpr);
  const g=c.getContext('2d'); g.setTransform(dpr,0,0,dpr,0,0);
  return [r.width,r.height];
}
function ctrlOf(A,B){
  const m=[(A[0]+B[0])/2,(A[1]+B[1])/2,(A[2]+B[2])/2];
  const rad=Math.hypot(m[0],m[2])||1, k=1.55, r=Math.hypot(m[0],m[2])*k;
  return [m[0]/rad*r, m[1]*0.96, m[2]/rad*r];
}
function framePts(){
  const pts=NODES.map(n=>n.p3);
  EDGES.forEach(e=>{const A=NODES[e.a-1],B=NODES[e.b-1];
    if(A&&B) pts.push(ctrlOf(A.p3,B.p3));});
  return pts;
}
function drawSpiral(){
  const [W,H]=resize(cv); cx.clearRect(0,0,W,H);
  const T=framing(framePts(),cam,W,H,cam.zoom,46);
  const P=NODES.map(n=>T(persp(rot(n.p3,cam))));
  /* 阅读轨道：分段画，近处实、远处虚（深度提示） */
  for(let i=1;i<P.length;i++){
    const a=P[i-1], b=P[i], z=(a[2]+b[2])/2, k=Math.min(1,Math.max(0.12,(1.6-z)/2.4));
    cx.beginPath(); cx.moveTo(a[0],a[1]); cx.lineTo(b[0],b[1]);
    cx.strokeStyle='rgba(120,124,132,'+(0.10+0.22*k).toFixed(3)+')';
    cx.setLineDash([2,5]); cx.lineWidth=0.9+0.7*k; cx.stroke(); cx.setLineDash([]);
  }
  const HI=cam.hover;
  /* 引用弧 */
  const arcs=[];
  EDGES.forEach(e=>{
    if(FILTER==='cross'&&!e.cross) return;
    if(FILTER==='within'&&e.cross) return;
    const A=NODES[e.a-1], B=NODES[e.b-1]; if(!A||!B) return;
    const a=T(persp(rot(A.p3,cam))), b=T(persp(rot(B.p3,cam)));
    const c=T(persp(rot(ctrlOf(A.p3,B.p3),cam)));
    arcs.push({a,b,c,z:(a[2]+b[2]+c[2])/3,e});
  });
  arcs.sort((p,q)=>p.z-q.z);
  arcs.forEach(o=>{
    const on=HI&&(o.e.a===HI.no||o.e.b===HI.no);
    cx.beginPath(); cx.moveTo(o.a[0],o.a[1]);
    cx.quadraticCurveTo(o.c[0],o.c[1],o.b[0],o.b[1]);
    cx.strokeStyle=o.e.cross?RGB.alt:RGB.ink;
    cx.globalAlpha=on?0.85:(o.e.cross?0.26:0.12);
    cx.lineWidth=on?1.6:(o.e.cross?Math.min(2.2,0.8+o.e.w*0.45):0.8);
    cx.stroke();
    /* 箭头：指到被引的那一头 */
    if(on||o.e.cross){
      const t=0.94, x=t*t*o.b[0]+2*t*(1-t)*o.c[0]+(1-t)*(1-t)*o.a[0];
      const y=t*t*o.b[1]+2*t*(1-t)*o.c[1]+(1-t)*(1-t)*o.a[1];
      const ang=Math.atan2(o.b[1]-y,o.b[0]-x), L=on?6:4.4;
      cx.beginPath(); cx.moveTo(o.b[0],o.b[1]);
      cx.lineTo(o.b[0]-L*Math.cos(ang-0.42),o.b[1]-L*Math.sin(ang-0.42));
      cx.lineTo(o.b[0]-L*Math.cos(ang+0.42),o.b[1]-L*Math.sin(ang+0.42));
      cx.closePath(); cx.globalAlpha=on?0.8:(o.e.cross?0.22:0.0);
      cx.fillStyle=o.e.cross?RGB.alt:RGB.ink; cx.fill();
    }
    cx.globalAlpha=1;
  });
  /* 节点 */
  const top5=new Set([...NODES].sort((a,b)=>b.d-a.d).slice(0,5).map(n=>n.no));
  const order=NODES.map((n,i)=>({n,p:P[i]})).sort((a,b)=>a.p[2]-b.p[2]);
  order.forEach(({n,p})=>{
    const near=HI&&(n.no===HI.no||EDGES.some(e=>(e.a===HI.no&&e.b===n.no)||(e.b===HI.no&&e.a===n.no)));
    const dim=HI&&!near;
    const dep=Math.min(1,Math.max(0,(1.9-p[2])/2.6));
    const r=(3.2+5.2*Math.sqrt(n.d/MAXD))*(0.82+0.38*dep);
    if(top5.has(n.no)||near){
      cx.beginPath(); cx.arc(p[0],p[1],r+3.4,0,7);
      cx.fillStyle=PCOL[n.p%PCOL.length]; cx.globalAlpha=dim?0.10:0.16; cx.fill();
    }
    cx.beginPath(); cx.arc(p[0],p[1],r,0,7);
    cx.fillStyle=PCOL[n.p%PCOL.length];
    cx.globalAlpha=dim?0.26:(0.60+0.40*dep); cx.fill();
    cx.lineWidth=1.3; cx.strokeStyle='#fff'; cx.stroke();
    const showLbl=!dim;
    if(showLbl){
      const t2=DATA.mode==='coll'?n.label:'第'+n.no+'章';
      const dx2=p[0]-W/2, dy2=p[1]-H/2, L2=Math.hypot(dx2,dy2)||1, off=r+8;
      const tx=p[0]+dx2/L2*off, ty=p[1]+dy2/L2*off;
      cx.globalAlpha=0.94;
      cx.font=(r>5.4?'600 ':'')+(NODES.length>30?10.5:11.5)+'px "Noto Sans SC",sans-serif';
      cx.textAlign=(dx2>8?'left':(dx2<-8?'right':'center'));
      cx.textBaseline='middle';
      cx.lineWidth=3.6; cx.strokeStyle='rgba(255,255,255,.94)';
      cx.strokeText(t2,tx,ty);
      cx.fillStyle='#243447'; cx.fillText(t2,tx,ty);
    }
    cx.globalAlpha=1;
  });
  const hi=$('#hint');
  if(hi) hi.textContent=cam.spin?'拖动旋转 · 滚轮缩放 · 悬停看章际引用':'已暂停自动旋转（点“自动旋转”继续）';
}
function jumpTo(no){
  if(DATA.mode==='coll') return;
  location.href = DATA.slug + '-reader.html#ch' + no;
}
function nearest(mx0,my0){
  const [W,H]=[cv.clientWidth,cv.clientHeight];
  const T=framing(framePts(),cam,W,H,cam.zoom,46);
  let best=null,bd=16;
  NODES.forEach(n=>{const p=T(persp(rot(n.p3,cam)));
    const d=Math.hypot(p[0]-mx0,p[1]-my0);
    if(d<bd){bd=d;best={n,p};}});
  return best;
}
"""

JS_MATRIX = r"""
/* ---------------- 视图二：部×部 3D 地形（阶梯面） ---------------- */
let mcam={yaw:-0.60,pitch:0.42,zoom:1,drag:false,px:0,py:0,hover:null};
const mv=$('#cv-matrix'), mx=mv.getContext('2d');
let MAT=null, MVMAX=1;
function buildMatrix(){
  const P=PARTS.length, m=[];
  for(let i=0;i<P;i++) m.push(new Array(P).fill(0));
  EDGES.forEach(e=>{const a=NODES[e.a-1],b=NODES[e.b-1]; if(a&&b) m[a.p][b.p]+=e.w;});
  MAT=m; MVMAX=Math.max(1,...m.flat());
}
function cells(){
  const P=MAT.length, gap=0.06, out=[];
  for(let i=0;i<P;i++)for(let j=0;j<P;j++){
    const v=MAT[i][j];
    out.push({i,j,v,h:0.05+(v/MVMAX)*1.05,
      x0:(i-P/2+0.5),z0:(j-P/2+0.5),s:(1-gap)/2});
  }
  return out;
}
function drawMatrix(){
  const [W,H]=resize(mv); mx.clearRect(0,0,W,H);
  const P=MAT.length, half=P/2, CS=cells();
  /* 取景：把全部柱体的顶角与底角都算进去 */
  const ext=[];
  CS.forEach(c=>{
    [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([a,b])=>{
      ext.push([c.x0+a*c.s,0,c.z0+b*c.s]);
      ext.push([c.x0+a*c.s,c.h,c.z0+b*c.s]);
    });
  });
  const T=framing(ext,mcam,W,H,mcam.zoom,78);
  const pr=p=>T(persp(rot(p,mcam)));
  /* 底座网格 */
  mx.strokeStyle='rgba(31,59,87,.09)'; mx.lineWidth=1;
  for(let k=0;k<=P;k++){
    const x=-half+k;
    let a=pr([x,0,-half]), b=pr([x,0,half]);
    mx.beginPath(); mx.moveTo(a[0],a[1]); mx.lineTo(b[0],b[1]); mx.stroke();
    a=pr([-half,0,x]); b=pr([half,0,x]);
    mx.beginPath(); mx.moveTo(a[0],a[1]); mx.lineTo(b[0],b[1]); mx.stroke();
  }
  /* 空单元：只留一层极薄的底片（不铺板，避免把“没有”画成“有”） */
  CS.filter(c=>c.v===0).forEach(c=>{
    const q=[[c.x0-c.s,0,c.z0-c.s],[c.x0+c.s,0,c.z0-c.s],
             [c.x0+c.s,0,c.z0+c.s],[c.x0-c.s,0,c.z0+c.s]].map(pr);
    mx.beginPath(); mx.moveTo(q[0][0],q[0][1]);
    for(let k=1;k<4;k++) mx.lineTo(q[k][0],q[k][1]);
    mx.closePath(); mx.fillStyle='rgba(31,59,87,.03)'; mx.fill();
    mx.strokeStyle='rgba(31,59,87,.10)'; mx.lineWidth=.7; mx.stroke();
  });
  /* 有值的单元：按深度画（画家算法） */
  const faces=[];
  CS.filter(c=>c.v>0).forEach(c=>{
    const {x0,z0,s,h}=c;
    const v=[[x0-s,0,z0-s],[x0+s,0,z0-s],[x0+s,0,z0+s],[x0-s,0,z0+s]].map(pr);
    const w=[[x0-s,h,z0-s],[x0+s,h,z0-s],[x0+s,h,z0+s],[x0-s,h,z0+s]].map(pr);
    [[w[0],w[1],w[2],w[3],1.0],[v[0],v[1],w[1],w[0],0.70],
     [v[1],v[2],w[2],w[1],0.82],[v[2],v[3],w[3],w[2],0.70],
     [v[3],v[0],w[0],w[3],0.82]].forEach(q=>{
      faces.push({q:q.slice(0,4),shade:q[4],
        z:q.slice(0,4).reduce((a,p)=>a+p[2],0)/4,c});
    });
  });
  faces.sort((a,b)=>a.z-b.z);
  const HI=mcam.hover;
  faces.forEach(f=>{
    const {c}=f, on=HI&&HI.i===c.i&&HI.j===c.j;
    const base=(c.i===c.j)?'31,59,87':'181,101,29';
    const inten=c.v/MVMAX;
    mx.beginPath(); mx.moveTo(f.q[0][0],f.q[0][1]);
    for(let k=1;k<4;k++) mx.lineTo(f.q[k][0],f.q[k][1]);
    mx.closePath();
    mx.fillStyle='rgba('+base+','+(on?0.94:(0.22+0.42*f.shade+0.28*inten)).toFixed(3)+')';
    mx.fill();
    mx.strokeStyle='rgba(255,255,255,.5)'; mx.lineWidth=.6; mx.stroke();
  });
  CS.filter(c=>c.v>0).forEach(c=>{
    const p=pr([c.x0,c.h+0.02,c.z0]);
    mx.font='600 11px "Noto Sans SC",sans-serif'; mx.textAlign='center';
    mx.fillStyle=(c.i===c.j)?'#1f3b57':'#8a4f14'; mx.globalAlpha=.95;
    mx.fillText(c.v,p[0],p[1]+3.5); mx.globalAlpha=1;
  });
  /* 轴标：只写序号（一…五），部名放到右侧图例里——避免长名互相压 */
  const CN=['一','二','三','四','五','六','七','八','九'];
  mx.font='600 12px "Noto Sans SC",sans-serif'; mx.fillStyle='#6b6255';
  PARTS.forEach((p,i)=>{
    const a=pr([(i-P/2+0.5),0,half+0.40]);
    mx.textAlign='center'; mx.fillText(CN[i],a[0],a[1]+4);
    const b=pr([-half-0.40,0,(i-P/2+0.5)]);
    mx.textAlign='right'; mx.fillText(CN[i],b[0]-2,b[1]+4);
  });
  mx.textAlign='left'; mx.font='11px "Noto Sans SC",sans-serif'; mx.fillStyle='#8c8c8c';
  mx.fillText('→ 横向：被引的一方　　纵深：引用的一方　　↑ 高：条数',30,26);
}
function hitMatrix(mx0,my0){
  const [W,H]=[mv.clientWidth,mv.clientHeight];
  const P=MAT.length, half=P/2, CS=cells(), ext=[];
  CS.forEach(c=>{[[-1,-1],[1,-1],[1,1],[-1,1]].forEach(([a,b])=>{
    ext.push([c.x0+a*c.s,0,c.z0+b*c.s]); ext.push([c.x0+a*c.s,c.h,c.z0+b*c.s]);});});
  const T=framing(ext,mcam,W,H,mcam.zoom,78);
  let best=null,bd=40;
  CS.forEach(c=>{
    const p=T(persp(rot([c.x0,c.h,c.z0],mcam)));
    const d=Math.hypot(p[0]-mx0,p[1]-my0);
    if(d<bd){bd=d;best={i:c.i,j:c.j};}
  });
  return best;
}
"""

JS_LEDGER = r"""
/* ---------------- 视图三：附录台账 ---------------- */
let TABLES=DATA.tables||[], curT=-1, q='';
function renderList(){
  const box=$('#tlist'); box.innerHTML='';
  const list=TABLES.map((t,i)=>({t,i})).filter(({t})=>
    !q|| (t.n+t.cap+t.where+t.rows.flat().join(' ')).toLowerCase().includes(q.toLowerCase()));
  $('#tcount').textContent=list.length+' 张';
  list.forEach(({t,i})=>{
    const d=document.createElement('div');
    d.className='row'+(i===curT?' on':'');
    d.innerHTML='<span class="n">'+(t.n||'表')+'</span>'+esc(t.cap)+
      '<span class="w">'+esc(t.where)+' · '+t.rows.length+' 行</span>';
    d.onclick=()=>{curT=i;renderList();renderPanel();};
    box.appendChild(d);
  });
  if(curT<0&&list.length){curT=list[0].i;renderList();renderPanel();}
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function renderPanel(){
  const t=TABLES[curT]; if(!t) return;
  const h=['<h2>'+esc(t.n||'表')+'　'+esc(t.cap)+'</h2>',
    '<div class="meta">'+esc(t.where)+' · '+t.rows.length+' 行 · 数据直接取自正文表格，未重算</div>',
    '<table><thead><tr>'];
  (t.head.length?t.head:['—']).forEach(x=>h.push('<th>'+esc(x)+'</th>'));
  h.push('</tr></thead><tbody>');
  t.rows.forEach(r=>{h.push('<tr>');r.forEach(c=>h.push('<td>'+esc(c)+'</td>'));h.push('</tr>');});
  h.push('</tbody></table>');
  $('#tpanel').innerHTML=h.join('');
}
"""

JS_FIGS = r"""
/* ---------------- 视图四：图件账（SVG 缩略图内联，PNG 列清单） ---------------- */
function renderFigs(){
  const f=DATA.figs||{svg:[],png:[]};
  const box=$('#figbox'); box.innerHTML='';
  f.svg.forEach(x=>{
    const d=document.createElement('div'); d.className='thumb';
    if(x.d){
      const im=document.createElement('img'); im.src=x.d; im.alt=x.n; im.loading='lazy';
      d.appendChild(im);
      const c=document.createElement('span'); c.className='cap';
      c.textContent=x.n.replace(/\.svg$/,''); d.appendChild(c);
    }else{
      d.className='thumb tiny';
      d.textContent='▱ '+x.n+(x.bad?'　（SVG 解析失败，未内联）':'');
    }
    box.appendChild(d);
  });
  const nb=$('#pngbox'); if(!nb) return; nb.innerHTML='';
  f.png.forEach(x=>{
    const d=document.createElement('div'); d.className='thumb tiny';
    d.textContent='▣ '+x.n+'　'+(x.b/1024).toFixed(0)+' KB';
    nb.appendChild(d);
  });
  const fc=$('#figcount');
  if(fc) fc.textContent=f.svg.length+' SVG（内联 '+f.svg.filter(x=>x.d).length+
    '）· '+f.png.length+' PNG（只列清单）';
}
"""

JS_MAIN = r"""
/* ---------------- 切换与交互 ---------------- */
function setView(v){
  $$('.view').forEach(x=>x.classList.toggle('on',x.id==='v-'+v));
  $$('[data-v]').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  if(v==='spiral') drawSpiral();
  if(v==='matrix') drawMatrix();
  if(v==='ledger') renderList();
  if(v==='figs') renderFigs();
}
function bindDrag(cv,cam,draw){
  cv.addEventListener('pointerdown',e=>{cam.drag=true;cam.spin=false;cam.px=e.clientX;cam.py=e.clientY;
    cv.setPointerCapture(e.pointerId);});
  cv.addEventListener('pointerup',e=>{cam.drag=false;});
  if(cv.id==='cv-spiral'){
    cv.addEventListener('click',e=>{
      if(Math.abs(e.clientX-(cv._dx||0))>4) return;
      const r=cv.getBoundingClientRect(); const h=nearest(e.clientX-r.left,e.clientY-r.top);
      if(h) jumpTo(h.n.no);
    });
    cv.addEventListener('pointerdown',e=>{cv._dx=e.clientX;});
  }
  cv.addEventListener('pointermove',e=>{
    if(cam.drag){
      cam.yaw+=(e.clientX-cam.px)*0.008;
      cam.pitch=Math.max(-1.2,Math.min(1.2,cam.pitch+(e.clientY-cam.py)*0.006));
      cam.px=e.clientX;cam.py=e.clientY;draw();
    }else{
      const r=cv.getBoundingClientRect();
      hoverAt(cv,cam,e.clientX-r.left,e.clientY-r.top,draw);
    }
  });
  cv.addEventListener('pointerleave',()=>{TIP.style.opacity=0;cam.hover=null;draw();});
  cv.addEventListener('wheel',e=>{e.preventDefault();
    cam.zoom=Math.max(0.55,Math.min(2.4,cam.zoom*(e.deltaY<0?1.08:0.93)));draw();},{passive:false});
}
function hoverAt(cv,cam,mx0,my0,draw){
  const box=cv.getBoundingClientRect();
  if(cv.id==='cv-spiral'){
    const h=nearest(mx0,my0);
    if(h){
      const n=h.n; cam.hover=n;
      TIP.innerHTML='<b>'+esc(label(n))+'　'+esc(n.t)+'</b><br>'+
        '<em>'+esc(PARTS[n.p].name)+'</em><br>'+
        '被引 <b>'+n.i+'</b> · 引出 <b>'+n.o+'</b> · 合计 '+n.d+
        (n.secs?(' · '+n.secs+' 节'):'')+
        (n.core?('<br>'+esc(n.core)):'')+
        (n.sub?('<br><span style="color:#8c8c8c">'+esc(n.sub)+'</span>'):'');
      TIP.style.opacity=1;
      TIP.style.left=Math.min(innerWidth-330,h.p[0]+box.left+16)+'px';
      TIP.style.top=Math.max(8,h.p[1]+box.top-6)+'px';
    }else{TIP.style.opacity=0;cam.hover=null;}
    draw();
  }else if(cv.id==='cv-matrix'){
    const b=hitMatrix(mx0,my0);
    if(b){mcam.hover=b;
      TIP.innerHTML='<b>'+esc(PARTS[b.i].name)+'</b> → <b>'+esc(PARTS[b.j].name)+'</b><br>'+
        '<em>'+MAT[b.i][b.j]+' 条</em>'+(b.i===b.j?'（部内互引）':'（跨部）');
      TIP.style.opacity=1;
      TIP.style.left=Math.min(innerWidth-390,mx0+box.left+16)+'px';
      TIP.style.top=(my0+box.top-6)+'px';
    }else{TIP.style.opacity=0;mcam.hover=null;}
    draw();
  }
}
function tick(){
  if(cam.spin&&$('#v-spiral').classList.contains('on')){cam.yaw+=0.0022;drawSpiral();}
  requestAnimationFrame(tick);
}
window.addEventListener('resize',()=>{drawSpiral();drawMatrix();});
document.addEventListener('DOMContentLoaded',()=>{
  buildGeo(); buildMatrix();
  bindDrag(cv,cam,drawSpiral); bindDrag(mv,mcam,drawMatrix);
  $$('[data-v]').forEach(b=>b.onclick=()=>setView(b.dataset.v));
  $$('[data-f]').forEach(b=>b.onclick=()=>{
    FILTERV=b.dataset.f; $$('[data-f]').forEach(x=>x.classList.toggle('on',x===b));
    FILTER=FILTERV; drawSpiral();
  });
  $('#spin').onclick=()=>{cam.spin=!cam.spin; $('#spin').classList.toggle('on',cam.spin);};
  const qEl=$('#q'); if(qEl) qEl.oninput=e=>{q=e.target.value; renderList();};
  const pk=$('#pkey'), CN2=['一','二','三','四','五','六','七'];
  if(pk) PARTS.forEach((p,i)=>{
    const d=document.createElement('div');
    d.innerHTML='<b>'+CN2[i]+'</b>　'+esc(p.name.replace(/^第.部分[　 ]?/,''))+
      '<span style="color:#8c8c8c">（'+p.chapters.length+'）</span>';
    pk.appendChild(d);
  });
  const leg=$('#legend');
  PARTS.forEach((p,i)=>{
    const n=NODES.filter(x=>x.p===i).length;
    const d=document.createElement('div'); d.className='lg';
    d.innerHTML='<i style="background:'+PCOL[i%PCOL.length]+'"></i><b>'+esc(p.name)+'</b><span>'+n+'</span>';
    leg.appendChild(d);
  });
  setView('spiral'); tick();
});
"""


def build_html(d: dict) -> str:
    m = d["meta"]
    is_coll = d["mode"] == "coll"
    if is_coll:
        cards = [("件", m["chapters"], ""), ("部", m["parts"], ""),
                 ("轨道", m["edges"], "段"), ("书", 9, ""), ("论文", 15, "")]
    else:
        cards = [("节点", m["chapters"], "章"), ("部", m["parts"], ""),
                 ("引用", m["mentions"], "条"), ("章对", m["pairs"], "对"),
                 ("节", m["sections"], ""), ("表", m["tables"], ""),
                 ("图件", m["svg"] + m["png"], "件")]
    card_html = "".join(
        f'<div class="card"><div class="k">{k}</div><div class="v">{v}<small>{u}</small></div></div>'
        for k, v, u in cards)
    views = ["spiral", "matrix", "ledger", "figs"] if not is_coll else ["spiral", "matrix"]
    names = {"spiral": "章际引用 · 3D 螺旋", "matrix": "部 × 部 · 3D 柱阵",
             "ledger": "附录台账", "figs": "图件账"}
    if is_coll:
        names["spiral"] = "二十四件 · 3D 螺旋"
    nav = "".join(f'<button data-v="{v}">{names[v]}</button>' for v in views)

    # 记录数：正文交叉引用
    src_line = ("来源：<code>合集/build_collection.py</code> 的 VOLUMES 与 PAPERS（部、序、题、体裁、核心、DOI）"
                if is_coll else
                "来源：<code>source/parts.json</code>（部与章）· <code>source/ch*.html</code>（正文交叉引用与节）· "
                "<code>source/appendix_*.html</code>（表）· <code>assets/</code>（图件）")

    legend = ""
    led = ('<aside><h3>%s</h3><div id="legend"></div>' % ("四部（九卷＋十五篇）" if is_coll else "部与章数") +
           '<h3 style="margin-top:14px">怎么读</h3>'
           '<div style="color:#6b6255;font-size:12px;line-height:1.8">'
           + ('螺旋＝阅读顺序（虚线＝轨道，23 段）；颜色＝所属部（四部）；点等大——这一页不编度数。'
              '柱阵的高＝部与部之间的阅读衔接数。'
              if is_coll else
              '螺旋＝阅读顺序（虚线＝轨道）；点的大小＝引用度数；颜色＝所属部。'
              '柱阵的高＝部与部之间的引用条数，对角线是部内互引。') +
           '</div></aside>')
    body_matrix_hint = ("<p class='sub' style='padding:0 0 8px'>"
                        "高＝引用条数；对角＝部内互引。拖动旋转，悬停看具体一格。</p>")

    if is_coll:
        bounds = [
            ("数据", "件数、部属、体裁、核心、DOI 全部取自 <code>合集/build_collection.py</code>；节数为各仓 <code>source/</code> 实测。"),
            ("等级", "A（结构与元数据，可重跑）／C（“位置说明什么”是本书的读法）。"),
            ("不能主张什么", "① 螺旋上的先后是阅读顺序，不是重要性顺序；② 点的大小是引用度数，"
                            "不是分量；③ 四部是编排，不是分类学；④ 同一核心不等于同一结论。"),
        ]
    else:
        bounds = [
            ("数据", src_line.replace("`","\u0001").replace("\u0001", "</code>", 1) + "" if False else src_line + "。全部由 <code>_series/tools/make_atlas.py</code> 现场统计，未手填一个数字。"),
            ("等级", "A（部与章、引用计数、表目——可算可重跑）／C（“度数说明什么”是读法，不是测量）。"),
            ("不能主张什么", "① 被引多不等于这一章重要，只说明它被别的章点名多；② 跨部引用多不等于部与部"
                            "关系深，只说明写的时候互相指路多；③ 部是作者编排，不是发现；"
                            "④ 台账里每一行是正文原表，本页不重算、不解释，要读解释请回原文。"),
            ("快照", "2026-11-26 的 <code>source/</code>；改稿后重跑本页，数字会变。"),
        ]
    foot = "".join(f"<span class='lb'>{k}</span><div>{v}</div>" for k, v in bounds)

    figs_view = ""
    if not is_coll:
        figs_view = ('<div class="view" id="v-figs"><div class="tools">'
                     '<span class="hint" id="figcount"></span></div>'
                     '<div class="figs" id="figbox"></div>'
                     '<div class="tools" style="margin-top:14px"><span class="hint" id="pnghint">'
                     'PNG 版图件（体积大，未内联）</span></div>'
                     '<div class="figs" id="pngbox"></div></div>')

    ledger_view = ('<div class="view" id="v-ledger">'
                   '<div class="tools"><input type="search" id="q" placeholder="搜表号、标题、所在章、单元格……">'
                   '<span class="hint" id="tcount"></span></div>'
                   '<div class="ledger"><div class="list" id="tlist"></div>'
                   '<div class="panel" id="tpanel"></div></div></div>'
                   if d["tables"] else
                   '<div class="view" id="v-ledger"><div class="panel">'
                   '这一件没有附录表格；表目见正文各章。'
                   '</div></div>')

    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{d['title']} · 结构化地图</title>
<style>{CSS}</style></head><body>
<header>
  <h1>{d['title']}<small>{d['sub']}</small></h1>
  <div class="sub">{'二十四件在同一张桌上看：位置＝阅读顺序，颜色＝部，虚线＝轨道。' if is_coll else
    '这一页只有一件事：把这本书的<b>结构</b>摊开——章与章互相指了多少次、部分与部分之间怎么连、附录里登记了什么。'
    '每一个数字都从 <code>source/</code> 现场数出来，不手填。'}</div>
</header>
<div class="cards">{card_html}</div>
<div class="bar">{nav}
  <span class="sep"></span>
  <button data-f="all" class="on">全部引用</button>
  <button data-f="cross">只看跨部</button>
  <button data-f="within">只看部内</button>
  <span class="sep"></span>
  <button id="spin" class="on">自动旋转</button>
  <a class="jump" href="{d['slug']}-reader.html">正文阅读页 →</a>
  <span class="hint" id="hint"></span>
</div>
<main>
  <div class="view on" id="v-spiral">
    <div class="stage"><canvas id="cv-spiral"></canvas>{led}</div>
  </div>
  <div class="view" id="v-matrix">
    {body_matrix_hint}
    <div class="stage"><canvas id="cv-matrix"></canvas>
      <aside><h3>坐标</h3><div id="pkey" style="font-size:12px;line-height:1.95;color:#4a463d"></div>
      <h3 style="margin-top:12px">读法</h3><div style="color:#6b6255;font-size:12px;line-height:1.8">
      横向＝被引的一方，纵深＝引用的一方，高＝条数；对角线（深蓝）＝部内互引，赭石＝跨部。
      <b>高是条数，不是强度。</b></div></aside></div>
  </div>
  {ledger_view}
  {figs_view}
</main>
<div class="foot"><b>读法与边界</b>{foot}</div>
<div class="tip" id="tip"></div>
<script>
const DATA={json.dumps({k: d[k] for k in ('mode', 'slug', 'title', 'sub', 'parts', 'nodes', 'edges', 'tables', 'figs', 'meta')}, ensure_ascii=False)};
const PAL={json.dumps(PALETTE)};
const RGB={{"ink":"rgba(31,59,87,1)","alt":"rgba(181,101,29,1)"}};
{JS}{JS_SPIRAL}{JS_MATRIX}{JS_LEDGER}{JS_FIGS}{JS_MAIN}
</script>
</body></html>
"""


def write(repo: str, name: str, html_text: str):
    base = os.path.join(ROOT, repo)
    if repo == "合集":
        out = os.path.join(base, name)
    else:
        out = os.path.join(base, "interactive", name)   # 与阅读页同目录：两页互跳才能用相对链接
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(html_text)
    print(f"  {repo}/{os.path.relpath(out, base)}  {len(html_text) / 1024:.0f} KB")


def main(argv):
    targets = []
    if "--all" in argv or not argv:
        targets = [("book", b) for b in BOOKS]
    elif "--coll" in argv:
        targets = [("coll", "合集")]
    else:
        targets = [("book", a) for a in argv if a in BOOKS]
    for mode, repo in targets:
        d = coll_payload() if mode == "coll" else book_payload(repo)
        name = f"{repo}-explorer.html"
        write(repo, name, build_html(d))
        m = d["meta"]
        print(f"   → {m['chapters']} 节点 / {m['parts']} 部 / {m['edges']} 边 / {m['tables']} 表")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

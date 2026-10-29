# -*- coding: utf-8 -*-
"""交互页生成器：data/schemes.csv → interactive/periodization-explorer.html

纪律：
  * 只读一份 CSV（编码库），页面内嵌 JSON，单文件可离线打开；
  * 筛选（传统 / 范围 / 区域 / 世纪）+ 搜索 + 点行看详情，四件事，不做仪表盘；
  * 页脚写明数据来源、编码规则与边界；
  * 无数据时显示空状态。
运行：python analysis/build_explorer.py
"""
import csv
import json
import os
import sys

CONFIG = {
    "title": "门的数目 · 边界年浏览器",
    "subtitle": "60 部来源（核心 46、扩展 14）、252 条边界，逐条可查。"
                "左表筛选，点行看详情；数据与论文图 1—17 同源；NA 表示来源未印出年份。",
    "csv": "data/schemes.csv",
    "out": "interactive/periodization-explorer.html",
    "filters": ["tradition", "scope", "region", "era", "century"],
    "search": ["source", "period_name", "note"],
    "table": ["source", "boundary_year", "period_name"],
    "detail": ["tradition", "scope", "region", "era", "level", "year_published", "note"],
    "footer": "数据：<code>data/schemes.csv</code>（60 部来源、252 条边界；核心 46 部的 195 条落在 400—2000 窗内，扩展 14 部含 22 条无年份边界）。"
              "编码规则见 docs/codebook.md：边界年只记来源明确写出的年份，未写出记 NA，不推断；"
              "多边界分别记录；维基只作补充。"
              "边界：本页只呈现来源的分区位置，不评价哪个分期正确；不复制原文。",
}

TRAD_CN = {"european": "欧洲中心", "global": "全球史", "china": "中国教材", "other": "补充",
           "premodern_europe": "前现代欧洲", "islamic": "伊斯兰", "african": "非洲",
           "south_asian": "南亚", "east_asian_premodern": "东亚（前现代）", "americas": "美洲"}
SCOPE_CN = {"world": "世界", "region": "区域", "nation": "国别"}
ERA_CN = {"ancient": "古代", "medieval": "中世纪", "early_modern": "近代早期",
          "modern": "近代/现代", "contemporary": "当代", "sacred": "圣史"}
LEVEL_CN = {"part": "顶层分区", "chapter": "章级分区"}

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--red:#b3261e;--blue:#1f4e79;--green:#2e6b4f;--gray:#5f6368;--bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font-family:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","SimSun",serif}
header{padding:22px 5vw 12px;border-bottom:2px solid var(--red);background:#fff}
header>*{max-width:1220px;margin-left:auto;margin-right:auto}
h1{margin:0 0 6px;font-size:22px;letter-spacing:.01em}
.sub{color:#555;font-size:13px;line-height:1.7;max-width:70em}
.wrap{padding:14px 5vw 48px;max-width:1220px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(104px,1fr));gap:10px;margin:12px 0}
.card{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:10px 11px}
.card .k{font-size:11.5px;color:#666}.card .v{font-size:20px;font-weight:700;margin-top:2px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:#fff;
     border:1px solid #e3e0d8;border-radius:6px;padding:10px;margin:4px 0 12px;font-size:13px}
select,input[type=search]{padding:5px 8px;border:1px solid #ccc;border-radius:4px;
     background:#fff;font-size:13px;font-family:inherit;max-width:100%}
input[type=search]{min-width:170px;flex:1 1 170px}
.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:14px;align-items:start}
@media (max-width:900px){
  .grid{grid-template-columns:1fr}
  header{padding:18px 4vw 10px} h1{font-size:19px}
  .wrap{padding:12px 4vw 40px}
  .detail{position:static;order:-1;min-height:auto}
}
.tblbox{overflow:auto;max-height:72vh;border:1px solid #e3e0d8;border-radius:6px;background:#fff}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:7px 8px;border-bottom:1px solid #e8e5dd;text-align:left;vertical-align:top}
th{background:#efece4;position:sticky;top:0;z-index:2;font-size:12px}
tbody tr{cursor:pointer}
tbody tr:hover td{background:#fbf8f1}
tbody tr.sel td{background:#f6efe0}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;color:#fff;background:var(--gray)}
.detail{background:#fff;border:1px solid #e3e0d8;border-radius:8px;padding:15px;
        position:sticky;top:12px;min-height:230px}
.detail h2{margin:0 0 4px;font-size:17px;line-height:1.45}
.detail .row{margin:8px 0}
.detail .k{font-size:11px;color:#999;letter-spacing:.05em}
.detail .v{font-size:13.5px;line-height:1.7;margin-top:1px}
.note{font-size:12px;color:#666;line-height:1.9;margin-top:16px;border-top:1px solid #e3e0d8;padding-top:12px}
.hint{font-size:12.5px;color:#888;line-height:1.8}
.empty{padding:38px;text-align:center;color:#999}
@media (max-width:480px){
  th,td{padding:6px;font-size:12.5px}
  th:last-child,td:last-child{display:none}
  .detail h2{font-size:15.5px}
  .bar select{flex:1 1 44%}
}
</style></head><body>
<header><h1>__TITLE__</h1><div class="sub">__SUBTITLE__</div></header>
<div class="wrap">
  <div class="cards" id="cards"></div>
  <div class="bar" id="bar"></div>
  <div class="grid">
    <div class="tblbox">
      <table><thead id="thead"></thead><tbody id="tbody"></tbody></table>
    </div>
    <div class="detail" id="detail"><div class="hint">点左侧任意一行，查看该条边界所属的来源、传统、范围与编码备注。</div></div>
  </div>
  <div class="note">__FOOTER__</div>
</div>
<script>
const DATA = __DATA__;
const ROWS = DATA.rows, COLS = DATA.cols;
const state = {q: "", sel: null, f: {}};
COLS.filters.forEach(k => state.f[k] = "");

function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

function init(){
  document.getElementById("thead").innerHTML = "<tr>" +
    COLS.table.map(c => `<th>${esc(COLS.head[c] || c)}</th>`).join("") +
    `<th>${esc(COLS.head.tradition)}</th></tr>`;
  const bar = document.getElementById("bar");
  COLS.filters.forEach(k=>{
    const vals = [...new Set(ROWS.map(r=>r[k]).filter(v=>v!=null && v!==""))]
      .sort((a,b)=> (k==="century" ? (+a - +b) : String(a).localeCompare(String(b),"zh")));
    const sel = document.createElement("select");
    sel.innerHTML = `<option value="">${esc(COLS.head[k] || k)}：全部</option>` +
      vals.map(v=>`<option value="${esc(v)}">${esc(COLS.label[k] ? (COLS.label[k][v] || v) : v)}</option>`).join("");
    sel.onchange = e => { state.f[k] = e.target.value; render(); };
    bar.appendChild(sel);
  });
  const q = document.createElement("input");
  q.type = "search"; q.placeholder = "搜索来源 / 时期名 / 备注";
  q.oninput = e => { state.q = e.target.value.toLowerCase(); render(); };
  bar.appendChild(q);
}

function filtered(){
  const q = state.q;
  return ROWS.filter(r =>
    COLS.filters.every(k => !state.f[k] || String(r[k]) === state.f[k]) &&
    (!q || COLS.search.some(k => String(r[k]||"").toLowerCase().includes(q))));
}

function median(a){
  if(!a.length) return "—";
  const s=[...a].sort((x,y)=>x-y), m=Math.floor(s.length/2);
  return s.length%2 ? s[m] : Math.round((s[m-1]+s[m])/2);
}

function render(){
  const f = filtered();
  const years = f.map(r=>{const y=r.boundary_year; return (y===""||y==null)?NaN:+y;}).filter(v=>!isNaN(v));
  const srcs = new Set(f.map(r=>r.source));
  document.getElementById("cards").innerHTML = [
    ["当前边界", f.length],
    ["涉及来源", srcs.size],
    ["边界年中位", median(years)]
  ].map(([k,v])=>`<div class="card"><div class="k">${esc(k)}</div><div class="v">${esc(v)}</div></div>`).join("");
  const tb = document.getElementById("tbody");
  if (!f.length){
    tb.innerHTML = `<tr><td colspan="${COLS.table.length+1}"><div class="empty">没有符合条件的记录。清空筛选或换一个关键词。</div></td></tr>`;
    return;
  }
  tb.innerHTML = f.map(r=>{
    const i = ROWS.indexOf(r);
    return `<tr data-i="${i}" class="${i===state.sel?"sel":""}">` +
      COLS.table.map(c=>`<td class="${c==="boundary_year"?"num":""}">${c==="boundary_year"?(r[c]===""||r[c]==null?"NA":esc(r[c])):esc(r[c])}</td>`).join("") +
      `<td><span class="tag" style="background:${COLS.color[r.tradition]||"#777"}">${esc(COLS.label.tradition[r.tradition]||r.tradition)}</span></td>` +
      `</tr>`;
  }).join("");
  [...tb.querySelectorAll("tr")].forEach(tr=>tr.onclick=()=>show(+tr.dataset.i));
}

function show(i){
  state.sel = i; const r = ROWS[i];
  document.getElementById("detail").innerHTML =
    `<h2>${esc(r.period_name || "（未印出时期名）")}</h2>` +
    `<div class="row"><div class="k">边界年</div><div class="v" style="font-size:19px;font-weight:700">${r.boundary_year===""||r.boundary_year==null?"NA":esc(r.boundary_year)}</div></div>` +
    COLS.detail.map(k=>`<div class="row"><div class="k">${esc(COLS.head[k]||k)}</div>` +
      `<div class="v">${esc(COLS.label[k] ? (COLS.label[k][r[k]]||r[k]) : r[k]) || "—"}</div></div>`).join("") +
    `<div class="row"><div class="k">来源</div><div class="v">${esc(r.source)}</div></div>`;
  render();
}

init(); render();
</script></body></html>
"""


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, CONFIG["csv"])
    if not os.path.exists(csv_path):
        print("缺数据：%s（先建编码库，跑 analysis/make_figures.py）" % CONFIG["csv"])
        return 0
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    if not rows:
        print("CSV 为空：%s" % CONFIG["csv"])
        return 0
    for r in rows:
        y = r.get("boundary_year")
        try:
            r["century"] = str((int(y) // 100) * 100)
        except (TypeError, ValueError):
            r["century"] = "NA"
    cols = {
        "filters": CONFIG["filters"], "search": CONFIG["search"],
        "table": CONFIG["table"], "detail": CONFIG["detail"],
        "head": {"source": "来源", "boundary_year": "边界年", "period_name": "时期名",
                 "tradition": "传统", "scope": "范围", "region": "区域", "era": "时代",
                 "level": "分区层级", "year_published": "版次", "note": "备注",
                 "century": "世纪"},
        "label": {"tradition": TRAD_CN, "scope": SCOPE_CN, "era": ERA_CN,
                  "level": LEVEL_CN},
        "color": {"european": "#b3261e", "global": "#1f4e79", "china": "#2e6b4f",
                  "other": "#8a8a8a", "premodern_europe": "#7a5c3e",
                  "islamic": "#a8791f", "african": "#6b4c9a",
                  "south_asian": "#b5651d", "east_asian_premodern": "#3f6d6d",
                  "americas": "#8a3b5c"},
    }
    html = (HTML.replace("__TITLE__", CONFIG["title"])
                .replace("__SUBTITLE__", CONFIG["subtitle"])
                .replace("__FOOTER__", CONFIG["footer"])
                .replace("__DATA__", json.dumps({"rows": rows, "cols": cols},
                                                ensure_ascii=False)))
    out = os.path.join(base, CONFIG["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("   %s  (%d 行, %.1f KB)" % (CONFIG["out"], len(rows), os.path.getsize(out) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())

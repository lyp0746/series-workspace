# -*- coding: utf-8 -*-
"""Self-contained interactive explorer for the Hunan paper.

    python analysis/make_interactive.py -> interactive/hunan-explorer.html

Three tabs: network (SVG map), toponyms (scatter + jackknife), cost (sliders + histogram).
No CDN; opens offline.
"""
import csv
import json
import os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "interactive")
os.makedirs(OUT, exist_ok=True)

nodes = list(csv.DictReader(open(os.path.join(BASE, "stations.csv"), encoding="utf-8-sig")))
for n in nodes:
    n["lat"] = float(n["lat"]); n["lon"] = float(n["lon"])
    n["conf"] = n["confidence"]
gis = json.load(open(os.path.join(DATA, "gis_stats.json"), encoding="utf-8"))
rob = json.load(open(os.path.join(DATA, "robustness.json"), encoding="utf-8"))

# cost samples for histogram
rng = np.random.default_rng(20261021)
land = rng.uniform(25, 35, 20000); water = rng.uniform(8, 15, 20000); allland = rng.uniform(50, 70, 20000)
save = (1 - (land + water) / allland) * 100
hist, edges = np.histogram(save, bins=30, range=(0, 60))
cost = {"mean": float(save.mean()), "p5": float(np.percentile(save, 5)),
        "p95": float(np.percentile(save, 95)), "hist": hist.tolist(),
        "edges": edges.tolist()}

payload = {"nodes": nodes, "gis": gis, "top": rob["toponym"], "cost": cost,
           "lines": {"北": "北线（官驿）", "西": "西线（黑茶）", "东": "东线（花炮）", "南": "南线（矿产）"},
           "colors": {"北": "#b3261e", "西": "#1f4e79", "东": "#2e6b4f", "南": "#a8791f"}}

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>湘中驿道 · 交互探索器</title>
<style>
:root{--red:#b3261e;--blue:#1f4e79;--green:#2e6b4f;--gold:#a8791f;--bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Han Serif SC","Songti SC","SimSun",serif}
header{padding:26px 6vw 16px;background:#fff;border-bottom:2px solid var(--red)}
h1{margin:0 0 6px;font-size:25px}.sub{color:#555;font-size:13.5px}
.wrap{max-width:1180px;margin:0 auto;padding:18px 6vw 60px}
.tabs{display:flex;gap:8px;margin:16px 0}
.tab{padding:7px 14px;border:1px solid #ddd;border-radius:20px;background:#fff;cursor:pointer;font-size:13.5px}
.tab.on{background:var(--red);color:#fff;border-color:var(--red)}
.panel{display:none}.panel.on{display:block}
.bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:10px;margin:8px 0 14px}
label{font-size:13px}select{padding:4px 8px;border:1px solid #ccc;border-radius:4px;background:#fff}
.pill{display:inline-flex;gap:5px;align-items:center;border:1px solid #ddd;border-radius:16px;padding:3px 8px;font-size:12.5px;cursor:pointer}
svg{width:100%;background:#fff;border:1px solid #e3e0d8;border-radius:6px}
table{width:100%;border-collapse:collapse;background:#fff;font-size:12.5px}
th,td{padding:6px 7px;border-bottom:1px solid #eee;text-align:left}th{background:#efece4}
.note{font-size:12px;color:#666;line-height:1.7;margin-top:14px}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:10px 0}
.k div{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:12px}
.k b{display:block;font-size:22px;margin-top:4px}
input[type=range]{width:180px}
</style></head><body>
<header><h1>湘中驿道 · 交互探索器</h1>
<div class="sub">28 个关键节点 · 六县地名截面 · 成本区间抽样。数字为 B/C 级估计，只作方向。</div></header>
<div class="wrap">
<div class="tabs">
 <div class="tab on" data-t="net">网络</div><div class="tab" data-t="top">地名</div><div class="tab" data-t="cost">成本</div>
</div>

<div class="panel on" id="net">
 <div class="bar">
  <label>线路 <select id="route"><option value="">全部</option></select></label>
  <span id="conf"></span>
 </div>
 <svg id="map" viewBox="0 0 760 620"></svg>
 <div class="k" id="netk"></div>
 <table id="nettbl"><thead><tr><th>线</th><th>节点</th><th>段数</th><th>平均 km</th><th>中位 km</th><th>总长 km</th></tr></thead><tbody></tbody></table>
</div>

<div class="panel" id="top">
 <svg id="scatter" viewBox="0 0 760 380"></svg>
 <div class="k" id="topk"></div>
 <svg id="jack" viewBox="0 0 760 260"></svg>
 <div class="note">斜率随剔除单县在 −0.73 到 −1.29 之间；95% CI −1.95—0.17，包含 0。方向为负、强度不足。</div>
</div>

<div class="panel" id="cost">
 <div class="bar">
  <label>陆运 <span id="lv">30</span> 两/吨<br><input type="range" id="land" min="20" max="40" value="30"></label>
  <label>水运 <span id="wv">11</span> 两/吨<br><input type="range" id="water" min="6" max="18" value="11"></label>
  <label>全陆路 <span id="av">60</span> 两/吨<br><input type="range" id="all" min="45" max="75" value="60"></label>
  <div style="font-size:15px">节省 <b id="save">32.5%</b></div>
 </div>
 <svg id="hist" viewBox="0 0 760 300"></svg>
 <div class="note">区间抽样：均值 30.2%，90% 区间 14.2—44.1，P(>25%)=0.72。滑杆只做即时演示，不替代文献运价。</div>
</div>

<div class="note">
 <b>来源。</b>节点：<code>stations.csv</code>；网络统计：<code>analysis/gis_pilot.py</code>；地名与成本：<code>analysis/robustness.py</code>。
 图 8、图 9 与表 11、表 12 见论文第 4.9 节。
</div>
</div>
<script>
const D = __DATA__;
const L = D.lines, C = D.colors;
const $ = s => document.querySelector(s);

// tabs
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  t.classList.add('on'); $('#'+t.dataset.t).classList.add('on');
});

// ---------- network ----------
const LAT0=28.2, LON0=113.0;
const proj = n => [ (n.lon-LON0)*111.32*Math.cos(LAT0*Math.PI/180), (n.lat-LAT0)*110.57 ];
const ROUTES = {"北":["长沙总铺","黄花铺","永安铺","枫浆桥铺","蕉溪铺","浏阳总铺","北盛铺","乌龙铺","沙市铺","龙伏铺","社港铺"],
 "西":["玉潭铺","双凫铺","黄材铺"],"东":["浏阳总铺","大瑶铺","金刚铺","上栗驿"],"南":["飞羊铺","中路铺","衡州"]};
$('#route').innerHTML += Object.keys(L).map(r=>`<option value="${r}">${L[r]}</option>`).join('');
let confSet = new Set(["A","B","C"]);
$('#conf').innerHTML = ["A","B","C"].map(c=>`<label class="pill"><input type="checkbox" checked value="${c}">${c} 级</label>`).join(' ');
document.querySelectorAll('#conf input').forEach(cb=>cb.onchange=()=>{
  cb.checked?confSet.add(cb.value):confSet.delete(cb.value); drawMap();
});
$('#route').onchange = drawMap;

function drawMap(){
  const sel = $('#route').value;
  const rows = D.nodes.filter(n=>confSet.has(n.conf[0]) && (!sel || n.route===sel));
  const by = Object.fromEntries(rows.map(n=>[n.name,n]));
  const pts = rows.map(proj);
  const xs = pts.map(p=>p[0]), ys = pts.map(p=>p[1]);
  const minx=Math.min(...xs)-15, maxx=Math.max(...xs)+15, miny=Math.min(...ys)-15, maxy=Math.max(...ys)+15;
  const W=760,H=620,pad=30;
  const sx = x => pad + (x-minx)/(maxx-minx)*(W-2*pad);
  const sy = y => H-pad - (y-miny)/(maxy-miny)*(H-2*pad);
  let s = '';
  Object.entries(ROUTES).forEach(([r,seq])=>{
    if(sel && r!==sel) return;
    const line = seq.map(n=>by[n]).filter(Boolean).map(proj);
    if(line.length>1) s += `<polyline points="${line.map(p=>sx(p[0])+','+sy(p[1])).join(' ')}" fill="none" stroke="${C[r]}" stroke-width="2" opacity=".55"/>`;
  });
  rows.forEach(n=>{
    const [x,y]=proj(n); const r = n.conf[0]==='A'?5:(n.conf[0]==='B'?4:3.5);
    s += `<circle cx="${sx(x)}" cy="${sy(y)}" r="${r}" fill="${C[n.route]}" stroke="#fff" stroke-width="1"><title>${n.name}｜${n.modern_town}｜${n.route}线｜${n.conf}</title></circle>`;
    if(n.conf[0]==='A') s += `<text x="${sx(x)+6}" y="${sy(y)-5}" font-size="10" fill="#333" paint-order="stroke" stroke="#fff" stroke-width="3">${n.name}</text>`;
  });
  $('#map').innerHTML = s;
  const byr = D.gis.by_route;
  $('#netk').innerHTML = Object.entries(L).filter(([r])=>!sel||r===sel).map(([r,cn])=>
    `<div>${cn}<b>${byr[r].mean_km.toFixed(1)} km</b><span style="font-size:11px;color:#666">均值 · ${byr[r].n_nodes} 节点</span></div>`).join('');
  $('#nettbl tbody').innerHTML = Object.entries(L).filter(([r])=>!sel||r===sel).map(([r,cn])=>{
    const v=byr[r]; return `<tr><td>${cn}</td><td>${v.n_nodes}</td><td>${v.n_segments}</td><td>${v.mean_km.toFixed(1)}</td><td>${v.median_km.toFixed(1)}</td><td>${v.length_km.toFixed(1)}</td></tr>`;
  }).join('');
}
drawMap();

// ---------- toponym ----------
const TOP = [["宁乡",9,95],["长沙县",0,52],["浏阳",33,18],["湘潭",34,55],["茶陵",0,72],["衡州",70,11]];
function drawTop(){
  const W=760,H=380,pad=50;
  const sx=t=>pad+t/75*(W-2*pad), sy=v=>H-pad-v/100*(H-2*pad);
  let s=`<line x1="${pad}" y1="${H-pad}" x2="${W-pad}" y2="${H-pad}" stroke="#999"/>`;
  s+=`<line x1="${pad}" y1="${pad}" x2="${pad}" y2="${H-pad}" stroke="#999"/>`;
  for(let t=0;t<=70;t+=10){ s+=`<text x="${sx(t)}" y="${H-pad+16}" font-size="10" text-anchor="middle" fill="#666">${t}</text>`; }
  for(let v=0;v<=100;v+=20){ s+=`<text x="${pad-8}" y="${sy(v)+4}" font-size="10" text-anchor="end" fill="#666">${v}</text>`;}
  const b=D.top; // slope, intercept
  s+=`<line x1="${sx(0)}" y1="${sy(b.intercept)}" x2="${sx(75)}" y2="${sy(b.intercept+b.slope*75)}" stroke="#b3261e" stroke-width="2"/>`;
  TOP.forEach(([n,t,v])=>{ s+=`<circle cx="${sx(t)}" cy="${sy(v)}" r="6" fill="#1f4e79" stroke="#fff"><title>${n}</title></circle><text x="${sx(t)+8}" y="${sy(v)-6}" font-size="10.5">${n}</text>`; });
  $('#scatter').innerHTML = s;
  $('#topk').innerHTML = `<div>斜率<b>${b.slope.toFixed(2)}</b><span style="font-size:11px;color:#666">95% CI ${b.ci[0].toFixed(2)}—${b.ci[1].toFixed(2)}</span></div>
    <div>R²<b>${b.r2.toFixed(2)}</b></div><div>Spearman ρ<b>${b.spearman_rho.toFixed(2)}</b><span style="font-size:11px;color:#666">p=${b.spearman_p.toFixed(2)}</span></div>`;
  // jackknife
  const J=b.jackknife, W2=760,H2=260, p2=40;
  const names=J.map(x=>x.dropped).concat(["全样本"]), vals=J.map(x=>x.slope).concat([b.slope]);
  const min=Math.min(...vals)-.2, max=0.1;
  let js='';
  vals.forEach((v,i)=>{
    const y=p2+i*(H2-2*p2)/(vals.length-1);
    const x=p2+(v-min)/(max-min)*(W2-2*p2);
    js+=`<line x1="${p2}" y1="${y}" x2="${x}" y2="${y}" stroke="#ccc"/>`;
    js+=`<circle cx="${x}" cy="${y}" r="4" fill="${i===vals.length-1?'#b3261e':'#5f6368'}"/><text x="${p2+4}" y="${y-5}" font-size="10">${names[i]}</text><text x="${x+6}" y="${y+4}" font-size="10">${v.toFixed(2)}</text>`;
  });
  js+=`<line x1="${p2+(0-min)/(max-min)*(W2-2*p2)}" y1="${p2-10}" x2="${p2+(0-min)/(max-min)*(W2-2*p2)}" y2="${H2-p2}" stroke="#999" stroke-dasharray="4"/>`;
  $('#jack').innerHTML = js;
}
drawTop();

// ---------- cost ----------
function drawCost(){
  const land=+$('#land').value, water=+$('#water').value, all=+$('#all').value;
  $('#lv').textContent=land; $('#wv').textContent=water; $('#av').textContent=all;
  const s=(1-(land+water)/all)*100; $('#save').textContent=s.toFixed(1)+'%';
  const H=D.cost, W=760,Hh=300,pad=45, maxv=Math.max(...H.hist)*1.1;
  let sv=`<line x1="${pad}" y1="${Hh-pad}" x2="${W-pad}" y2="${Hh-pad}" stroke="#999"/>`;
  H.hist.forEach((v,i)=>{
    const x=pad+i*(W-2*pad)/H.hist.length, h=(Hh-2*pad)*v/maxv;
    sv+=`<rect x="${x}" y="${Hh-pad-h}" width="${(W-2*pad)/H.hist.length-1}" height="${h}" fill="#a8791f" opacity=".8"/>`;
  });
  const ex=(s-H.edges[0])/(H.edges[H.edges.length-1]-H.edges[0]);
  sv+=`<line x1="${pad+ex*(W-2*pad)}" y1="${pad}" x2="${pad+ex*(W-2*pad)}" y2="${Hh-pad}" stroke="#b3261e" stroke-width="2"/>`;
  for(let e=0;e<=60;e+=10){ const x=pad+e/60*(W-2*pad); sv+=`<text x="${x}" y="${Hh-pad+16}" font-size="10" text-anchor="middle" fill="#666">${e}%</text>`; }
  $('#hist').innerHTML=sv;
}
['land','water','all'].forEach(id=>$('#'+id).oninput=drawCost);
drawCost();
</script></body></html>"""

html = HTML.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
open(os.path.join(OUT, "hunan-explorer.html"), "w", encoding="utf-8").write(html)
print("wrote", len(html))

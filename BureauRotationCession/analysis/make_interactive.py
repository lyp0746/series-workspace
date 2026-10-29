# -*- coding: utf-8 -*-
"""Build a self-contained interactive explorer for the Tang–Song control sample.

    python analysis/make_interactive.py  ->  interactive/control-explorer.html

No CDN: data, CSS and JS are inlined, so the file opens offline.
"""
import csv
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "interactive")
os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open(os.path.join(DATA, "control_tangsong.csv"), encoding="utf-8-sig")))
res = json.load(open(os.path.join(DATA, "control_results.json"), encoding="utf-8"))

LINE = {"inner": "内廷", "outer": "外派", "military": "军职", "regular": "正官"}
COL = {"inner": "#b3261e", "outer": "#1f4e79", "military": "#2e6b4f", "regular": "#5f6368"}
KIND = {"割据": "割据", "虚化": "虚化/禁戒", "正官化": "正官化", "禁戒": "虚化/禁戒", "降格": "虚化/禁戒", "": "无变化"}

data = []
for r in rows:
    data.append({
        "id": r["id"], "dyn": r["dynasty"], "office": r["office"],
        "line": r["line"], "line_cn": LINE[r["line"]], "rank": r["rank"],
        "start": int(r["start"]), "end": int(r["end"]),
        "event": int(r["event"]), "year": int(r["first_event"]) if r["first_event"] else None,
        "type": r["event_type"], "kind": KIND.get(r["event_type"], "无变化"),
        "note": r["note"], "grade": r["grade"],
    })

payload = {
    "rows": data,
    "summary": {
        "n": res["n"], "events": res["events"],
        "irr": round(res["irr_outer_inner"], 2),
        "irr_lo": round(res["irr_ci"][0], 2), "irr_hi": round(res["irr_ci"][1], 2),
        "logrank_p": round(res["logrank_p"], 3),
        "sec_outer": res["secession_table"][0][0], "outer_n": res["secession_table"][0][0] + res["secession_table"][0][1],
        "sec_inner": res["secession_table"][1][0], "inner_n": res["secession_table"][1][0] + res["secession_table"][1][1],
        "sec_p": round(res["secession_fisher_p"], 3),
    },
    "lines": LINE, "colors": COL,
}

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>唐宋官职类型 · 对照样本探索器</title>
<style>
:root{--red:#b3261e;--blue:#1f4e79;--green:#2e6b4f;--gray:#5f6368;--bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","SimSun",serif}
header{padding:28px 6vw 18px;border-bottom:2px solid var(--red);background:#fff}
h1{margin:0 0 6px;font-size:26px}
.sub{color:#555;font-size:14px}
.wrap{padding:22px 6vw 60px;max-width:1200px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}
.card{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:14px}
.card .k{font-size:12px;color:#666}.card .v{font-size:24px;font-weight:700;margin-top:4px}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:12px;margin:8px 0 18px}
select,label{font-size:13px}
select{padding:5px 8px;border:1px solid #ccc;border-radius:4px;background:#fff}
.pill{display:inline-flex;align-items:center;gap:6px;padding:4px 8px;border:1px solid #ddd;border-radius:20px;cursor:pointer;background:#fafafa}
.pill input{accent-color:var(--red)}
h2{font-size:17px;margin:26px 0 8px}
#chart{width:100%;height:260px}
table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}
th,td{padding:7px 8px;border-bottom:1px solid #e8e5dd;text-align:left;vertical-align:top}
th{background:#efece4;cursor:pointer;position:sticky;top:0}
tr:hover td{background:#fbf8f1}
.tag{display:inline-block;padding:1px 6px;border-radius:10px;font-size:11px;color:#fff}
.note{font-size:12px;color:#666;line-height:1.7;margin-top:16px}
.legend{font-size:12px;color:#444;display:flex;gap:14px;flex-wrap:wrap;margin:6px 0}
.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px}
</style></head><body>
<header>
  <h1>唐宋官职类型 · 对照样本探索器</h1>
  <div class="sub">67 个官职类型，24 次性质变化；按线、朝代与结局筛选。编码为探索性（B/C），不是定论。</div>
</header>
<div class="wrap">
  <div class="cards" id="cards"></div>
  <div class="bar">
    <label>朝代 <select id="dyn"><option value="">全部</option><option>唐</option><option>宋</option></select></label>
    <label>结局 <select id="kind"><option value="">全部</option><option>割据</option><option>虚化/禁戒</option><option>正官化</option><option>无变化</option></select></label>
    <span id="lines"></span>
  </div>
  <h2>结局构成</h2>
  <div class="legend" id="legend"></div>
  <svg id="chart" viewBox="0 0 720 260" preserveAspectRatio="xMidYMid meet"></svg>
  <h2>逐条记录</h2>
  <table id="tbl"><thead><tr>
    <th data-k="office">官职</th><th data-k="dyn">朝代</th><th data-k="line_cn">线</th>
    <th data-k="start">始</th><th data-k="end">终</th><th data-k="year">变化年</th>
    <th data-k="kind">结局</th><th data-k="note">备注</th><th data-k="grade">等级</th>
  </tr></thead><tbody></tbody></table>
  <div class="note">
    <b>读法。</b>“任何变化”的发生率：外派/内廷 IRR=__IRR__（95% CI __IRLO__—__IRHI__），log-rank p=__LRP__；
    说明两条线<strong>变化的概率</strong>没有显著差异。“结局构成”则显示：割据只出现在外派（__SECOUT__/__OUTN__ 对 __SECIN__/__INN__，Fisher p=__SECP__），
    虚化/禁戒集中于内廷。因此路径预测的是<strong>失败形态</strong>，不是<strong>变化概率</strong>。<br>
    <b>边界。</b>类型级样本，非每一次任命；事件年份取正史与制度史通行系年；未控制品级与朝代；样本小，只作方向。数据：<code>data/control_tangsong.csv</code>。
  </div>
</div>
<script>
const DATA = __DATA__;
const rows = DATA.rows, S = DATA.summary, LINE = DATA.lines, COL = DATA.colors;
let state = {dyn:"", kind:"", lines:new Set(Object.keys(LINE)), sortK:"office", asc:true};

function filtered(){
  return rows.filter(r => (!state.dyn || r.dyn===state.dyn) && (!state.kind || r.kind===state.kind) && state.lines.has(r.line));
}
function cards(){
  const f = filtered();
  const ev = f.filter(r=>r.event).length;
  const sec = f.filter(r=>r.kind==="割据").length;
  document.getElementById("cards").innerHTML = [
    ["筛选后类型", f.length], ["其中发生变化", ev], ["其中割据", sec],
    ["全样本 IRR（外派/内廷）", S.irr + " (" + S.irr_lo + "—" + S.irr_hi + ")"],
    ["割据 Fisher p", S.sec_p]
  ].map(([k,v])=>`<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`).join("");
}
function legend(){
  document.getElementById("legend").innerHTML =
    `<span><i class="dot" style="background:#b3261e"></i>割据</span>
     <span><i class="dot" style="background:#a8791f"></i>虚化/禁戒/降格</span>
     <span><i class="dot" style="background:#c9c9c9"></i>无变化</span>
     <span><i class="dot" style="background:#2e6b4f"></i>正官化</span>`;
}
function draw(){
  const f = filtered();
  const lines = Object.keys(LINE).filter(l=>state.lines.has(l));
  const kinds = [["割据","#b3261e"],["虚化/禁戒","#a8791f"],["正官化","#2e6b4f"],["无变化","#c9c9c9"]];
  const counts = {};
  lines.forEach(l=>{counts[l]={}; kinds.forEach(([k])=>counts[l][k]=0);});
  f.forEach(r=>{ if(counts[r.line]) counts[r.line][r.kind] = (counts[r.line][r.kind]||0)+1; });
  const max = Math.max(1, ...lines.map(l=>kinds.reduce((a,[k])=>a+counts[l][k],0)));
  const W=720,H=260, padL=50, padB=40, bw=Math.min(70, (W-padL-30)/Math.max(1,lines.length)-20);
  let svg = `<line x1="${padL}" y1="${H-padB}" x2="${W-10}" y2="${H-padB}" stroke="#999"/>`;
  for(let g=0; g<=4; g++){
    const y=H-padB-(H-padB-20)*g/4;
    svg += `<line x1="${padL}" y1="${y}" x2="${W-10}" y2="${y}" stroke="#eee"/>`;
    svg += `<text x="${padL-8}" y="${y+4}" font-size="10" fill="#666" text-anchor="end">${Math.round(max*g/4)}</text>`;
  }
  lines.forEach((l,i)=>{
    const x = padL + 30 + i*((W-padL-60)/Math.max(1,lines.length));
    let y0 = H-padB;
    kinds.forEach(([k,c])=>{
      const v = counts[l][k]; if(!v) return;
      const h = (H-padB-20)*v/max; y0 -= h;
      svg += `<rect x="${x}" y="${y0}" width="${bw}" height="${h}" fill="${c}"><title>${LINE[l]} · ${k}: ${v}</title></rect>`;
    });
    svg += `<text x="${x+bw/2}" y="${H-padB+16}" font-size="12" fill="#333" text-anchor="middle">${LINE[l]}</text>`;
  });
  document.getElementById("chart").innerHTML = svg;
}
function table(){
  const f = filtered().slice().sort((a,b)=>{
    const k=state.sortK; let va=a[k], vb=b[k];
    if(va==null) va=-1; if(vb==null) vb=-1;
    if(typeof va==="string") return state.asc? va.localeCompare(vb,"zh"): vb.localeCompare(va,"zh");
    return state.asc? va-vb : vb-va;
  });
  document.querySelector("#tbl tbody").innerHTML = f.map(r=>{
    const c = r.kind==="割据"?"#b3261e":r.kind==="虚化/禁戒"?"#a8791f":r.kind==="正官化"?"#2e6b4f":"#999";
    return `<tr><td>${r.office}</td><td>${r.dyn}</td><td>${r.line_cn}</td><td>${r.start}</td><td>${r.end}</td>
      <td>${r.year??"—"}</td><td><span class="tag" style="background:${c}">${r.kind}</span></td>
      <td>${r.note}</td><td>${r.grade}</td></tr>`;
  }).join("");
}
function render(){ cards(); draw(); table(); }
document.getElementById("dyn").onchange = e => {state.dyn=e.target.value; render();};
document.getElementById("kind").onchange = e => {state.kind=e.target.value; render();};
document.getElementById("lines").innerHTML = Object.keys(LINE).map(l=>
  `<label class="pill"><input type="checkbox" checked value="${l}">${LINE[l]}</label>`).join(" ");
document.querySelectorAll("#lines input").forEach(cb=>{
  cb.onchange = ()=>{ cb.checked? state.lines.add(cb.value): state.lines.delete(cb.value); render(); };
});
document.querySelectorAll("#tbl th").forEach(th=>{
  th.onclick = ()=>{ const k=th.dataset.k; state.asc = state.sortK===k? !state.asc : true; state.sortK=k; table(); };
});
legend(); render();
</script></body></html>"""

html = (HTML.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
        .replace("__IRR__", str(payload["summary"]["irr"]))
        .replace("__IRLO__", str(payload["summary"]["irr_lo"]))
        .replace("__IRHI__", str(payload["summary"]["irr_hi"]))
        .replace("__LRP__", str(payload["summary"]["logrank_p"]))
        .replace("__SECOUT__", str(payload["summary"]["sec_outer"]))
        .replace("__OUTN__", str(payload["summary"]["outer_n"]))
        .replace("__SECIN__", str(payload["summary"]["sec_inner"]))
        .replace("__INN__", str(payload["summary"]["inner_n"]))
        .replace("__SECP__", str(payload["summary"]["sec_p"])))

open(os.path.join(OUT, "control-explorer.html"), "w", encoding="utf-8").write(html)
print("wrote", os.path.join(OUT, "control-explorer.html"), len(html))

# -*- coding: utf-8 -*-
"""生成 interactive/term-explorer.html（单文件，无外部依赖）。

数据来自 data/concepts.py，与 concepts.csv、正文表格同源。
运行：python analysis/build_explorer.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(ROOT, "data"))
from concepts import TERMS, LAYERS, BNECK, SWAP, stats  # noqa: E402

OUT = os.path.join(ROOT, "interactive", "term-explorer.html")
S = stats()

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>术语账本 · 六十条计算机术语还原</title>
<style>
:root{--red:#b3261e;--blue:#1f4e79;--green:#2e6b4f;--gold:#a8791f;--gray:#5f6368;
      --bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font-family:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","SimSun",serif}
header{padding:26px 5vw 16px;border-bottom:2px solid var(--red);background:#fff}
h1{margin:0 0 6px;font-size:24px}
.sub{color:#555;font-size:13px;line-height:1.7}
.wrap{padding:18px 5vw 60px;max-width:1180px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.card{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:12px}
.card .k{font-size:12px;color:#666}.card .v{font-size:22px;font-weight:700;margin-top:3px}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:#fff;
     border:1px solid #e3e0d8;border-radius:6px;padding:12px;margin:8px 0 14px;font-size:13px}
select,input[type=search]{padding:5px 8px;border:1px solid #ccc;border-radius:4px;
     background:#fff;font-size:13px;font-family:inherit}
input[type=search]{min-width:190px}
.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:14px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}
th,td{padding:7px 8px;border-bottom:1px solid #e8e5dd;text-align:left;vertical-align:top}
th{background:#efece4;position:sticky;top:0;z-index:1}
tbody tr{cursor:pointer}
tbody tr:hover td{background:#fbf8f1}
tbody tr.sel td{background:#f6efe0}
.tag{display:inline-block;padding:1px 6px;border-radius:10px;font-size:11px;color:#fff}
.detail{background:#fff;border:1px solid #e3e0d8;border-radius:8px;padding:18px;
        position:sticky;top:14px;min-height:260px}
.detail h2{margin:0 0 2px;font-size:19px}
.detail .en{color:#777;font-size:12px;margin-bottom:12px}
.q{margin:11px 0}
.q .lbl{font-size:11px;color:#999;letter-spacing:.08em;text-transform:uppercase}
.q .txt{font-size:13.5px;line-height:1.75;margin-top:2px}
pre{background:#f6f6f4;border:1px solid #e6e4dc;border-radius:4px;padding:8px 10px;
    font-size:12px;overflow-x:auto;margin:4px 0 0;white-space:pre-wrap}
code{font-family:Consolas,Menlo,monospace}
.note{font-size:12px;color:#666;line-height:1.8;margin-top:14px}
.rowline{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 10px}
.hint{font-size:12px;color:#888}
</style></head><body>
<header>
  <h1>术语账本 · 六十条计算机术语还原</h1>
  <div class="sub">按层、瓶颈、置换、顶点筛选；点一行看四问（瓶颈 / 置换 / 最朴素的 if-for / 谁付账）、
  Agent 影子与证据等级。数据与 <code>concepts.csv</code> 同源，取自《术语的账单》。</div>
</header>
<div class="wrap">
  <div class="cards" id="cards"></div>
  <div class="bar">
    <label>层 <select id="f-layer"><option value="">全部</option></select></label>
    <label>瓶颈 <select id="f-bneck"><option value="">全部</option></select></label>
    <label>置换 <select id="f-swap"><option value="">全部</option></select></label>
    <label>顶点 <select id="f-cat"><option value="">全部</option>
      <option value="C">C 完备</option><option value="A">A 可组合</option>
      <option value="T">T 传递</option><option value="无">无让出</option></select></label>
    <label>等级 <select id="f-grade"><option value="">全部</option>
      <option>A</option><option>B</option><option>C</option></select></label>
    <input type="search" id="f-q" placeholder="搜术语 / 英文 / 影子">
    <span class="hint" id="count"></span>
  </div>
  <div class="grid">
    <div style="overflow:auto;max-height:72vh;border:1px solid #e3e0d8;border-radius:6px">
      <table><thead><tr><th>术语</th><th>瓶颈→置换</th><th>顶点</th><th>等级</th></tr></thead>
      <tbody id="tbl"></tbody></table>
    </div>
    <div class="detail" id="detail"><div class="hint">点左侧任意一行。</div></div>
  </div>
  <div class="note">
    <b>读法。</b>「顶点」是这条术语让出的东西：C 完备、A 可组合、T 传递、无（纯资源置换）。
    全表 60 条中，让出顶点 36 条、无让出 24 条——C-A-T 三角只覆盖六成，剩下四成记在时间与容量的账上。
    <br><b>边界。</b>编码由作者一人完成（单编码者）；<code>cross</code> 与 <code>cat</code> 同轮编码，
    存在循环论证风险，15 条例外逐条列在正文第 4.3 节。等级是证据等级，不是重要性。
    <br><b>数据。</b><code>data/concepts.csv</code> · 生成脚本 <code>analysis/build_explorer.py</code>。
  </div>
</div>
<script>
const DATA = __DATA__;
const rows = DATA.terms, META = DATA.meta;
const LAYERS = META.layers, BNECK = META.bneck, SWAP = META.swap;
const VC = {C:"#b3261e", A:"#1f4e79", T:"#2e6b4f", "无":"#5f6368"};
const VN = {C:"C 完备", A:"A 可组合", T:"T 传递", "无":"无让出"};

function opt(id, arr){
  const el = document.getElementById(id);
  arr.forEach(v => { const o = document.createElement("option"); o.value = v; o.textContent = v; el.appendChild(o); });
}
opt("f-layer", LAYERS); opt("f-bneck", BNECK); opt("f-swap", SWAP);

const state = {layer:"", bneck:"", swap:"", cat:"", grade:"", q:""};
let selId = null;

function filtered(){
  const q = state.q.trim().toLowerCase();
  return rows.filter(r =>
    (!state.layer || r.layer === state.layer) &&
    (!state.bneck || r.bneck === state.bneck) &&
    (!state.swap  || r.swap  === state.swap) &&
    (!state.cat   || r.cat   === state.cat) &&
    (!state.grade || r.grade === state.grade) &&
    (!q || (r.term + r.en + r.shadow + r.plain).toLowerCase().includes(q)));
}

function renderCards(f){
  const nv = f.filter(r => r.cat === "无").length;
  const pct = f.length ? Math.round(100 * nv / f.length) : 0;
  document.getElementById("cards").innerHTML = [
    ["当前条数", f.length],
    ["其中无让出", nv + "（" + pct + "%）"],
    ["涉及层", new Set(f.map(r => r.layer)).size],
    ["可写成循环（A 级）", f.filter(r => r.impl_g === "A").length]
  ].map(([k, v]) => `<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`).join("");
  document.getElementById("count").textContent = f.length + " / " + rows.length;
}

function renderTable(f){
  const tb = document.getElementById("tbl");
  tb.innerHTML = f.map(r => `<tr data-id="${r.id}" class="${r.id === selId ? "sel" : ""}">
      <td><b>${r.term}</b><div class="hint">${r.en}</div></td>
      <td>${r.bneck}→${r.swap}</td>
      <td><span class="tag" style="background:${VC[r.cat]}">${r.cat}</span></td>
      <td>${r.grade} · ${r.cgrade}</td></tr>`).join("");
  [...tb.querySelectorAll("tr")].forEach(tr =>
    tr.addEventListener("click", () => show(tr.dataset.id)));
}

function show(id){
  selId = id;
  const r = rows.find(x => x.id === id);
  document.getElementById("detail").innerHTML = `
    <h2>${r.term}</h2>
    <div class="en">${r.en} · ${r.layer} · ${r.id}</div>
    <div class="rowline">
      <span class="tag" style="background:${VC[r.cat]}">${VN[r.cat]}</span>
      <span class="tag" style="background:#8a8a8a">证据 ${r.grade}</span>
      <span class="tag" style="background:#8a8a8a">概念 ${r.cgrade}</span>
      <span class="tag" style="background:#8a8a8a">可写 ${r.impl_g}</span>
      <span class="tag" style="background:#8a8a8a">跨主体 ${r.cross}</span>
    </div>
    <div class="q"><div class="lbl">大白话</div><div class="txt">${r.plain}</div></div>
    <div class="q"><div class="lbl">Q1 瓶颈</div><div class="txt"><b>${r.bneck}</b>——${r.bneck_txt}</div></div>
    <div class="q"><div class="lbl">Q2 置换</div><div class="txt"><b>${r.swap}</b>——${r.swap_txt}</div></div>
    <div class="q"><div class="lbl">Q3 最朴素的 if / for</div><pre><code>${esc(r.impl)}</code></pre></div>
    <div class="q"><div class="lbl">顶点</div><div class="txt">${r.cat === "无" ? "无让出：" : ""}${r.cat_txt}</div></div>
    <div class="q"><div class="lbl">Q4 在 Agent 里</div><div class="txt">${r.shadow}</div></div>
    ${r.note ? `<div class="q"><div class="lbl">编码备注</div><div class="txt">${r.note}</div></div>` : ""}
  `;
  renderTable(filtered());
}

function esc(s){ return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function update(){
  const f = filtered();
  renderCards(f); renderTable(f);
  if (selId && !f.some(r => r.id === selId)) { /* 保留右侧详情 */ }
}
document.getElementById("f-layer").onchange = e => { state.layer = e.target.value; update(); };
document.getElementById("f-bneck").onchange = e => { state.bneck = e.target.value; update(); };
document.getElementById("f-swap").onchange  = e => { state.swap  = e.target.value; update(); };
document.getElementById("f-cat").onchange   = e => { state.cat   = e.target.value; update(); };
document.getElementById("f-grade").onchange = e => { state.grade = e.target.value; update(); };
document.getElementById("f-q").oninput      = e => { state.q     = e.target.value; update(); };

update();
show(rows[0].id);
</script>
</body></html>
"""


def main():
    data = {
        "meta": {
            "layers": LAYERS, "bneck": BNECK, "swap": SWAP,
            "n": S["n"], "vertex": dict(S["vertex"]),
        },
        "terms": [{k: t[k] for k in
                   ("id", "layer", "term", "en", "plain", "bneck", "bneck_txt",
                    "swap", "swap_txt", "impl", "impl_g", "cat", "cat_txt",
                    "shadow", "cross", "grade", "cgrade", "note")}
                  for t in TERMS],
    }
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("   interactive/term-explorer.html  (%d terms, %.1f KB)"
          % (len(TERMS), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()

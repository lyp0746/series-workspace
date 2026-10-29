# -*- coding: utf-8 -*-
"""通用交互页生成器：CSV → 单文件 HTML（无外部依赖）。

用法：复制到 <Paper>/analysis/build_explorer.py，改 CONFIG 即可。
    python analysis/build_explorer.py

设计纪律（与论文图表同源）：
  * 只读一份 CSV（编码库），不读第二份数据；
  * 页面内嵌 JSON，单文件可离线打开；
  * 表 + 筛选 + 搜索 + 点行看详情，四件事，不做仪表盘；
  * 页脚写明数据来源、编码规则、边界；
  * 无数据时显示空状态。
"""
import csv
import json
import os
import sys

# ------------------------------------------------------------------ 配置
CONFIG = {
    "title": "十二个记忆方案 · 六变量编码库",
    "subtitle": "从 schemes.csv 生成；左表筛选，点行看详情。六变量定义见正文 3.1，判定规则见 3.3。",
    "csv": "schemes.csv",
    "out": "interactive/schemes.html",
    "slug": "schemes",
    "filters": ["kind", "anchor", "hetero", "judge", "failmode"],
    "search": ["name", "note", "granular", "failmode"],
    "table": ["id", "name", "anchor", "hetero", "judge"],
    "detail": ["kind", "granular", "cues", "failmode", "grade", "refs", "note"],
    "footer": "数据：data/schemes.py（唯一数据源，12 方案 × 12 字段）；编码：六变量与判定规则（正文 3.1—3.3）；边界：这是编码库不是性能数据，本文无实验，最高等级 B。",
}

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--red:#b3261e;--blue:#1f4e79;--gray:#5f6368;--bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font-family:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","SimSun",serif}
header{padding:24px 5vw 14px;border-bottom:2px solid var(--red);background:#fff}
h1{margin:0 0 6px;font-size:23px}
.sub{color:#555;font-size:13px;line-height:1.7}
.wrap{padding:16px 5vw 52px;max-width:1180px;margin:0 auto}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.card{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:11px}
.card .k{font-size:12px;color:#666}.card .v{font-size:21px;font-weight:700;margin-top:2px}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;background:#fff;
     border:1px solid #e3e0d8;border-radius:6px;padding:11px;margin:6px 0 14px;font-size:13px}
select,input[type=search]{padding:5px 8px;border:1px solid #ccc;border-radius:4px;
     background:#fff;font-size:13px;font-family:inherit}
input[type=search]{min-width:180px}
.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:14px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;background:#fff;font-size:13px}
th,td{padding:7px 8px;border-bottom:1px solid #e8e5dd;text-align:left;vertical-align:top}
th{background:#efece4;position:sticky;top:0}
tbody tr{cursor:pointer}
tbody tr:hover td{background:#fbf8f1}
tbody tr.sel td{background:#f6efe0}
.tag{display:inline-block;padding:1px 6px;border-radius:10px;font-size:11px;color:#fff;background:var(--gray)}
.detail{background:#fff;border:1px solid #e3e0d8;border-radius:8px;padding:16px;
        position:sticky;top:12px;min-height:220px}
.detail h2{margin:0 0 10px;font-size:18px}
.detail .row{margin:9px 0}
.detail .k{font-size:11px;color:#999;letter-spacing:.06em}
.detail .v{font-size:13.5px;line-height:1.7;margin-top:2px}
.note{font-size:12px;color:#666;line-height:1.8;margin-top:14px}
.hint{font-size:12px;color:#888}
.empty{padding:40px;text-align:center;color:#999}
</style></head><body>
<header><h1>__TITLE__</h1><div class="sub">__SUBTITLE__</div></header>
<div class="wrap">
  <div class="cards" id="cards"></div>
  <div class="bar" id="bar"></div>
  <div class="grid">
    <div style="overflow:auto;max-height:72vh;border:1px solid #e3e0d8;border-radius:6px">
      <table><thead id="thead"></thead><tbody id="tbody"></tbody></table>
    </div>
    <div class="detail" id="detail"><div class="hint">点左侧任意一行。</div></div>
  </div>
  <div class="note">__FOOTER__</div>
</div>
<script>
const DATA = __DATA__;
const ROWS = DATA.rows, COLS = DATA.cols, CONF = DATA.conf;
const state = {q: "", sel: null, f: {}};
COLS.filters.forEach(k => state.f[k] = "");

function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}

function init(){
  document.getElementById("thead").innerHTML = "<tr>" + COLS.table.map(c=>`<th>${esc(c)}</th>`).join("") + "</tr>";
  const bar = document.getElementById("bar");
  COLS.filters.forEach(k=>{
    const vals = [...new Set(ROWS.map(r=>r[k]).filter(v=>v!=null && v!==""))].sort();
    const sel = document.createElement("select");
    sel.innerHTML = `<option value="">${esc(k)}：全部</option>` + vals.map(v=>`<option>${esc(v)}</option>`).join("");
    sel.onchange = e => { state.f[k] = e.target.value; render(); };
    bar.appendChild(sel);
  });
  const q = document.createElement("input");
  q.type = "search"; q.placeholder = "搜索：" + COLS.search.join(" / ");
  q.oninput = e => { state.q = e.target.value.toLowerCase(); render(); };
  bar.appendChild(q);
}

function filtered(){
  const q = state.q;
  return ROWS.filter(r =>
    COLS.filters.every(k => !state.f[k] || r[k] === state.f[k]) &&
    (!q || COLS.search.some(k => String(r[k]||"").toLowerCase().includes(q))));
}

function render(){
  const f = filtered();
  document.getElementById("cards").innerHTML = [
    ["当前条数", f.length],
    ["总计", ROWS.length]
  ].map(([k,v])=>`<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`).join("");
  const tb = document.getElementById("tbody");
  if (!f.length){ tb.innerHTML = `<tr><td colspan="${COLS.table.length}"><div class="empty">没有符合条件的记录。</div></td></tr>`; return; }
  tb.innerHTML = f.map((r,i)=>`<tr data-i="${ROWS.indexOf(r)}" class="${ROWS.indexOf(r)===state.sel?"sel":""}">` +
    COLS.table.map(c=>`<td>${esc(r[c])}</td>`).join("") + "</tr>").join("");
  [...tb.querySelectorAll("tr")].forEach(tr=>tr.onclick=()=>show(+tr.dataset.i));
}

function show(i){
  state.sel = i; const r = ROWS[i];
  document.getElementById("detail").innerHTML =
    `<h2>${esc(r[COLS.table[0]])}</h2>` +
    COLS.detail.map(k=>`<div class="row"><div class="k">${esc(k)}</div><div class="v">${esc(r[k])}</div></div>`).join("");
  render();
}

init(); render();
</script></body></html>
"""


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, CONFIG["csv"])
    if not os.path.exists(csv_path):
        print("缺数据：%s（先建编码库）" % CONFIG["csv"])
        return 0
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    if not rows:
        print("CSV 为空：%s" % CONFIG["csv"])
        return 0
    cols = {"filters": CONFIG["filters"], "search": CONFIG["search"],
            "table": CONFIG["table"], "detail": CONFIG["detail"]}
    html = (HTML.replace("__TITLE__", CONFIG["title"])
                .replace("__SUBTITLE__", CONFIG["subtitle"])
                .replace("__FOOTER__", CONFIG["footer"])
                .replace("__DATA__", json.dumps({"rows": rows, "cols": cols,
                                                 "conf": {"slug": CONFIG["slug"]}},
                                                ensure_ascii=False)))
    out = os.path.join(base, CONFIG["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("   %s  (%d 行, %.1f KB)" % (CONFIG["out"], len(rows), os.path.getsize(out) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())

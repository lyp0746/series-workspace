# -*- coding: utf-8 -*-
"""为一篇论文生成单文件交互探索器（内联 JSON，无外部依赖）。

用法：python _series/tools/make_explorers.py [paper ...]
产出：<paper>/interactive/<slug>-explorer.html
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CSS = """
:root{--red:#b3261e;--blue:#1f4e79;--green:#2e6b4f;--gold:#a8791f;--bg:#f7f6f3;--ink:#1d1d1f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font-family:"Songti SC","SimSun","Source Han Serif SC",serif}
header{padding:24px 5vw 14px;background:#fff;border-bottom:2px solid var(--red)}
h1{margin:0 0 6px;font-size:24px}.sub{color:#555;font-size:13.5px;line-height:1.6}
.wrap{max-width:1200px;margin:0 auto;padding:16px 5vw 60px}
.bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;background:#fff;
border:1px solid #e3e0d8;border-radius:6px;padding:10px;margin:8px 0 14px}
label{font-size:13px}select{padding:4px 8px;border:1px solid #ccc;border-radius:4px;background:#fff;font-size:13px}
svg{width:100%;background:#fff;border:1px solid #e3e0d8;border-radius:6px;display:block}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:10px 0}
.k div{background:#fff;border:1px solid #e3e0d8;border-radius:6px;padding:11px 12px;font-size:12.5px;color:#555}
.k b{display:block;font-size:21px;color:var(--ink);margin-top:3px;font-family:"Helvetica Neue",Arial,sans-serif}
table{width:100%;border-collapse:collapse;background:#fff;font-size:12.5px;margin-top:12px}
th,td{padding:6px 7px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
th{background:#efece4;position:sticky;top:0}
tr.r{cursor:pointer}tr.r:hover{background:#f4f1e8}
.detail{background:#fff;border:1px solid #d9d4c7;border-left:3px solid var(--blue);
border-radius:5px;padding:12px 14px;margin-top:12px;font-size:13px;line-height:1.8;display:none}
.detail.on{display:block}
.detail h3{margin:0 0 6px;font-size:14.5px}
.tag{display:inline-block;border:1px solid #ddd;border-radius:12px;padding:1px 8px;font-size:11.5px;
color:#555;margin-right:6px;background:#fafafa}
.note{font-size:12px;color:#666;line-height:1.75;margin-top:14px}
.hint{font-size:12px;color:#777}
@media(max-width:700px){h1{font-size:19px}.k b{font-size:18px}}
"""

JS = r"""
const $ = s => document.querySelector(s);
const el = (t, a = {}, ...kids) => {
  const n = document.createElementNS(t.startsWith('svg:') ? 'http://www.w3.org/2000/svg' : 'http://www.w3.org/1999/xhtml', t.replace('svg:', ''));
  for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); }
  kids.forEach(k => n.appendChild(k));
  return n;
};
function uniq(rows, k) { return [...new Set(rows.map(r => r[k]).filter(v => v !== '' && v != null))]; }
function fmt(v, d = 1) { return v == null || isNaN(v) ? '—' : (+v).toFixed(d).replace(/\.0$/, ''); }
function median(a) { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; }

function makeFilters(rows, spec) {
  const bar = $('#filters'); bar.innerHTML = '';
  const state = {};
  spec.forEach(f => {
    const wrap = document.createElement('label');
    wrap.textContent = f.label + ' ';
    const sel = document.createElement('select');
    sel.innerHTML = '<option value="">全部</option>' + uniq(rows, f.key).map(v => `<option>${v}</option>`).join('');
    sel.onchange = () => { state[f.key] = sel.value; render(); };
    wrap.appendChild(sel); bar.appendChild(wrap);
    state[f.key] = '';
  });
  return state;
}
function filtered() {
  return DATA.filter(r => Object.entries(STATE).every(([k, v]) => !v || String(r[k]) === v));
}
"""


def page(title, subtitle, body_js, data, extra_head=""):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>{CSS}{extra_head}</style></head><body>
<header><h1>{title}</h1><div class="sub">{subtitle}</div></header>
<div class="wrap">
<div class="bar" id="filters"></div>
<div class="k" id="stats"></div>
<svg id="chart" viewBox="0 0 900 420"></svg>
<div class="detail" id="detail"></div>
<table id="tbl"><thead></thead><tbody></tbody></table>
<div class="note" id="note"></div>
</div>
<script>
const DATA = {json.dumps(data, ensure_ascii=False)};
{JS}
const STATE = makeFilters(DATA, CONFIG_FILTERS);
function stats(items, cards) {{
  const box = document.getElementById('stats'); box.innerHTML = '';
  cards.forEach(c => {{
    const d = document.createElement('div'); d.innerHTML = c.label + '<b>' + c.value(items) + '</b>';
    box.appendChild(d);
  }});
}}
function table(items) {{
  const th = document.querySelector('#tbl thead'), tb = document.querySelector('#tbl tbody');
  th.innerHTML = '<tr>' + CONFIG_COLS.map(c => `<th>${{c.label}}</th>`).join('') + '</tr>';
  tb.innerHTML = '';
  items.slice(0, 400).forEach(r => {{
    const tr = document.createElement('tr'); tr.className = 'r';
    CONFIG_COLS.forEach(c => {{ const td = document.createElement('td'); td.textContent = r[c.key] ?? ''; tr.appendChild(td); }});
    tr.onclick = () => showDetail(r);
    tb.appendChild(tr);
  }});
}}
function showDetail(r) {{
  const d = document.getElementById('detail');
  d.innerHTML = '<h3>' + (r[CONFIG_TITLE] ?? '') + '</h3>' +
    CONFIG_DETAIL.map(([k, label]) => r[k] ? `<div><span class="tag">${{label}}</span>${{String(r[k])}}</div>` : '').join('');
  d.className = 'detail on';
}}
{body_js}
render();
</script></body></html>"""


def write(repo, slug, html):
    d = os.path.join(ROOT, repo, "interactive")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, slug + "-explorer.html")
    open(p, "w", encoding="utf-8").write(html)
    print("wrote", os.path.relpath(p, ROOT), len(html), "bytes")


# ---------------------------------------------------------------- SleepingResidue
def sleeping():
    rows = []
    with open(os.path.join(ROOT, "SleepingResidue", "cases.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            def num(x):
                try:
                    return int(str(x).strip())
                except Exception:
                    return None
            rows.append({
                "id": r["id"], "case": r["case"], "claim": r["claim"],
                "t_prop": num(r["t_prop"]), "t_rev": num(r["t_rev"]),
                "decoder": r["decoder"], "t_dec": num(r["t_dec"]),
                "outcome": r["outcome"], "coord_old": r["coord_old"],
                "coord_new": r["coord_new"], "dec_type": r["dec_type"],
                "silence": num(r["silence"]), "lag": num(r["lag"]),
                "grade": r["grade"], "note": r["note"],
            })
    cfg_f = [{"key": "outcome", "label": "结局"}, {"key": "coord_old", "label": "旧范式坐标"},
             {"key": "dec_type", "label": "解码器类型"}]
    cfg_cols = [{"key": "id", "label": "编号"}, {"key": "case", "label": "案例"},
                {"key": "silence", "label": "沉寂年"}, {"key": "lag", "label": "解码器滞后"},
                {"key": "outcome", "label": "结局"}, {"key": "coord_old", "label": "旧坐标"},
                {"key": "dec_type", "label": "类型"}, {"key": "grade", "label": "等级"}]
    js = r"""
const CFG = {
  x: 'silence', y: 'lag', color: 'outcome',
  xlab: '沉寂期（年，对数）', ylab: '解码器出现到被承认（年）',
  note: '横轴是“被埋没多久”，纵轴是“可读之后多久被承认”。论文的结论是：纵轴几乎都落在 5 年以内（18/18），决定沉寂的不是文献，而是解码器。点按一行可看该案例的判据与出处。'
};
const COLORS = {'恢复': '#1f4e79', '重发明': '#a8791f', '沉默': '#b3261e'};
function render() {
  const items = filtered();
  stats(items, [
    {label: '案例数', value: a => a.length},
    {label: '沉寂中位数（年）', value: a => fmt(median(a.map(r => r.silence)), 0)},
    {label: '解码器滞后中位数（年）', value: a => fmt(median(a.map(r => r.lag)), 1)},
    {label: '≤5 年占比', value: a => (100 * a.filter(r => r.lag <= 5).length / (a.length || 1)).toFixed(0) + '%'},
  ]);
  const svg = document.getElementById('chart'); svg.innerHTML = '';
  const W = 900, H = 420, P = {l: 70, r: 30, t: 20, b: 56};
  const xs = items.map(r => r.silence), ys = items.map(r => r.lag);
  const x0 = Math.log10(10), x1 = Math.log10(Math.max(2000, ...xs)), y0 = 0, y1 = Math.max(...ys, 10);
  const X = v => P.l + (Math.log10(Math.max(v, 10)) - x0) / (x1 - x0) * (W - P.l - P.r);
  const Y = v => H - P.b - (v - y0) / (y1 - y0) * (H - P.t - P.b);
  const mk = (t, a, txt) => { const n = document.createElementNS('http://www.w3.org/2000/svg', t); for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); } if (txt != null) n.textContent = txt; svg.appendChild(n); return n; };
  mk('line', {x1: P.l, y1: H - P.b, x2: W - P.r, y2: H - P.b, stroke: '#999'});
  mk('line', {x1: P.l, y1: P.t, x2: P.l, y2: H - P.b, stroke: '#999'});
  [10, 30, 100, 300, 1000, 2000].forEach(v => { if (Math.log10(v) <= x1) mk('text', {x: X(v), y: H - P.b + 18, 'font-size': 11, fill: '#666', 'text-anchor': 'middle', text: v}); });
  for (let v = 0; v <= y1; v += 2) { mk('text', {x: P.l - 8, y: Y(v) + 4, 'font-size': 11, fill: '#666', 'text-anchor': 'end', text: v}); }
  mk('text', {x: (W) / 2, y: H - 12, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', text: CFG.xlab});
  mk('text', {x: 16, y: H / 2, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', transform: `rotate(-90 16 ${H / 2})`, text: CFG.ylab});
  mk('line', {x1: P.l, y1: Y(5), x2: W - P.r, y2: Y(5), stroke: '#b3261e', 'stroke-dasharray': '4 4', 'stroke-width': 1});
  mk('text', {x: W - P.r - 4, y: Y(5) - 6, 'font-size': 11, fill: '#b3261e', 'text-anchor': 'end', text: '5 年线'});
  items.forEach(r => {
    const c = mk('circle', {cx: X(r.silence), cy: Y(r.lag), r: 5.5, fill: COLORS[r.outcome] || '#666', 'fill-opacity': .82, stroke: '#fff', 'stroke-width': 1});
    c.style.cursor = 'pointer'; c.onclick = () => showDetail(r);
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); t.textContent = r.case; c.appendChild(t);
  });
  table(items); document.getElementById('note').textContent = CFG.note;
}
"""
    html = page("线外的残余 · 交互探索器",
                "24 个延迟承认案例 · 三标记检验 · 数据来自 cases.csv（A/B/C 等级逐行标注）",
                js, rows)
    html = html.replace("CONFIG_FILTERS", json.dumps(cfg_f, ensure_ascii=False)) \
               .replace("CONFIG_COLS", json.dumps(cfg_cols, ensure_ascii=False)) \
               .replace("CONFIG_TITLE", "'case'") \
               .replace("CONFIG_DETAIL", json.dumps([["claim", "主张"], ["decoder", "解码器"], ["coord_old", "旧坐标"],
                                                    ["coord_new", "新坐标"], ["grade", "等级"], ["note", "注"]], ensure_ascii=False))
    write("SleepingResidue", "sleeping-residue", html)


# ---------------------------------------------------------------- OptimizationBoundary
def optimization():
    rows = []
    with open(os.path.join(ROOT, "OptimizationBoundary", "cases.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({"id": r["id"], "case": r["case"], "domain": r["domain"],
                         "premise": r["premise"], "mechanism": r["mechanism"],
                         "outcome": r["outcome"], "severity": r["severity"],
                         "grade": r["grade"], "note": r["note"]})
    cfg_f = [{"key": "premise", "label": "越界前提"}, {"key": "severity", "label": "后果"},
             {"key": "domain", "label": "领域"}]
    cfg_cols = [{"key": "id", "label": "编号"}, {"key": "case", "label": "案例"},
                {"key": "domain", "label": "领域"}, {"key": "premise", "label": "越界前提"},
                {"key": "outcome", "label": "后果"}, {"key": "severity", "label": "严重度"},
                {"key": "grade", "label": "等级"}]
    js = r"""
const COLS = ['目标', '空间', '预算', '停止'];
const SEV = ['轻', '中', '重'];
function render() {
  const items = filtered();
  stats(items, [
    {label: '案例数', value: a => a.length},
    {label: '最常越界的前提', value: a => COLS.map(p => [p, a.filter(r => r.premise === p).length]).sort((x, y) => y[1] - x[1])[0]?.[0] || '—'},
    {label: '后果为“重”的占比', value: a => (100 * a.filter(r => r.severity === '重').length / (a.length || 1)).toFixed(0) + '%'},
    {label: '停止规则越界中“重”的比例', value: a => { const s = a.filter(r => r.premise === '停止'); return s.length ? (100 * s.filter(r => r.severity === '重').length / s.length).toFixed(0) + '%' : '—'; }},
  ]);
  const svg = document.getElementById('chart'); svg.innerHTML = '';
  const W = 900, H = 420, P = {l: 80, r: 30, t: 30, b: 60};
  const mk = (t, a, txt) => { const n = document.createElementNS('http://www.w3.org/2000/svg', t); for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); } if (txt != null) n.textContent = txt; svg.appendChild(n); return n; };
  const cx = i => P.l + i * ((W - P.l - P.r) / COLS.length) + ((W - P.l - P.r) / COLS.length) / 2;
  const maxY = Math.max(1, ...[].concat(...COLS.map(p => SEV.map(s => items.filter(r => r.premise === p && r.severity === s).length))));
  const bw = (W - P.l - P.r) / COLS.length / (SEV.length + 2);
  const COL = {'轻': '#9bb7cf', '中': '#3f6f9c', '重': '#b3261e'};
  COLS.forEach((p, i) => {
    SEV.forEach((s, j) => {
      const n = items.filter(r => r.premise === p && r.severity === s).length;
      const h = (n / maxY) * (H - P.t - P.b);
      mk('rect', {x: cx(i) - (SEV.length * bw) / 2 + j * bw, y: H - P.b - h, width: bw - 4, height: h, fill: COL[s], opacity: .9});
      if (n) mk('text', {x: cx(i) - (SEV.length * bw) / 2 + j * bw + (bw - 4) / 2, y: H - P.b - h - 5, 'font-size': 11, fill: '#444', 'text-anchor': 'middle', text: n});
    });
    mk('text', {x: cx(i), y: H - P.b + 20, 'font-size': 12.5, fill: '#222', 'text-anchor': 'middle', text: p});
  });
  mk('line', {x1: P.l, y1: H - P.b, x2: W - P.r, y2: H - P.b, stroke: '#999'});
  mk('text', {x: P.l, y: P.t - 10, 'font-size': 12, fill: '#555', text: '柱高＝案例数；颜色＝后果严重度（浅→重）'});
  table(items); document.getElementById('note').textContent = '论文的结论：目标越界最常见，停止规则越界的后果最重（5 例中 4 例为“重”）。点一行看机制。';
}
"""
    html = page("优化的边界 · 交互探索器",
                "20 个越界案例 · 四前提（目标/空间/预算/停止）× 后果严重度 · 数据来自 cases.csv",
                js, rows)
    html = html.replace("CONFIG_FILTERS", json.dumps(cfg_f, ensure_ascii=False)) \
               .replace("CONFIG_COLS", json.dumps(cfg_cols, ensure_ascii=False)) \
               .replace("CONFIG_TITLE", "'case'") \
               .replace("CONFIG_DETAIL", json.dumps([["mechanism", "机制"], ["outcome", "后果"], ["grade", "等级"], ["note", "注"]], ensure_ascii=False))
    write("OptimizationBoundary", "optimization-boundary", html)


# ---------------------------------------------------------------- CapacityProxies
def capacity():
    d = json.load(open(os.path.join(ROOT, "CapacityProxies", "data", "proxy_slots.json"), encoding="utf-8"))
    rows = []
    for name, v in d.items():
        rows.append({"source": name, "n": v.get("n", 0), "g1500": v.get("g1500", 0),
                     "g1914": v.get("g1914", 0), "tradition": v.get("tradition", ""),
                     "doors": v.get("g1500", 0) + v.get("g1914", 0)})
    cfg_f = [{"key": "tradition", "label": "传统"}, {"key": "doors", "label": "含“通货门”数"}]
    cfg_cols = [{"key": "source", "label": "来源"}, {"key": "tradition", "label": "传统"},
                {"key": "n", "label": "顶层槽位"}, {"key": "g1500", "label": "含 1500"},
                {"key": "g1914", "label": "含 1914"}, {"key": "doors", "label": "门依赖度"}]
    js = r"""
const TRAD = {'european': '#b3261e', 'global': '#1f4e79', 'china': '#2e6b4f', 'other': '#a8791f'};
function render() {
  const items = filtered();
  const byT = {};
  items.forEach(r => (byT[r.tradition] = byT[r.tradition] || []).push(r));
  stats(items, [
    {label: '来源数', value: a => a.length},
    {label: '槽位中位数', value: a => fmt(median(a.map(r => r.n)), 1)},
    {label: '含 1500 的条数', value: a => a.filter(r => r.g1500).length + ' / ' + a.length},
    {label: '含 1914 的条数', value: a => a.filter(r => r.g1914).length + ' / ' + a.length},
  ]);
  const svg = document.getElementById('chart'); svg.innerHTML = '';
  const W = 900, H = 420, P = {l: 70, r: 30, t: 24, b: 60};
  const mk = (t, a, txt) => { const n = document.createElementNS('http://www.w3.org/2000/svg', t); for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); } if (txt != null) n.textContent = txt; svg.appendChild(n); return n; };
  const x0 = 0, x1 = Math.max(12, ...items.map(r => r.n)), y0 = -0.3, y1 = 2.3;
  const X = v => P.l + (v - x0) / (x1 - x0) * (W - P.l - P.r);
  const Y = v => H - P.b - (v - y0) / (y1 - y0) * (H - P.t - P.b);
  mk('line', {x1: P.l, y1: H - P.b, x2: W - P.r, y2: H - P.b, stroke: '#999'});
  mk('line', {x1: P.l, y1: P.t, x2: P.l, y2: H - P.b, stroke: '#999'});
  for (let v = 0; v <= x1; v += 2) mk('text', {x: X(v), y: H - P.b + 18, 'font-size': 11, fill: '#666', 'text-anchor': 'middle', text: v});
  for (let v = 0; v <= 2; v++) mk('text', {x: P.l - 8, y: Y(v) + 4, 'font-size': 11, fill: '#666', 'text-anchor': 'end', text: v});
  mk('text', {x: W / 2, y: H - 12, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', text: '顶层槽位数'});
  mk('text', {x: 16, y: H / 2, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', transform: `rotate(-90 16 ${H / 2})`, text: '含“通货门”（1500/1914）数'});
  items.forEach(r => {
    const c = mk('circle', {cx: X(r.n) + (Math.random() - .5) * 8, cy: Y(r.doors) + (Math.random() - .5) * 8,
      r: 5, fill: TRAD[r.tradition] || '#666', 'fill-opacity': .8, stroke: '#fff', 'stroke-width': 1});
    c.style.cursor = 'pointer'; c.onclick = () => showDetail(r);
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); t.textContent = r.source; c.appendChild(t);
  });
  table(items); document.getElementById('note').textContent = '本表含 46 部核心语料与 8 部扩展编年史，故计数与正文的 51 部口径不完全相同；相关系数（r=−0.245）与分组比例以论文为准。结论只支持弱版本。';
}
"""
    html = page("容量的三个代理 · 交互探索器（分期槽位）",
                "51 部世界史来源 · 顶层槽位 × 通货门依赖 · 数据来自 proxy_slots.json（B 级，样本有限）",
                js, rows)
    html = html.replace("CONFIG_FILTERS", json.dumps(cfg_f, ensure_ascii=False)) \
               .replace("CONFIG_COLS", json.dumps(cfg_cols, ensure_ascii=False)) \
               .replace("CONFIG_TITLE", "'source'") \
               .replace("CONFIG_DETAIL", json.dumps([["tradition", "传统"], ["n", "顶层槽位"], ["doors", "门依赖度"]], ensure_ascii=False))
    write("CapacityProxies", "capacity-proxies", html)


# ---------------------------------------------------------------- Ledger
def ledger():
    rows = []
    with open(os.path.join(ROOT, "LedgerReconciliation", "ledger.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({k: r[k] for k in ["paper", "pid", "stmt", "test", "result", "status", "grade", "core", "scale"]})
    cfg_f = [{"key": "core", "label": "核心"}, {"key": "status", "label": "状态"},
             {"key": "grade", "label": "等级"}, {"key": "scale", "label": "尺度"}]
    cfg_cols = [{"key": "paper", "label": "篇"}, {"key": "pid", "label": "编号"},
                {"key": "stmt", "label": "命题"}, {"key": "status", "label": "状态"},
                {"key": "grade", "label": "等级"}, {"key": "core", "label": "核心"},
                {"key": "scale", "label": "尺度"}]
    js = r"""
const CORES = ['看见', '记住', '跟上', '选择', '讲述', '临界'];
const STATUS = ['成立', '支持', '部分', '待检验', '待核', '开放', '撤回', '证伪'];
const COL = {'A': '#1f4e79', 'B': '#3f6f9c', 'C': '#a8791f'};
function render() {
  const items = filtered();
  stats(items, [
    {label: '命题数', value: a => a.length},
    {label: '已核销', value: a => a.filter(r => ['成立', '支持', '部分', '证伪', '撤回'].includes(r.status)).length},
    {label: 'A 级', value: a => a.filter(r => r.grade === 'A').length},
    {label: '证伪＋撤回', value: a => a.filter(r => ['证伪', '撤回'].includes(r.status)).length},
  ]);
  const svg = document.getElementById('chart'); svg.innerHTML = '';
  const W = 900, H = 420, P = {l: 70, r: 20, t: 34, b: 64};
  const mk = (t, a, txt) => { const n = document.createElementNS('http://www.w3.org/2000/svg', t); for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); } if (txt != null) n.textContent = txt; svg.appendChild(n); return n; };
  const cw = (W - P.l - P.r) / CORES.length, ch = (H - P.t - P.b) / STATUS.length;
  CORES.forEach((c, i) => mk('text', {x: P.l + i * cw + cw / 2, y: P.t - 10, 'font-size': 12, fill: '#222', 'text-anchor': 'middle', text: c}));
  STATUS.forEach((s, j) => mk('text', {x: P.l - 8, y: P.t + j * ch + ch / 2 + 4, 'font-size': 11.5, fill: '#444', 'text-anchor': 'end', text: s}));
  const maxN = Math.max(1, ...[].concat(...CORES.map(c => STATUS.map(s => items.filter(r => r.core === c && r.status === s).length))));
  CORES.forEach((c, i) => STATUS.forEach((s, j) => {
    const cell = items.filter(r => r.core === c && r.status === s);
    const n = cell.length;
    const a = .12 + .8 * n / maxN;
    const rect = mk('rect', {x: P.l + i * cw + 3, y: P.t + j * ch + 3, width: cw - 6, height: ch - 6,
      fill: n ? `rgba(31,78,121,${a})` : '#f4f2ec', rx: 3});
    if (n) {
      mk('text', {x: P.l + i * cw + cw / 2, y: P.t + j * ch + ch / 2 + 5, 'font-size': 12,
        fill: a > .5 ? '#fff' : '#1d1d1f', 'text-anchor': 'middle', text: n});
      rect.style.cursor = 'pointer';
      rect.onclick = () => { showDetail(cell[0]); };
    }
  }));
  table(items);
  document.getElementById('note').textContent = '这是论文的“账本”本身：110 条命题、六核心 × 八种状态。格子深浅＝条数；点有数字的格子可看该格第一条；点表格任意行看全文。';
}
"""
    html = page("六张账单的对账 · 交互探索器",
                "110 条登记命题 · 六核心 × 状态 × 等级 × 尺度 · 数据来自 ledger.csv（唯一来源）",
                js, rows)
    html = html.replace("CONFIG_FILTERS", json.dumps(cfg_f, ensure_ascii=False)) \
               .replace("CONFIG_COLS", json.dumps(cfg_cols, ensure_ascii=False)) \
               .replace("CONFIG_TITLE", "'stmt'") \
               .replace("CONFIG_DETAIL", json.dumps([["paper", "篇"], ["pid", "编号"], ["test", "检验"], ["result", "结果"], ["status", "状态"], ["grade", "等级"], ["core", "核心"], ["scale", "尺度"]], ensure_ascii=False))
    write("LedgerReconciliation", "ledger-reconciliation", html)


# ---------------------------------------------------------------- Monarch
def monarch():
    rows = []
    md = open(os.path.join(ROOT, "MonarchCompetition", "data", "table_models.md"), encoding="utf-8").read()
    for line in md.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "模型" in line.split("|")[1]:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 9:
            continue
        def money(x):
            try:
                return float(x.replace("$", "").replace(",", ""))
            except Exception:
                return None
        def num(x):
            try:
                return float(x.replace("×", "").replace("K", "000").replace(",", ""))
            except Exception:
                return None
        rows.append({"model": c[0], "tier": c[1], "out": money(c[2]), "inp": money(c[3]),
                     "cache": money(c[4]), "rjs": num(c[5]), "ctx": num(c[6]),
                     "hosts": c[7], "weights": c[8], "license": c[9] if len(c) > 9 else ""})
    cfg_f = [{"key": "tier", "label": "层"}, {"key": "weights", "label": "权重"},
             {"key": "hosts", "label": "托管商数"}]
    cfg_cols = [{"key": "model", "label": "模型"}, {"key": "tier", "label": "层"},
                {"key": "out", "label": "输出 $/1M"}, {"key": "cache", "label": "缓存读 $/1M"},
                {"key": "rjs", "label": "重放—判断价差"}, {"key": "ctx", "label": "上下文"},
                {"key": "hosts", "label": "托管商"}, {"key": "weights", "label": "权重"}]
    js = r"""
function render() {
  const items = filtered().filter(r => r.rjs > 0);
  stats(items, [
    {label: '本表模型数', value: a => a.length},
    {label: '本表价差中位', value: a => fmt(median(a.map(r => r.rjs)), 1) + '×'},
    {label: '闭源中位', value: a => fmt(median(a.filter(r => r.weights === '闭').map(r => r.rjs)), 1) + '×'},
    {label: '开放中位', value: a => fmt(median(a.filter(r => r.weights === '开').map(r => r.rjs)), 1) + '×'},
  ]);
  const svg = document.getElementById('chart'); svg.innerHTML = '';
  const W = 900, H = 420, P = {l: 74, r: 30, t: 24, b: 58};
  const mk = (t, a, txt) => { const n = document.createElementNS('http://www.w3.org/2000/svg', t); for (const k in a) { if (k === 'text') n.textContent = a[k]; else n.setAttribute(k, a[k]); } if (txt != null) n.textContent = txt; svg.appendChild(n); return n; };
  const x0 = Math.log10(8), x1 = Math.log10(Math.max(2000, ...items.map(r => r.ctx || 8)));
  const y0 = Math.log10(2), y1 = Math.log10(260);
  const X = v => P.l + (Math.log10(Math.max(v, 8)) - x0) / (x1 - x0) * (W - P.l - P.r);
  const Y = v => H - P.b - (Math.log10(Math.max(v, 2)) - y0) / (y1 - y0) * (H - P.t - P.b);
  mk('line', {x1: P.l, y1: H - P.b, x2: W - P.r, y2: H - P.b, stroke: '#999'});
  mk('line', {x1: P.l, y1: P.t, x2: P.l, y2: H - P.b, stroke: '#999'});
  [8, 32, 128, 512, 2048].forEach(v => { if (v <= Math.pow(10, x1)) mk('text', {x: X(v), y: H - P.b + 18, 'font-size': 11, fill: '#666', 'text-anchor': 'middle', text: v + 'K'}); });
  [2, 5, 10, 20, 50, 100, 200].forEach(v => mk('text', {x: P.l - 8, y: Y(v) + 4, 'font-size': 11, fill: '#666', 'text-anchor': 'end', text: v + '×'}));
  mk('text', {x: W / 2, y: H - 12, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', text: '上下文窗口（token，对数）'});
  mk('text', {x: 16, y: H / 2, 'font-size': 12, fill: '#333', 'text-anchor': 'middle', transform: `rotate(-90 16 ${H / 2})`, text: '重放—判断价差 RJS（对数）'});
  const COL = {'闭': '#b3261e', '开': '#2e6b4f'};
  items.forEach(r => {
    const c = mk('circle', {cx: X(r.ctx || 8) + (Math.random() - .5) * 10, cy: Y(r.rjs), r: 5,
      fill: COL[r.weights] || '#666', 'fill-opacity': .78, stroke: '#fff', 'stroke-width': 1});
    c.style.cursor = 'pointer'; c.onclick = () => showDetail(r);
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); t.textContent = r.model + ' · ' + r.rjs + '×'; c.appendChild(t);
  });
  table(items.sort((a, b) => b.rjs - a.rjs));
  document.getElementById('note').textContent = '本表是论文 438 个模型快照中的 27 条代表性子集，故中位数与正文的 294/98/196 口径不同（正文中位 34.5×，闭源 50×、开放 19×）。结论是：价目表本身就把“执行”与“方向”分开标价；按上下文长度分组后，闭源—开放差异只在部分档位成立。';
}
"""
    html = page("开明君主与两层竞争 · 交互探索器",
                "价目表快照 · 重放—判断价差（RJS）＝输出单价 ÷ 缓存读单价 · 数据来自 data/table_models.md",
                js, rows)
    html = html.replace("CONFIG_FILTERS", json.dumps(cfg_f, ensure_ascii=False)) \
               .replace("CONFIG_COLS", json.dumps(cfg_cols, ensure_ascii=False)) \
               .replace("CONFIG_TITLE", "'model'") \
               .replace("CONFIG_DETAIL", json.dumps([["tier", "层"], ["out", "输出 $/1M"], ["inp", "输入 $/1M"], ["cache", "缓存读 $/1M"], ["rjs", "RJS"], ["ctx", "上下文"], ["license", "许可"]], ensure_ascii=False))
    write("MonarchCompetition", "monarch-competition", html)


if __name__ == "__main__":
    which = sys.argv[1:] or ["sleeping", "optimization", "capacity", "ledger", "monarch"]
    if "sleeping" in which: sleeping()
    if "optimization" in which: optimization()
    if "capacity" in which: capacity()
    if "ledger" in which: ledger()
    if "monarch" in which: monarch()

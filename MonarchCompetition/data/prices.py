# -*- coding: utf-8 -*-
"""价目读数库（单一数据源）：从 raw/ 快照计算本文全部价格类指标。

数据快照
--------
raw/or_models.json      OpenRouter 公开模型目录（/api/v1/models），含 list price、
                        上下文、模态、hugging_face_id（权重是否可下载）、created
raw/endpoints.json     28 个旗舰模型的 /endpoints 读数（托管商数与名单）
raw/hf_licenses.json   175 个开放权重模型的 HuggingFace 许可证读数
raw/*.txt              官方价目页与 OpenRouter Inferred 周报的正文快照

口径
----
价格一律换算为「美元／百万 token」。RJS（重放—判断价差）=
completion 单价 ÷ input_cache_read 单价；分母缺失或为 0 的模型不计入。
「开放权重」＝ hugging_face_id 非空（权重可下载）；这是可自托管的下界代理，
不等于许可证允许商用（后者另有一列）。

所有指标由本文件计算，正文数字不得另写。
"""
import json
import pathlib
import datetime
import collections

import numpy as np

RAW = pathlib.Path(__file__).resolve().parent.parent / "raw"
SNAPSHOT = "2026-10-26"

LABS = ["openai", "anthropic", "google", "deepseek", "x-ai", "moonshotai", "qwen", "z-ai", "meta"]
LAB_ZH = {
    "openai": "OpenAI", "anthropic": "Anthropic", "google": "Google DeepMind",
    "deepseek": "深度求索 DeepSeek", "x-ai": "xAI（Grok）", "moonshotai": "月之暗面（Kimi）",
    "qwen": "阿里（千问 Qwen）", "z-ai": "智谱（GLM）", "meta": "Meta（Muse／Llama）",
}
# 28 个用于托管商读数的旗舰／代表模型（人工选定，规则见正文 3.3：
# 每家实验室取「最贵旗舰」「次旗舰」「开放权重代表」三类，缺者为空）
FLAGSHIPS = [
    "openai/gpt-6.1-sol", "openai/gpt-6-luna", "openai/gpt-6-astra", "openai/gpt-oss-120b",
    "anthropic/claude-fable-5.1", "anthropic/claude-opus-5.5", "anthropic/claude-sonnet-5.5",
    "anthropic/claude-haiku-5.5",
    "google/gemini-4-argon", "google/gemini-3.8-flash", "google/gemma-4-31b-it",
    "deepseek/deepseek-v4.1-flash", "deepseek/deepseek-v4-pro",
    "x-ai/grok-4.7", "x-ai/grok-4.20",
    "moonshotai/kimi-k3.1-pro", "moonshotai/kimi-k3", "moonshotai/kimi-k2.6",
    "qwen/qwen3.8-max-prime", "qwen/qwen3.8-flash", "qwen/qwen3.8-max-0902",
    "z-ai/glm-5.3-prime", "z-ai/glm-5.3", "z-ai/glm-5.3-flash",
    "meta/muse-wonder", "meta/muse-spark-1.3", "meta/muse-spark-open", "meta/muse-glimmer-30b",
]


def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def load():
    d = json.loads((RAW / "or_models.json").read_text(encoding="utf-8"))["data"]
    ep = json.loads((RAW / "endpoints.json").read_text(encoding="utf-8"))
    lic = json.loads((RAW / "hf_licenses.json").read_text(encoding="utf-8"))
    return d, ep, lic


def models():
    """逐模型读数表。"""
    d, ep, lic = load()
    out = []
    for m in d:
        mid = m["id"]
        if mid.startswith("~") or mid.split("/")[0] == "openrouter":
            continue
        p = m.get("pricing") or {}
        comp, prm, cac = _f(p.get("completion")), _f(p.get("prompt")), _f(p.get("input_cache_read"))
        out.append(dict(
            id=mid, lab=mid.split("/")[0], name=m.get("name") or mid,
            out=round(comp * 1e6, 4) if comp else None,
            inp=round(prm * 1e6, 4) if prm else None,
            cache=round(cac * 1e6, 4) if cac else None,
            rjs=round(comp / cac, 2) if (comp and cac) else None,
            ctx=m.get("context_length") or 0,
            open_w=bool(m.get("hugging_face_id")),
            hf=m.get("hugging_face_id"),
            license=(lic.get(mid) or {}).get("license"),
            created=m.get("created") or 0,
            providers=len((ep.get(mid) or {}).get("providers") or []) or None,
            n_endpoints=(ep.get(mid) or {}).get("n_endpoints"),
        ))
    return out


MODELS = models()
BY_ID = {m["id"]: m for m in MODELS}


def _pct(xs, q):
    return float(np.percentile(xs, q))


def stats():
    rs = [m["rjs"] for m in MODELS if m["rjs"]]
    ro = [m["rjs"] for m in MODELS if m["rjs"] and m["open_w"]]
    rc = [m["rjs"] for m in MODELS if m["rjs"] and not m["open_w"]]
    po = [m["out"] for m in MODELS if m["out"] and m["open_w"]]
    pc = [m["out"] for m in MODELS if m["out"] and not m["open_w"]]

    lab_rjs = {}
    for lab in LABS:
        v = [m["rjs"] for m in MODELS if m["lab"] == lab and m["rjs"]]
        lab_rjs[lab] = (len(v), float(np.median(v)) if v else None)

    # 按发布月份的价格中位（vintage series：当月进入市场的新模型的标价）
    bucket = collections.defaultdict(lambda: {"open": [], "closed": []})
    for m in MODELS:
        if not m["out"] or not m["created"]:
            continue
        dt = datetime.datetime.fromtimestamp(m["created"], datetime.UTC)
        key = "%04d-%02d" % (dt.year, dt.month)
        bucket[key]["open" if m["open_w"] else "closed"].append(m["out"])
    series = []
    for k in sorted(bucket):
        a, b = bucket[k]["open"], bucket[k]["closed"]
        series.append(dict(month=k, n_open=len(a), n_closed=len(b),
                           med_open=round(float(np.median(a)), 2) if a else None,
                           med_closed=round(float(np.median(b)), 2) if b else None))

    def vintage(months):
        a = [x for k in months for x in bucket[k]["open"]]
        b = [x for k in months for x in bucket[k]["closed"]]
        return (round(float(np.median(a)), 2), round(float(np.median(b)), 2)) if a and b else (None, None)

    keys = sorted(bucket)
    first_v = vintage(keys[:6])
    last_v = vintage(keys[-6:])

    # 各家实验室的双层价目：在 28 个代表模型内比较（规则见正文 3.3），
    # 商品层＝该实验室可自托管的开放权重代表里最便宜的一个；
    # 旗舰层＝该实验室闭源代表里最贵的一个。用 28 例而非全库，是为了避免
    # 免费档、试用档与超长上下文附加价把极值拉爆（全库极值见附录 D）。
    tiers = []
    for lab in LABS:
        ms = [BY_ID[i] for i in FLAGSHIPS if i in BY_ID and BY_ID[i]["lab"] == lab and BY_ID[i]["out"]]
        cheap = [m for m in ms if m["open_w"]]
        dear = [m for m in ms if not m["open_w"]]
        com = min((m["out"] for m in cheap), default=None)
        top = max((m["out"] for m in dear), default=None)
        tiers.append(dict(
            lab=lab, n=len(ms),
            commodity=com, commodity_models=[m["id"] for m in cheap if m["out"] == com][:2],
            flag=top, flag_models=[m["id"] for m in dear if m["out"] == top][:2],
            premium=round(top / com, 1) if (com and top) else None,
            spread=round(max(m["out"] for m in ms) / min(m["out"] for m in ms), 1) if ms else None,
        ))

    prov = [(m["providers"], m["out"], m["rjs"], m["id"]) for m in MODELS
            if m["providers"] is not None and m["out"]]
    return dict(
        snapshot=SNAPSHOT, n_models=len(MODELS),
        n_open=sum(1 for m in MODELS if m["open_w"]),
        n_rjs=len(rs), rjs_med=round(float(np.median(rs)), 1), rjs_p25=round(_pct(rs, 25), 1),
        rjs_p75=round(_pct(rs, 75), 1), rjs_p90=round(_pct(rs, 90), 1), rjs_max=round(max(rs), 1),
        rjs_open=(len(ro), round(float(np.median(ro)), 1)),
        rjs_closed=(len(rc), round(float(np.median(rc)), 1)),
        lab_rjs=lab_rjs,
        out_open=(len(po), round(float(np.median(po)), 2), round(_pct(po, 75), 2)),
        out_closed=(len(pc), round(float(np.median(pc)), 2), round(_pct(pc, 25), 2)),
        out_ratio=round(float(np.median(pc)) / float(np.median(po)), 1),
        series=series, vintage_first=first_v, vintage_last=last_v,
        tiers=tiers, prov=prov,
    )


def confounds():
    """RJS 的三个混淆变量（正文 4.7）：上下文长度、上线时间、托管商数。"""
    from scipy import stats as st
    M = [m for m in MODELS if m["rjs"]]
    out = {}
    for name, key in [("ctx", "ctx"), ("created", "created")]:
        v = [(m[key], m["rjs"]) for m in M if m[key]]
        r = st.spearmanr([a for a, b in v], [b for a, b in v])
        out[name] = (len(v), round(r.statistic, 3), float(r.pvalue))
    v = [(m["providers"], m["rjs"]) for m in M if m["providers"]]
    r = st.spearmanr([a for a, b in v], [b for a, b in v])
    out["providers"] = (len(v), round(r.statistic, 3), float(r.pvalue))

    cs = sorted(m["ctx"] for m in M if m["ctx"])
    qs = [float(np.percentile(cs, q)) for q in (25, 50, 75)]

    def grp(c):
        return "Q1" if c <= qs[0] else ("Q2" if c <= qs[1] else ("Q3" if c <= qs[2] else "Q4"))

    import collections
    d = collections.defaultdict(lambda: {"o": [], "c": []})
    for m in M:
        if m["ctx"]:
            d[grp(m["ctx"])]["o" if m["open_w"] else "c"].append(m["rjs"])
    out["quartile"] = {}
    for k in ("Q1", "Q2", "Q3", "Q4"):
        o, c = d[k]["o"], d[k]["c"]
        out["quartile"][k] = (len(o), round(float(np.median(o)), 1) if o else None,
                              len(c), round(float(np.median(c)), 1) if c else None)
    out["ctx_med"] = (round(float(np.median([m["ctx"] for m in M if m["open_w"]])) / 1000),
                      round(float(np.median([m["ctx"] for m in M if not m["open_w"]])) / 1000))
    # 按上下文四分位的中位 RJS（不分开放闭源）
    allq = collections.defaultdict(list)
    for m in M:
        if m["ctx"]:
            allq[grp(m["ctx"])].append(m["rjs"])
    out["quartile_all"] = [(k, len(allq[k]), round(float(np.median(allq[k])), 1)) for k in ("Q1", "Q2", "Q3", "Q4")]
    return out


S = stats()
CF = confounds()


if __name__ == "__main__":
    s = stats()
    print("快照 %s：模型 %d（开放权重 %d）" % (s["snapshot"], s["n_models"], s["n_open"]))
    print("RJS n=%d 中位 %.1f  p25 %.1f  p75 %.1f  p90 %.1f  max %.0f"
          % (s["n_rjs"], s["rjs_med"], s["rjs_p25"], s["rjs_p75"], s["rjs_p90"], s["rjs_max"]))
    print("RJS 开放 %s  闭源 %s" % (s["rjs_open"], s["rjs_closed"]))
    for lab in LABS:
        n, med = s["lab_rjs"][lab]
        print("   %-11s n=%-3d 中位 %s" % (lab, n, med))
    print("输出价 开放 %s  闭源 %s  比值 %.1f" % (s["out_open"], s["out_closed"], s["out_ratio"]))
    print("新模型标价中位 前六个月 %s  后六个月 %s" % (s["vintage_first"], s["vintage_last"]))
    print("双层价目：")
    for t in s["tiers"]:
        print("   %-11s 商品层 %-7s 旗舰层 %-7s 溢价 %-6s 内部价差 %-6s"
              % (t["lab"], t["commodity"], t["flag"], t["premium"], t["spread"]))

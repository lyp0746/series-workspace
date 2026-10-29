#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""存活度的无偏度量：用 total_count 而不是抽样。

搜索接口的排序只有 stars/forks/updated 三档，用 page 抽样必然偏向热门仓库
（实测：按默认相关度取前 200 条，零星仓库占比是 0%，而全库零星占比显然远高）。
所以退回"计数"这个不会被排序污染的量：
    存活率(队列) = count(队列 ∩ pushed:>=2026-10-16) / count(队列)
pushed 截止日 2026-10-16 给所有队列至少 7 天的观察窗。
"""
import json, time, urllib.parse, urllib.request, urllib.error, pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
COUNTS = BASE / "data" / "counts.json"
UA = "HarnessEcology-Paper/1.0"
SEARCH = "https://api.github.com/search/repositories"
CUT = "2026-10-16"

COHORT_Q = {
    "dsh|p1": "topic:dsh-plugin created:2026-08-13..2026-08-19",
    "dsh|p2": "topic:dsh-plugin created:2026-08-20..2026-08-31",
    "dsh|p3": "topic:dsh-plugin created:2026-09-01..2026-09-30",
    "dsh|p4a": "topic:dsh-plugin created:2026-10-01..2026-10-09",
    "skills|jan": "topic:agent-skills created:2026-01-01..2026-01-31",
    "skills|jun": "topic:agent-skills created:2026-06-01..2026-06-30",
    "skills|sept": "topic:agent-skills created:2026-09-01..2026-09-30",
    "skills|octa": "topic:agent-skills created:2026-10-01..2026-10-09",
}

def count(q):
    url = SEARCH + "?" + urllib.parse.urlencode({"q": q, "per_page": 1})
    for k in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r).get("total_count")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                print(f"  403 {q}, wait 75s", flush=True); time.sleep(75); continue
            print(f"  HTTP {e.code} {q}", flush=True); return None
        except Exception as e:
            print(f"  ERR {e}", flush=True); time.sleep(10)
    return None

done = {r["key"]: r for r in json.loads(COUNTS.read_text(encoding="utf-8"))}
jobs = []
for name, q in COHORT_Q.items():
    jobs.append((f"ret|{name}|base", q))
    jobs.append((f"ret|{name}|active7", f"{q} pushed:>={CUT}"))
    jobs.append((f"ret|{name}|active7_star10", f"{q} pushed:>={CUT} stars:>=10"))
for key, q in jobs:
    if key in done and done[key].get("total_count") is not None:
        continue
    c = count(q)
    done[key] = {"key": key, "query": q, "total_count": c}
    COUNTS.write_text(json.dumps([done[k] for k in sorted(done)], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{key:26s} -> {c}", flush=True)
    time.sleep(7)
print("done", flush=True)

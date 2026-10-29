#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""取 GitHub 公开搜索接口的一手计数（可断点续跑）。

产出：
  data/raw/NNN_<key>.json   每一次查询的原始响应（含 total_count、抓取时间）
  data/counts.json          扁平结果表，已完成的 key 会被跳过（续跑安全）

未认证接口：search 10 次/分钟。脚本按 7 秒/次、每 8 次歇 62 秒的节奏跑，
遇到 403 就等 75 秒重试——宁可慢，不留空值。
"""
import json, time, urllib.parse, urllib.request, urllib.error, datetime, pathlib, calendar

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
COUNTS = BASE / "data" / "counts.json"
UA = "HarnessEcology-Paper/1.0"
SEARCH = "https://api.github.com/search/repositories"
SLEEP, BATCH, PAUSE = 7.0, 8, 62

def fetch(query, per_page=1, sort=None, tries=6):
    params = {"q": query, "per_page": per_page}
    if sort:
        params["sort"] = sort; params["order"] = "desc"
    url = SEARCH + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                body = json.load(r)
                body["_query"] = query
                body["_fetched_at"] = datetime.datetime.now().isoformat(timespec="seconds")
                return body, None
        except urllib.error.HTTPError as e:
            detail = e.read()[:200].decode(errors="replace")
            if e.code in (403, 429):
                print(f"  403 on {query!r} (try {k+1}), wait 75s", flush=True)
                time.sleep(75); continue
            return None, f"HTTP {e.code} {detail}"
        except Exception as e:
            print(f"  ERR {query!r}: {e}", flush=True); time.sleep(10)
    return None, "exhausted retries"

def jobs():
    J = []
    for t in ["topic:dsh-plugin", "topic:agent-skills"]:
        J.append((f"{t}|top50", t, 50, "stars"))
    J.append(("overlap|dsh-plugin+agent-skills", "topic:dsh-plugin topic:agent-skills", 1, None))
    J.append(("dsh|pre2026", "topic:dsh-plugin created:<2026-01-01", 1, None))
    J.append(("skills|pre2025", "topic:agent-skills created:<2025-01-01", 1, None))

    DSHP = [("pre", "created:<2026-08-13"),
            ("p1", "created:2026-08-13..2026-08-19"),
            ("p2", "created:2026-08-20..2026-08-31"),
            ("p3", "created:2026-09-01..2026-09-30"),
            ("p4", "created:2026-10-01..2026-10-23")]
    for name, rng in DSHP:
        specs = [("all", ""), ("star10", " stars:>=10 fork:false")]
        if name in ("p1", "p3", "p4"):
            specs.append(("star100", " stars:>=100 fork:false"))
        for thr, extra in specs:
            J.append((f"dsh|{name}|{thr}", f"topic:dsh-plugin {rng}{extra}", 1, None))

    d0 = datetime.date(2026, 8, 6)
    for i in range(19):
        day = (d0 + datetime.timedelta(days=i)).isoformat()
        J.append((f"dsh|day|{day}", f"topic:dsh-plugin created:{day}", 1, None))

    SK = [("pre", "created:<2025-09-22"),
          ("s0", "created:2025-09-22..2025-10-31"),
          ("s1", "created:2025-11-01..2025-11-30"),
          ("s2", "created:2025-12-01..2025-12-31")]
    for y, m in [(2026, m) for m in range(1, 9)] + [(2025, m) for m in (10, 11, 12)]:
        if (y, m) in ((2025, 11), (2025, 12)): continue
        last = calendar.monthrange(y, m)[1]
        SK.append((f"s{y}{m:02d}", f"created:{y}-{m:02d}-01..{y}-{m:02d}-{last}"))
    SK.append(("s202610", "created:2026-10-01..2026-10-23"))
    for name, rng in SK:
        for thr, extra in [("all", ""), ("star10", " stars:>=10 fork:false")]:
            J.append((f"skills|{name}|{thr}", f"topic:agent-skills {rng}{extra}", 1, None))
    return J

def main():
    done = {}
    if COUNTS.exists():
        try:
            done = {r["key"]: r for r in json.loads(COUNTS.read_text(encoding="utf-8"))}
        except Exception:
            done = {}
    J = jobs()
    todo = [j for j in J if j[0] not in done or done[j[0]]["total_count"] is None]
    print(f"{len(J)} queries, {len(todo)} to do", flush=True)
    for i, (key, q, per_page, sort) in enumerate(todo, 1):
        body, err = fetch(q, per_page, sort)
        rec = {"key": key, "query": q, "per_page": per_page}
        if body is None:
            rec.update(total_count=None, error=err)
        else:
            rec.update(total_count=body.get("total_count"), fetched_at=body.get("_fetched_at"))
            safe = key.replace("|", "__").replace(" ", "_").replace(":", "").replace("*", "x").replace("&", "and").replace("+", "plus")
            (RAW / f"{safe}.json").write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        done[key] = rec
        COUNTS.write_text(json.dumps([done[k] for k in sorted(done)], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{i}/{len(todo)}] {key:34s} -> {rec['total_count']} {err or ''}", flush=True)
        time.sleep(SLEEP)
        if i % BATCH == 0:
            print("  pause 62s", flush=True); time.sleep(PAUSE)
    miss = [k for k, r in done.items() if r.get("total_count") is None]
    print("missing:", miss, flush=True)

if __name__ == "__main__":
    main()

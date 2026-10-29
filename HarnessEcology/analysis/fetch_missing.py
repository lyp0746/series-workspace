import json, time, urllib.parse, urllib.request, urllib.error, pathlib
BASE = pathlib.Path(__file__).resolve().parent.parent
COUNTS = BASE / "data" / "counts.json"; UA = "HarnessEcology-Paper/1.0"
S = "https://api.github.com/search/repositories"
J = [("skills|s202609|all", "topic:agent-skills created:2026-09-01..2026-09-30"),
     ("skills|s202609|star10", "topic:agent-skills created:2026-09-01..2026-09-30 stars:>=10 fork:false")]
done = {r["key"]: r for r in json.loads(COUNTS.read_text(encoding="utf-8"))}
for key, q in J:
    url = S + "?" + urllib.parse.urlencode({"q": q, "per_page": 1})
    for k in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                c = json.load(r).get("total_count"); break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429): print("403 wait", flush=True); time.sleep(75); continue
            c = None; break
        except Exception as e:
            print("ERR", e, flush=True); time.sleep(8)
    done[key] = {"key": key, "query": q, "total_count": c}
    print(key, c, flush=True)
    COUNTS.write_text(json.dumps([done[k] for k in sorted(done)], ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(7)

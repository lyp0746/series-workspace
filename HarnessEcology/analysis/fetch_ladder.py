import json,time,urllib.parse,urllib.request,urllib.error,pathlib
BASE=pathlib.Path(__file__).resolve().parent.parent; COUNTS=BASE/"data"/"counts.json"
UA="HarnessEcology-Paper/1.0"; S="https://api.github.com/search/repositories"
PER={"p1":"created:2026-08-13..2026-08-19","p2":"created:2026-08-20..2026-08-31",
     "p3":"created:2026-09-01..2026-09-30","p4":"created:2026-10-01..2026-10-23"}
J=[]
for p,rng in PER.items():
    for k in (1,1000):
        J.append((f"lad|dsh|{p}|star{k}", f"topic:dsh-plugin {rng} stars:>={k} fork:false"))
done={r["key"]:r for r in json.loads(COUNTS.read_text(encoding="utf-8"))}
for key,q in J:
    if key in done and done[key].get("total_count") is not None: continue
    url=S+"?"+urllib.parse.urlencode({"q":q,"per_page":1}); c=None
    for i in range(6):
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req,timeout=45) as r: c=json.load(r).get("total_count"); break
        except urllib.error.HTTPError as e:
            if e.code in (403,429): time.sleep(75); continue
            c=None; break
        except Exception: time.sleep(8)
    done[key]={"key":key,"query":q,"total_count":c}
    print(key,c,flush=True); time.sleep(7)
COUNTS.write_text(json.dumps([done[k] for k in sorted(done)],ensure_ascii=False,indent=1),encoding="utf-8")

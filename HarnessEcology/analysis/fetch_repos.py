import json,urllib.request,urllib.parse,time,pathlib
BASE=pathlib.Path(__file__).resolve().parent.parent
UA="HarnessEcology-Paper/1.0"
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req,timeout=40) as r: return json.load(r)
    except Exception as e:
        return {"_error":str(e)}
out={}
for fn in ["deepseek-ai/deepseek-harness","anthropics/skills"]:
    d=get(f"https://api.github.com/repos/{fn}")
    out[fn]={k:d.get(k) for k in ("full_name","created_at","pushed_at","stargazers_count","forks_count","description","homepage","license","topics","language")}
    if isinstance(d.get("license"),dict): out[fn]["license"]=d["license"].get("spdx_id")
    print(fn, out[fn]["created_at"], out[fn]["stargazers_count"], (out[fn]["description"] or "")[:90], flush=True)
    time.sleep(2)
for q in ["agentskills in:name","koishi in:name","cordis in:name"]:
    url="https://api.github.com/search/repositories?"+urllib.parse.urlencode({"q":q,"per_page":5,"sort":"stars","order":"desc"})
    d=get(url)
    items=[(i["full_name"],i["created_at"][:10],i["stargazers_count"],(i.get("description") or "")[:70]) for i in d.get("items",[])]
    out["search:"+q]=items
    print(q, items, flush=True)
    time.sleep(6)
(BASE/"data"/"repos.json").write_text(json.dumps(out,ensure_ascii=False,indent=1),encoding="utf-8")

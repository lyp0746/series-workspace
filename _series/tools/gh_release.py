# -*- coding: utf-8 -*-
"""为每个书籍仓库建/补一个 release（tag v2026.10.30），并上传 release/ 下全部文件。"""
import urllib.request, urllib.parse, json, os, io, sys
tok=open(os.path.join(os.path.dirname(__file__),"..","ghtok")).read().strip()
BOOKS=["knowledge-tradeoffs","distinction-evolution","capacity-cascade","entropy-spiral",
       "impossibility-triangle","interpretation-tradeoff","emergence-critical","hotspot-bills","mind-forks"]
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
TAG="v2026.10.30"

def call(url, method="GET", data=None, ctype="application/json", tries=3):
    for i in range(tries):
        try:
            r=urllib.request.Request(url,data=data,method=method,
                headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json",
                         "User-Agent":"pi","Content-Type":ctype})
            with urllib.request.urlopen(r,timeout=600) as x:
                return x.status, json.loads(x.read() or b"{}")
        except urllib.error.HTTPError as e:
            body=e.read()[:200]
            if i==tries-1: return e.code, {"err":body.decode("utf-8","replace")}
        except Exception as e:
            if i==tries-1: return 0, {"err":str(e)}

for b in BOOKS:
    st,rel=call(f"https://api.github.com/repos/lyp0746/{b}/releases/tags/{TAG}")
    if st!=200: print(b,"取 release 失败",st,rel.get("err")); continue
    rid=rel["id"]; have={a["name"] for a in rel.get("assets",[])}
    d=os.path.join(ROOT,b,"release"); up=0; fail=[]
    for f in sorted(os.listdir(d)):
        p=os.path.join(d,f)
        if not os.path.isfile(p) or f in have: continue
        data=open(p,'rb').read()
        url=f"https://uploads.github.com/repos/lyp0746/{b}/releases/{rid}/assets?name={urllib.parse.quote(f)}"
        s,_=call(url,"POST",data,"application/octet-stream")
        if s in (200,201): up+=1
        else: fail.append((f,s))
    print(f"{b:24} 已传 {up} 个，失败 {len(fail)} {fail[:2]}")

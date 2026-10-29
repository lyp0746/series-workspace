# -*- coding: utf-8 -*-
"""只补缺失文件 + PUT 元数据 + 发布；每步短超时、失败即停，可反复重跑。"""
import argparse, json, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
API = "https://zenodo.org/api"
TOK = pathlib.Path(r"D:\0_Article\zenodo_token.txt").read_text(encoding="utf-8").strip()

def call(method, url, data=None, raw=None, headers=None, timeout=150, tries=2):
    h = {"Authorization": "Bearer " + TOK, "User-Agent": "finish/1.0", "Accept": "application/json"}
    if headers: h.update(headers)
    body = raw
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8"); h.setdefault("Content-Type","application/json")
    for i in range(tries):
        r = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                t = resp.read().decode("utf-8","replace")
                return json.loads(t) if t.strip().startswith(("{","[")) else t
        except urllib.error.HTTPError as e:
            d = e.read().decode("utf-8","replace")
            print("  HTTP", e.code, d[:120], flush=True)
            if e.code in (429,500,502,503,504) and i+1 < tries: time.sleep(8); continue
            return None
        except Exception as e:
            print("  ERR", type(e).__name__, flush=True)
            if i+1 < tries: time.sleep(8); continue
            return None
    return None

ap = argparse.ArgumentParser()
ap.add_argument("--record", required=True); ap.add_argument("--repo", required=True)
ap.add_argument("--publish", action="store_true")
ap.add_argument("--fresh", action="store_true")
a = ap.parse_args()
root = pathlib.Path(a.repo); rel = root/"release"
files = sorted(p for p in rel.iterdir() if p.is_file())
meta = json.loads((root/".zenodo.json").read_text(encoding="utf-8"))
d = call("GET", f"{API}/deposit/depositions/{a.record}?size=1")
did = d["id"]; bucket = d["links"]["bucket"]
if a.fresh:
    for f in d.get("files", []):
        fid = f.get("id")
        if fid:
            call("DELETE", f"{API}/deposit/depositions/{did}/files/{fid}?size=1", timeout=120, tries=2)
    d = call("GET", f"{API}/deposit/depositions/{did}?size=1")
have = {f.get("filename") or f.get("key") for f in d.get("files", [])}
missing = [p for p in files if p.name not in have]
print(f"draft {did} | on record {len(have)} | release {len(files)} | missing {len(missing)}", flush=True)
for p in missing:
    out = call("PUT", "%s/%s" % (bucket, urllib.parse.quote(p.name)), raw=p.read_bytes(),
               headers={"Content-Type":"application/octet-stream"}, timeout=300, tries=3)
    print(("   + " if out is not None else "   ! ") + p.name, flush=True)
    if out is None: print("   stop: retry later", flush=True); sys.exit(2)
out = call("PUT", f"{API}/deposit/depositions/{did}?size=1", {"metadata": meta}, timeout=240, tries=3)
print("metadata", "ok" if out is not None else "FAILED", flush=True)
if out is None: sys.exit(3)
if a.publish:
    out = call("POST", f"{API}/deposit/depositions/{did}/actions/publish?size=1", timeout=300, tries=3)
    print("PUBLISHED" if isinstance(out, dict) else "publish FAILED", (out or {}).get("doi") if isinstance(out, dict) else "", flush=True)

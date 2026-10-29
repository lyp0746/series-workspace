# -*- coding: utf-8 -*-
"""清空草稿文件 → 上传 release/ 白名单 → 元数据 → 发布（只这两篇）。"""
import io, os, re, sys, glob, json, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import api
from publish_two_v3 import title_of, descr, CREATOR, SHARED, MONO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clear(rec):
    _, d = api.req("GET", f"https://zenodo.org/api/records/{rec}/draft", tries=2, timeout=90)
    for f in d.get("files", []):
        api.req("DELETE", f"https://zenodo.org/api/records/{rec}/draft/files/{urllib.parse.quote(f['key'])}", tries=2, timeout=90)
    return len(d.get("files", []))

def upload(rec, folder):
    keys = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(folder, "*"))) if os.path.isfile(p)]
    api.req("POST", f"https://zenodo.org/api/records/{rec}/draft/files", data=[{"key": k} for k in keys], tries=2, timeout=180)
    for k in keys:
        r = urllib.request.Request(f"https://zenodo.org/api/records/{rec}/draft/files/{urllib.parse.quote(k)}/content",
            data=open(os.path.join(folder, k), "rb").read(), method="PUT",
            headers={"Authorization": "Bearer " + api.TOK, "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(r, timeout=900) as x: x.read()
    return len(keys)

JOBS = [("OptimizationBoundary", None)]
for slug, rec in JOBS:
    if rec is None:
        _, d = api.req("POST", "https://zenodo.org/api/records/23774015/versions", tries=2, timeout=120)
        rec = d.get("id") or d["links"]["self"].rstrip("/").split("/")[-1]
    n0 = clear(rec)
    n = upload(rec, os.path.join(ROOT, slug, "release"))
    meta = {"title": title_of(slug), "description": descr(slug), "creators": [CREATOR],
            "publication_date": "2026-10-30", "version": "2026-10-30",
            "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
            "languages": [{"id": "zho"}], "publisher": "Zenodo",
            "related_identifiers": [{"identifier": SHARED, "scheme": "url",
                                     "relation_type": {"id": "issupplementedby"}}] +
                [{"identifier": v, "scheme": "doi", "relation_type": {"id": "ispartof"}} for v in MONO.values()]}
    api.req("PUT", f"https://zenodo.org/api/records/{rec}/draft", data={"metadata": meta}, tries=2, timeout=180)
    _, pub = api.req("POST", f"https://zenodo.org/api/records/{rec}/draft/actions/publish", tries=2, timeout=180)
    print(f"{slug:22} {pub.get('doi')} 清除 {n0} → 上传 {n} 文件", flush=True)

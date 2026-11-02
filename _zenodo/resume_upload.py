# -*- coding: utf-8 -*-
"""Resume a Zenodo RDM draft: upload missing files, PUT metadata, optionally publish.

Usage: python _zenodo/resume_upload.py <slug> <draft_id> [--publish]
Robust to SSL EOF / 5xx: retries each step with backoff; skips existing files.
"""
import json, os, sys, time, urllib.parse
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api, republish_book as rb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {"Authorization": "Bearer " + api.TOK}
S = requests.Session()


def call(method, url, **kw):
    last = None
    for i in range(8):
        try:
            hdr = dict(H); hdr.update(kw.pop("headers", {}) or {})
            r = S.request(method, url, headers=hdr, timeout=kw.pop("timeout", 180), **kw)
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {r.status_code}"
                time.sleep(4 * (i + 1)); continue
            r.raise_for_status()
            return r
        except Exception as e:
            last = repr(e)
            print("   retry", method, url.split('/')[-1][:40], last[:120], flush=True)
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"failed {method} {url}: {last}")


def main():
    slug, did = sys.argv[1], sys.argv[2]
    publish = "--publish" in sys.argv
    base = f"https://zenodo.org/api/records/{did}/draft/files"
    r = call("GET", base)
    entries = r.json().get("entries") or []
    # drop uncommitted entries (no size) so they do not block re-upload
    for e in entries:
        if not e.get("size"):
            print("  - drop uncommitted", e.get("key"), flush=True)
            call("DELETE", f"{base}/{urllib.parse.quote(e['key'])}", timeout=120)
    r = call("GET", base)
    have = {e.get("key") for e in (r.json().get("entries") or []) if e.get("size")}
    folder = os.path.join(ROOT, slug, "release")
    names = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    print("draft", did, "have", len(have), "release", len(names), flush=True)
    for name in names:
        if name in have:
            print("  = skip", name, flush=True); continue
        p = os.path.join(folder, name)
        data = open(p, "rb").read()
        print("  +", name, len(data)//1024, "KB", flush=True)
        r = call("POST", base, json=[{"key": name}], timeout=300)
        entries = r.json().get("entries") or []
        ent = next((e for e in entries if e.get("key") == name), None)
        if ent is None:
            # Zenodo sometimes returns the single created entry directly
            if r.json().get("key") == name: ent = r.json()
        assert ent, f"no entry for {name}: {r.text[:300]}"
        call("PUT", ent["links"]["content"], data=data,
             headers={**H, "Content-Type": "application/octet-stream"}, timeout=1800)
        call("POST", f"{base}/{urllib.parse.quote(name)}/commit", timeout=600)
    # metadata
    _, d = api.req("GET", f"https://zenodo.org/api/records/{did}/draft", tries=2, timeout=120)
    meta = rb.metadata(slug, d)
    r = call("PUT", f"https://zenodo.org/api/records/{did}/draft", json=meta, timeout=300)
    got = r.json().get("metadata", {})
    print("  meta:", got.get("title","")[:70], "| rights", bool(got.get("rights")),
          "| subjects", len(got.get("subjects") or []), "| related", len(got.get("related_identifiers") or []),
          "| stars", (got.get("description") or "").count("*"), flush=True)
    if publish:
        r = call("POST", f"https://zenodo.org/api/records/{did}/draft/actions/publish", timeout=600)
        out = r.json()
        print("PUBLISHED", out.get("doi"), "| concept", out.get("conceptdoi"), flush=True)
    else:
        print("ready to publish", did, flush=True)


if __name__ == "__main__":
    main()

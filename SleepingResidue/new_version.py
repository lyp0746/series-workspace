# -*- coding: utf-8 -*-
"""Publish a NEW VERSION of a published Zenodo record from release/.

    python new_version.py --record 23497842 [--publish]

Flow: newversion -> draft -> delete inherited files -> upload release/ -> PUT metadata -> publish.
Published records are immutable; a new version is the supported way to replace files.
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://zenodo.org/api"
ROOT = Path(__file__).parent
TOKEN_FILE = ROOT.parent / "zenodo_token.txt"
QS = "?size=1"


def token():
    t = os.environ.get("ZENODO_TOKEN")
    if not t and TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not t:
        raise SystemExit("no token")
    return t


def req(method, url, tok, data=None, raw=None, headers=None, tries=4):
    h = {"Authorization": "Bearer " + tok}
    if headers:
        h.update(headers)
    body = raw
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    last = None
    for i in range(tries):
        r = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=600) as resp:
                txt = resp.read().decode("utf-8", "replace")
                return resp.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and i + 1 < tries:
                print("   retry HTTP", e.code)
                time.sleep(8 * (i + 1)); last = detail; continue
            raise RuntimeError("HTTP %d %s %s\n%s" % (e.code, method, url, detail[:1500]))
        except Exception as e:
            last = str(e)
            if i + 1 < tries:
                print("   retry", type(e).__name__)
                time.sleep(8 * (i + 1)); continue
            raise
    raise RuntimeError(last)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True)
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--release", default="release")
    args = ap.parse_args()
    tok = token()
    rel = ROOT / args.release
    files = sorted(p for p in rel.iterdir() if p.is_file())
    meta = json.load(open(ROOT / ".zenodo.json", encoding="utf-8"))
    print("files:", len(files))

    _, r = req("POST", "%s/deposit/depositions/%s/actions/newversion%s" % (API, args.record, QS), tok)
    draft_url = r["links"]["latest_draft"]
    _, d = req("GET", draft_url + QS, tok)
    did = d["id"]
    bucket = d["links"]["bucket"]
    print("new draft:", did, d["links"].get("html"))

    # remove inherited files
    for f in d.get("files", []):
        fid = f.get("id")
        name = f.get("filename") or f.get("key")
        if fid:
            req("DELETE", "%s/deposit/depositions/%s/files/%s%s" % (API, did, fid, QS), tok)
            print("   -", name)

    for p in files:
        url = "%s/%s" % (bucket, urllib.parse.quote(p.name))
        with open(p, "rb") as fh:
            req("PUT", url, tok, raw=fh.read(),
                headers={"Content-Type": "application/octet-stream"})
        print("   +", p.name)

    req("PUT", "%s/deposit/depositions/%s%s" % (API, did, QS), tok, data={"metadata": meta})
    print("metadata updated")

    if args.publish:
        _, d2 = req("GET", "%s/deposit/depositions/%s%s" % (API, did, QS), tok)
        print("files on draft:", len(d2.get("files", [])))
        _, d3 = req("POST", "%s/deposit/depositions/%s/actions/publish%s" % (API, did, QS), tok)
        print("PUBLISHED new version")
        print("  DOI:        ", d3.get("doi"))
        print("  concept DOI:", d3.get("conceptdoi"))
        print("  URL:        ", d3.get("links", {}).get("html") or d3.get("links", {}).get("self_html"))
    else:
        print("draft left unpublished:", did)


if __name__ == "__main__":
    main()

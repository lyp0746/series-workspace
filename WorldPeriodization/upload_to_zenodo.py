# -*- coding: utf-8 -*-
"""Create a Zenodo record for the paper and upload release/ files.

Follows the pattern of zenodo.org/records/23480796 (Hunan relay paper):
flat file list, PDF prefixed 00-, HTML, Markdown, figures, CSV, README, MANIFEST.

Usage:
    python upload_to_zenodo.py                 # create draft + upload, leave unpublished
    python upload_to_zenodo.py --record ID     # reuse a draft
    python upload_to_zenodo.py --record ID --publish

Notes
-----
* zenodo.org's WAF answers 403 to bare /api/deposit/... requests from some networks;
  appending a harmless query parameter (?size=1) is enough to pass.
* The token is read from $ZENODO_TOKEN or ../zenodo_token.txt.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://zenodo.org/api"
ROOT = Path(__file__).parent
TOKEN_FILE = ROOT.parent / "zenodo_token.txt"
QS = "?size=1"          # WAF workaround


def token():
    t = os.environ.get("ZENODO_TOKEN")
    if not t and TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not t:
        raise SystemExit("No token: set $ZENODO_TOKEN or put it in ../zenodo_token.txt")
    return t


def req(method, url, tok, data=None, raw=None, headers=None, tries=3):
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
                print("   retry after HTTP %d ..." % e.code)
                time.sleep(5 * (i + 1))
                last = detail
                continue
            raise RuntimeError("HTTP %d %s %s\n%s" % (e.code, method, url, detail[:2000]))
        except Exception as e:            # timeouts, connection resets
            last = str(e)
            if i + 1 < tries:
                print("   retry after %s ..." % type(e).__name__)
                time.sleep(5 * (i + 1))
                continue
            raise
    raise RuntimeError("failed: %s" % last)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", default=None, help="existing draft id")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    tok = token()
    meta = json.load(open(ROOT / ".zenodo.json", encoding="utf-8"))
    rel = ROOT / "release"
    files = sorted([p for p in rel.iterdir() if p.is_file()])
    if not files:
        raise SystemExit("release/ is empty; run release.sh first")
    print("files: %d, %.1f MB" % (len(files), sum(p.stat().st_size for p in files) / 1e6))
    for p in files:
        print("   %-46s %8.1f KB" % (p.name, p.stat().st_size / 1024))

    if args.record:
        _, d = req("GET", "%s/deposit/depositions/%s%s" % (API, args.record, QS), tok)
        did = d["id"]
        print("draft:", did, d["links"].get("html"))
    else:
        _, d = req("POST", API + "/deposit/depositions" + QS, tok, data={"metadata": meta})
        did = d["id"]
        print("created draft:", did, d["links"].get("html"))

    bucket = d["links"]["bucket"]
    existing = {f.get("key") or f.get("filename") for f in d.get("files", [])}
    for p in files:
        if p.name in existing:
            print("   = skip existing", p.name)
            continue
        url = "%s/%s" % (bucket, urllib.parse.quote(p.name))
        with open(p, "rb") as fh:
            req("PUT", url, tok, raw=fh.read(),
                headers={"Content-Type": "application/octet-stream"})
        print("   + " + p.name)

    if args.publish:
        # re-read to confirm files landed, then publish
        _, d2 = req("GET", "%s/deposit/depositions/%s%s" % (API, did, QS), tok)
        print("files on record:", len(d2.get("files", [])))
        _, d3 = req("POST", "%s/deposit/depositions/%s/actions/publish%s" % (API, did, QS), tok)
        print("PUBLISHED")
        print("  DOI:  ", d3.get("doi"))
        print("  URL:  ", d3.get("links", {}).get("html") or d3.get("links", {}).get("self_html"))
        print("  concept DOI:", d3.get("conceptdoi"))
    else:
        print("\nDraft left unpublished. Inspect it, then:")
        print("  python upload_to_zenodo.py --record %s --publish" % did)


if __name__ == "__main__":
    sys.exit(main())

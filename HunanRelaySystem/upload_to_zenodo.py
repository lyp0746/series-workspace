# -*- coding: utf-8 -*-
"""Create a Zenodo record for the Hunan relay paper and upload release/ files."""
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error
from pathlib import Path

API = "https://zenodo.org/api"
ROOT = Path(__file__).parent
TOKEN_FILE = ROOT.parent / "zenodo_token.txt"

def token():
    t = os.environ.get("ZENODO_TOKEN")
    if not t and TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not t:
        raise SystemExit("No token")
    return t

def req(method, url, tok, data=None, raw=None, headers=None):
    h = {"Authorization": f"Bearer {tok}"}
    if headers: h.update(headers)
    body = raw
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            txt = resp.read().decode("utf-8", "replace")
            return resp.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code} {method} {url}\n{detail[:2000]}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--record", default=None, help="existing draft id (optional)")
    args = ap.parse_args()
    tok = token()
    meta = json.load(open(ROOT / ".zenodo.json", encoding="utf-8"))
    rel = ROOT / "release"
    files = [p for p in sorted(rel.iterdir()) if p.is_file()]
    print(f"files: {len(files)}")
    for p in files: print(f"  {p.name}  {p.stat().st_size}")

    if args.record:
        _, d = req("GET", f"{API}/deposit/depositions/{args.record}", tok)
    else:
        _, d = req("POST", f"{API}/deposit/depositions", tok, data={"metadata": meta})
    did = d["id"]
    bucket = d["links"]["bucket"]
    print("draft id:", did)
    print("draft html:", d["links"].get("html"))
    print("bucket:", bucket)

    if not args.record:
        # upload
        for p in files:
            url = f"{bucket}/{urllib.parse.quote(p.name)}"
            with open(p, "rb") as fh:
                req("PUT", url, tok, raw=fh.read(), headers={"Content-Type": "application/octet-stream"})
            print("  +", p.name)

    if args.publish:
        _, d2 = req("POST", f"{API}/deposit/depositions/{did}/actions/publish", tok)
        print("published:", d2.get("doi"), d2.get("links", {}).get("html"))
    else:
        print("draft left unpublished; inspect, then re-run with --record", did, "--publish")

if __name__ == "__main__":
    main()

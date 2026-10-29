# -*- coding: utf-8 -*-
"""Replace files on an existing published Zenodo record without creating a new version.

Usage:
  python _zenodo/replace_assets.py --repo hotspot-bills --record 23447353
  python _zenodo/replace_assets.py --repo hotspot-bills --record 23447353 --dry-run

It uses the deposition "edit" action, deletes the current files, uploads the
files in <repo>/release/ (the print PDF is renamed with a 00- prefix to keep
the existing ordering), updates metadata from <repo>/.zenodo.json, and
republishes the same record.
"""
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error

API = "https://zenodo.org/api"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zenodo_token.txt")


def token():
    t = os.environ.get("ZENODO_TOKEN")
    if not t:
        with open(TOKEN_FILE, encoding="utf-8") as f:
            t = f.read().strip()
    return t


def req(method, url, tok, data=None, raw=None, headers=None):
    h = {"Authorization": f"Bearer {tok}"}
    if headers:
        h.update(headers)
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
        raise RuntimeError(f"HTTP {e.code} {method} {url}\n{detail[:1000]}")


def upload_name(repo, name):
    if name.endswith("-print.pdf") and not name.startswith("00-"):
        return "00-" + name
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--record", required=True, type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    args = ap.parse_args()

    tok = token()
    repo_dir = os.path.abspath(args.repo)
    rel_dir = os.path.join(repo_dir, "release")
    meta = json.load(open(os.path.join(repo_dir, ".zenodo.json"), encoding="utf-8"))
    files = []
    for name in sorted(os.listdir(rel_dir)):
        p = os.path.join(rel_dir, name)
        if os.path.isfile(p):
            files.append((name, p))
    if len(files) != 13:
        print(f"WARNING: release has {len(files)} files (expected 13)", file=sys.stderr)

    print(f"[1/5] GET deposition {args.record}")
    _, d = req("GET", f"{API}/deposit/depositions/{args.record}", tok)
    print("      state:", d.get("state"), "submitted:", d.get("submitted"), "files:", len(d.get("files", [])))

    if args.dry_run:
        print("[dry-run] would delete:")
        for f in d.get("files", []):
            print("  -", f["filename"])
        print("[dry-run] would upload:")
        for name, p in files:
            print(f"  + {upload_name(args.repo, name)}  ({os.path.getsize(p)} bytes)")
        print("[dry-run] metadata title:", meta.get("title"))
        return

    if d.get("state") != "inprogress":
        print("[2/5] edit action")
        _, d = req("POST", f"{API}/deposit/depositions/{args.record}/actions/edit", tok)
        print("      state:", d.get("state"))
    else:
        print("[2/5] already in edit mode")

    bucket = d["links"]["bucket"]
    print("[3/5] delete existing files")
    for f in d.get("files", []):
        req("DELETE", f["links"]["self"], tok)
        print("      -", f["filename"])

    print("[4/5] upload")
    for name, p in files:
        up = upload_name(args.repo, name)
        url = f"{bucket}/{urllib.parse.quote(up)}"
        with open(p, "rb") as fh:
            req("PUT", url, tok, raw=fh.read(), headers={"Content-Type": "application/octet-stream"})
        print("      +", up, os.path.getsize(p))

    print("[5/5] metadata + publish")
    try:
        _, d = req("PUT", f"{API}/deposit/depositions/{args.record}", tok, data={"metadata": meta})
    except RuntimeError as e:
        if "subjects" in str(e):
            print("      subjects rejected; retrying without subjects")
            meta2 = {k: v for k, v in meta.items() if k != "subjects"}
            _, d = req("PUT", f"{API}/deposit/depositions/{args.record}", tok, data={"metadata": meta2})
        else:
            raise
    print("      metadata ok:", d.get("metadata", {}).get("title", "")[:60])
    if not args.no_publish:
        _, d = req("POST", f"{API}/deposit/depositions/{args.record}/actions/publish", tok)
        print("      published:", d.get("state"), "doi:", d.get("doi"), "concept:", d.get("conceptdoi"))
        print("      files:", len(d.get("files", [])))
    else:
        print("      skipped publish (--no-publish); record left editable")


if __name__ == "__main__":
    main()

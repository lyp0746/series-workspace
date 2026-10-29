# -*- coding: utf-8 -*-
"""大文件补传：逐个文件、超长超时、可重跑（已存在的跳过）。

用法：python _zenodo/push.py <draft_id> <repo_dir>
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://zenodo.org/api"
QS = "?size=1"
TOK = pathlib.Path(__file__).resolve().parent.parent.joinpath("zenodo_token.txt").read_text(encoding="utf-8").strip()


def get(url):
    for i in range(4):
        try:
            r = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOK})
            with urllib.request.urlopen(r, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except Exception as e:
            print("  get retry", type(e).__name__)
            time.sleep(5)
    raise SystemExit("get failed")


def put_big(url, path):
    data = path.read_bytes()
    for i in range(6):
        try:
            r = urllib.request.Request(url, data=data, method="PUT",
                                       headers={"Authorization": "Bearer " + TOK,
                                                "Content-Type": "application/octet-stream"})
            with urllib.request.urlopen(r, timeout=1800) as resp:
                resp.read()
                return True
        except urllib.error.HTTPError as e:
            print("  HTTP %d %s" % (e.code, e.read()[:120]))
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(10 * (i + 1))
                continue
            return False
        except Exception as e:
            print("  retry %s (%d/6)" % (type(e).__name__, i + 1))
            time.sleep(10 * (i + 1))
    return False


def main():
    did, repo = sys.argv[1], pathlib.Path(sys.argv[2])
    d = get("%s/deposit/depositions/%s%s" % (API, did, QS))
    bucket = d["links"]["bucket"]
    have = {f.get("key") or f.get("filename") for f in d.get("files", [])}
    files = sorted(p for p in (repo / "release").iterdir() if p.is_file())
    print("draft %s | on record %d | release %d" % (did, len(have), len(files)))
    for p in files:
        if p.name in have:
            print("   = skip", p.name)
            continue
        print("   + %s (%.1f MB)" % (p.name, p.stat().st_size / 1e6), flush=True)
        ok = put_big("%s/%s" % (bucket, urllib.parse.quote(p.name)), p)
        print("     ", "ok" if ok else "FAILED", flush=True)
        if not ok:
            print("stop: rerun this script later"); return 2
    d2 = get("%s/deposit/depositions/%s%s" % (API, did, QS))
    print("files on record:", len(d2.get("files", [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Zenodo 小工具：带重试的 API 调用 + 记录查询。

用法：
    python _zenodo/api.py show 23664233 [23663027 ...]
    python _zenodo/api.py list_drafts
    python _zenodo/api.py newversion <记录ID>          # 建新版本，打印 draft id
    python _zenodo/api.py meta <draft> <json文件>      # PUT 元数据
    python _zenodo/api.py publish <draft>             # 发布
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


def req(method, url, data=None, raw=None, headers=None, tries=5, timeout=600):
    h = {"Authorization": "Bearer " + TOK}
    if headers:
        h.update(headers)
    body = raw
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(url, data=body, headers=h, method=method)
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                txt = resp.read().decode("utf-8", "replace")
                return resp.status, (json.loads(txt) if txt.strip().startswith(("{", "[")) else txt)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504, 403) and i + 1 < tries:
                print("   retry HTTP %d ..." % e.code)
                time.sleep(4 * (i + 1))
                last = detail
                continue
            raise RuntimeError("HTTP %d %s %s\n%s" % (e.code, method, url, detail[:1500]))
        except Exception as e:
            print("   retry %s ..." % type(e).__name__)
            last = str(e)
            time.sleep(4 * (i + 1))
    raise RuntimeError("failed: %s" % last)


def main(argv):
    cmd = argv[1]
    if cmd == "show":
        for rid in argv[2:]:
            _, d = req("GET", "%s/records/%s%s" % (API, rid, QS))
            m = d.get("metadata") or {}
            print("%s | ver %s | concept %s | %s" % (rid, d.get("doi"), d.get("conceptdoi"), m.get("title", "")[:56]))
    elif cmd == "list_drafts":
        _, ds = req("GET", API + "/deposit/depositions" + QS)
        for d in ds:
            m = (d.get("metadata") or {})
            print("%s | files %d | %s | %s" % (d["id"], len(d.get("files", [])),
                                               d.get("submitted"), m.get("title", "")[:50]))
    elif cmd == "newversion":
        rid = argv[2]
        _, d = req("POST", "%s/deposit/depositions/%s/actions/newversion%s" % (API, rid, QS))
        _, d2 = req("GET", d["links"]["latest_draft"] + QS)
        print(d2["id"])
    elif cmd == "meta":
        did, path = argv[2], argv[3]
        meta = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        _, d = req("PUT", "%s/deposit/depositions/%s%s" % (API, did, QS), data={"metadata": meta})
        print("meta ok:", (d.get("metadata") or {}).get("title", "")[:60])
    elif cmd == "publish":
        did = argv[2]
        _, d = req("POST", "%s/deposit/depositions/%s/actions/publish%s" % (API, did, QS))
        print("PUBLISHED", d.get("doi"), d.get("conceptdoi"))
    elif cmd == "files":
        did = argv[2]
        _, d = req("GET", "%s/deposit/depositions/%s%s" % (API, did, QS))
        print("files:", len(d.get("files", [])))
        for f in d.get("files", []):
            print("  ", f.get("key") or f.get("filename"), f.get("filesize"))
        print("bucket:", d["links"]["bucket"])
    elif cmd == "delete":
        did = argv[2]
        req("DELETE", "%s/deposit/depositions/%s%s" % (API, did, QS))
        print("deleted", did)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

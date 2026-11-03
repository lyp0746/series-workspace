# -*- coding: utf-8 -*-
"""finish_publish.py — 断点续传式发布：跳过已上传文件，逐个重试，最后写元数据并发布。

用法：
    python _zenodo/finish_publish.py <slug> <draft_id>
    python _zenodo/finish_publish.py <slug> <draft_id> --nopublish
"""
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api
import republish_book as R

ROOT = R.ROOT


def sync(slug, did, tries=4):
    import requests
    base = "https://zenodo.org/api/records/%s/draft/files" % did
    H = {"Authorization": "Bearer " + api.TOK}
    have = set()
    for k in range(tries):
        try:
            r = requests.get(base, headers=H, timeout=300)
            have = {e.get("key") for e in (r.json().get("entries") or [])}
            break
        except Exception as e:
            print("   list retry", k, type(e).__name__)
            time.sleep(8)
    folder = os.path.join(ROOT, slug, "release")
    names = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    done = 0
    for name in names:
        if name in have:
            print("   = skip", name)
            continue
        p = os.path.join(folder, name)
        data = open(p, "rb").read()
        ok = False
        for k in range(tries):
            try:
                r = requests.post(base, headers=H, json=[{"key": name}], timeout=600)
                r.raise_for_status()
                ent = next(e for e in (r.json().get("entries") or [r.json()]) if e.get("key") == name)
                r2 = requests.put(ent["links"]["content"],
                                  headers={**H, "Content-Type": "application/octet-stream"},
                                  data=data, timeout=1800)
                r2.raise_for_status()
                r3 = requests.post("%s/%s/commit" % (base, urllib.parse.quote(name)), headers=H, timeout=600)
                r3.raise_for_status()
                ok = True
                print("   + %-40s %5d MB" % (name, len(data) // 1024 // 1024))
                break
            except Exception as e:
                print("   retry", name, k, type(e).__name__)
                time.sleep(10)
        if not ok:
            # 清掉未提交的条目，否则草稿会进入 500 状态
            try:
                requests.delete("%s/%s" % (base, urllib.parse.quote(name)), headers=H, timeout=300)
                print("   - cleanup", name)
            except Exception:
                pass
            print("   !! FAIL", name)
        else:
            done += 1
    return done


if __name__ == "__main__":
    slug, did = sys.argv[1], sys.argv[2]
    n = sync(slug, did)
    print("uploaded", n)
    if "--nopublish" in sys.argv:
        sys.exit(0)
    R.meta(slug, did)
    R.publish(did)

# -*- coding: utf-8 -*-
"""Zenodo 可续传：按 release/ 目录逐个上传，已完成跳过；单文件长超时 + 重试。

用法：
    python _zenodo/upload_resume.py <slug> <draft_id>
"""
import io
import os
import sys
import time
import urllib.parse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_zenodo"))
import api


def main(slug, did):
    base = f"https://zenodo.org/api/records/{did}/draft/files"
    H = {"Authorization": "Bearer " + api.TOK}
    done = set()
    r = requests.get(base, headers=H, timeout=300)
    for f in (r.json().get("entries") or []):
        if f.get("status") == "completed":
            done.add(f.get("key"))
    folder = os.path.join(ROOT, slug, "release")
    names = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    for name in names:
        if name in done:
            print("  =", name, "(completed)")
            continue
        path = os.path.join(folder, name)
        size = os.path.getsize(path)
        for attempt in (1, 2, 3):
            try:
                rr = requests.post(base, headers=H, json=[{"key": name}], timeout=600)
                if rr.status_code == 400:
                    # 条目已存在（上次中断留下的 pending）：直接复用
                    ent = requests.get(base, headers=H, timeout=300).json().get("entries") or []
                    keys = {e.get("key") for e in ent}
                    if name not in keys:
                        rr.raise_for_status()
                with open(path, "rb") as fh:
                    rr = requests.put(f"{base}/{urllib.parse.quote(name)}/content", data=fh,
                                      headers={**H, "Content-Type": "application/octet-stream",
                                               "Content-Length": str(size)}, timeout=1800)
                rr.raise_for_status()
                rr = requests.post(f"{base}/{urllib.parse.quote(name)}/commit", headers=H, timeout=600)
                rr.raise_for_status()
                print("  +", name, round(size / 1e6, 1), "MB")
                break
            except Exception as e:
                print("  !", name, "attempt", attempt, type(e).__name__, str(e)[:120])
                time.sleep(5)
        else:
            print("  x failed", name)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))

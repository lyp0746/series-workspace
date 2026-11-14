# -*- coding: utf-8 -*-
"""为工作区仓（papers + collection）创建单一 GitHub release 并上传产物。

约定：一个 tag（edition-YYYY-MM-DD）承载全部可见产物；已存在同名资产则跳过。
Token 从 git credential helper 读取，不落盘。
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GIT = os.environ.get("GIT_BIN", r"D:\Git\cmd\git.exe")
REPO = "lyp0746/series-workspace"
PAPERS = ["ComputingDemystified", "WorldPeriodization", "SleepingResidue", "HunanRelaySystem",
          "BureauRotationCession", "HarnessEcology", "OptimizationBoundary", "CapacityProxies",
          "LedgerReconciliation", "MonarchCompetition", "DomainCrossSection", "IsomorphismStrength",
          "MemoryAnchor", "MemoryStressTest", "SeamLedger"]


def token():
    out = subprocess.run([GIT, "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                         capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    for line in out.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")


def api(tok, method, url, **kw):
    r = requests.request(method, url, headers={"Authorization": f"token {tok}",
                                               "Accept": "application/vnd.github+json"}, **kw)
    if r.status_code >= 300:
        raise SystemExit(f"{method} {url} -> {r.status_code} {r.text[:300]}")
    return r.json() if r.text else {}


def assets():
    out = []
    for p in PAPERS:
        cands = [x for x in glob.glob(os.path.join(ROOT, p, "*.pdf")) if "ereader" not in x]
        if not cands:
            continue
        src = max(cands, key=os.path.getmtime)
        out.append((src, f"{p}.pdf"))
    rel = os.path.join(ROOT, "合集", "release")
    for name in ["00-合集-印刷版.pdf", "01-合集-电子版.pdf", "合集.epub", "03-合集.md"]:
        src = os.path.join(rel, name)
        if os.path.exists(src):
            out.append((src, name))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    tag = f"edition-{a.date}"
    files = assets()
    if a.dry:
        for s, n in files:
            print(round(os.path.getsize(s) / 1e6, 1), "MB", n)
        return
    tok = token()
    base = f"https://api.github.com/repos/{REPO}"
    # 复用已有 release（同 tag）
    try:
        rel = api(tok, "GET", f"{base}/releases/tags/{tag}")
    except SystemExit:
        rel = api(tok, "POST", f"{base}/releases", json={
            "tag_name": tag, "name": f"有限系统的取舍 · {a.date}",
            "body": "24 件（九本书 + 十五篇论文）与合集；正文、图表与登记簿以同日子仓为准。",
            "draft": False, "prerelease": False})
    have = {x["name"] for x in rel.get("assets", [])}
    up = rel["upload_url"].split("{")[0]
    for src, name in files:
        if name in have:
            print("[skip]", name); continue
        size = os.path.getsize(src)
        with open(src, "rb") as fh:
            r = requests.post(f"{up}?name={requests.utils.quote(name)}", data=fh,
                              headers={"Authorization": f"token {tok}",
                                       "Content-Type": "application/octet-stream",
                                       "Content-Length": str(size)}, timeout=1800)
        print(r.status_code, name, round(size / 1e6, 1), "MB")
        if r.status_code >= 300:
            print(r.text[:200])
    print("done", rel.get("html_url"))


if __name__ == "__main__":
    main()

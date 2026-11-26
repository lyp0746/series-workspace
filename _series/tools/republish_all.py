# -*- coding: utf-8 -*-
"""把每个仓的 release/ 重新发成「一个 tag ＋ 一个 release」。

顺序是安全序（先建新的、传完再删旧的）：
  1) 建 tag（若远端没有）
  2) 建/复用该 tag 的 release
  3) 逐个上传 release/ 下的文件（大小一致视为已存在，跳过）
  4) 校验资产数 == 文件数
  5) 只有校验通过，才删除其它 release 与其它 tag

用法：  "$PY" _series/tools/republish_all.py [repo ...] --tag 2026-11-26
"""
import json, os, sys, urllib.request, urllib.error
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOK = open(os.path.join(ROOT, "_series", "ghtok")).read().strip()
H = {"Authorization": "Bearer " + TOK, "Accept": "application/vnd.github+json", "User-Agent": "pi"}
REPOS = ["knowledge-tradeoffs", "capacity-cascade", "emergence-critical", "entropy-spiral",
         "interpretation-tradeoff", "impossibility-triangle", "distinction-evolution",
         "mind-forks", "hotspot-bills", "resolution-grain", "series-workspace"]

# 文集/仓库里中文名资产 → 上传用的 ASCII 名（GitHub 对中文名不稳）
ALIAS = {"修订说明.md": "RELEASE-NOTES-zh.md", "数据缺口清单.md": "DATA-GAPS-zh.md",
         "欢迎补充数据.md": "WANTED-DATA-zh.md", "数据缺口与边界.md": "DATA-GAPS-zh.md"}


def call(url, method="GET", data=None, tries=3):
    for i in range(tries):
        try:
            r = requests.request(method, url, headers={**H, "Content-Type": "application/json"},
                                 json=data, timeout=60)
            if r.status_code in (200, 201, 204):
                return r.status_code, (r.json() if r.content else {})
            if r.status_code == 404:
                return 404, {}
        except Exception:
            pass
    return 0, {}


def do_repo(repo, tag):
    api = "https://api.github.com/repos/lyp0746/" + repo
    rel_dir = os.path.join(ROOT, repo, "release")
    if not os.path.isdir(rel_dir):
        print(f"  {repo:22} 无 release/，跳过"); return False
    files = [f for f in sorted(os.listdir(rel_dir)) if os.path.isfile(os.path.join(rel_dir, f))]
    # 1) tag
    st, ref = call(f"{api}/git/ref/tags/{tag}")
    if st == 404:
        st2, head = call(f"{api}/git/ref/heads/main")
        if st2 != 200:
            print(f"  {repo:22} 取 HEAD 失败"); return False
        call(f"{api}/git/refs", "POST", {"ref": f"refs/tags/{tag}", "sha": head["object"]["sha"]})
    # 2) release
    st, rel = call(f"{api}/releases/tags/{tag}")
    if st != 200:
        st, rel = call(f"{api}/releases", "POST", {
            "tag_name": tag, "name": f"{tag}", "draft": False, "prerelease": False,
            "body": "本版含：印刷版／阅读版 PDF、EPUB、网页版、Markdown、视觉包，以及**可视化阅读台**两个入口——"
                    f"`{repo}-reader.html`（三档阅读＋章末审问卡）与 `{repo}-explorer.html`（结构地图／台账）。"
                    "二者离线单文件，断网可开。"})
        if st not in (200, 201):
            print(f"  {repo:22} 建 release 失败 {st}"); return False
    rid = rel["id"]
    have = {a["name"]: a["size"] for a in rel.get("assets", [])}
    up = 0
    for f in files:
        p = os.path.join(rel_dir, f)
        name = ALIAS.get(f, f)
        if have.get(name) == os.path.getsize(p):
            continue
        try:
            with open(p, "rb") as fh:
                r = requests.post(f"https://uploads.github.com/repos/lyp0746/{repo}/releases/{rid}/assets",
                                  headers={**H, "Content-Type": "application/octet-stream"},
                                  params={"name": name}, data=fh, timeout=1800)
            if r.status_code in (200, 201):
                up += 1
            else:
                print(f"  {repo:22} 上传失败 {name} {r.status_code}")
                return False
        except Exception as e:
            print(f"  {repo:22} 上传异常 {name} {str(e)[:60]}")
            return False
    # 4) 校验
    st, rel = call(f"{api}/releases/tags/{tag}")
    got = {a["name"] for a in rel.get("assets", [])}
    want = {ALIAS.get(f, f) for f in files}
    if not want <= got:
        print(f"  {repo:22} 校验失败：缺 {sorted(want - got)[:3]}")
        return False
    # 5) 清理其它 release / tag
    removed = []
    for r in call(f"{api}/releases")[1]:
        if r["tag_name"] != tag:
            call(f"{api}/releases/{r['id']}", "DELETE")
            removed.append(r["tag_name"])
    for t in call(f"{api}/tags")[1]:
        if t["name"] != tag:
            call(f"{api}/git/refs/tags/{t['name']}", "DELETE")
    print(f"  {repo:22} OK 资产 {len(got)}/{len(want)}（新传 {up}）｜删旧 release/tag：{removed or '无'}")
    return True


def main(argv):
    tag = "2026-11-26"
    if "--tag" in argv:
        tag = argv[argv.index("--tag") + 1]
        argv = [a for a in argv if a not in ("--tag", tag)]
    repos = [a for a in argv if not a.startswith("--")] or REPOS
    ok = 0
    for r in repos:
        if do_repo(r, tag):
            ok += 1
    print(f"完成 {ok}/{len(repos)}")
    return 0 if ok == len(repos) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

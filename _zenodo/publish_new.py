# -*- coding: utf-8 -*-
"""新建一条 Zenodo 记录并发布（本册：resolution-grain）。

与 `republish_book.py` 的分工：
  `republish_book.py` 只给**已登记**的作品发新版本（先 /versions 建草稿）；
  本脚本给**首次发布**用：从零建草稿 → 预留 DOI → 上传 release/ → PUT 元数据 → 发布。

四条执行纪律（根 AGENTS.md §6b 的坑）：
  ① 元数据走 RDM 键名（rights / subjects / languages / resource_type），legacy 的 license/keywords 只作兼容同写；
  ② 上传是三步：POST 建条目（只带 key）→ PUT 内容（用 requests，urllib 会被重定向吞掉正文）→ POST commit；
     创建条目的响应会把**已有条目一并返回**，必须按 `key == name` 选对条目；
  ③ publisher 必填（DOI 注册要求），用“独立出版 / Independently published”；
  ④ 发布后立刻断言 license / keywords / creators 非空、description 无 `*`、version 与真实完成日一致。

用法：
    python _zenodo/publish_new.py            # 建草稿并上传，打印草稿 ID（不发布）
    python _zenodo/publish_new.py --go       # 上面全部 + 发布 + 写 published_<slug>.json
"""
import io
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import api

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "resolution-grain"
DATE = "2026-11-18"
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}


def load():
    z = json.load(io.open(os.path.join(ROOT, SLUG, ".zenodo.json"), encoding="utf-8"))
    reg = json.load(io.open(os.path.join(ROOT, "_zenodo", "registry.json"), encoding="utf-8"))
    return z, reg


def related(z, reg):
    """自身仓库 + 共用库 + 24 件已发布作品（六本学术专著 ispartof，其余 isrelatedto）。"""
    ACADEMIC = {"entropy-spiral", "capacity-cascade", "distinction-evolution",
                "impossibility-triangle", "interpretation-tradeoff", "emergence-critical"}
    out = [{"identifier": "https://github.com/lyp0746/" + SLUG,
            "scheme": "url", "relation_type": {"id": "issupplementedby"}},
           {"identifier": "https://github.com/lyp0746/series-workspace",
            "scheme": "url", "relation_type": {"id": "ispartof"}}]
    n = 0
    for w in reg["works"]:
        if w.get("类") not in ("书", "论文"):
            continue
        doi = w.get("最新版本DOI")
        if not doi:
            continue
        rel = "ispartof" if w["slug"] in ACADEMIC else "references"
        out.append({"identifier": doi, "scheme": "doi", "relation_type": {"id": rel}})
        n += 1
    print("   关联已发布作品 %d 件（%d 件 ispartof + %d 件 references）"
          % (n, len(ACADEMIC), n - len(ACADEMIC)))
    return out


def payload(z, reg):
    return {"metadata": {
        "title": z["title"],
        "description": z["description"],
        "creators": [CREATOR],
        "publication_date": DATE,
        "version": DATE,
        "resource_type": {"id": "publication-book"},
        "rights": [{"id": "cc-by-4.0"}],
        "subjects": [{"subject": k} for k in z.get("keywords", [])][:24],
        "languages": [{"id": "zho"}],
        "publisher": "独立出版 / Independently published",
        "related_identifiers": related(z, reg),
        # legacy 兼容（同写一份，防止被静默丢弃）
        "license": "cc-by-4.0",
        "keywords": z.get("keywords", []),
        "upload_type": "publication",
        "publication_type": "book",
        "access_right": "open",
        "language": "zho",
    }, "files": {"enabled": True}}


def create(z, reg):
    _, d = api.req("POST", "%s/records" % api.API, data=payload(z, reg), tries=3, timeout=300)
    rid = d["id"]
    print("DRAFT", rid, "| 状态", d.get("status"))
    return rid


def reserve_doi(rid):
    try:
        _, d = api.req("POST", "%s/records/%s/draft/pids/doi" % (api.API, rid), tries=3, timeout=180)
        print("   DOI 预留:", d.get("pids", {}).get("doi", {}).get("identifier") or d)
    except Exception as e:
        print("   DOI 预留失败（发布时会自动分配）：", str(e)[:160])


def upload(rid):
    import requests
    base = "%s/records/%s/draft/files" % (api.API, rid)
    H = {"Authorization": "Bearer " + api.TOK}
    folder = os.path.join(ROOT, SLUG, "release")
    names = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    for name in names:
        p = os.path.join(folder, name)
        r = requests.post(base, headers=H, json=[{"key": name}], timeout=600)
        r.raise_for_status()
        ent = next(e for e in (r.json().get("entries") or [r.json()]) if e.get("key") == name)
        data = open(p, "rb").read()
        r2 = requests.put(ent["links"]["content"],
                          headers={**H, "Content-Type": "application/octet-stream"},
                          data=data, timeout=1800)
        r2.raise_for_status()
        r3 = requests.post("%s/%s/commit" % (base, urllib.parse.quote(name)), headers=H, timeout=600)
        r3.raise_for_status()
        print("   + %-42s %5.1f MB" % (name, len(data) / 1024 / 1024))
    return len(names)


def verify(rid):
    _, d = api.req("GET", "%s/records/%s/draft" % (api.API, rid), tries=3, timeout=180)
    m = d.get("metadata") or {}
    lic = m.get("rights") or m.get("license")
    kw = m.get("subjects") or m.get("keywords") or []
    desc = m.get("description") or ""
    print("   license:", lic, "| keywords:", len(kw), "| creators:", bool(m.get("creators")),
          "| related:", len(m.get("related_identifiers") or []),
          "| version:", m.get("version"), "| stars:", desc.count("*"))
    assert lic, "license 空"
    assert kw, "keywords 空"
    assert m.get("creators"), "creators 空"
    assert desc.count("*") == 0, "描述里有 *"
    assert m.get("version") == DATE, "version 不是 %s" % DATE
    print("   四条断言通过")


def publish(rid):
    _, r = api.req("POST", "%s/records/%s/draft/actions/publish" % (api.API, rid), tries=2, timeout=600)
    print("PUBLISHED", r.get("doi"), "| concept", r.get("conceptdoi"))
    return r


def main():
    z, reg = load()
    rid = create(z, reg)
    reserve_doi(rid)
    n = upload(rid)
    verify(rid)
    if "--go" in sys.argv:
        r = publish(rid)
        out = {"slug": SLUG, "id": str(r.get("id") or rid), "doi": r.get("doi"),
               "conceptdoi": r.get("conceptdoi"), "date": DATE, "files": n,
               "title": z["title"]}
        json.dump(out, io.open(os.path.join(ROOT, "_zenodo", "published_%s.json" % SLUG),
                               "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("草稿 %s 已上传 %d 个文件；加 --go 再发布" % (rid, n))


if __name__ == "__main__":
    main()

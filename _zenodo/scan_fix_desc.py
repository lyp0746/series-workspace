# -*- coding: utf-8 -*-
"""扫 14 篇论文：描述里的 Markdown 记号转 HTML、标题补齐中英双语（只改元数据）。"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import api
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = {"ComputingDemystified":23602360,"WorldPeriodization":23602364,"SleepingResidue":23603016,
       "HunanRelaySystem":23601983,"BureauRotationCession":23602311,"HarnessEcology":23603015,
       "OptimizationBoundary":23611782,"CapacityProxies":23611799,"DomainCrossSection":23695806,
       "IsomorphismStrength":23695810,"MemoryAnchor":23665882,"MemoryStressTest":23667929,
       "LedgerReconciliation":23695813,"MonarchCompetition":23695757}

def md2html(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![A-Za-z0-9])_([^_\n]+?)_(?![A-Za-z0-9])", r"<i>\1</i>", s)
    return s.replace("*", "")

reg = {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT,"_zenodo","registry.json"),encoding="utf-8"))["works"]}
for slug, old in OLD.items():
    rid = reg[slug]["记录ID"]
    try:
        _, r = api.req("GET", f"https://zenodo.org/api/records/{rid}", tries=2, timeout=90)
        m = r["metadata"]
        desc, title = m["description"], m["title"]
        stars = desc.count("*")
        need_title = " / " not in title
        if not stars and not need_title:
            print(f"{slug:24} 无需改动（星号 0，标题双语）", flush=True); continue
        if need_title:
            _, o = api.req("GET", f"https://zenodo.org/api/records/{old}", tries=2, timeout=90)
            t2 = o["metadata"]["title"]
            if " / " in t2 and len(t2) > len(title): title = t2
        newdesc = md2html(desc)
        try: api.req("POST", f"https://zenodo.org/api/records/{rid}/draft", tries=1, timeout=90)
        except Exception: pass
        _, d = api.req("GET", f"https://zenodo.org/api/records/{rid}/draft", tries=2, timeout=90)
        mm = d["metadata"]
        meta = {"title": title, "description": newdesc, "creators": mm.get("creators") or
                    [{"person_or_org": {"type": "personal", "name": "李毅芃"},
                      "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}],
                "publication_date": mm.get("publication_date"), "version": mm.get("version"),
                "resource_type": {"id": "publication-preprint"}, "license": {"id": "cc-by-4.0"},
                "languages": [{"id": "zho"}], "publisher": "Zenodo",
                "related_identifiers": mm.get("related_identifiers", [])}
        api.req("PUT", f"https://zenodo.org/api/records/{rid}/draft", data={"metadata": meta}, tries=2, timeout=180)
        api.req("POST", f"https://zenodo.org/api/records/{rid}/draft/actions/publish", tries=2, timeout=180)
        print(f"{slug:24} 星号 {stars}→{newdesc.count('*')}  标题{len(title)}字 双语={' / ' in title}", flush=True)
    except Exception as e:
        print(f"{slug:24} 失败 {str(e)[:140]}", flush=True)

# -*- coding: utf-8 -*-
"""把 _series/content/*_parts.json 里的部分导语与小结写回各书 parts.json（只填空）。"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOBS = {
    "capacity-cascade": "capacity_parts.json",
    "emergence-critical": "emergence_parts.json",
    "impossibility-triangle": "impossibility_parts.json",
    "interpretation-tradeoff": "interpretation_parts.json",
    "hotspot-bills": "hotspot_parts.json",
}
for repo, fn in JOBS.items():
    pj = os.path.join(ROOT, repo, "source", "parts.json")
    d = json.load(open(pj, encoding="utf-8"))
    src = json.load(open(os.path.join(ROOT, "_series", "content", fn), encoding="utf-8"))["parts"]
    assert len(src) == len(d), (repo, len(src), len(d))
    for part, new in zip(d, src):
        part["intro"] = new["intro"]
        part["summary"] = new["summary"]
    json.dump(d, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("filled", repo, len(src), "parts")

# -*- coding: utf-8 -*-
"""发布脚本共用的常量与工具：六本专著 DOI、共用库地址、标题、Markdown→HTML。"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = "2026-10-30"
SHARED = "https://github.com/lyp0746/series-workspace"
MONO = {"entropy-spiral": "10.5281/zenodo.23771608",
        "capacity-cascade": "10.5281/zenodo.23771832",
        "distinction-evolution": "10.5281/zenodo.23771933",
        "impossibility-triangle": "10.5281/zenodo.23772040",
        "interpretation-tradeoff": "10.5281/zenodo.23771397",
        "emergence-critical": "10.5281/zenodo.23772106"}
CREATOR_LEGACY = {"name": "李毅芃", "affiliation": "独立研究者 / Independent Researcher"}
CREATOR = {"person_or_org": {"type": "personal", "name": "李毅芃",
                             "given_name": "毅芃", "family_name": "李"},
           "affiliations": [{"name": "独立研究者 / Independent Researcher"}]}


def title_of(slug, is_paper=False):
    """完整中英标题：以 CITATION.cff 为准（inventory.tsv 的英文列会被截断，不可用）。"""
    t = io.open(os.path.join(ROOT, slug, "CITATION.cff"), encoding="utf-8").read()
    zh = re.search(r'^title:\s*"?(.+?)"?\s*$', t, re.M).group(1).strip().strip('"')
    if " / " in zh:
        return zh
    en = re.search(r'^title-en:\s*"?(.+?)"?\s*$', t, re.M)
    return f"{zh} / {en.group(1).strip().strip(chr(34))}" if en else zh


def md2html(s):
    """把摘要里的 Markdown 记号转成 HTML；description 是 HTML 字段，不能留 *。"""
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s, flags=re.S)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![A-Za-z0-9])_([^_\n]+?)_(?![A-Za-z0-9])", r"<i>\1</i>", s)
    return s.replace("*", "")


def related(slug, kind):
    """kind: mono（六本专著，只关联自身仓库）/ book3（另三本）/ paper（论文用共用库）。"""
    R = lambda i, rt: {"identifier": i, "scheme": "doi" if i.startswith("10.") else "url",
                       "relation_type": {"id": rt}}
    if kind == "mono":
        return [R(f"https://github.com/lyp0746/{slug}", "issupplementedby")]
    if kind == "book3":
        return [R(f"https://github.com/lyp0746/{slug}", "issupplementedby")] + \
               [R(d, "ispartof") for d in MONO.values()]
    return [R(SHARED, "issupplementedby")] + [R(d, "ispartof") for d in MONO.values()]


def registry():
    return {w["slug"]: w for w in json.load(io.open(os.path.join(ROOT, "_zenodo", "registry.json"),
                                                    encoding="utf-8"))["works"]}

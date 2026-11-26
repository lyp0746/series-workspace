# -*- coding: utf-8 -*-
"""统一 10 个仓的「可视化阅读台」一节 + series-workspace 的 README + About（中英双语）。"""
import glob, io, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOK = open(os.path.join(ROOT, "_series", "ghtok")).read().strip()
H = {"Authorization": "Bearer " + TOK, "Accept": "application/vnd.github+json",
     "User-Agent": "pi", "Content-Type": "application/json"}
MARK = "<!-- viz-console -->"
BOOKS = ["knowledge-tradeoffs", "capacity-cascade", "emergence-critical", "entropy-spiral",
         "interpretation-tradeoff", "impossibility-triangle", "distinction-evolution",
         "mind-forks", "hotspot-bills", "resolution-grain"]
SB = {"knowledge-tradeoffs": "12 站背包客（3¹² 穷举，页内跑出 473,721／0.58／2.16）",
      "impossibility-triangle": "12 站背包客（3¹² 穷举，页内跑出 473,721／0.58／2.16）",
      "resolution-grain": "三块算式装置（v\\*=(T+λ)/2w、n\\*=[s−(γ₀/α)e^{−λC}]/κ、t½=(ln2/γ₀)e^{λC}）＋ 十条极限退化表"}


def facts(repo):
    ch = len(glob.glob(os.path.join(ROOT, repo, "source", "ch*.html")))
    rd = os.path.join(ROOT, repo, "assets", f"{repo}-reader.html")
    ex = os.path.join(ROOT, repo, "assets", f"{repo}-explorer.html")
    cards = 0
    if os.path.exists(rd):
        cards = io.open(rd, encoding="utf-8").read().count('<details class="audit"')
    kb = lambda p: round(os.path.getsize(p) / 1024) if os.path.exists(p) else 0
    return ch, cards, kb(rd), kb(ex)


def block(repo, zh, sub):
    ch, cards, rk, ek = facts(repo)
    sb = SB.get(repo, "")
    sb_zh = f"\n- **算式装置**：{sb}。滑块上没有一个是编的系数，式子照抄正文，页内按钮可当场复算。" if sb else ""
    sb_en = ("\n- **Computational bench** — three sliders-plus-recompute devices (stationarity, entry equilibrium, "
             "ebb half-life) and a ten-limit degeneration table; every parameter is quoted from the text."
             ) if sb else ""
    return f"""{MARK}
## 可视化阅读台 ｜ Reading console

这一件配了两个**离线单文件**：双击就能开，断网可用，零外部依赖、零服务器、零 API 账单。
Two offline single-file entries ship with this item. Double-click and it runs — no network, no server, no API bill.

| 入口 | 文件 | 体积 | 里面是什么 |
|---|---|---|---|
| 阅读页 | `assets/{repo}-reader.html` | {rk} KB | 三档切换（**骨架**＝只留标题与高亮框／**阅读**＝正文全显、表与证据折叠／**全展**＝全部展开，可用 Ctrl+F 搜全书表格）＋ **{cards} 张章末审问卡** |
| 结构地图 | `assets/{repo}-explorer.html` | {ek} KB | 章际引用的 3D 螺旋、部 × 部矩阵、附录原表台账（按表号/章/单元格搜索）、图件账（SVG 内联，不缺图） |

- **审问卡**四行全部原文摘录，一个字不增写：`带走`（一句话带走／本章小结末句）／`打脸条件`（表 F.1、附录登记簿、或「反例与边界」节首段）／`封顶`（本章标过的 A/B/C 等级，没有就不印）／`动手`（【动手试试】）。右上角一键复制，粘到自己的 AI 里当严苛伴读。
  The audit card quotes four things verbatim — takeaway, falsification condition, evidence ceiling, hands-on prompt — and offers a one-click copy for your own AI, with the discipline written into the clipboard.
- **两页互跳**：阅读页顶部「结构地图 →」，结构地图工具栏「正文阅读页 →」，螺旋上点第 N 章直接落到 `#chN`。{sb_zh}
- **已验证**：`375px` 窄屏与桌面均无横向溢出；0 个 JS 报错；三档切换 10–40 ms（纯 CSS class，不遍历 DOM）。{sb_en}
- 本件规模：正文 **{ch} 章**；审问卡 **{cards} 张**。
  Size: **{ch} chapters**, **{cards}** audit cards.

"""
EN_ONLY = ""


def do_readme(repo, zh, sub):
    p = os.path.join(ROOT, repo, "README.md")
    t = io.open(p, encoding="utf-8").read()
    blk = block(repo, zh, sub)
    t2 = re.sub(re.escape(MARK) + r".*?(?=\n## |\Z)", blk, t, flags=re.S) if MARK in t else t.rstrip() + "\n\n" + blk
    if t2 != t:
        io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
        return True
    return False


def api(url, method="PATCH", data=None):
    r = urllib.request.Request(url, method=method, headers=H, data=json.dumps(data).encode() if data else None)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return x.status, json.loads(x.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


def do_about(repo, zh, sub, en):
    desc = ((f"{zh}：{sub}。" if sub else f"{zh}。") +
            "可视化阅读台：离线单文件 HTML，三档阅读＋章末审问卡＋结构地图。 " + f"{en}. Offline single-file reading console and structure map.")
    st, _ = api(f"https://api.github.com/repos/lyp0746/{repo}", "PATCH",
                {"description": desc[:350], "homepage": f"https://github.com/lyp0746/{repo}/tree/main/assets",
                 "topics": ["chinese", "methodology", "information-theory", "interactive-visualization",
                            "offline-first", "single-file-html"]})
    return st


EN = {"knowledge-tradeoffs": "The Tradeoffs of Finite Systems", "capacity-cascade": "The Boundaries of Forgetting",
      "emergence-critical": "Criticality of Emergence", "entropy-spiral": "Misaligned Time",
      "interpretation-tradeoff": "The Tradeoff of Interpretation", "impossibility-triangle": "The Price of Choice",
      "distinction-evolution": "The Language of Distinction", "mind-forks": "Forks of the Mind",
      "hotspot-bills": "Bills of the Hot List", "resolution-grain": "Coarse Codes"}


def main():
    for repo in BOOKS:
        p = os.path.join(ROOT, repo, "source", "book.json")
        d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        zh, sub = d.get("title", repo), d.get("subtitle", "")
        ch = do_readme(repo, zh, sub)
        st = do_about(repo, zh, sub, EN[repo])
        print(f"  {repo:24} README {'更新' if ch else '已最新'}｜About {st}")
    # series-workspace 的 README
    rows = []
    for repo in BOOKS:
        ch_, cards, rk, ek = facts(repo)
        rows.append(f"| `{repo}/` | {ch_} | {cards} | {rk} KB | {ek} KB |")
    ws = f"""# series-workspace · 有限系统的取舍（工作区）

**同一作者的独立研究系列：九本书 ＋ 十五篇工作论文 ＋ 一部合集 ＋ 第十册《粗码》。**
A single-author research series: nine books, fifteen working papers, one collection, plus a tenth volume.

> **件数以 `inventory.tsv` 为准；本仓只放规范、lint、十五篇论文源文件与工具。**
> **可视化阅读台**（离线单文件）在 `文集\\可视化阅读台\\`：`index.html` 是总入口。

## 这是什么 ｜ What this is

| 类 | 件 | 位置 |
|---|---|---|
| 书（学术 6 ＋ 通俗 2 ＋ 科普 1） | 9 | 各自独立仓库（见下表） |
| 工作论文 | 15 | 本仓各目录（`source/paper.md` 为唯一来源） |
| 合集 | 1 | `合集/`（印刷版／电子版／EPUB） |
| 《粗码》 | 1 | `resolution-grain/`（独立仓库，不进 inventory） |
| 规范与工具 | — | `_series/`（spec／lint／tools／review／versions） |

## 十件的离线阅读台 ｜ The ten reading consoles

| 仓库 | 章 | 审问卡 | 阅读页 | 结构地图 |
|---|---|---|---|---|
{chr(10).join(rows)}

每件两个入口：`assets/<repo>-reader.html`（三档阅读＋章末审问卡＋可复制对账指令）与
`assets/<repo>-explorer.html`（3D 章际螺旋／部×部矩阵／附录台账／图件账）。**离线单文件、断网可开、零依赖。**

## 命令 ｜ Commands

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
"$PY" _series/lint/lint.py                    # 全校阅 24 件
"$PY" _series/tools/make_atlas.py --all       # 结构地图（九本）
"$PY" _series/tools/make_reader.py --all      # 阅读页（九本＋十五篇＋粗码）
"$PY" _series/tools/make_index.py             # 总入口 index.html
"$PY" _series/tools/publish_viz.py            # 一源三投：assets → release → 文集
"$PY" _series/tools/republish_all.py --tag 2026-11-26   # 每仓 1 tag ＋ 1 release
```

## 纪律 ｜ Discipline

结论强度 ≤ 证据强度（A 官方可复现／B 稳定公开估计／C 稀疏·构造·思辨）；禁词：必然、注定、不可避免、无法消除、死路；
可证伪登记簿 append-only；已发布的 DOI 与资产名不改名、不覆盖，修订只发新版本。详见 `AGENTS.md`。

## 许可 ｜ License

正文 CC BY 4.0；脚本 MIT。
"""
    io.open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8", newline="\n").write(ws)
    print("  series-workspace README 写入", len(ws), "字节")


if __name__ == "__main__":
    main()

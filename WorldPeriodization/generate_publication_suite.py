#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paper-mode publication suite (generic template).

Markdown → HTML (images base64-inlined) → A4 PDF via Playwright/Chromium.

Usage:
    python generate_publication_suite.py [--md paper.md] [--author 李毅芃]

Defaults: the single *.md in this folder whose name does not start with "_".
Outputs: <stem>.pdf and <stem>.html next to the Markdown file.

Copy this file into a paper folder; no other edits are needed.
"""
import argparse
import asyncio
import base64
import re
from pathlib import Path

import markdown
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
TEMP = BASE / "_temp"
TEMP.mkdir(exist_ok=True)

CSS = """
<style>
@page { size: A4; margin: 27mm 25mm 25mm 25mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", "SimSun", serif;
  font-size: 12.6pt; line-height: 2.2; color: #1d1d1f; margin: 0 auto; max-width: 46em;
  text-align: justify; hyphens: auto;
}
h1 { font-size: 21pt; line-height: 1.4; text-align: center; margin: 0 0 .3em;
     font-weight: 700; letter-spacing: .02em; }
h1 + h3 { text-align: center; font-size: 12.5pt; font-weight: 500; color: #444;
          margin: 0 0 1.2em; line-height: 1.6; }
h2 { font-size: 15pt; margin: 1.9em 0 .7em; padding-bottom: .25em;
     border-bottom: 1.5px solid #b3261e; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 1.4em 0 .5em; color: #8c1d18; page-break-after: avoid; }
h4 { font-size: 11pt; margin: 1.1em 0 .4em; page-break-after: avoid; }
p { margin: .55em 0; orphans: 2; widows: 2; }
strong { color: #111; font-weight: 700; }
em { font-style: normal; color: #555; }
blockquote { margin: .9em 0; padding: .5em 1em; border-left: 3px solid #d8c9a8;
             background: #fbf8f1; color: #333; }
hr { border: 0; border-top: 1px solid #ddd; margin: 1.6em 0; }
ul, ol { margin: .5em 0 .5em 1.2em; padding-left: 1em; }
li { margin: .22em 0; }
table { border-collapse: collapse; width: 100%; margin: .9em 0; font-size: 8.8pt;
        page-break-inside: auto; line-height: 1.5; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #f2ede3; border: .6px solid #c9c0ad; padding: 5px 6px;
     font-weight: 700; text-align: center; }
td { border: .6px solid #d8d2c4; padding: 4px 6px; vertical-align: top; }
td code { font-size: 7.9pt; }
td:first-child, th:first-child { white-space: normal; }
td:nth-child(3), th:nth-child(3), td:nth-child(4), th:nth-child(4) { white-space: nowrap; }
td { word-break: normal; overflow-wrap: break-word; }
tr:nth-child(even) td { background: #fcfbf8; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto .4em;
      page-break-inside: avoid; }
pre { background: #f6f6f4; border: .6px solid #ddd; border-radius: 3px;
      padding: 9px 11px; font-size: 8.6pt; line-height: 1.55; overflow-x: auto;
      page-break-inside: avoid; white-space: pre-wrap; }
code { font-family: "Consolas", "Menlo", monospace; font-size: 8.8pt;
       background: #f2f2f0; padding: 0 3px; border-radius: 2px; }
pre code { background: none; padding: 0;
           font-family: "Consolas", "Menlo", "SimHei", monospace; }
p.caption { font-size: 8.9pt; color: #555; margin: .1em 0 1.3em; line-height: 1.6; }
a { color: #1f4e79; text-decoration: none; }
</style>
"""


def pick_md(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    cands = [p for p in BASE.glob("*.md") if not p.name.startswith("_")
             and p.name.lower() not in ("readme.md", "plan.md")]
    if not cands:
        raise SystemExit("no Markdown file found; pass --md")
    return max(cands, key=lambda p: p.stat().st_size)


def title_of(md: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md.splitlines()[0][:60]


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def embed_images(html: str) -> str:
    def repl(m):
        p = BASE / m.group(2)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return '%ssrc="data:image/png;base64,%s"%s' % (m.group(1), b64, m.group(3))
        return m.group(0)

    return re.sub(r'(<img\s+[^>]*?)src="([^"]+\.png)"([^>]*?>)', repl, html)


def style_captions(html: str) -> str:
    return re.sub(r"<p><em>((?:图|表)\s?\d+.*?)</em></p>", r'<p class="caption">\1</p>', html, flags=re.S)


async def render(page_html: str, out_pdf: Path, out_html: Path, title: str, author: str):
    full = ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            "<title>" + title + "</title>" + CSS + "</head><body>" + page_html + "</body></html>")
    tmp = TEMP / "_combined.html"
    tmp.write_text(full, encoding="utf-8")
    out_html.write_text(full, encoding="utf-8", newline="\n")

    header = ('<div style="font-size:7.5px;color:#999;width:100%;text-align:center;'
              'padding-top:4mm;">' + title + " — " + author + "</div>")
    footer = ('<div style="font-size:7.5px;color:#777;width:100%;text-align:center;">'
              '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(tmp.as_uri(), wait_until="load")
        await page.wait_for_timeout(1200)
        await page.pdf(
            path=str(out_pdf), format="A4", print_background=True,
            display_header_footer=True, header_template=header, footer_template=footer,
            margin={"top": "22mm", "bottom": "18mm", "left": "18mm", "right": "18mm"},
        )
        await browser.close()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=None)
    ap.add_argument("--author", default="李毅芃")
    args = ap.parse_args()

    md_path = pick_md(args.md)
    md = md_path.read_text(encoding="utf-8")
    title = title_of(md)
    out_pdf = md_path.with_suffix(".pdf")
    out_html = md_path.with_suffix(".html")

    print("[1/3] %s (%s chars)" % (md_path.name, format(len(md), ",")))
    html = md_to_html(md)
    html = style_captions(html)
    html = embed_images(html)
    print("[2/3] HTML: %s chars" % format(len(html), ","))
    await render(html, out_pdf, out_html, title, args.author)
    print("[3/3] %s (%.2f MB)" % (out_pdf.name, out_pdf.stat().st_size / 1024 / 1024))
    print("      %s" % out_html.name)


if __name__ == "__main__":
    asyncio.run(main())

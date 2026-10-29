# -*- coding: utf-8 -*-
"""用 Playwright 渲染 JS 页面，取正文文本（绕过 SPA/403）。"""
import sys, pathlib, asyncio
from playwright.async_api import async_playwright
async def main(specs):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(locale="en-US", user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"))
        pg = await ctx.new_page()
        for spec in specs:
            name, url = spec.split("=", 1)
            try:
                await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                await pg.wait_for_timeout(3500)
                txt = await pg.inner_text("body")
                pathlib.Path("raw", name + ".txt").write_text(txt, encoding="utf-8")
                print("OK  ", name, len(txt))
            except Exception as e:
                print("FAIL", name, e)
        await b.close()
asyncio.run(main(sys.argv[1:]))

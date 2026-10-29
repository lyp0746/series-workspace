import asyncio, pathlib
from playwright.async_api import async_playwright
BASE=pathlib.Path(__file__).resolve().parent.parent
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":900,"height":1180}, device_scale_factor=2)
        await pg.goto((BASE/"source"/"paper.html").as_uri()); await pg.wait_for_timeout(900)
        h=await pg.evaluate("document.body.scrollHeight")
        for frac,out in [(0.72,"p_tables.png"),(0.93,"p_appendix.png")]:
            await pg.evaluate(f"window.scrollTo(0,{int(h*frac)})")
            await pg.wait_for_timeout(350)
            await pg.screenshot(path=str(BASE/"_temp"/out))
        await b.close()
asyncio.run(main())

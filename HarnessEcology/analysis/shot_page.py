import asyncio, pathlib, sys
from playwright.async_api import async_playwright
BASE=pathlib.Path(__file__).resolve().parent.parent
async def main():
    url=(BASE/"interactive"/"harness-ecology-explorer.html").as_uri()
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for name,vw,vh in [("desk",1280,800),("mob",390,844)]:
            pg=await b.new_page(viewport={"width":vw,"height":vh}, device_scale_factor=2)
            await pg.goto(url); await pg.wait_for_timeout(500)
            await pg.screenshot(path=str(BASE/"_temp"/f"exp_{name}.png"))
            await pg.close()
        await b.close()
asyncio.run(main())

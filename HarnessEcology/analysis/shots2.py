import asyncio, pathlib
from playwright.async_api import async_playwright
BASE=pathlib.Path(__file__).resolve().parent.parent
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":900,"height":1180}, device_scale_factor=2)
        await pg.goto((BASE/"source"/"paper.html").as_uri()); await pg.wait_for_timeout(900)
        for i,(sel,out) in enumerate([("img[src*='fig09']","p_fig09.png"),
                                      ("img[src*='fig10']","p_fig10.png")]):
            el=await pg.query_selector(sel)
            if el: await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(BASE/"_temp"/out))
        await b.close()
asyncio.run(main())

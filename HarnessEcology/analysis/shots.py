import asyncio, pathlib
from playwright.async_api import async_playwright
BASE=pathlib.Path(__file__).resolve().parent.parent
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":900,"height":1200}, device_scale_factor=2)
        await pg.goto((BASE/"source"/"paper.html").as_uri())
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=str(BASE/"_temp"/"shot_top.png"))
        for i,sel in enumerate(["h2:nth-of-type(1)"]):
            pass
        # 滚到图表附近
        await pg.evaluate("window.scrollTo(0, document.body.scrollHeight*0.18)")
        await pg.wait_for_timeout(300); await pg.screenshot(path=str(BASE/"_temp"/"shot_mid.png"))
        await pg.evaluate("window.scrollTo(0, document.body.scrollHeight*0.62)")
        await pg.wait_for_timeout(300); await pg.screenshot(path=str(BASE/"_temp"/"shot_late.png"))
        # 移动端
        pg2=await b.new_page(viewport={"width":390,"height":844}, device_scale_factor=2)
        await pg2.goto((BASE/"source"/"paper.html").as_uri()); await pg2.wait_for_timeout(600)
        await pg2.screenshot(path=str(BASE/"_temp"/"shot_mobile.png"))
        await b.close()
asyncio.run(main())

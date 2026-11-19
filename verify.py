import asyncio, json
from playwright.async_api import async_playwright

URL = "file:///home/user/Doubao/chats/38445857795465986/periodic-wallpaper/index.html"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/local/bin/chromium",
                                    args=["--no-sandbox","--disable-gpu"])
        page = await b.new_page(viewport={"width":1920,"height":1080}, device_scale_factor=1)
        errors=[]
        page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error","warning") else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(2200)
        cells = await page.locator(".cell").count()
        ph = await page.locator(".placeholder").count()
        # 页面是否溢出
        overflow = await page.evaluate("() => ({sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight})")
        # 截图主界面
        await page.screenshot(path="preview.jpg", type="jpeg", quality=90)
        # 点击 Fe(26)
        await page.locator('.cell[data-z="26"]').click()
        await page.wait_for_timeout(700)
        det_open = await page.evaluate("() => document.getElementById('detail').classList.contains('open')")
        fe_text = await page.evaluate("() => document.getElementById('dBody').innerText.slice(0,300)")
        await page.screenshot(path="preview-detail.jpg", type="jpeg", quality=90)
        print(json.dumps({
            "cells": cells, "placeholders": ph, "overflow": overflow,
            "errors": errors[:10], "detail_open": det_open,
            "detail_excerpt": fe_text
        }, ensure_ascii=False, indent=2))
        await b.close()

asyncio.run(main())

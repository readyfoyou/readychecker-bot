from playwright.async_api import async_playwright
import asyncio
async def fetch_data1(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        print(await page.content())
        await browser.close()
asyncio.run(fetch_data1("https://comfy.ua/ua/smartfon-apple-iphone-16e-128gb-white.html"))
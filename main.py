import asyncio
from datetime import datetime
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright

# ✅ قراءة بيانات الاعتماد من متغير بيئة
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])

# الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1hCUbHbSM2ylgf9L0fpUxsxvZN8ffi21k9i1OolAgL-o").worksheet("Sheet1")

# روابط المواقع المستهدفة
urls = [
    "https://online.koora4live.live/home3/",
    "https://www.yalla-shooot.com/",
    "https://www.hd7.live/",
    "https://yalla--shoot.today/",
    "https://www.syrialive.cc/"
]

# استخراج الروابط
async def extract_links(page, url):
    try:
        await page.goto(url, timeout=60000)
        html = await page.content()
        matches = []
        for line in html.split("\n"):
            if any(word in line.lower() for word in ["vs", "مقابل", "x"]) and "http" in line:
                text = line.strip()
                matches.append((text, url))
        return matches
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return []

# المهمة الرئيسية
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        sheet.clear()
        sheet.append_row(["Title", "Link", "Date"])

        today = datetime.now().strftime("%Y-%m-%d")
        for url in urls:
            print(f"🔍 Scraping: {url}")
            matches = await extract_links(page, url)
            for title, link in matches:
                sheet.append_row([title, link, today])

        await browser.close()
        print("✅ تم التحديث بنجاح.")

if __name__ == "__main__":
    asyncio.run(run())

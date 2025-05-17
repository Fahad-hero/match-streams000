import asyncio
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright

# إعداد الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
with open("service_account.json") as f:
    creds_dict = json.load(f)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1hCUbHbSM2ylgf9L0fpUxsxvZN8ffi21k9i1OolAgL-o").worksheet("Sheet1")

# دالة استخراج الروابط من كل موقع
async def extract_links(playwright, url):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=60000)
        html = await page.content()
        matches = []
        lines = html.split("\n")
        for line in lines:
            if any(keyword in line.lower() for keyword in ["vs", "مقابل", "x"]):
                title = line.strip()
                link = url
                matches.append((title, link))
        return matches
    except Exception as e:
        print(f"Error at {url}: {e}")
        return []
    finally:
        await browser.close()

# المواقع المستهدفة
urls = [
    "https://online.koora4live.live/home3/",
    "https://www.yalla-shooot.com/",
    "https://www.hd7.live/",
    "https://yalla--shoot.today/",
    "https://www.syrialive.cc/"
]

# الوظيفة الرئيسية
async def run():
    async with async_playwright() as playwright:
        all_matches = []
        for url in urls:
            matches = await extract_links(playwright, url)
            all_matches.extend(matches)

        # حذف البيانات القديمة
        sheet.clear()
        sheet.append_row(["Title", "Link", "Date"])

        today = datetime.now().strftime("%Y-%m-%d")
        for title, link in all_matches:
            sheet.append_row([title, link, today])
        print("✅ تمت إضافة الروابط إلى الشيت بنجاح.")

# تشغيل البوت
if __name__ == "__main__":
    asyncio.run(run())

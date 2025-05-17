import asyncio
from playwright.async_api import async_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ بيانات Google Sheets - استبدل القيم الحقيقية
creds_dict = {
    "type": "service_account",
    "project_id": "YOUR_PROJECT_ID",
    "private_key_id": "YOUR_PRIVATE_KEY_ID",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "YOUR_CLIENT_EMAIL",
    "client_id": "YOUR_CLIENT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "YOUR_CERT_URL"
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1j4pzqKqgm9Umae7sdP1t6RkXKqELkWuIusUl1on9lz8/edit#gid=0")
worksheet = sheet.get_worksheet(0)

# 🧠 دالة استخراج من موقع معيّن
async def extract_from_site(page, url, selector, source_name):
    await page.goto(url)
    await page.wait_for_timeout(5000)  # انتظر التحميل

    matches = await page.query_selector_all(selector)
    for match in matches:
        text = await match.inner_text()
        worksheet.append_row([source_name, text])

# ✅ المواقع المستهدفة و السيلكتورات الخاصة بها
sites = [
    {
        "url": "https://livehd7.today/",
        "selector": "div.match-title",  # غيّره إذا تغيّر
        "name": "livehd7"
    },
    {
        "url": "https://yalla-shoot.io/",
        "selector": ".match-card h3",  # مثال: غيّره إذا تغيّر
        "name": "yalla-shoot.io"
    },
    {
        "url": "https://www.yallashoot-news.com/",
        "selector": ".matches .match .teams",  # غيّره إذا تغيّر
        "name": "yallashoot-news"
    },
    {
        "url": "https://www.yalla-shoot.today/",
        "selector": ".content .match-card .teams",  # غيّره إذا تغيّر
        "name": "yalla-shoot.today"
    },
    {
        "url": "https://www.alostora.live/",
        "selector": ".match-title",  # غيّره إذا تغيّر
        "name": "alostora"
    }
]

# ✅ التشغيل الرئيسي
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for site in sites:
            try:
                await extract_from_site(page, site["url"], site["selector"], site["name"])
            except Exception as e:
                print(f"❌ Error scraping {site['url']}: {e}")

        await browser.close()

asyncio.run(run())

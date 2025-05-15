import subprocess; subprocess.run(["playwright", "install", "chromium"])

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعداد Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("بث المباريات").sheet1

# قائمة المواقع التي تدعم نفس البنية (يتم توسيعها لاحقًا)
sites = {
    "الأسطورة": "https://hd7.live",
    "كورة لايف": "https://www.koraa-live.com",
    "يلا شوت": "https://www.yalla-shooot.com",
    "كورة 4 لايف": "https://online.koora4live.live/home33/",
    "كورة اون لاين": "https://m6.kora-online-tv.com"
}

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        for name, url in sites.items():
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector(".match-card", timeout=15000)
                matches = await page.query_selector_all(".match-card")

                for match in matches:
                    try:
                        team1 = await match.query_selector(".team-1")
                        team2 = await match.query_selector(".team-2")
                        match_time = await match.query_selector(".match-time")

                        team1_text = await team1.inner_text()
                        team2_text = await team2.inner_text()
                        match_time_text = await match_time.inner_text()

                        sheet.append_row([
                            f"{team1_text.strip()} - {team2_text.strip()}",
                            match_time_text.strip(),
                            today
                        ])
                        print(f"✅ [{name}] {team1_text.strip()} vs {team2_text.strip()} | {match_time_text.strip()}")
                    except Exception as e:
                        print(f"⚠️ خطأ في مباراة داخل {name}: {e}")
            except Exception as e:
                print(f"❌ تعذر الوصول إلى الموقع {name}: {e}")
            finally:
                await page.close()

        await browser.close()

asyncio.run(run())

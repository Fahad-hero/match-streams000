import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# تحميل بيانات Google Sheets من متغير البيئة GOOGLE_CREDS
creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("بث المباريات").sheet1

# المواقع المستهدفة (تُفعل واحدة في كل دورة)
TARGET_SITES = [
    {"name": "الأسطورة", "url": "https://www.hd7.live"},
    {"name": "كورة لايف", "url": "https://www.koraa-live.com"},
    {"name": "يلا شوت", "url": "https://www.yalla-shooot.com"},
    {"name": "كورة 4 لايف", "url": "https://online.koora4live.live/home33"},
    {"name": "كورة أون لاين", "url": "https://m6.kora-online-tv.com"},
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        for site in TARGET_SITES:
            page = await browser.new_page()
            try:
                await page.goto(site["url"], timeout=60000)
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

                        print(f"✅ {site['name']} | {team1_text.strip()} vs {team2_text.strip()} | {match_time_text.strip()}")

                    except Exception as e:
                        print(f"⚠️ فشل في استخراج مباراة داخل {site['name']}: {e}")

            except Exception as e:
                print(f"❌ الموقع {site['name']} لا يعمل أو لم يُحمّل بنجاح: {e}")

            await page.close()

        await browser.close()

# لجعل البوت يعمل باستمرار كل ساعة (على Render)
if __name__ == "__main__":
    import time
    while True:
        asyncio.run(run())
        print("🕒 تم الانتظار ساعة قبل التشغيل التالي...")
        time.sleep(3600)

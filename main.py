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

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://hd7.live", timeout=60000)

        await page.wait_for_selector(".match-card")

        matches = await page.query_selector_all(".match-card")

        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        for match in matches:
            try:
                team1 = await match.query_selector(".team-1")
                team2 = await match.query_selector(".team-2")
                match_time = await match.query_selector(".match-time")

                team1_text = await team1.inner_text()
                team2_text = await team2.inner_text()
                match_time_text = await match_time.inner_text()

                sheet.append_row([f"{team1_text.strip()} - {team2_text.strip()}", match_time_text.strip(), today])
                print(f"✅ {team1_text.strip()} vs {team2_text.strip()} | {match_time_text.strip()}")
            except Exception as e:
                print("❌ خطأ في استخراج المباراة:", e)

        await browser.close()

asyncio.run(run())

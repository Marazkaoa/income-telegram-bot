import asyncio
from datetime import datetime
from .database import load_data

async def auto_daily_report(app):
    while True:
        now = datetime.now()
        if now.hour == 23 and now.minute == 59:
            db = load_data()
            d = now.strftime("%d-%m-%Y")
            val = db.get(d, 0)
            msg = f"📢 Báo cáo cuối ngày {d}\n👉 Lợi nhuận: {val:,} VND"

            # phát cho owner
            cfg = json.load(open("config.json"))
            owner = cfg["owner_id"]
            await app.bot.send_message(owner, msg)

            await asyncio.sleep(61)
        await asyncio.sleep(20)

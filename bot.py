#!/usr/bin/env python3
# Telegram Finance Bot PRO — MENU + QUYỀN + BIỂU ĐỒ + TỰ ĐỘNG LƯU

import os
import json
import asyncio
from datetime import datetime
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

from modules.access import is_allowed, owner_only
from modules.database import load_data, save_data, add_amount, delete_date, reset_all
from modules.finance import format_vnd, stats_for_month, sorted_days
from modules.charts import make_chart
from modules.menu import build_menu, build_admin_menu
from modules.report import auto_daily_report

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"


async def start(update: Update, context: ContextTypes.OBJECT):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot.")
        return

    await update.message.reply_text(
        "👋 Chào bạn!\nNhấn /menu để mở Menu quản lý lợi nhuận."
    )


async def menu(update: Update, context: ContextTypes.OBJECT):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot.")
        return

    await update.message.reply_text(
        "📌 MENU QUẢN LÝ LỢI NHUẬN",
        reply_markup=build_menu()
    )


async def admin(update: Update, context: ContextTypes.OBJECT):
    await owner_only(update, context)
    await update.message.reply_text(
        "🔐 MENU QUẢN TRỊ",
        reply_markup=build_admin_menu()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user_id = q.from_user.id
    await q.answer()

    if not is_allowed(user_id):
        await q.message.reply_text("❌ Bạn không có quyền sử dụng bot.")
        return

    data = q.data

    # ————— MENU CHÍNH —————
    if data == "add":
        await q.message.reply_text("Nhập số tiền +VD: +3000000")
    elif data == "sub":
        await q.message.reply_text("Nhập số tiền -VD: -2000000")

    elif data == "today":
        today = datetime.now().strftime("%d-%m-%Y")
        db = load_data()
        profit = db.get(today, 0)
        await q.message.reply_text(f"📅 Hôm nay ({today}): {format_vnd(profit)}")

    elif data == "total":
        db = load_data()
        text = "📊 Tổng kết:\n"
        for d, v in db.items():
            text += f"{d} → {format_vnd(v)}\n"
        text += f"\nTổng: {format_vnd(sum(db.values()))}"
        await q.message.reply_text(text)

    elif data == "chart":
        bio = make_chart()
        await q.message.reply_photo(InputFile(bio, "profit.png"))

    elif data == "stat":
        await q.message.reply_text("Gõ: /stat MM-YYYY")

    # ————— ADMIN —————
    if data == "admin_add_user":
        await owner_only(update, context)
        await q.message.reply_text("Gõ: /adduser USER_ID")
    elif data == "admin_del_user":
        await owner_only(update, context)
        await q.message.reply_text("Gõ: /deluser USER_ID")
    elif data == "admin_list_user":
        await owner_only(update, context)
        from modules.access import list_allowed
        await q.message.reply_text(list_allowed())


async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_allowed(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng bot.")
        return

    txt = update.message.text.strip()

    if txt.startswith("+") or txt.startswith("-"):
        try:
            amount = int(txt.replace(",", "").replace(".", ""))
        except:
            await update.message.reply_text("⚠ Sai định dạng số.")
            return

        add_amount(amount)
        await update.message.reply_text("✔ Đã cập nhật!")
    else:
        await update.message.reply_text("⚠ Gửi số kiểu +1000000 hoặc -2000000")


async def stat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("❌ Bạn không có quyền.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Gõ: /stat MM-YYYY")
        return

    mm, yy = context.args[0].split("-")
    s = stats_for_month(int(mm), int(yy))

    if not s:
        await update.message.reply_text("Không có dữ liệu tháng này.")
        return

    msg = (
        f"📉 THỐNG KÊ THÁNG {mm}-{yy}\n"
        f"Số ngày có dữ liệu: {s['count_days']}\n"
        f"Ngày lời nhất: {s['best'][0]} ({format_vnd(s['best'][1])})\n"
        f"Ngày lỗ nhất: {s['worst'][0]} ({format_vnd(s['worst'][1])})\n"
        f"Tổng: {format_vnd(s['total'])}\n"
        f"Trung bình ngày: {format_vnd(s['avg'])}"
    )
    await update.message.reply_text(msg)


async def add_user(update: Update, context):
    await owner_only(update, context)

    if len(context.args) < 1:
        await update.message.reply_text("Dùng: /adduser USER_ID")
        return

    new = int(context.args[0])

    cfg = json.load(open("config.json"))
    if new in cfg["allowed_users"]:
        await update.message.reply_text("⚠ User đã có quyền.")
        return

    cfg["allowed_users"].append(new)
    json.dump(cfg, open("config.json", "w"), indent=2)

    await update.message.reply_text(f"✔ Đã thêm user {new}")


async def del_user(update: Update, context):
    await owner_only(update, context)

    if len(context.args) < 1:
        await update.message.reply_text("Dùng: /deluser USER_ID")
        return

    uid = int(context.args[0])

    cfg = json.load(open("config.json"))
    if uid not in cfg["allowed_users"]:
        await update.message.reply_text("⚠ User không có trong danh sách.")
        return

    cfg["allowed_users"].remove(uid)
    json.dump(cfg, open("config.json", "w"), indent=2)

    await update.message.reply_text(f"🗑 Đã xoá user {uid}")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("deluser", del_user))
    app.add_handler(CommandHandler("stat", stat_cmd))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler))

    # tự động báo cuối ngày
    app.create_task(auto_daily_report(app))

    print("BOT RUNNING...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())

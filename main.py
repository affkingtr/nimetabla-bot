
import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask
from waitress import serve
import threading

GROUP_ID = -1002626758977
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_site_buttons():
    keyboard = [[InlineKeyboardButton("Sponsorlara Git", url="https://nimetablasponsorlar.com/")]]
    return InlineKeyboardMarkup(keyboard)

async def send_sponsor_message(chat_id, context):
    try:
        if os.path.exists("attached_assets/sponsor.jpg"):
            with open("attached_assets/sponsor.jpg", "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption="📌 Güncel sponsor bağlantısı 👇",
                    reply_markup=get_site_buttons()
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="📌 Güncel sponsor bağlantısı 👇",
                reply_markup=get_site_buttons()
            )
    except Exception as e:
        logging.error(f"Hata: {e}")

async def handle_message(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        text = update.message.text.lower()
        if any(word in text for word in ["site", "sponsor"]):
            await send_sponsor_message(update.effective_chat.id, context)

@app.route("/")
def index():
    return "Bot çalışıyor!"

def run_flask():
    serve(app, host="0.0.0.0", port=8080)

async def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN eksik.")
        return

    bot = Application.builder().token(token).build()
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.add_handler(CommandHandler("site", handle_message))

    job_queue = bot.job_queue
    job_queue.run_repeating(lambda context: send_sponsor_message(GROUP_ID, context), interval=6*60*60, first=10)

    await bot.initialize()
    await bot.start()
    logging.info("🚀 Bot başlatıldı.")
    await bot.updater.start_polling()
    await bot.updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())

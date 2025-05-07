import os
import logging
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from waitress import serve
import threading
import nest_asyncio

# Telegram sabit grup ID
GROUP_ID = -1002626758977

# Logging
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Nimet Abla Bot is running!"

# Butonlar
def get_site_buttons():
    keyboard = [[InlineKeyboardButton("Sponsorlara Git", url="https://nimetablasponsorlar.com/")]]
    return InlineKeyboardMarkup(keyboard)

# Sponsor mesajı gönderici
async def send_sponsor_message(chat_id, context):
    try:
        if os.path.exists("sponsor.jpg"):
            with open("sponsor.jpg", "rb") as img:
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
        logger.error(f"Mesaj gönderme hatası: {e}")

# Komutlar
async def site_command(update: Update, context: CallbackContext):
    await send_sponsor_message(update.effective_chat.id, context)

async def id_command(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

async def handle_message(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        text = update.message.text.lower().strip()
        trigger_words = ["site", "!site", "sponsor", "!sponsor", "sponsorlar", "!sponsorlar"]
        if any(word in text for word in trigger_words):
            await send_sponsor_message(update.effective_chat.id, context)

# Periyodik mesaj
async def send_periodic_message(context: CallbackContext):
    await send_sponsor_message(GROUP_ID, context)

# Bot başlatıcı
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler(["site", "sponsor", "sponsorlar"], site_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_periodic_message, "interval", hours=6, args=[app.bot])
    scheduler.start()

    logger.info("🚀 Bot başlatıldı ve mesajları dinliyor.")
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

# Flask sunucusunu başlat
def run_flask():
    serve(flask_app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# Ana giriş
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(run_bot())

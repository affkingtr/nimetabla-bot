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

# --- Butonlar ---
def get_site_buttons():
    keyboard = [[InlineKeyboardButton("Sponsorlara Git", url="https://nimetablasponsorlar.com/")]]
    return InlineKeyboardMarkup(keyboard)

def get_bilet_buttons():
    keyboard = [
        [InlineKeyboardButton("KAZANCIN ADRESİ ELİPSBET", url="https://tracker.elipspartners.com/link?btag=94701154_428195")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Sponsor mesajı ---
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

# --- Bilet mesajı ---
async def send_bilet_message(chat_id, context):
    caption = (
        "✅️  SADECE LİNK ÜYELERİNE ÖZELDİR\n\n"
        "💸  100.000 TL ÖDÜL\n\n"
        "Her 100 TL Yatırım Başına 1 Bilet Talep Edebilirsiniz\n\n"
        "Toplam 10.000 Bilet\n\n"
        "Yatırım Yaptıktan Sonra Biletlerinizi 72 saat içinde Moderatörlerden Talep Ediniz.\n\n"
        "Eklenen nakit ödül çevrimsizdir\n\n"
        "Almış olduğunuz bilet tutarının 5 katı kadar çekim işlemi yapabilirsiniz.\n\n"
        "1 kişi en fazla 1 ödül kazanabilir\n\n"
        "2 kişiye 20.000 ₺\n"
        "3 kişiye 10.000 ₺\n"
        "4 kişiye 5.000 ₺\n"
        "5 kişiye 2.000 ₺"
    )

    try:
        if os.path.exists("elips.jpg"):
            with open("elips.jpg", "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption=caption,
                    reply_markup=get_bilet_buttons()
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=caption,
                reply_markup=get_bilet_buttons()
            )
    except Exception as e:
        logger.error(f"Bilet mesajı gönderme hatası: {e}")

# --- Komutlar ---
async def site_command(update: Update, context: CallbackContext):
    await send_sponsor_message(update.effective_chat.id, context)

async def id_command(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

async def bilet_command(update: Update, context: CallbackContext):
    await send_bilet_message(update.effective_chat.id, context)

async def handle_message(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        text = update.message.text.lower().strip()
        trigger_words = [
            "site", "!site",
            "sponsor", "!sponsor",
            "sponsorlar", "!sponsorlar",
            "bilet", "!bilet"
        ]
        if any(word in text for word in trigger_words):
            if "bilet" in text:
                await send_bilet_message(update.effective_chat.id, context)
            else:
                await send_sponsor_message(update.effective_chat.id, context)

# --- Periyodik mesaj ---
async def send_periodic_message(context: CallbackContext):
    await send_sponsor_message(GROUP_ID, context)

# --- Bot başlatıcı ---
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler(["site", "sponsor", "sponsorlar"], site_command))
    app.add_handler(CommandHandler("bilet", bilet_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_periodic_message, "interval", hours=6, args=[app.bot])
    scheduler.start()

    logger.info("🚀 Bot başlatıldı ve mesajları dinliyor.")
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

# --- Flask sunucusu ---
def run_flask():
    serve(flask_app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- Ana giriş ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(run_bot())

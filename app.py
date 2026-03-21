# app.py
# Render-ready Telegram bot using Pyrogram + optional telebot

import os
import json
import logging
import threading
import asyncio
import signal
from datetime import datetime, timedelta

from flask import Flask, jsonify
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
)

# Optional telebot compatibility
try:
    import telebot
except ImportError:
    telebot = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables (recommended in Render secrets)
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("Missing API_ID, API_HASH, or BOT_TOKEN environment variables")

# Telegram clients
app = Client(
    "autoPost",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

telebot_client = None
if telebot is not None:
    telebot_client = telebot.TeleBot(BOT_TOKEN)

# DB files
USERS_DB = "users.json"
CHANNELS_DB = "channels.json"

# Utils for JSON DB

def _read_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_users():
    return _read_json(USERS_DB, {})


def save_users(data):
    _write_json(USERS_DB, data)


def get_user_data(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "subscription_end": (datetime.now() + timedelta(days=1)).isoformat(),
            "referrals_count": 0,
            "referred_by": None,
            "session": None,
            "groups": [],
            "caption": None,
            "waitTime": 60,
            "posting": False,
        }
        save_users(users)
    return users[uid]


def update_user(user_id, data):
    users = load_users()
    users[str(user_id)].update(data)
    save_users(users)


def has_active_subscription(user_id):
    data = get_user_data(user_id)
    end_str = data.get("subscription_end")
    if not end_str:
        return False
    end = datetime.fromisoformat(end_str)
    return end > datetime.now()


def get_referral_link(user_id):
    return f"https://t.me/{app.me.username}?start=ref_{user_id}"

# channel list
channels = _read_json(CHANNELS_DB, [])
FORCED_CHANNEL = channels[0] if channels else "TJUI9"


def is_subscribed(user_id):
    try:
        member = app.get_chat_member(f"@{FORCED_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Keyboard
homeMarkup = Markup([
    [Button("👤 حسابي", callback_data="account")],
    [Button("📋 السوبرات المضافة", callback_data="currentSupers")],
    [Button("➕ إضافة سوبر", callback_data="newSuper")],
])

# Pyrogram handlers

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        await message.reply("برجاء الاشتراك بالقناة أولاً.")
        return
    if not has_active_subscription(user_id):
        update_user(user_id, {"subscription_end": (datetime.now() + timedelta(days=1)).isoformat()})

    await message.reply(
        f"مرحباً {message.from_user.first_name}!\n- تم تشغيل البوت بنجاح.",
        reply_markup=homeMarkup,
    )


@app.on_callback_query(filters.regex(r"^(account)$"))
async def account_menu(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    end_date = datetime.fromisoformat(data["subscription_end"]).strftime("%Y-%m-%d")
    caption = (
        f"اشتراكك ينتهي: {end_date}\n"
        f"دعوات: {data.get('referrals_count', 0)}\n"
        f"رابط: {get_referral_link(user_id)}"
    )
    await callback.message.edit_text(caption)


# Background tasks
async def posting(user_id):
    data = get_user_data(user_id)
    if not data.get("posting"):
        return
    groups = data.get("groups", [])
    caption_data = data.get("caption")
    if not caption_data:
        return

    for group_id in groups:
        try:
            if caption_data.get("type") == "text":
                await app.send_message(group_id, caption_data.get("text"))
        except Exception as e:
            logger.warning("Post failed for %s: %s", group_id, e)


async def schedule_tasks():
    await asyncio.sleep(5)
    while True:
        users = load_users()
        for uid, data in users.items():
            if data.get("posting"):
                asyncio.create_task(posting(int(uid)))
        await asyncio.sleep(30)


async def subscription_checker():
    while True:
        await asyncio.sleep(3600)
        users = load_users()
        for uid, data in users.items():
            if data.get("posting") and not has_active_subscription(int(uid)):
                update_user(int(uid), {"posting": False})
                try:
                    await app.send_message(int(uid), "انتهى اشتراكك، تم إيقاف الخدمة.")
                except Exception:
                    pass


# Flask healthcheck
flask_app = Flask(__name__)


@flask_app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


def run_flask():
    port = int(os.getenv("PORT", 10000))
    logger.info("Starting Flask on port %s", port)
    flask_app.run(host="0.0.0.0", port=port, threaded=True)


def run_telebot():
    if telebot_client is None:
        return
    logger.info("Starting pyTelegramBotAPI polling thread")
    telebot_client.infinity_polling(timeout=10, long_polling_timeout=5)


async def main():
    logger.info("Starting pyrogram and background tasks")
    asyncio.create_task(schedule_tasks())
    asyncio.create_task(subscription_checker())

    await app.start()
    logger.info("Pyrogram started")
    
    # Instead of idle(), use an event to keep the loop running
    shutdown_event = asyncio.Event()
    
    # Register signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    def handle_shutdown(sig):
        logger.info("Received signal %s, initiating graceful shutdown", sig)
        shutdown_event.set()
    
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown, signal.SIGTERM)
    loop.add_signal_handler(signal.SIGINT, handle_shutdown, signal.SIGINT)
    
    try:
        await shutdown_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Stopping pyrogram")
        await app.stop()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    if telebot_client is not None:
        telebot_thread = threading.Thread(target=run_telebot, daemon=True)
        telebot_thread.start()

    asyncio.run(main())

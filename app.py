from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, json
from datetime import datetime, timedelta

API_ID = 29510141
API_HASH = "14c074a5aed49dc7752a9f8d54cf4ad4"
BOT_TOKEN = "8666985104:AAEZ_NgKD3KaaYyt1WVM4ZgQ8CMZwmZGEqE"
REQUIRED_CHANNEL = "TJUI9"
OWNER_ID = 8226014028

app = Client("autoPost", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------- بيانات المستخدمين --------------------
users_db = "users.json"
def read():
    if not os.path.exists(users_db):
        return {}
    with open(users_db) as f:
        return json.load(f)
def write(data):
    with open(users_db, "w") as f:
        json.dump(data, f, indent=2)

users = read()

def init_user(user_id):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "groups": [],
            "captions": [],
            "active_caption": None,
            "waitTime": 60,
            "posting": False,
            "referrals": 0,
            "vip_until": None if user_id == OWNER_ID else (datetime.now() + timedelta(days=1)).isoformat(),
            "required_referrals": 5
        }
        write(users)

def is_vip(user_id):
    if user_id == OWNER_ID:
        return True
    u = users.get(str(user_id), {})
    until = u.get("vip_until")
    if until is None:
        return True
    try:
        return datetime.fromisoformat(until) > datetime.now()
    except:
        return False

def generate_referral_link(user_id):
    return f"https://t.me/{app.me.username}?start=ref_{user_id}"

# -------------------- القوائم --------------------
home_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton("👤 حساڀي", callback_data="account")],
    [
        InlineKeyboardButton("📋 السوبرات", callback_data="supers"),
        InlineKeyboardButton("➕ ضيف سوبر", callback_data="add_super")
    ],
    [
        InlineKeyboardButton("⏱️ المده", callback_data="wait_time"),
        InlineKeyboardButton("📝 الكليشات", callback_data="captions")
    ],
    [
        InlineKeyboardButton("⏹️ أوقف", callback_data="stop"),
        InlineKeyboardButton("▶️ ابدأ", callback_data="start")
    ],
    [InlineKeyboardButton("🛡️ أمان", callback_data="safety")],
    [InlineKeyboardButton("🔗 رابط الإحالة", callback_data="referral")]
])

# -------------------- التحقق من الاشتراك --------------------
async def check_sub(user_id):
    try:
        await app.get_chat_member(REQUIRED_CHANNEL, user_id)
        return True
    except:
        return False

# -------------------- بداية البوت --------------------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    # معالجة الإحالة
    if len(message.command) > 1 and message.command[1].startswith("ref_"):
        ref = message.command[1][4:]
        if ref.isdigit() and int(ref) != user_id:
            referrer = int(ref)
            init_user(referrer)
            users[str(referrer)]["referrals"] += 1
            if users[str(referrer)]["referrals"] >= users[str(referrer)]["required_referrals"]:
                users[str(referrer)]["vip_until"] = None
                await app.send_message(referrer, "🎉 مبروك! أكملت 5 إحالات وأصبح اشتراكك دائماً.")
            write(users)
            await message.reply("✅ تم التسجيل عبر إحالة!\n🎁 حصلت على يوم مجاني.")
    if not await check_sub(user_id):
        return await message.reply(f"🚫 لازم تشترك بالقناة أولاً:\n@{REQUIRED_CHANNEL}")
    init_user(user_id)
    name = message.from_user.first_name
    await message.reply(
        f"✨ أهلاً بك [{name}](tg://settings) في بوت النشر التلقائي\n\n"
        "📢 **هذا البوت مجاني 100%**\n"
        "🕹️ تحكم بالبوت من الأزرار\n\n"
        "👑 المطور: @ypui5",
        reply_markup=home_markup,
        disable_web_page_preview=True
    )

# -------------------- معالجة الأزرار --------------------
@app.on_callback_query()
async def handle_callback(client, cb):
    user_id = cb.from_user.id
    if not await check_sub(user_id):
        return await cb.answer("لازم تشترك بالقناة أولاً", show_alert=True)
    init_user(user_id)
    data = cb.data

    if data == "home":
        await cb.message.edit_text(
            "✨ **أهلاً بك في بوت النشر التلقائي**\n"
            "📢 مجاني 100%\n🕹️ تحكم بالأزرار\n\n"
            "👑 المطور: @ypui5",
            reply_markup=home_markup
        )
    elif data == "account":
        await cb.message.edit_text(
            "👤 **حسابك**\n\n"
            "• لتسجيل حساب: أرسل /login\n"
            "• لتبديل الحساب: أرسل /switch\n"
            "⚠️ لا تشارك جلسة الحساب مع أي شخص.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]])
        )
    elif data == "supers":
        groups = users[str(user_id)].get("groups", [])
        if not groups:
            return await cb.answer("ماكو سوبرات مضافة", show_alert=True)
        text = "📋 **السوبرات المضافة:**\n"
        for g in groups:
            text += f"• {g}\n"
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]]))
    elif data == "add_super":
        await cb.message.edit_text(
            "🔗 **أرسل رابط السوبر أو المعرف الرقمي**\n"
            "مثال: @username\nأو -100123456789\nأو https://t.me/+xxxxx\n\n"
            "أرسل /cancel للإلغاء",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]])
        )
    elif data == "wait_time":
        await cb.message.edit_text(
            f"⏱️ **أرسل المدة بالثواني بين كل رسالة**\n"
            f"الحد الأدنى: {30}\nالحد الأقصى: {86400//3600} ساعة\nمثال: 60\n\n"
            "أرسل /cancel للإلغاء",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]])
        )
    elif data == "captions":
        captions = users[str(user_id)].get("captions", [])
        active = users[str(user_id)].get("active_caption")
        text = "📝 **الكليشات المحفوظة:**\n"
        if captions:
            for idx, cap in enumerate(captions):
                if cap.get("type") == "text":
                    short = cap.get("text", "")[:30]
                elif cap.get("type") == "photo":
                    short = "📷 صورة"
                else:
                    short = "🎥 فيديو"
                mark = "✅ " if cap == active else "   "
                text += f"{mark}{idx+1}. {short}\n"
        else:
            text += "لا توجد كليشات\n"
        text += "\nاستخدم الأوامر:\n/addtext – إضافة نصية\n/addphoto – إضافة صورة\n/addvideo – إضافة فيديو\n/select [رقم] – اختيار نشطة\n/delcap [رقم] – حذف"
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]]))
    elif data == "start":
        users[str(user_id)]["posting"] = True
        write(users)
        await cb.message.edit_text(
            "✅ **بدأ النشر التلقائي**\n\n"
            "🔔 نصيحة: إذا حسيت ببطء أو مشكلة، أوقف النشر.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹️ إيقاف", callback_data="stop")], [InlineKeyboardButton("رجوع", callback_data="home")]])
        )
    elif data == "stop":
        users[str(user_id)]["posting"] = False
        write(users)
        await cb.message.edit_text(
            "⏸️ **تم إيقاف النشر**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ بدء", callback_data="start")], [InlineKeyboardButton("رجوع", callback_data="home")]])
        )
    elif data == "safety":
        text = (
            "🛡️ **تعليمات الأمان**\n\n"
            "1️⃣ استخدم حسابك الأساسي بأمان.\n"
            "2️⃣ لا تشارك جلسة الحساب.\n"
            "3️⃣ لا تضبط مدة أقل من 30 ثانية.\n"
            "4️⃣ لا تنشر بأكثر من 10 مجموعات بالدورة.\n\n"
            "📌 أي استفسار: @ypui5"
        )
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]]))
    elif data == "referral":
        link = generate_referral_link(user_id)
        referrals = users[str(user_id)].get("referrals", 0)
        needed = users[str(user_id)].get("required_referrals", 5)
        text = (
            f"🔗 **رابط الإحالة الخاص بك:**\n`{link}`\n\n"
            f"👥 عدد الإحالات: {referrals}/{needed}\n"
            f"🔁 تحتاج {needed-referrals} إحالات لتصبح دائم.\n\n"
            "📢 أرسل الرابط لأصدقائك، كل من يسجل عبره يحصل على يوم مجاني، وأنت تحصل على إحالة."
        )
        await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="home")]]))
    else:
        await cb.answer("قيد التطوير")

# -------------------- أوامر إضافية --------------------
@app.on_message(filters.command("login") & filters.private)
async def login_cmd(client, message):
    await message.reply("📱 أرسل رقم هاتفك (مثال: +964xxxxxxxxx)\nأو /cancel للإلغاء")

@app.on_message(filters.command("switch") & filters.private)
async def switch_cmd(client, message):
    await message.reply("🔄 أرسل رقم الهاتف الجديد\nأو /cancel للإلغاء")

@app.on_message(filters.command("addtext") & filters.private)
async def add_text_cmd(client, message):
    await message.reply("📝 أرسل النص الجديد (الكليشة النصية)\nأو /cancel للإلغاء")

@app.on_message(filters.command("addphoto") & filters.private)
async def add_photo_cmd(client, message):
    await message.reply("🖼️ أرسل الصورة (كصورة)\nيمكنك إضافة نص تعليق مع الصورة.\nأو /cancel للإلغاء")

@app.on_message(filters.command("addvideo") & filters.private)
async def add_video_cmd(client, message):
    await message.reply("🎬 أرسل الفيديو (كفيديو)\nيمكنك إضافة نص تعليق.\nأو /cancel للإلغاء")

@app.on_message(filters.command("select") & filters.private)
async def select_caption_cmd(client, message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("استخدم: /select [رقم]")
    try:
        idx = int(parts[1]) - 1
        captions = users[str(message.from_user.id)].get("captions", [])
        if 0 <= idx < len(captions):
            users[str(message.from_user.id)]["active_caption"] = captions[idx]
            write(users)
            await message.reply(f"✅ تم اختيار الكليشة رقم {idx+1} كالنشطة.")
        else:
            await message.reply("❌ الرقم غير صحيح.")
    except:
        await message.reply("❌ الرقم غير صحيح.")

@app.on_message(filters.command("delcap") & filters.private)
async def del_caption_cmd(client, message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("استخدم: /delcap [رقم]")
    try:
        idx = int(parts[1]) - 1
        captions = users[str(message.from_user.id)].get("captions", [])
        if 0 <= idx < len(captions):
            removed = captions.pop(idx)
            if removed == users[str(message.from_user.id)].get("active_caption"):
                users[str(message.from_user.id)]["active_caption"] = captions[0] if captions else None
            write(users)
            await message.reply(f"🗑 تم حذف الكليشة رقم {idx+1}.")
        else:
            await message.reply("❌ الرقم غير صحيح.")
    except:
        await message.reply("❌ الرقم غير صحيح.")

# -------------------- تشغيل البوت --------------------
if __name__ == "__main__":
    print("🚀 البوت يعمل...")
    app.run()
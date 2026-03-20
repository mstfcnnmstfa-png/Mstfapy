import os
import json
import re
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, ForceReply,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button
)
from pyrogram.errors import (
    UserNotParticipant, FloodWait,
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid
)

# -------------------- إعدادات البوت --------------------
API_ID = 29510141
API_HASH = "14c074a5aed49dc7752a9f8d54cf4ad4"
BOT_TOKEN = "8666985104:AAEZ_NgKD3KaaYyt1WVM4ZgQ8CMZwmZGEqE"
REQUIRED_CHANNEL = "TJUI9"
OWNER_ID = 8226014028
MIN_WAIT_TIME = 30
MAX_WAIT_TIME = 86400

app = Client("autoPost", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------- تخزين البيانات --------------------
users_db = "users.json"

def read(fp):
    if not os.path.exists(fp):
        with open(fp, "w") as f:
            json.dump({}, f)
    with open(fp) as f:
        return json.load(f)

def write(fp, data):
    with open(fp, "w") as f:
        json.dump(data, f, indent=2)

users = read(users_db)

# -------------------- هيكل بيانات المستخدم --------------------
def init_user(user_id):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "sessions": [],           # قائمة الحسابات المسجلة
            "groups": [],              # قائمة السوبرات (معرفات أو روابط)
            "waitTime": 60,
            "auto_delete": 0,         # 0 = لا يحذف، أي رقم = ثواني
            "captions": [],           # قائمة الكليشات (نص/صورة/فيديو)
            "active_caption": None,
            "posting": False,
            "referrals": 0,           # عدد الإحالات
            "vip_until": None if user_id == OWNER_ID else (datetime.now() + timedelta(days=1)).isoformat(),
            "required_referrals": 5
        }
        write(users_db, users)

def is_vip(user_id):
    if user_id == OWNER_ID:
        return True
    uid = str(user_id)
    if uid not in users:
        return False
    vip_until = users[uid].get("vip_until")
    if vip_until is None:
        return True
    try:
        expiry = datetime.fromisoformat(vip_until)
        return expiry > datetime.now()
    except:
        return False

# -------------------- دوال الإحالة --------------------
def generate_referral_link(user_id):
    return f"https://t.me/{app.me.username}?start=ref_{user_id}"

async def handle_referral(message, referrer_id):
    referrer_id = int(referrer_id)
    uid = str(message.from_user.id)
    if uid not in users:
        init_user(message.from_user.id)
    if str(referrer_id) in users and referrer_id != OWNER_ID:
        users[str(referrer_id)]["referrals"] += 1
        if users[str(referrer_id)]["referrals"] >= users[str(referrer_id)]["required_referrals"]:
            users[str(referrer_id)]["vip_until"] = None
            await app.send_message(referrer_id, "🎉 مبروك! أكملت 5 إحالات وأصبح اشتراكك دائماً مدى الحياة.")
        write(users_db, users)
    await message.reply(
        "✅ تم تسجيل دخولك عبر رابط إحالة.\n"
        "🎁 لقد حصلت على **يوم مجاني** تجريبي.\n"
        "🔁 إذا أردت الحصول على اشتراك دائم، قم بدعوة 5 أشخاص عبر رابط الإحالة الخاص بك.\n"
        "📌 يمكنك الحصول على رابط الإحالة من خلال الزر المخصص له في لوحة التحكم."
    )

# -------------------- القوائم --------------------
home_markup = Markup([
    [Button("👤 حساڀي", callback_data="account")],
    [
        Button("📋 السوبرات اللي مضافه", callback_data="supers"),
        Button("➕ ضيف سوبر", callback_data="add_super")
    ],
    [
        Button("⏱️ المده بين كل نشر", callback_data="wait_time"),
        Button("📋 الكليشات", callback_data="captions")
    ],
    [
        Button("⏹️ أوقف النشر", callback_data="stop"),
        Button("▶️ ابدأ النشر", callback_data="start")
    ],
    [Button("🛡️ تعليمات الأمان", callback_data="safety")],
    [Button("🔗 رابط الإحالة", callback_data="referral")]
])

# -------------------- دوال التحقق --------------------
async def check_sub(user_id: int) -> bool:
    try:
        await app.get_chat_member(REQUIRED_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return False

# -------------------- بداية البوت --------------------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if len(message.command) > 1 and message.command[1].startswith("ref_"):
        referrer_id = message.command[1][4:]
        if referrer_id.isdigit() and int(referrer_id) != user_id:
            await handle_referral(message, referrer_id)
    if not await check_sub(user_id):
        return await message.reply(
            f"🚫 **عذراً عزيزي، لازم تشترك بالقناة أولاً.**\n"
            f"🔗 **القناة:** @{REQUIRED_CHANNEL}\n"
            f"✅ **اشترك ورجع أرسل /start**"
        )
    init_user(user_id)
    name = message.from_user.first_name
    reply_markup = home_markup
    if user_id == OWNER_ID:
        owner_button = [Button("🔧 لوحة المالك", callback_data="owner_panel")]
        new_buttons = list(home_markup.inline_keyboard)
        new_buttons.append(owner_button)
        reply_markup = Markup(new_buttons)
    await message.reply(
        f"✨ **أهلاً بك [{name}](tg://settings) في بوت النشر التلقائي**\n\n"
        "📢 **هذا البوت مجاني 100% بالكامل يخليك تنشر رسايلك بكل الكروبات وبدون أي تعب**\n\n"
        "🕹️ **اتحكم بالبوت من الدكم (الأزرار) الموجودة جوه**\n\n"
        "👑 **البوت من تطوير: @ypui5**\n\n"
        "⚠️ **تنبيه:** تكدر تستخدم حسابك الأساسي وبكل أمان بس لازم تتبع التعليمات\n"
        "أي مشكله تواجهك راسل المطور @ypui5",
        reply_markup=reply_markup
    )

# -------------------- دوال الأزرار الرئيسية --------------------
@app.on_callback_query()
async def handle_callback(client: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    data = cb.data

    if not await check_sub(user_id):
        return await cb.answer("لازم تشترك بالقناة أولاً", show_alert=True)

    if data == "home":
        await to_home(cb)
    elif data == "account":
        await account_menu(cb)
    elif data == "supers":
        await current_supers(cb)
    elif data == "add_super":
        await add_super(cb)
    elif data == "wait_time":
        await set_wait_time(cb)
    elif data == "captions":
        await manage_captions(cb)
    elif data == "start":
        await start_posting(cb)
    elif data == "stop":
        await stop_posting(cb)
    elif data == "safety":
        await safety(cb)
    elif data == "referral":
        await referral_menu(cb)
    elif data.startswith("del_super_"):
        await del_super(cb, data.split("_")[2])
    elif data.startswith("select_caption_"):
        await select_caption(cb, int(data.split("_")[2]))
    elif data.startswith("del_caption_"):
        await delete_caption(cb, int(data.split("_")[2]))
    elif data == "add_text_caption":
        await add_text_caption(cb)
    elif data == "add_photo_caption":
        await add_photo_caption(cb)
    elif data == "add_video_caption":
        await add_video_caption(cb)
    elif data == "add_account":
        await add_account(cb)
    elif data == "list_accounts":
        await list_accounts(cb)
    elif data.startswith("del_account_"):
        await del_account(cb, int(data.split("_")[2]))
    elif data == "owner_panel" and user_id == OWNER_ID:
        await owner_panel(cb)
    elif data == "stats" and user_id == OWNER_ID:
        await stats(cb)
    elif data == "list_users" and user_id == OWNER_ID:
        await list_users(cb)
    elif data == "give_free_form" and user_id == OWNER_ID:
        await give_free_form(cb)

async def to_home(cb):
    name = cb.from_user.first_name
    reply_markup = home_markup
    if cb.from_user.id == OWNER_ID:
        owner_button = [Button("🔧 لوحة المالك", callback_data="owner_panel")]
        new_buttons = list(home_markup.inline_keyboard)
        new_buttons.append(owner_button)
        reply_markup = Markup(new_buttons)
    await cb.message.edit_text(
        f"✨ **أهلاً بك [{name}](tg://settings) في بوت النشر التلقائي**\n\n"
        "📢 **هذا البوت مجاني 100% بالكامل يخليك تنشر رسايلك بكل الكروبات وبدون أي تعب**\n\n"
        "🕹️ **اتحكم بالبوت من الدكم (الأزرار) الموجودة جوه**\n\n"
        "👑 **البوت من تطوير: @ypui5**\n\n"
        "⚠️ **تنبيه:** تكدر تستخدم حسابك الأساسي وبكل أمان بس لازم تتبع التعليمات\n"
        "أي مشكله تواجهك راسل المطور @ypui5",
        reply_markup=reply_markup
    )

async def safety(cb):
    text = (
        "🛡️ **تعليمات الأمان لحماية حسابك (بوت مجاني):**\n\n"
        "1️⃣ **تقدر تستخدم حسابك الأساسي بأمان** إذا اتبعت الإرشادات.\n"
        "2️⃣ **لا تشارك جلسة التسجيل (session) مع أي شخص** – من يملك الجلسة يملك حسابك كاملاً.\n"
        "3️⃣ **لا تضبط مدة أقل من 30 ثانية** – النشر السريع جداً يسبب حظر مؤقت. الأفضل 200 ثانية فأكثر.\n"
        "4️⃣ **إذا صار خطأ FloodWait** – البوت راح ينتظر تلقائياً وينشر بعدها.\n"
        "5️⃣ **لإيقاف النشر بسرعة** – استخدم زر إيقاف النشر.\n"
        "6️⃣ **لا تنشر في أكثر من 10 مجموعات في الدورة الواحدة** – لتجنب الحظر.\n\n"
        "📌 **أي استفسار**: @ypui5"
    )
    await cb.message.edit_text(text, reply_markup=Markup([[Button("- رجوع -", callback_data="home")]]))

async def referral_menu(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    link = generate_referral_link(user_id)
    referrals = users[str(user_id)].get("referrals", 0)
    needed = users[str(user_id)].get("required_referrals", 5)
    remaining = needed - referrals
    text = (
        f"🔗 **رابط الإحالة الخاص بك:**\n`{link}`\n\n"
        f"👥 عدد الإحالات: **{referrals}** / {needed}\n"
        f"🔁 تحتاج **{remaining}** إحالات لتصبح عضو **دائم** (مدى الحياة).\n\n"
        "📢 **كيف تعمل؟**\n"
        "• أرسل الرابط لأصدقائك.\n"
        "• عندما يدخل شخص عبر رابطك، يحصل هو على يوم مجاني، وأنت تحصل على إحالة.\n"
        "• عند وصولك إلى 5 إحالات، يصبح اشتراكك **دائماً** دون انتهاء.\n\n"
        "✅ **ملاحظة:** أنت حالياً في الفترة التجريبية المجانية (يوم واحد)."
    )
    await cb.message.edit_text(text, reply_markup=Markup([[Button("- رجوع -", callback_data="home")]]))

# -------------------- إدارة الحسابات المتعددة --------------------
async def account_menu(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    name = cb.from_user.first_name
    sessions = users[str(user_id)].get("sessions", [])
    count = len(sessions)
    markup = Markup([
        [Button("➕ إضافة حساب جديد", callback_data="add_account")],
        [Button(f"📱 الحسابات المسجلة ({count})", callback_data="list_accounts")],
        [Button("- رجوع -", callback_data="home")]
    ])
    await cb.message.edit_text(
        f"👤 **مرحباً [{name}](tg://settings) هذي صفحة حسابك**\n\n"
        f"📱 لديك **{count}** حساب مسجل.\n"
        "➕ **إضافة حساب جديد** = تضيف حساب تليگرام آخر للنشر.\n"
        "📋 **الحسابات المسجلة** = تعرضها ويمكنك حذف أي حساب.\n\n"
        "⚠️ **لا تشارك جلسة حسابك مع أي شخص.**",
        reply_markup=markup
    )

async def add_account(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            "📱 **دز رقم هاتف الحساب الجديد (مثال: +964xxxxxxxxx)**\n❌ **إذا تريد تلغي اكتب /cancel**",
            timeout=30
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- رجوع -", callback_data="account")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="account")]]))
    await perform_login(ask, user_id)

async def perform_login(msg, main_user_id):
    phone = msg.text
    wait_msg = await msg.reply("🔄 **يتم تسجيل الدخول...**")
    client = Client("user_temp", in_memory=True, api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    reMarkup = Markup([[Button("- حاول مرة ثانية -", callback_data="add_account"),
                        Button("- رجوع -", callback_data="account")]])
    try:
        sent_code = await client.send_code(phone)
    except PhoneNumberInvalid:
        return await wait_msg.edit_text("❌ **رقم الهاتف خطأ**", reply_markup=reMarkup)
    try:
        code_msg = await app.ask(
            main_user_id,
            "🔢 **دز الكود اللي وصلك (أرقام فقط)**",
            timeout=120
        )
    except:
        return await wait_msg.reply("⏰ **انتهت المدة**", reply_markup=reMarkup)
    try:
        await client.sign_in(phone, sent_code.phone_code_hash, code_msg.text.replace(" ", ""))
    except PhoneCodeInvalid:
        return await code_msg.reply("❌ **الكود غلط**", reply_markup=reMarkup)
    except PhoneCodeExpired:
        return await code_msg.reply("⌛ **الكود انتهت صلاحيته**", reply_markup=reMarkup)
    except SessionPasswordNeeded:
        try:
            pwd_msg = await app.ask(
                main_user_id,
                "🔐 **الحساب عليه تحقق بخطوتين، دز كلمة المرور**",
                timeout=180
            )
        except:
            return await wait_msg.reply("⏰ **انتهت المدة**", reply_markup=reMarkup)
        try:
            await client.check_password(pwd_msg.text)
        except PasswordHashInvalid:
            return await pwd_msg.reply("❌ **كلمة المرور غلط**", reply_markup=reMarkup)
    session = await client.export_session_string()
    await client.disconnect()
    users[str(main_user_id)]["sessions"].append({
        "session": session,
        "phone": phone
    })
    write(users_db, users)
    await app.send_message(
        main_user_id,
        "✅ **تم تسجيل الحساب بنجاح**\n\n"
        "🔐 **نصيحة:** لا تشارك جلسة الحساب مع أي شخص.",
        reply_markup=Markup([[Button("- الرئيسية -", callback_data="home")]])
    )

async def list_accounts(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    sessions = users[str(user_id)].get("sessions", [])
    if not sessions:
        await cb.answer("ماكو حسابات مسجلة", show_alert=True)
        return await account_menu(cb)
    markup = []
    for idx, acc in enumerate(sessions):
        phone = acc.get("phone", f"حساب {idx+1}")
        markup.append([Button(f"{phone}", callback_data="noop"),
                       Button("🗑", callback_data=f"del_account_{idx}")])
    markup.append([Button("- رجوع -", callback_data="account")])
    await cb.message.edit_text("📱 **الحسابات المسجلة:**", reply_markup=Markup(markup))

async def del_account(cb, idx):
    user_id = cb.from_user.id
    init_user(user_id)
    sessions = users[str(user_id)].get("sessions", [])
    if 0 <= idx < len(sessions):
        sessions.pop(idx)
        write(users_db, users)
        await cb.answer("🗑 تم حذف الحساب", show_alert=True)
    else:
        await cb.answer("❌ الحساب غير موجود", show_alert=True)
    await list_accounts(cb)

# -------------------- إدارة السوبرات --------------------
async def add_super(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            "🔗 **دز رابط السوبر أو المعرف الرقمي**\n❌ **إذا تريد تلغي اكتب /cancel**\n\n"
            "📌 **ملاحظة:** يمكنك إرسال أي رابط (حتى الخاص) وسيتم حفظه.",
            timeout=60
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- رجوع -", callback_data="home")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="home")]]))
    text = ask.text.strip()
    if re.match(r'https?://t\.me/\+', text) or re.match(r'https?://t\.me/joinchat/', text):
        chat_id = text
    elif text.startswith('@'):
        chat_id = text
    elif text.lstrip('-').isdigit():
        chat_id = int(text)
    else:
        chat_id = text
    # محاولة تحويل إلى معرف
    if isinstance(chat_id, (int, str)) and not (isinstance(chat_id, str) and chat_id.startswith('https://t.me/+')):
        try:
            if isinstance(chat_id, int):
                chat = await app.get_chat(chat_id)
            else:
                chat = await app.get_chat(chat_id)
            chat_id = chat.id
        except:
            pass
    if chat_id not in users[str(user_id)]["groups"]:
        users[str(user_id)]["groups"].append(chat_id)
        write(users_db, users)
        await ask.reply("✅ **تمت الإضافة**", reply_markup=Markup([[Button("- الرئيسية -", callback_data="home")]]))
    else:
        await ask.reply("⚠️ **هالمجموعة مضافة مسبقاً**", reply_markup=Markup([[Button("- الرئيسية -", callback_data="home")]]))

async def current_supers(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    groups = users[str(user_id)].get("groups", [])
    if not groups:
        return await cb.answer("ماكو سوبرات مضافة", show_alert=True)
    markup = []
    for g in groups:
        if isinstance(g, int):
            try:
                chat = await app.get_chat(g)
                title = chat.title
            except:
                title = str(g)
        elif isinstance(g, str) and (g.startswith('https://t.me/+') or g.startswith('https://t.me/joinchat/')):
            title = "رابط خاص"
        elif isinstance(g, str) and g.startswith('@'):
            try:
                chat = await app.get_chat(g)
                title = chat.title
            except:
                title = g
        else:
            title = str(g)[:20]
        if len(title) > 25:
            title = title[:22] + "..."
        markup.append([Button(title, callback_data="noop"),
                       Button("🗑", callback_data=f"del_super_{g}")])
    markup.append([Button("- الرئيسية -", callback_data="home")])
    await cb.message.edit_text("📋 **السوبرات المضافة:**", reply_markup=Markup(markup))

async def del_super(cb, g):
    user_id = cb.from_user.id
    init_user(user_id)
    try:
        g = int(g)
    except:
        pass
    if g in users[str(user_id)]["groups"]:
        users[str(user_id)]["groups"].remove(g)
        write(users_db, users)
        await cb.answer("🗑 **تم الحذف**", show_alert=True)
    await current_supers(cb)

# -------------------- إدارة الكليشات --------------------
async def manage_captions(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    captions = users[str(user_id)].get("captions", [])
    active = users[str(user_id)].get("active_caption")
    markup = []
    if captions:
        for idx, cap in enumerate(captions):
            if cap.get("type") == "photo":
                short = "📷 صورة"
            elif cap.get("type") == "video":
                short = "🎥 فيديو"
            else:
                short = cap.get("text", "")[:25] + ("..." if len(cap.get("text", "")) > 25 else "")
            prefix = "✅ " if cap == active else "   "
            markup.append([Button(f"{prefix}{short}", callback_data=f"select_caption_{idx}"),
                           Button("🗑", callback_data=f"del_caption_{idx}")])
    else:
        markup.append([Button("📭 لا توجد كليشات", callback_data="noop")])
    markup.append([Button("➕ إضافة كليشة نصية", callback_data="add_text_caption")])
    markup.append([Button("🖼️ إضافة صورة", callback_data="add_photo_caption")])
    markup.append([Button("🎬 إضافة فيديو", callback_data="add_video_caption")])
    markup.append([Button("- الرئيسية -", callback_data="home")])
    await cb.message.edit_text(
        "📋 **قائمة الكليشات:**\n(✅ = النشطة حالياً)\n\n"
        "يمكنك إضافة كليشات نصية، صور، أو فيديوهات.\n"
        "اختر النوع المناسب.",
        reply_markup=Markup(markup)
    )

async def add_text_caption(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            "📝 **أرسل النص الجديد (الكليشة النصية)**\n❌ **إذا تريد تلغي اكتب /cancel**",
            timeout=120
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    new_caption = {"type": "text", "text": ask.text}
    users[str(user_id)]["captions"].append(new_caption)
    if users[str(user_id)]["active_caption"] is None:
        users[str(user_id)]["active_caption"] = new_caption
    write(users_db, users)
    await ask.reply("✅ **تمت إضافة الكليشة النصية**", reply_markup=Markup([[Button("- رجوع للكليشات -", callback_data="captions")]]))

async def add_photo_caption(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            "🖼️ **أرسل الصورة (كصورة)**\nيمكنك إضافة نص تعليق مع الصورة.\n❌ **إذا تريد تلغي اكتب /cancel**",
            timeout=120,
            filters=lambda m: m.photo or m.text
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    if ask.photo:
        new_caption = {"type": "photo", "file_id": ask.photo.file_id, "caption": ask.caption or ""}
        users[str(user_id)]["captions"].append(new_caption)
        if users[str(user_id)]["active_caption"] is None:
            users[str(user_id)]["active_caption"] = new_caption
        write(users_db, users)
        await ask.reply("✅ **تمت إضافة الصورة ككليشة**", reply_markup=Markup([[Button("- رجوع للكليشات -", callback_data="captions")]]))
    else:
        await ask.reply("❌ لم يتم إرسال صورة صالحة.", reply_markup=Markup([[Button("- حاول مرة ثانية -", callback_data="add_photo_caption")]]))

async def add_video_caption(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            "🎬 **أرسل الفيديو (كفيديو)**\nيمكنك إضافة نص تعليق مع الفيديو.\n❌ **إذا تريد تلغي اكتب /cancel**",
            timeout=120,
            filters=lambda m: m.video or m.text
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="captions")]]))
    if ask.video:
        new_caption = {"type": "video", "file_id": ask.video.file_id, "caption": ask.caption or ""}
        users[str(user_id)]["captions"].append(new_caption)
        if users[str(user_id)]["active_caption"] is None:
            users[str(user_id)]["active_caption"] = new_caption
        write(users_db, users)
        await ask.reply("✅ **تمت إضافة الفيديو ككليشة**", reply_markup=Markup([[Button("- رجوع للكليشات -", callback_data="captions")]]))
    else:
        await ask.reply("❌ لم يتم إرسال فيديو صالح.", reply_markup=Markup([[Button("- حاول مرة ثانية -", callback_data="add_video_caption")]]))

async def select_caption(cb, idx):
    user_id = cb.from_user.id
    init_user(user_id)
    captions = users[str(user_id)].get("captions", [])
    if 0 <= idx < len(captions):
        users[str(user_id)]["active_caption"] = captions[idx]
        write(users_db, users)
        await cb.answer("✅ تم تعيين الكليشة كالنشطة", show_alert=True)
    else:
        await cb.answer("❌ الكليشة غير موجودة", show_alert=True)
    await manage_captions(cb)

async def delete_caption(cb, idx):
    user_id = cb.from_user.id
    init_user(user_id)
    captions = users[str(user_id)].get("captions", [])
    active = users[str(user_id)].get("active_caption")
    if 0 <= idx < len(captions):
        removed = captions.pop(idx)
        if removed == active:
            users[str(user_id)]["active_caption"] = captions[0] if captions else None
        write(users_db, users)
        await cb.answer("🗑 تم حذف الكليشة", show_alert=True)
    else:
        await cb.answer("❌ الكليشة غير موجودة", show_alert=True)
    await manage_captions(cb)

# -------------------- تعيين المدة --------------------
async def set_wait_time(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    await cb.message.delete()
    try:
        ask = await app.ask(
            user_id,
            f"⏱️ **دز المدة بالثواني بين كل رسالة والثانية**\n"
            f"الحد الأدنى: {MIN_WAIT_TIME} ثانية (حماية للحساب)\n"
            f"الحد الأقصى: {MAX_WAIT_TIME//3600} ساعة\n"
            f"مثال: 60 = دقيقة\n"
            f"❌ **إذا تريد تلغي اكتب /cancel**",
            timeout=120
        )
    except:
        return await cb.message.reply("⏰ **انتهت المدة**", reply_markup=Markup([[Button("- حاول مرة ثانية -", callback_data="wait_time"), Button("- رجوع -", callback_data="home")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ **تم الإلغاء**", reply_markup=Markup([[Button("- رجوع -", callback_data="home")]]))
    try:
        sec = int(ask.text)
    except:
        return await ask.reply("❌ **دز رقم صحيح**", reply_markup=Markup([[Button("- حاول مرة ثانية -", callback_data="wait_time"), Button("- رجوع -", callback_data="home")]]))
    if sec < MIN_WAIT_TIME or sec > MAX_WAIT_TIME:
        return await ask.reply(f"⚠️ **المدة خارج الحدود المسموحة**", reply_markup=Markup([[Button("- حاول مرة ثانية -", callback_data="wait_time"), Button("- رجوع -", callback_data="home")]]))
    users[str(user_id)]["waitTime"] = sec
    write(users_db, users)
    await ask.reply("✅ **تم تعيين المدة**", reply_markup=Markup([[Button("- الرئيسية -", callback_data="home")]]))

# -------------------- بدء وإيقاف النشر --------------------
async def start_posting(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    data = users[str(user_id)]
    if not data.get("sessions"):
        return await cb.answer("❌ لازم تسجل حساب أولاً", show_alert=True)
    if not data.get("groups"):
        return await cb.answer("❌ أضف سوبرات أولاً", show_alert=True)
    if not data.get("active_caption"):
        return await cb.answer("❌ ماكو كليشة نشطة. أضف كليشة من زر 📋 الكليشات", show_alert=True)
    if not is_vip(user_id):
        return await cb.answer("❌ اشتراكك انتهى. استخدم رابط الإحالة لتجديده.", show_alert=True)
    if data.get("posting"):
        return await cb.answer("النشر شغال من قبل", show_alert=True)
    data["posting"] = True
    write(users_db, users)
    asyncio.create_task(posting_task(user_id))
    await cb.message.edit_text(
        "✅ **بدأ النشر التلقائي**\n\n"
        "🔔 **نصيحة:** إذا حسيت إن الحساب يتأخر أو يصير فيه مشاكل، أوقف النشر فوراً.",
        reply_markup=Markup([[Button("- إيقاف النشر -", callback_data="stop"),
                              Button("- الرئيسية -", callback_data="home")]])
    )

async def stop_posting(cb):
    user_id = cb.from_user.id
    init_user(user_id)
    if not users[str(user_id)].get("posting"):
        return await cb.answer("النشر متوقف من قبل", show_alert=True)
    users[str(user_id)]["posting"] = False
    write(users_db, users)
    await cb.message.edit_text(
        "⏸️ **تم إيقاف النشر**",
        reply_markup=Markup([[Button("- بدء النشر -", callback_data="start"),
                              Button("- الرئيسية -", callback_data="home")]])
    )

# -------------------- مهمة النشر --------------------
async def posting_task(user_id):
    user_data = users[str(user_id)]
    sessions = user_data.get("sessions", [])
    if not sessions:
        return
    # إنشاء عملاء للحسابات
    clients = []
    for acc in sessions:
        cl = Client(f"user_{user_id}_{len(clients)}", api_id=API_ID, api_hash=API_HASH, session_string=acc["session"])
        await cl.start()
        clients.append(cl)
    idx = 0
    while user_data.get("posting") and is_vip(user_id):
        wait = user_data.get("waitTime", 60)
        caption_obj = user_data.get("active_caption")
        if not caption_obj:
            break
        groups = user_data["groups"][:]
        for group in groups:
            cl = clients[idx % len(clients)]
            idx += 1
            try:
                if isinstance(group, int):
                    chat_id = group
                elif isinstance(group, str) and (group.startswith('https://t.me/+') or group.startswith('https://t.me/joinchat/')):
                    try:
                        chat = await cl.join_chat(group)
                        chat_id = chat.id
                        # تحديث القائمة
                        i = user_data["groups"].index(group)
                        user_data["groups"][i] = chat_id
                        write(users_db, users)
                    except Exception as e:
                        await app.send_message(user_id, f"❌ فشل الانضمام إلى {group}: {e}")
                        continue
                elif isinstance(group, str) and group.startswith('@'):
                    chat_id = group
                else:
                    await app.send_message(user_id, f"⚠️ نوع غير معروف: {group}")
                    continue
                # إرسال حسب النوع
                if caption_obj["type"] == "text":
                    await cl.send_message(chat_id, caption_obj["text"])
                elif caption_obj["type"] == "photo":
                    await cl.send_photo(chat_id, caption_obj["file_id"], caption=caption_obj.get("caption", ""))
                elif caption_obj["type"] == "video":
                    await cl.send_video(chat_id, caption_obj["file_id"], caption=caption_obj.get("caption", ""))
                print(f"✅ تم الإرسال إلى {chat_id}")
            except FloodWait as e:
                await app.send_message(user_id, f"⏳ انتظار {e.x} ثانية")
                await asyncio.sleep(e.x)
            except Exception as e:
                await app.send_message(user_id, f"❌ خطأ في {group}: {e}")
        await asyncio.sleep(wait)
    for cl in clients:
        await cl.stop()

# -------------------- دوال المالك --------------------
async def owner_panel(cb):
    markup = Markup([
        [Button("📊 إحصائيات البوت", callback_data="stats")],
        [Button("👥 قائمة المستخدمين", callback_data="list_users")],
        [Button("🎁 منح اشتراك", callback_data="give_free_form")],
        [Button("- رجوع -", callback_data="home")]
    ])
    await cb.message.edit_text("🔧 **لوحة المالك**\nاختر أحد الخيارات:", reply_markup=markup)

async def stats(cb):
    total = len(users)
    active = sum(1 for u in users.values() if u.get("posting", False))
    vip = sum(1 for uid in users if is_vip(int(uid)))
    await cb.answer(f"📊 إحصائيات:\nإجمالي المستخدمين: {total}\nنشط: {active}\nمشتركين: {vip}", show_alert=True)

async def list_users(cb):
    users_list = list(users.items())[:10]
    text = "👥 **أول 10 مستخدمين:**\n\n"
    for uid, data in users_list:
        text += f"🆔 `{uid}` | اشتراك: {'دائم' if is_vip(int(uid)) else 'تجريبي'}\n"
    markup = Markup([[Button("- رجوع -", callback_data="owner_panel")]])
    await cb.message.edit_text(text, reply_markup=markup)

async def give_free_form(cb):
    await cb.message.delete()
    try:
        ask = await app.ask(
            OWNER_ID,
            "🎁 **أرسل ايدي المستخدم وعدد الأيام (اختياري)**\nمثال: `8226014028 30`\nإذا لم ترسل أيام، يصبح دائم.\nأو ارسل /cancel للإلغاء.",
            timeout=60
        )
    except:
        return await cb.message.reply("⏰ انتهت المدة.", reply_markup=Markup([[Button("- رجوع -", callback_data="owner_panel")]]))
    if ask.text == "/cancel":
        return await ask.reply("✅ تم الإلغاء", reply_markup=Markup([[Button("- رجوع -", callback_data="owner_panel")]]))
    parts = ask.text.split()
    if len(parts) < 1:
        return await ask.reply("❌ صيغة غير صحيحة.")
    try:
        target_id = int(parts[0])
    except:
        return await ask.reply("❌ ايدي المستخدم غير صحيح.")
    days = None
    if len(parts) >= 2:
        try:
            days = int(parts[1])
        except:
            return await ask.reply("❌ عدد الأيام غير صحيح.")
    init_user(target_id)
    if days is None:
        users[str(target_id)]["vip_until"] = None
        expiry_text = "دائم (مدى الحياة)"
    else:
        new_date = datetime.now() + timedelta(days=days)
        users[str(target_id)]["vip_until"] = new_date.isoformat()
        expiry_text = new_date.strftime("%Y-%m-%d")
    write(users_db, users)
    await ask.reply(f"✅ تم منح اشتراك {expiry_text} للمستخدم {target_id}.")
    try:
        await app.send_message(target_id, f"🎁 لقد تم منحك اشتراك {'دائم' if days is None else f'لمدة {days} يوماً'} مجاناً بواسطة المطور.")
    except:
        pass

# -------------------- تشغيل البوت --------------------
if __name__ == "__main__":
    print("🚀 بوت النشر التلقائي شغال...")
    app.run()
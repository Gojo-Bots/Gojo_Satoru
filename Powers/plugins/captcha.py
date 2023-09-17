import os
from random import shuffle
from traceback import format_exc

from pyrogram import filters
from pyrogram.types import CallbackQuery, ChatMemberUpdated, ChatPermissions
from pyrogram.types import InlineKeyboardButton as ikb
from pyrogram.types import InlineKeyboardMarkup as ikm
from pyrogram.types import Message

from Powers import LOGGER, get_support_staff
from Powers.bot_class import Gojo
from Powers.database.captcha_db import CAPTCHA, CAPTCHA_DATA
from Powers.utils.captcha_helper import (genrator, get_image_captcha,
                                         get_qr_captcha)
from Powers.utils.custom_filters import admin_filter, command

SUPPORT_STAFF = get_support_staff()

@Gojo.on_message(command("captcha") & admin_filter & ~filters.private)
async def start_captcha(c: Gojo, m: Message):
    captcha = CAPTCHA()
    split = m.command
    if len(split) == 1:
        is_cap = captcha.is_captcha(m.chat.id)
        if is_cap:
            txt = "Captcha verification is currently **on** for this chat"
        else:
            txt = "Captcha verification is currently **off** for this chat"
        await m.reply_text(txt)
        return
    else:
        on_off = split[1]
        if on_off in ["on","yes","enable"]:
            captcha.insert_captcha(m.chat.id)
            await m.reply_text("Captcha verification is now **on** for this chat")
            return
        elif on_off in ["off","no","disable"]:
            captcha.remove_captcha(m.chat.id)
            await m.reply_text("Captcha verification is now **off** for this chat")
            return
        else:
            await m.reply_text("**USAGE**\n/captcha [on | yes | enable | off | no | disable]")
            return

@Gojo.on_message(command("captchamode") & admin_filter & ~filters.private)
async def set_captcha_mode(c: Gojo, m: Message):
    split = m.command
    captcha = CAPTCHA()
    if len(split) == 1:
        curr = captcha.get_captcha(m.chat.id)
        if curr:
            capatcha_type = curr["captcha_type"]
            await m.reply_text(f"Current captcha verification methode is {capatcha_type}\nAvailable methodes:\n■ qr\n■ image")
            return
        else:
            await m.reply_text("Captcha verification is off for the current chat")
            return
    else:
        type_ = split[1].lower()
        if type_ == "qr":
            captcha.update_type(m.chat.id, "qr")
            await m.reply_text("Captcha verification is now changed to qr code")
            return
        elif type_ == "image":
            captcha.update_type(m.chat.id,"image")
            await m.reply_text("Captcha verication is now changed to image")
            return
        else:
            await m.reply_text("**USAGE**\n/captchamode [qr | image]")
            return

@Gojo.on_chat_member_updated(filters.group & filters.service,18)
async def joinss(c: Gojo, u: ChatMemberUpdated, m: Message):
    chat = u.chat.id
    user = u.from_user.id

    is_qr = CAPTCHA().is_captcha()
    if not is_qr:
        return
    
    captcha = CAPTCHA()
    cap_data = CAPTCHA_DATA()

    if user in SUPPORT_STAFF:
        return
    try:
        await c.restrict_chat_member(chat,user,ChatPermissions())
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

    captcha_type = captcha.get_captcha(chat)

    if captcha_type == "qr":
        is_already = cap_data.is_already_data(chat, user)

        try:
            if is_already:
                mess = await c.get_messages(chat,int(is_already))
        except Exception:
            cap_data.del_message_id(chat,is_already)
            is_already = False

        if not is_already:
            pic = get_qr_captcha(chat, user)
            cap = f"Please {u.from_user.mention} scan this qr code with your phone to verify that you are human"
            ms = await m.reply_photo(pic,caption=cap)
            cap_data.store_message_id(chat,user,ms.id)
            return
        else:
            kb = ikm(
                [
                    [
                        ikb("Click here to verify",url=mess.link)
                    ]
                ]
            )
            await m.reply_text("You verification is already pending",reply_markup=kb)
            return
    
    elif captcha_type == "image":
        is_already = cap_data.is_already_data(chat, user)

        try:
            if is_already:
                mess = await c.get_messages(chat,int(is_already))
        except Exception:
            cap_data.del_message_id(chat,is_already)
            is_already = False

        if not is_already:
            img, code = get_image_captcha(chat, user)
            cap = f"Please {u.from_user.mention} please choose the correct code from the one given bellow\nYou have three tries if you get all three wrong u will be kicked from the chat.\nTries left: 3"
            cap_data.load_cap_data(chat, user, code)
            rand = [code]
            while len(rand) != 5:
                hehe = genrator()
                rand.append(hehe)

            shuffle(rand)

            ini = f"captcha_{chat}_{user}_"

            kb = ikm(
                [
                    ikb(rand[0],ini+rand[0])
                ],
                [
                    ikb(rand[1],ini+rand[1])
                ],
                [
                    ikb(rand[2],ini+rand[2])
                ],
                [
                    ikb(rand[3],ini+rand[3])
                ],
                [
                    ikb(rand[4],ini+rand[4])
                ]
            )
            await m.reply_photo(img,caption=cap,reply_markup=kb)
            return
        else:
            kb = ikm(
                [
                    [
                        ikb("Click here to verify",url=mess.link)
                    ]
                ]
            )
            await m.reply_text("You verification is already pending",reply_markup=kb)
            return

@Gojo.on_callback_query(filters.regex("^captcha_"))
async def captcha_codes_check(c: Gojo, q: CallbackQuery):
    split = q.data.split("_")
    chat = int(split[1])
    user = int(split[2])
    code = split[3]

    if q.from_user.id != user:
        await q.answer("Not for you BAKA!")
        return

    c_data = CAPTCHA_DATA()
    code_ = c_data.get_cap_data(chat,user)
    
    
    if code_ == code:
        cap = "You guessed the captcha right...Now you can talk in the chat with no restrictions"
        c_data.remove_cap_data(chat,user)
        await q.answer(cap)
        try:
            await q.message.chat.unban_member(user)
        except Exception as e:
            await q.message.reply_text(f"Unable to unmute {q.from_user.mention} this user")
            await q.message.reply_text(e)
            return
        await c.send_message(f"{q.from_user.mention} now you are free to talk")
        await q.message.delete()
        return
    else:
        await q.answer("Wrong")
        caps = q.message.caption.split(":")
        tries = int(caps[1].strip()) - 1
        caps.pop(-1)
        caps.append(f" {tries}")
        new_cap = ":".join(caps)
        if not tries:
            new_cap = f"You have zero tries left now. I am going to kick you know coz you failed to solve captcha...see yaa {q.from_user.mention}"
            try:
                await q.message.chat.ban_member(user)
            except Exception as e:
                await q.message.reply_text("Failed to kick member")
                return
            await q.message.delete()
            await q.message.reply_text(new_cap)
            await c.unban_chat_member(chat,user)

        else:
            await q.edit_message_caption(new_cap)
            return

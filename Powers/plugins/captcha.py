import os
from random import choice, shuffle
from traceback import format_exc
from typing import List

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ParseMode as PM
from pyrogram.types import CallbackQuery, ChatPermissions
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as ikm
from pyrogram.types import Message, User

from Powers import LOGGER, MESSAGE_DUMP
from Powers.bot_class import Gojo
from Powers.database.captcha_db import CAPTCHA, CAPTCHA_DATA
from Powers.supports import get_support_staff
from Powers.utils.captcha_helper import (genrator, get_image_captcha,
                                         get_qr_captcha)
from Powers.utils.custom_filters import admin_filter, captcha_filter, command
from Powers.utils.extras import BAN_GIFS


@Gojo.on_message(command("captcha") & admin_filter & ~filters.private)
async def start_captcha(_, m: Message):
    captcha = CAPTCHA()
    split = m.command
    if len(split) == 1:
        is_cap = captcha.is_captcha(m.chat.id)
        if is_cap:
            txt = "Captcha verification is currently **on** for this chat"
        else:
            txt = "Captcha verification is currently **off** for this chat"
        await m.reply_text(txt)
    else:
        on_off = split[1].lower()
        if on_off in ["on", "yes", "enable"]:
            captcha.insert_captcha(m.chat.id)
            await m.reply_text("Captcha verification is now **on** for this chat")
        elif on_off in ["off", "no", "disable"]:
            captcha.remove_captcha(m.chat.id)
            await m.reply_text("Captcha verification is now **off** for this chat")
        else:
            await m.reply_text("**USAGE**\n/captcha [on | yes | enable | off | no | disable]")

    return


@Gojo.on_message(command("captchamode") & admin_filter & ~filters.private)
async def set_captcha_mode(c: Gojo, m: Message):
    split = m.command
    captcha = CAPTCHA()
    if len(split) == 1:
        if curr := captcha.get_captcha(m.chat.id):
            capatcha_type = curr["captcha_type"]
            await m.reply_text(
                f"Current captcha verification methode is {capatcha_type}\nAvailable methodes:\n■ qr\n■ image")
        else:
            await m.reply_text("Captcha verification is off for the current chat")
    else:
        type_ = split[1].lower()
        if type_ == "qr":
            await m.reply_text("This feature is not implemented yet\nUse /captchamode image")
        elif type_ == "image":
            captcha.update_type(m.chat.id, "image")
            await m.reply_text("Captcha verication is now changed to image")
        else:
            await m.reply_text("**USAGE**\n/captchamode [qr | image]")

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
    code_ = c_data.get_cap_data(chat, user)

    if code_ == code:
        cap = "You guessed the captcha right...Now you can talk in the chat with no restrictions"
        c_data.remove_cap_data(chat, user)
        await q.answer(cap, True)
        try:
            await q.message.chat.unban_member(user)
        except Exception as e:
            await q.message.reply_text(f"Unable to unmute {q.from_user.mention} this user")
            await q.message.reply_text(e)
            return
        await c.send_message(chat, f"{q.from_user.mention} now you are free to talk")
        await q.message.delete()
    else:
        caps = q.message.caption.split(":")
        tries = int(caps[1].strip()) - 1
        caps.pop(-1)
        caps.append(f" {tries}")
        new_cap = ":".join(caps)
        await q.answer(f"Wrong\nTries left: {tries}", True)
        if not tries:
            txt = f"{q.from_user.mention} was not able to pass captcha verification thus banned from the group"
            try:
                await q.message.chat.ban_member(user)
            except Exception as e:
                await q.message.reply_text("Failed to ban member")
                return
            await q.message.delete()
            keyboard = ikm(
                [
                    [
                        IKB(
                            "Unban",
                            callback_data=f"unban_={user}",
                        ),
                    ],
                ],
            )
            anim = choice(BAN_GIFS)
            try:
                await c.send_animation(
                    chat_id=q.message.chat.id,
                    animation=str(anim),
                    caption=txt,
                    reply_markup=keyboard,
                    parse_mode=PM.HTML,
                )
            except Exception:

                await c.send_animation(
                    chat_id=q.message.chat.id,
                    text=txt,
                    reply_markup=keyboard,
                    parse_mode=PM.HTML,
                )
                await c.send_message(MESSAGE_DUMP, f"#REMOVE from BAN_GFIS\n{anim}")
            c_data.remove_cap_data(chat, user)
            c_data.del_message_id(q.message.chat.id, user)
        else:
            await q.edit_message_caption(new_cap, reply_markup=q.message.reply_markup)

    return


@Gojo.on_message(filters.group & captcha_filter & filters.new_chat_members, group=3)
async def on_chat_members_updatess(c: Gojo, m: Message):
    chat = m.chat.id

    users: List[User] = m.new_chat_members
    for user in users:
        captcha = CAPTCHA()
        cap_data = CAPTCHA_DATA()

        if user.is_bot:
            continue
        SUPPORT_STAFF = get_support_staff()

        try:
            status = (await m.chat.get_member(user)).status
            if status in [CMS.OWNER, CMS.ADMINISTRATOR]:
                continue
        except Exception:
            pass
        if user.id in SUPPORT_STAFF:
            continue
        captcha_info = captcha.get_captcha(chat)
        captcha_type = captcha_info["captcha_type"]
        is_already = cap_data.is_already_data(chat, user.id)

        mess = False
        try:
            if is_already:
                mess = await c.get_messages(chat, int(is_already))
        except Exception:
            cap_data.del_message_id(chat, is_already)
            mess = False
            is_already = False

        if is_already and mess.empty:
            cap_data.del_message_id(chat, is_already)
            continue

        try:
            await c.restrict_chat_member(chat, user.id, ChatPermissions())
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error(format_exc())
            continue

        if not is_already:
            captcha_type = "image"  # I am not going to apply qr captcha in this update
            if captcha_type == "image":
                img, code = await get_image_captcha(chat, user.id)
                cap = f"Please {user.mention} please choose the correct code from the one given bellow\nYou have three tries if you get all three wrong u will be banned from the chat.\nTries left: 3"
                cap_data.load_cap_data(chat, user.id, code)
                rand = [code]
                while len(rand) != 5:
                    hehe = genrator()
                    if hehe != code:
                        rand.append(hehe)

                shuffle(rand)

                ini = f"captcha_{chat}_{user.id}_"

                kb = ikm(
                    [
                        [
                            IKB(rand[0], ini + rand[0])
                        ],
                        [
                            IKB(rand[1], ini + rand[1])
                        ],
                        [
                            IKB(rand[2], ini + rand[2])
                        ],
                        [
                            IKB(rand[3], ini + rand[3])
                        ],
                        [
                            IKB(rand[4], ini + rand[4])
                        ]
                    ]
                )
                await c.send_photo(chat, img, caption=cap, reply_markup=kb)
                os.remove(img)
            elif captcha_type == "qr":
                pic = await get_qr_captcha(chat, user.id, c.me.username)
                cap = f"Please {user.mention} scan this qr code with your phone to verify that you are human"
                ms = await c.send_photo(chat, pic, caption=cap)
                os.remove(pic)
                cap_data.store_message_id(chat, user.id, ms.id)
        elif mess:
            kb = ikm(
                [
                    [
                        IKB("Click here to verify", url=mess.link)
                    ]
                ]
            )
            await c.send_message(f"{user.mention} your verification is already pending", reply_markup=kb)
            continue
        else:
            await c.unban_chat_member(chat, user.id)
            continue


__PLUGIN__ = "captcha"

__HELP__ = """
• /captcha [on|yes|enable|off|no|disable] : To enable or disable captcha verification
• /captchamode [qr|image] : To change captcha mode
"""

import time
from random import choice
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType as CT
from pyrogram.errors import RPCError, UserAdminInvalid
from pyrogram.types import (CallbackQuery, ChatPermissions,
                            InlineKeyboardButton, InlineKeyboardMarkup,
                            Message)

from Powers import LOGGER, SUPPORT_GROUP
from Powers.bot_class import Gojo
from Powers.database.approve_db import Approve
from Powers.database.flood_db import Floods
from Powers.supports import get_support_staff
from Powers.utils.custom_filters import admin_filter, command
from Powers.utils.extras import BAN_GIFS, KICK_GIFS, MUTE_GIFS
from Powers.utils.kbhelpers import ikb
from Powers.vars import Config

SUPPORT_STAFF = get_support_staff()

on_key = ["on", "start", "disable"]
off_key = ["off", "end", "enable", "stop"]

close_kb =InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Close ❌",
                callback_data="f_close"
            )
        ]
    ]
)

action_kb = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Mute 🔇",
                callback_data="f_mute"
            ),
            InlineKeyboardButton(
                "Ban 🚷",
                callback_data="f_ban"
            ),
            InlineKeyboardButton(
                "Kick 🦿",
                callback_data="f_kick"
            )
        ],
        [
            InlineKeyboardButton(
                "➡️ Skip",
                callback_data="f_skip"
            )
        ]
    ]
)

within_kb = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "5",
                callback_data="f_f_5"
            ),
            InlineKeyboardButton(
                "10",
                callback_data="f_f_10"
            ),
            InlineKeyboardButton(
                "15",
                callback_data="f_f_15"
            )
        ],
        [
            InlineKeyboardButton(
                "➡️ Skip",
                callback_data="f_f_skip"
            )
        ]
    ]
)

limit_kb = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "5",
                callback_data="f_5"
            ),
            InlineKeyboardButton(
                "10",
                callback_data="f_10"
            ),
            InlineKeyboardButton(
                "15",
                callback_data="f_15"
            )
        ],
        [
            InlineKeyboardButton(
                "➡️ Skip",
                callback_data="f_f_f_skip"
            )
        ]
    ]
)

@Gojo.on_message(command(['floodaction','actionflood']) & admin_filter)
async def flood_action(c: Gojo, m: Message):
    Flood = Floods()
    bot = await c.get_chat_member(m.chat.id, Config.BOT_ID)
    status = bot.status
    if not status in [CMS.OWNER, CMS.ADMINISTRATOR]:
      if not bot.privileges.can_restrict_members:
        return await m.reply_text("Give me permission to restict member first")
    if m.chat.type == CT.PRIVATE:
        await m.reply_text("Use this command in group")
        return
    c_id = m.chat.id
    is_flood = Flood.is_chat(c_id)
    if is_flood:
        saction = is_flood[2]
        await m.reply_text(
            f"Choose a action given bellow to do when flood happens.\n **CURRENT ACTION** is {saction}",
            reply_markup=action_kb
        )
        return
    await m.reply_text("Switch on the flood protection first.")
    return

@Gojo.on_message(command(['isflood', 'flood']) & ~filters.bot)
async def flood_on_off(c: Gojo, m: Message):
    if m.chat.type == CT.PRIVATE:   
      return await m.reply_text("This command is ment to be used in groups.")
    Flood = Floods()
    c_id = m.chat.id
    is_flood = Flood.is_chat(c_id)
    c_id = m.chat.id
    if is_flood:
      saction = is_flood[2]
      slimit = is_flood[0]
      swithin = is_flood[1]
      return await m.reply_text(f"Flood is on for this chat\n**Action**: {saction}\n**Messages**: {slimit} within {swithin} sec")
    return await m.reply_text("Flood protection is off for this chat.")

@Gojo.on_message(command(['setflood']) & ~filters.bot & admin_filter)
async def flood_set(c: Gojo, m: Message):
    bot = await c.get_chat_member(m.chat.id, Config.BOT_ID)
    Flood = Floods()
    status = bot.status
    if not status in [CMS.OWNER, CMS.ADMINISTRATOR]:
      if not bot.privileges.can_restrict_members:
        return await m.reply_text("Give me permission to restict member first")
    if m.chat.type == CT.PRIVATE:
        return await m.reply_text("This command is ment to be used in groups.")
    split = m.text.split(None, 1)
    c_id = m.chat.id
    is_flood = Flood.is_chat(c_id)

    if len(split) == 1:
        c_id = m.chat.id
        if is_flood: 
            saction = is_flood[2]
            slimit = is_flood[0]
            swithin = is_flood[1]   
            return await m.reply_text(f"Flood is on for this chat\n**Action**:{saction}\n**Messages**:{slimit} within {swithin} sec")
        return await m.reply_text("Flood protection is off of this chat.")
    
    if len(split) == 2:
        c_id = m.chat.id
        if split[1].lower() in on_key:
            if is_flood:    
                return await m.reply_text(f"Flood is on for this chat\n**Action**:{saction}\n**Messages**:{slimit} within {swithin} sec")
            Flood.save_flood(m.chat.id, 5, 5, 'mute')
            await m.reply_text("Flood protection has been started for this group.")
            return
        if split[1].lower() in off_key:
            x = Flood.rm_flood(c_id)
            if x:
                await m.reply_text("Flood protection has been stopped for this chat")
                return
            await m.reply_text("Failed to stop flood protection")
            return
    await m.reply_text("**Usage:**\n `/setflood on/off`")
    return

@Gojo.on_callback_query(filters.regex("^f_"))
async def callbacks(c: Gojo, q: CallbackQuery):
    data = q.data
    if data == "f_close":
        await q.answer("Closed")
        await q.message.delete()
        return
    c_id = q.message.chat.id
    Flood = Floods()
    is_flood = Flood.is_chat(c_id)
    if is_flood:
        saction = is_flood[2]
        slimit = is_flood[0]
        swithin = is_flood[1]
    user = q.from_user.id
    user_status = (await q.message.chat.get_member(q.from_user.id)).status
    if user in SUPPORT_STAFF or user_status in [CMS.OWNER, CMS.ADMINISTRATOR]:
        if data in ["f_mute", "f_ban", "f_kick", "f_skip"]:
            change = data.split("_")[1]
            if not change == saction:
                Flood.save_flood(c_id, slimit, swithin, change)
                await q.answer("Updated action", show_alert=True)
                await q.edit_message_text(
                    f"Set the limit of message after the flood protection will be activated\n **CURRENT LIMIT** {slimit} messages",
                    reply_markup=limit_kb
                )
                return
            elif change == "skip":
                await q.answer("Skip", show_alert=True)
                await q.edit_message_text(
                    f"Set the limit of message after the flood protection will be activated\n **CURRENT LIMIT** {slimit} messages",
                    reply_markup=limit_kb
                )
            else:
                await q.answer("Updated action", show_alert=True)
                await q.edit_message_text(
                    f"Set the limit of message after the flood protection will be activated\n **CURRENT LIMIT** {slimit} messages",
                    reply_markup=limit_kb
                )
        elif data in ["f_5", "f_10", "f_15", "f_f_f_skip"]:
            try:
                change = int(data.split("_")[-1])
            except ValueError:
                await q.answer("skip")
                await q.edit_message_text(
                    f"Set the time with the number of message recived treated as flood\n **CUURENT TIME** {swithin}",
                    reply_markup=within_kb
                )
                return
            if not change == slimit:
                Flood.save_flood(c_id, change, swithin, saction)
                await q.answer("Updated limit", show_alert=True)
                await q.edit_message_text(
                    f"Set the time with the number of message recived treated as flood\n **CUURENT TIME** {swithin}",
                    reply_markup=within_kb
                )
                return
            else:
                await q.answer("Updated action", show_alert=True)
                await q.edit_message_text(
                    f"Set the time with the number of message recived treated as flood\n **CUURENT TIME** {swithin}",
                    reply_markup=within_kb
                )
                return
        elif data in ["f_f_5", "f_f_10", "f_f_15", "f_f_skip"]:
            data = data.split("_")[-1]
            try:
                change = int(data)
            except ValueError:
                await q.edit_message_text(
                    "Flood protection setting has been updated",
                    reply_markup=close_kb
                )
                return
                await q.answer("skip")
            if not change == swithin:
                Flood.save_flood(c_id, slimit, change, saction)
                await q.answer("Updated", show_alert=True)
                await q.edit_message_text(
                    "Flood protection setting has been updated",
                    reply_markup=close_kb
                )
                return
            else:
                await q.answer("Updated action", show_alert=True)
                await q.edit_message_text(
                    f"Set the limit of message after the flood protection will be activated\n **CURRENT LIMIT** {slimit} messages",
                    reply_markup=limit_kb
                )
    else:
        await q.answer(
            "You don't have enough permission to do this!\nStay in your limits!",
            show_alert=True,
            )
        return

@Gojo.on_callback_query(filters.regex("^un_"))
async def reverse_callbacks(c: Gojo, q: CallbackQuery):
    data = q.data.split("_")
    action = data[1]
    user_id = int(q.data.split("=")[1])
    if not q.from_user:
        return q.answer("Looks like you are not an user 👀")
    if action == "ban":
        user = await q.message.chat.get_member(q.from_user.id)
        if user.privileges and not user.privileges.can_restrict_members and q.from_user.id not in SUPPORT_STAFF:
            await q.answer(
                "You don't have enough permission to do this!\nStay in your limits!",
                show_alert=True,
            )
            return
        whoo = await c.get_chat(user_id)
        doneto = whoo.first_name if whoo.first_name else whoo.title
        try:
            await q.message.chat.unban_member(user_id)
        except RPCError as e:
            await q.message.edit_text(f"Error: {e}")
            return
        await q.message.edit_text(f"{q.from_user.mention} unbanned {doneto}!")
        return

    if action == "mute":
        user = await q.message.chat.get_member(q.from_user.id)

        if not user.privileges.can_restrict_members and q.from_user.id in SUPPORT_STAFF:
            await q.answer(
                "You don't have enough permission to do this!\nStay in your limits!",
                show_alert=True,
            )
            return
        whoo = await c.get_users(user_id)
        try:
            await q.message.chat.unban_member(user_id)
        except RPCError as e:
            await q.message.edit_text(f"Error: {e}")
            return
        await q.message.edit_text(f"{q.from_user.mention} unmuted {whoo.mention}!")
        return

dic = {}
@Gojo.on_message(filters.all & ~filters.bot | ~filters.private, 10)
async def flood_watcher(c: Gojo, m: Message):
    c_id = m.chat.id
    
    if not m.chat:
        return
    
    Flood = Floods()
    
    try:
        u_id = m.from_user.id
    except AttributeError:
        return # Get this error when the message received is not by an user and return
    
    is_flood = Flood.is_chat(c_id)
    
    if not is_flood:
        return # return of chat is not in anti flood protection
    
    app_users = Approve(m.chat.id).list_approved()
    
    if u_id in {i[0] for i in app_users}:
        return #return if the user is approved
    
    if not is_flood or u_id in SUPPORT_STAFF:
        return #return if the user is in support_staff
    
    try:
        user_status = (await m.chat.get_member(m.from_user.id)).status
    except Exception:
        return
    
    if user_status in [CMS.OWNER, CMS.ADMINISTRATOR]:
        return #return if the user is owner or admin
    
    action = is_flood[2]
    limit = int(is_flood[0])
    within = int(is_flood[1])
    
    if not len(dic):
        z = {c_id : {u_id : [[],[]]}}
        dic.update(z)
    
    try:
      dic[c_id] # access and check weather the c_id present or not
    except KeyError:
      z = {c_id : {u_id : [[],[]]}}
      dic.update(z)

    try:
      dic[c_id][u_id]
    except KeyError:
      z = {u_id : [[],[]]}
      dic[c_id].update(z) # make the dic something like {c_id : {u_id : [[for time],[for msg]]}}
    
    sec = round(time.time())
    
    try:
        dic[c_id][u_id][0].append(sec)
        dic[c_id][u_id][1].append("x")
    except KeyError:
        dic[c_id].update({u_id : [[sec], ["x"]]})
    
    x = int(dic[c_id][u_id][0][0])
    y = int(dic[c_id][u_id][0][-1])
    
    if len(dic[c_id][u_id][1]) == limit:
        if y-x <= within:
            if action == "ban":
                try:
                    await m.chat.ban_member(u_id)
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Unban",
                                    callback_data=f"un_ban_={u_id}",
                                ),
                            ],
                        ],
                    )
                    txt = "Don't dare to spam here if I am around! Nothing can escape my 6 eyes\nAction: Baned\nReason: Spaming"
                    await m.reply_animation(
                        animation=str(choice(BAN_GIFS)),
                        caption=txt,
                        reply_markup=keyboard,
                    )
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return

                except UserAdminInvalid:
                    await m.reply_text(
                        "I can't protect this chat from this user",
                        )
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                except RPCError as ef:
                    await m.reply_text(
                        text=f"""Some error occured, report it using `/bug`

                        <b>Error:</b> <code>{ef}</code>"""
                        )
                    LOGGER.error(ef)
                    LOGGER.error(format_exc())
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                
            elif action == "kick":
                try:
                    await m.chat.ban_member(u_id)
                    txt = "Don't dare to spam here if I am around! Nothing can escape my 6 eyes\nAction: kicked\nReason: Spaming"
                    await m.reply_animation(
                        animation=str(choice(KICK_GIFS)),
                        caption=txt,
                    )
                    await m.chat.unban_member(u_id)
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                except UserAdminInvalid:
                    await m.reply_text(
                        "I can't protect this chat from this user",
                    )
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                except RPCError as ef:
                    await m.reply_text(
                        text=f"""Some error occured, report it using `/bug`

                        <b>Error:</b> <code>{ef}</code>"""
                    )
                    LOGGER.error(ef)
                    LOGGER.error(format_exc())
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
            elif action == "mute":
                try:
                    await m.chat.restrict_member(
                        u_id,
                        ChatPermissions(),
                    )
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Unmute",
                                    callback_data=f"un_mute_={u_id}",
                                ),
                            ],
                        ],
                    )
                    txt = "Don't dare to spam here if I am around! Nothing can escape my 6 eyes\nAction: Muted\nReason: Spaming"
                    await m.reply_animation(
                        animation=str(choice(MUTE_GIFS)),
                        caption=txt,
                        reply_markup=keyboard,
                    )
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                except UserAdminInvalid:
                    await m.reply_text(
                        "I can't protect this chat from this user",
                    )
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
                except RPCError as ef:
                    await m.reply_text(
                        text=f"""Some error occured, report it using `/bug`

                        <b>Error:</b> <code>{ef}</code>"""
                    )
                    LOGGER.error(ef)
                    LOGGER.error(format_exc())
                    dic[c_id][u_id][1].clear()
                    dic[c_id][u_id][0].clear()
                    return
    elif y-x > within:
      try:
        dic[c_id][u_id][1].clear()
        dic[c_id][u_id][0].clear()
        return
      except Exception:
        pass
    else:
        return


__PLUGIN__ = "flood"
__alt_name__ = [
  "anit-flood",
  "flood",
  "spam",
  "anti-spam",
]
__HELP__ = """
**Anti Flood**
**User Commands:**
• /flood: to check weather the group is protected from spam or not.

**Admin only:**
• /setflood `on/off`: To activate or deactivate the flood protection
• /floodaction: To customize the flood settings.

**Example:**
`/setflood on`
"""


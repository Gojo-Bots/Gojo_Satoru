from pyrogram.errors import (
    ChatAdminRequired,
    RightForbidden,
    RPCError,
    UserNotParticipant,
)
from pyrogram.filters import regex
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from Powers import LOGGER, OWNER_ID, SUPPORT_GROUP, SUPPORT_STAFF
from Powers.bot_class import Gojo
from Powers.utils.caching import ADMIN_CACHE, admin_cache_reload
from Powers.utils.custom_filters import command, restrict_filter
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html
from Powers.utils.string import extract_time
from Powers.vars import Config


@Gojo.on_message(command("tmute") & restrict_filter)
async def tmute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text="This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    r_id = m.reply_to_message.message_id if m.reply_to_message else m.message_id

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 2)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()

    reason = split_reason[1] if len(split_reason) > 1 else ""

    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        LOGGER.info(f"{m.from_user.id} tmuted {user_id} in {m.chat.id}")
        admin=(await mention_html(m.from_user.first_name, m.from_user.id))
        muted=(await mention_html(user_first_name, user_id))
        txt =f"Admin {admin} muted {muted}!"
        if reason:
            txt += f"\n<b>Reason</b>: {reason}"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unmute",
                        callback_data=f"unmute_={user_id}",
                    ),
                ],
            ],
        )
        await m.reply_text(txt, reply_markup=keyboard, reply_to_message_id=r_id)
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("dtmute") & restrict_filter)
async def dtmute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    if not m.reply_to_message:
        return await m.reply_text("No replied message and user to delete and mute!")

    reason = None
    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text = "This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text = "This user is an admin, I cannot mute them!")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 2)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        LOGGER.info(f"{m.from_user.id} dtmuted {user_id} in {m.chat.id}")
        await m.reply_to_message.delete()
        admin=(await mention_html(m.from_user.first_name, m.from_user.id))
        muted=(await mention_html(user_first_name, user_id))
        txt = f"Admin {admin} muted {muted}!"
        if reason:
            txt += f"\n<b>Reason</b>: {reason}"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unmute",
                        callback_data=f"unmute_={user_id}",
                    ),
                ],
            ],
        )
        await c.send_message(m.chat.id, txt, reply_markup=keyboard)
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text = "I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("stmute") & restrict_filter)
async def stmute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text = "This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text = "This user is an admin, I cannot mute them!")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 2)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        LOGGER.info(f"{m.from_user.id} stmuted {user_id} in {m.chat.id}")
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text = "I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("mute") & restrict_filter)
async def mute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    reason = None
    if m.reply_to_message:
        r_id = m.reply_to_message.message_id
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        r_id = m.message_id
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text = "This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text = "This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        LOGGER.info(f"{m.from_user.id} muted {user_id} in {m.chat.id}")
        admin=(await mention_html(m.from_user.first_name, m.from_user.id))
        muted=(await mention_html(user_first_name, user_id))
        txt = f"Admin {admin} muted {muted}!"
        if reason:
            txt += f"\n<b>Reason</b>: {reason}"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unmute",
                        callback_data=f"unmute_={user_id}",
                    ),
                ],
            ],
        )
        await m.reply_text(txt, reply_markup=keyboard, reply_to_message_id=r_id)
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text = "I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("smute") & restrict_filter)
async def smute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text = "This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text = "This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        LOGGER.info(f"{m.from_user.id} smuted {user_id} in {m.chat.id}")
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
            return
        return
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text = "I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("dmute") & restrict_filter)
async def dmute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return
    if not m.reply_to_message:
        return await m.reply_text("No replied message and user to delete and mute!")

    reason = None
    if m.reply_to_message:
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I mute myself?")
        return

    if user_id in SUPPORT_STAFF:
        LOGGER.info(
            f"{m.from_user.id} trying to mute {user_id} (SUPPORT_STAFF) in {m.chat.id}",
        )
        await m.reply_text(text = "This user is in my support staff, cannot restrict them.")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text = "This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        LOGGER.info(f"{m.from_user.id} dmuted {user_id} in {m.chat.id}")
        await m.reply_to_message.delete()
        admin=(await mention_html(m.from_user.first_name, m.from_user.id))
        muted=(await mention_html(user_first_name, user_id))
        txt = f"Admin {admin} muted {muted}!"
        if reason:
            txt += f"\n<b>Reason</b>: {reason}"
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unmute",
                        callback_data=f"unmute_={user_id}",
                    ),
                ],
            ],
        )
        await c.send_message(m.chat.id, txt, reply_markup=keyboard)
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text = "I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("unmute") & restrict_filter)
async def unmute_usr(c: Gojo, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't unmute nothing!")
        return

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, why would I unmute myself if you are using me?")
        return

    try:
        await m.chat.unban_member(user_id)
        LOGGER.info(f"{m.from_user.id} unmuted {user_id} in {m.chat.id}")
        admin=(await mention_html(m.from_user.first_name, m.from_user.id))
        unmuted=(await mention_html(user_first_name, user_id))
        await m.reply_text(
            text=f"Admin {admin} unmuted {unmuted}!"
        )
    except ChatAdminRequired:
        await m.reply_text(text = "I'm not admin or I don't have rights.")
    except UserNotParticipant:
        await m.reply_text("How can I unmute a user who is not a part of this chat?")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text = f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
    return


@Gojo.on_callback_query(regex("^unmute_"))
async def unmutebutton(c: Gojo, q: CallbackQuery):
    splitter = (str(q.data).replace("unmute_", "")).split("=")
    user_id = int(splitter[1])
    user = await q.message.chat.get_member(q.from_user.id)

    if not user.can_restrict_members and user.id != OWNER_ID:
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


__PLUGIN__ = "muting"

__alt_name__ = [
    "mute",
    "tmute",
    "unmute",
]

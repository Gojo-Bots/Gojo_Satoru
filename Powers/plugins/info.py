import os
from pyrogram import enums
from datetime import datetime
from traceback import format_exc
from Powers.bot_class import Gojo
from pyrogram.types import Message
from Powers.utils.chat_type import c_type
from Powers.database.antispam_db import GBan
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Powers import (
    LOGGER, DEV_USERS, SUDO_USERS, SUPPORT_STAFF, WHITELIST_USERS)


gban_db = GBan()


async def count(c: Gojo, chat):
    administrator = []
    async for admin in c.get_chat_members(
        chat_id=chat, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        total_admin = administrator.append(admin)
    bot = []
    async for tbot in c.get_chat_members(
        chat_id=chat, filter=enums.ChatMembersFilter.BOTS
    ):
        total_bot = bot.append(tbot)
    bot_admin = 0
    ban = []
    async for banned in c.get_chat_members(chat, filter=enums.ChatMembersFilter.BANNED):
        total_banned = ban.append(banned)
    for x in total_admin:
        for y in total_bot:
            if x == y:
                bot_admin += 1
    total_admin = len(total_admin)
    total_bot = len(total_bot)
    total_banned = len(total_banned)
    return total_bot, total_admin, bot_admin, total_banned


async def user_info(c: Gojo, user, already=False):
    if not already:
        user = await c.get_users(user_ids=user)
    if not user.first_name:
        return ["Deleted account", None]

    gbanned, reason_gban = gban_db.get_gban(user)
    if gbanned:
        gban = True
        reason = f"The user is gbanned because {reason_gban}"
    else:
        gban = False
        reason = "User is not gbanned"

    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    mention = user.mention(f"{first_name}")
    dc_id = user.dc_id
    is_verified = user.is_verified
    is_restricted = user.is_restricted
    photo_id = user.photo.big_file_id if user.photo else None
    is_support = user_id in SUPPORT_STAFF
    if user_id in SUPPORT_STAFF:
        if user_id in DEV_USERS:
            omp = "User is dev"
        elif user_id in SUDO_USERS:
            omp = "User is sudoer"
        elif user_id in WHITELIST_USERS:
            omp = "User is in whitelist"
        else:
            omp = "Hmmm.......Who is that again?"
    is_bot = user.is_bot
    is_fake = user.is_fake
    status = user.status

    if is_bot is True:
        last_date = "Targeted user is a bot"
    elif status == "recently":
        last_date = "Last seen Recently"
    elif status == "within_week":
        last_date = "Last seen within the last week"
    elif status == "within_month":
        last_date = "Last seen within the last month"
    elif status == "long_time_ago":
        last_date = "Last seen a long time ago or may be I am blocked by the user  :("
    elif status == "online":
        last_date = "User is currently Online"
    elif status == "offline":
        last_date = datetime.fromtimestamp(user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"
        )
    else:
        last_date = "User is currently online"

    caption = f"""
<b><i><u>⚡ Extracted User info From Telegram ⚡</b></i></u>

<b>🆔️ User ID</b>: <code>{user_id}</code>
<b>📎 Link To Profile</b>: <a href='tg://user?id={user_id}'>Click Here🚪</a>
<b>🗣️ Mention</b>: {mention}
<b>🗣️ First Name</b>: <code>{first_name}</code>
<b>🗣️ Second Name</b>: <code>{last_name}</code>
<b>🔍 Username</b>: {("@" + username) if username else "NA"}
<b>🥸 Support</b>: {is_support}
<b>🤓 Support user type</b>: <code>{omp}</code>
<b>💣 Gbanned</b>: {gban}
<b>🤭 Gban reason</b>: <code>{reason}</code>
<b>🌐 DC ID</b>: {dc_id}
<b>🧐 RESTRICTED</b>: {is_restricted}
<b>✅ VERIFIED</b>: {is_verified}
<b>🧐 FAKE</b> : {is_fake}
<b>🤖 BOT</b>: {is_bot}
<b>👀 Last seen</b>: <code>{last_date}</code>

"""

    return caption, photo_id


async def chat_info(c: Gojo, chat, already=False):
    if not already:
        chat = await c.get_chat(chat)
    online_mem = await c.get_chat_online_count(chat)
    chat_id = chat.id
    username = chat.username
    total_bot, total_admin, total_bot_admin, total_banned = await count(c, chat)
    title = chat.title
    type_ = c_type(c, chat_id=chat)
    is_scam = chat.is_scam
    is_fake = chat.is_fake
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    if is_restricted:
        reasons = chat.restrictions
    else:
        reasons = "Chat is not restricted..."
    invite_link = chat.invite_link
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    can_save = chat.has_protected_content
    sticker_set = chat.sticker_set_name
    linked_chat = chat.linked_chat
    reactions = chat.available_reactions

    caption = f"""
🔰 <b>CHAT INFO</b> 🔰

<b>🆔 ID</b>: <code>{chat_id}</code>
<b>🚀 Chat Title</b>: {title}
<b>✨ Chat Type</b>: {type_}
<b>🌐 DataCentre ID</b>: {dc_id}
<b>🔍 Username</b>: {("@" + username) if username else "NA"}
<b>⚜️ Administrators</b>: {total_admin}
<b>🤖 Bots</b>: {total_bot}
<b>🚫 Banned</b>: {total_banned}
<b>⚜️ Admin 🤖 Bots</b>: {total_bot_admin}
<b>👨‍💻 Currently online</b>: {online_mem}
<b>🧐 Scam</b>: {is_scam}
<b>🤨 Fake</b>: {is_fake}
<b>🧐 Restricted</b>: {is_restricted}
<b>🤭 Reasons</b>: {reasons}
<b>👨🏿‍💻 Description: <code>{description}</code>
<b>👪 Total members</b>: {members}
<b>📎 Link to the chat</b>: <a href={invite_link}>Click Here🚪</a>
<b>🚫 Can Save Content</b>: {can_save}
<b>😋 Sticker set</b>: {sticker_set}
<b>🔗 Linked Chat</b>: {linked_chat if linked_chat else "Not Linked"}
<b>🔥 Reactions</b>: {reactions}

"""

    return caption, photo_id


@Gojo.on_message(command(["info", "whois"]))
async def info_func(c: Gojo, message: Message):
    try:
        user, _, _ = await extract_user(c, message)
    except Exception as e:
        return await message.reply_text(
            f"Got an error while running extract_user function error is {e}.....Give this message in supoort group"
        )

    if not user:
        message.reply_text("Can't find user to fetch info!")

    m = await message.reply_text(
        f"Fetching user info of user {message.from_user.id}..."
    )

    try:
        info_caption, photo_id = await user_info(c, user=user)
        LOGGER.info(
            f"{message.from_user.id} tried to fetch user info of user {message.from_user.id} in {message.chat.id}"
        )
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return await m.edit(str(e))

    if not photo_id:
        return await m.edit(info_caption, disable_web_page_preview=True)
    photo = await Gojo.download_media(photo_id)

    await message.reply_photo(photo, caption=info_caption, quote=False)
    await m.delete()
    os.remove(photo)
    LOGGER.info(
        f"{message.from_user.id} fetched user info of user {user.username} in {m.chat.id}"
    )


@Gojo.on_message(command(["chinfo", "chatinfo", "chat_info"]))
async def chat_info_func(c: Gojo, message: Message):
    splited = message.text.split()
    try:
        if len(splited) == 1:
            chat = message.chat.id

        else:
            chat = splited[1]

        try:
            chat = int(chat)
        except ValueError:
            return await message.reply_text("**Usage:**/chinfo [USERNAME|ID]")

        m = await message.reply_text(
            f"Fetching chat info of chat **{message.chat.title}**....."
        )

        info_caption, photo_id = await chat_info(c, chat=chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await Gojo.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        LOGGER.info(
            f"{message.from_user.id} fetched chat info of chat {chat} in {message.chat.id}"
        )

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.reply_text(text=e)
        LOGGER.error(e)
        LOGGER.error(format_exc())


__PLUGIN__ = "info"
__alt_name__ = [
    "info",
    "chinfo",
]

__HELP__ = """
***Information***

* /info - To get info about the user
* /chinfo - To get info about the chat
"""

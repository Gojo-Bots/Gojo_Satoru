import os
from traceback import format_exc

from pyrogram.types import Message

from Powers import DEV_USERS, SUDO_USERS, WHITELIST_USERS, SUPPORT_STAFF, LOGGER
from Powers.bot_class import Gojo
from Powers.utils.custom_filters import command


async def info(user, already=False):
    if not already:
        user = await Gojo.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention(f"{first_name}")
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_support = user_id in SUPPORT_STAFF
    if user_id in SUPPORT_STAFF:
        if user_id in DEV_USERS:
            omp = "User is in devs' list"
        elif user_id in SUDO_USERS:
            omp = "User is in sudo users' list"
        elif user_id in WHITELIST_USERS:
            omp = "User is in whitelist users' list"
        else:
            omp = "User is not even in SUPPORT_STAFF....."
    is_bot = user.is_bot
    is_fake = user.is_fake
    status = user.status
    if status == "offline":
        last_date = user.last_online_date
    else:
        last_date = "User is currently online"
    body = {
        "ID": user_id,
        "DC": dc_id,
        "Name": [first_name],
        "Username": [("@" + username) if username else None],
        "Mention": [mention],
        "Support": is_support,
        "Support user type": [omp],
        "Bot" : is_bot,
        "Fake" : is_fake,
        "Status" : status,
        "Last seen" : [last_date],
    }
    caption = body
    return [caption, photo_id]


async def chat_info(chat, already=False):
    if not already:
        chat = await Gojo.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = chat.type
    is_scam = chat.is_scam
    is_fake = chat.is_fake
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[Link](t.me/{username})" if username else None
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    can_save = chat.has_protected_content
    body = {
        "ID": chat_id,
        "DC": dc_id,
        "Type": type_,
        "Name": [title],
        "Username": [("@" + username) if username else None],
        "Mention": [link],
        "Members": members,
        "Scam": is_scam,
        "Fake" : is_fake,
        "Can save content" : can_save,
        "Restricted": is_restricted,
        "Description": [description],
    }
    caption = body
    return [caption, photo_id]



@Gojo.on_message(command("info") & ~filters.edited)
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]

    m = await message.reply_text(f"Fetching user info of user {user}...")

    try:
        info_caption, photo_id = await info(user)
        LOGGER.info(f"{message.from_user.id} tried to fetch user info of user {user} in {m.chat.id}")
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
    LOGGER.info(f"{message.from_user.id} fetched user info of user {user} in {m.chat.id}")


@Gojo.on_message(command("chinfo") & ~filters.edited)
async def chat_info_func(_, message: Message):
    try:
        if len(message.command) > 2:
            return await message.reply_text(
                "**Usage:**/chat_info [USERNAME|ID]"
            )

        if len(message.command) == 1:
            chat = message.chat.id
        elif len(message.command) == 2:
            chat = message.text.split(None, 1)[1]

        m = await message.reply_text(f"Fetching chat info of chat {chat}.....")

        info_caption, photo_id = await chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await Gojo.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        LOGGER.info(f"{message.from_user.id} fetched chat info of user {chat} in {m.chat.id}")

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(e)
        LOGGER.error(e)
        LOGGER.error(format_exc())

__PLUGIN__ = "info"
__alt_name__ = [
    "info",
    "chinfo",
] 

__HELP__ = """/info - To get info about the user
/chinfo - To get info about the chat"""

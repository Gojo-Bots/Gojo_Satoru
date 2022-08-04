import os
from traceback import format_exc
from datetime import datetime

from pyrogram.types import Message

from Powers import DEV_USERS, SUDO_USERS, WHITELIST_USERS, SUPPORT_STAFF, LOGGER
from Powers.bot_class import Gojo
from Powers.database.antispam_db import GBan
from Powers.database.users_db import Users
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Powers.utils.chat_type import c_type

gban_db=GBan()

escape = "\n"
empty = " "

bold = lambda x: f"**{x}:** "
bold_ul = lambda x: f"**--{x}:**-- "

single_func = lambda x: f"`{x}`{escape}"


def change(
        title: str,
        body: dict,
        indent: int = 2,
        underline: bool = False,
) -> str:
    text = (bold_ul(title) + escape) if underline else bold(title) + escape

    for key, value in body.items():
        text += (
                indent * empty
                + bold(key)
                + ((value[0] + escape) if isinstance(value, list) else single_func(value))
        )
    return text


async def user_info(c: Gojo, user, already=False):
    if not already:
        try:
            user = Users.get_user_info(int(user_id))  # Try to fetch user info form database if available give key error if user is not present
        except KeyError:
            user = await Gojo.get_users(user_ids=user) # Fetch user info in traditional way if not available in db
    if not user.first_name:
        return ["Deleted account", None]
    gbanned, reason_gban = gban_db.get_gban(user_id)
    if gbanned:
        gban=True
        reason = f"The user is gbanned because{reason_gban}"
    else:
        gban=False
        reason = "User is not gbanned"

    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention(f"{first_name}")
    dc_id = user.dc_id
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
        
    body = {
        "ID": user_id,
        "DC": dc_id,
        "Name": [first_name],
        "Username": [("@" + username) if username else None],
        "Mention": [mention],
        "Support": is_support,
        "Support user type": [omp],
        "Bot" : is_bot,
        "Gbanned": gban,
        "Gban reason":[reason],
        "Fake" : is_fake,
        "Last seen" : [last_date],
    }
    caption = change("User info", body)
    return [caption, photo_id]


async def chat_info(c: Gojo, chat, already=False):
    if not already:
        chat = await Gojo.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = c_type(c, chat_id=chat)
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
    caption = change("Chat info", body)
    return [caption, photo_id]


@Gojo.on_message(command(["info","whois"]))
async def info_func(c: Gojo, message: Message):
    if len(message.text.split()) == 1 and not message.reply_to_message:
        await message.reply_text(text="I can't info fecth of nothing!")
        await message.stop_propagation()
    elif len(message.text.split()) > 2 and not message.reply_to_message:
        await message.reply_text("You are not providing proper arguments.......**Usage:**/info [USERNAME|ID]....Example /info @iamgojoof6eyes")
        await message.stop_propagation()

    if message.reply_to_message and not message.reply_to_message.from_user:
        user = message.reply_to_message.from_user.id
    else:
        try:
            user, _ , _= await extract_user(c , message)
        except Exception as e:
            return await message.reply_text(f"Got an error while running extract_user function error is {e}.....Give this message in supoort group")
    
    if not user:
        message.reply_text("Can't find user to fetch info!")
    
    m = await message.reply_text(f"Fetching user info of user {user.username}...")

    try:
        info_caption, photo_id = await user_info(c , user=user)
        LOGGER.info(f"{message.from_user.id} tried to fetch user info of user {user.username} in {m.chat.id}")
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
    LOGGER.info(f"{message.from_user.id} fetched user info of user {user.username} in {m.chat.id}")



@Gojo.on_message(command(["chinfo","chatinfo","chat_info"]))
async def chat_info_func(c: Gojo, message: Message):
    splited = message.text.split()
    try:
        if len(splited) == 1:
            chat = message.chat.id

        elif len(splited) > 2:
            return await message.reply_text(
                "**Usage:**/chinfo [USERNAME|ID]"
            )
        
        else:
            chat = splited[1]
        

        m = await message.reply_text(f"Fetching chat info of chat **{message.chat.title}**.....")

        info_caption, photo_id = await chat_info(c, chat=chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await Gojo.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        LOGGER.info(f"{message.from_user.id} fetched chat info of chat {chat.title} in {m.chat.id}")

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.edit(chat_id=message.chat.id,                                                    
                           message_id=message.id,
                           e)
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

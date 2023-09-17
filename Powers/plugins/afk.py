from datetime import datetime
from random import choice

from pyrogram import filters
from pyrogram.enums import ParseMode as PM
from pyrogram.types import Message

# from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.database.afk_db import AFK
from Powers.plugins import till_date
from Powers.utils.cmd_senders import send_cmd
from Powers.utils.custom_filters import command
from Powers.utils.msg_types import Types, get_wlcm_type
from Powers.vars import Config

# from traceback import format_exc



cmds = Config.PREFIX_HANDLER

res = [
    "{first} is resting for a while...",
    "{first} living his real life, go and live yours.",
    "{first} is quite busy now-a-days.",
    "I am looking for {first} too...tell me if you see him/her around",
    "{first} ran away from the chat...",
    "{first} is busy in his/her work ||simping||",
    "{first} is busy saving the world",
    "{first} is now tired fighting all the curses"
]

back = [
    "{first} is finally back to life",
    "{first} welcome back",
    "{first} the spy is back watch what you talk about"
]

@Gojo.on_message(command(["afk","brb"]) & ~filters.private)
async def going_afk(c: Gojo, m: Message):
    user = m.from_user.id
    chat = m.chat.id
    afk = AFK()
    text, data_type, content = await get_wlcm_type(m)

    time = str(datetime.now()).rsplit(".",1)[0]

    if not text and not data_type:
        text = choice(res)
        data_type = Types.TEXT

    elif data_type and not text:
        text = choice(res)

    afk.insert_afk(chat,user,str(time),text,data_type,content)

    await m.reply_text(f"{m.from_user.mention} is now AFK")
    return

async def get_hours(hour:str):
    tim = hour.strip().split(":")

    if int(tim[0]):
        hour = tim[0] + "hours"
    if int(tim[1]):
        minute = tim[1] + " minutes"
    if int(tim[2]):
        second = tim[2] + " seconds"
    
    return hour + minute + second


@Gojo.on_message(filters.group,group=18)
async def afk_checker(c: Gojo, m: Message):
    if not m.from_user:
        return

    afk = AFK()
    back_ = choice(back)
    user = m.from_user.id
    chat = m.chat.id
    repl = m.reply_to_message

    if repl and repl.from_user:
        rep_user = repl.from_user.id
    else:
        rep_user = False

    is_afk = afk.check_afk(chat,user)

    if rep_user:
        is_rep_afk = afk.check_afk(chat,rep_user)

    if is_rep_afk:
        con = afk.get_afk(chat,rep_user)
        reason = con["reason"].format(repl.from_user.first_name)
        time = till_date(con["time"])
        media = con["media"]
        media_type = con["media_type"]
        tim_ = datetime.now() - time
        tim_ = str(tim_).split(",")
        tim = await get_hours(tim_[-1])

        tims = tim_[0] + " " + tim
        txt = reason + f"\nAfk since: {tims}"

        if media_type == Types.TEXT:        
            await (await send_cmd(c,media_type))(
                chat,
                txt,
                parse_mode=PM.MARKDOWN,
                reply_to_message_id=repl.id,
            )
        else:
            await (await send_cmd(c,media_type))(
                chat,
                media,
                txt,
                parse_mode=PM.MARKDOWN,
                reply_to_message_id=repl.id
            )
    
    if is_afk:
        txt = m.text

        for cmd in cmds:
            txt = txt.strip(cmd)

        if txt in ["afk","brb"]:
            return
        else:
            con = afk.get_afk(chat,user)
            time = till_date(con["time"])
            tim_ = datetime.now() - time
            tim_ = str(tim_).split(",")
            tim = await get_hours(tim_[-1])
            tims = tim_[0] + " " + tim
            txt = back_.fromat(m.from_user.mention) + f"\nAfk for: {tims}"
        afk.delete_afk(chat,user)
    return

__PLUGIN__ = "afk"

_DISABLE_CMDS_ = ["afk","brb"]

__alt_name__ = ["brb"]

__HELP__ = """
**AFK**
• /afk (/brb) [reason | reply to a message]

`reply to a message` can be any media or text
"""


    

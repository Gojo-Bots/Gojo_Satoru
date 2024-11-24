from datetime import datetime
from random import choice

from pyrogram import ContinuePropagation, filters
from pyrogram.enums import ParseMode as PM
from pyrogram.types import Message

from Powers.bot_class import Gojo
from Powers.database.afk_db import AFK
from Powers.plugins import till_date
from Powers.utils.cmd_senders import send_cmd
from Powers.utils.custom_filters import afk_filter, command
from Powers.utils.msg_types import Types, get_afk_type

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
    "{first} is now finally back from the dead"
]


@Gojo.on_message(command(["afk", "brb"]) & ~filters.private)
async def going_afk(c: Gojo, m: Message):
    user = m.from_user.id
    chat = m.chat.id
    afk = AFK()
    text, data_type, content = await get_afk_type(m)

    time = str(datetime.now()).rsplit(".", 1)[0]

    if len(m.command) == 1:
        text = choice(res)

    elif len(m.command) > 1:
        text = m.text.markdown.split(None, 1)[1]

    if not data_type:
        data_type = Types.TEXT

    afk.insert_afk(chat, user, str(time), text, data_type, content)

    await m.reply_text(f"{m.from_user.mention} is now AFK")

    return


async def get_hours(hour: str):
    tim = hour.strip().split(":")
    txt = ""
    if int(tim[0]):
        txt += f"{tim[0]} hours "
    if int(tim[1]):
        txt += f"{tim[1]} minutes "
    if int(round(float(tim[2]))):
        txt += f"{str(round(float(tim[2])))} seconds"

    return txt


@Gojo.on_message(afk_filter & filters.group)
async def afk_checker(c: Gojo, m: Message):
    afk = AFK()
    back_ = choice(back)
    user = m.from_user.id
    chat = m.chat.id
    repl = m.reply_to_message

    rep_user = repl.from_user.id if repl and repl.from_user else False
    is_afk = afk.check_afk(chat, user)
    is_rep_afk = afk.check_afk(chat, rep_user) if rep_user else False
    if is_rep_afk and rep_user != user:
        con = afk.get_afk(chat, rep_user)
        time = till_date(con["time"])
        media = con["media"]
        media_type = con["media_type"]
        tim_ = datetime.now() - time
        tim_ = str(tim_).split(",")
        tim = await get_hours(tim_[-1])
        if len(tim_) == 1:
            tims = tim
        elif len(tim_) == 2:
            tims = f"{tim_[0]} {tim}"
        reason = f"{repl.from_user.first_name} is afk since {tims}\n"
        if con['reason'] not in res:
            reason += f"\nDue to: {con['reason'].format(first=repl.from_user.first_name)}"
        else:
            reason += f"\n{con['reason'].format(first=repl.from_user.first_name)}"
        txt = reason

        if media_type == Types.TEXT:
            await (await send_cmd(c, media_type))(
                chat,
                txt,
                parse_mode=PM.MARKDOWN,
                reply_to_message_id=m.id,
            )
        else:
            await (await send_cmd(c, media_type))(
                chat,
                media,
                txt,
                parse_mode=PM.MARKDOWN,
                reply_to_message_id=repl.id
            )

    if is_afk:
        txt = False
        try:
            txt = m.command[0]
        except Exception:
            pass

        if txt and txt in ["afk", "brb"]:
            raise ContinuePropagation
        else:
            con = afk.get_afk(chat, user)
            time = till_date(con["time"])
            tim_ = datetime.now() - time
            tim_ = str(tim_).split(",")
            tim = await get_hours(tim_[-1])
            if len(tim_) == 1:
                tims = tim
            elif len(tim_) == 2:
                tims = f"{tim_[0]} {tim}"
            txt = f"{back_.format(first=m.from_user.mention)}\n\nAfk for: {tims}"
            await m.reply_text(txt)
        afk.delete_afk(chat, user)
    raise ContinuePropagation


__PLUGIN__ = "afk"

_DISABLE_CMDS_ = ["afk", "brb"]

__alt_name__ = ["brb"]

__HELP__ = """
**AFK**
• /afk (/brb) [reason | reply to a message]

`reply to a message` can be any media or text
"""

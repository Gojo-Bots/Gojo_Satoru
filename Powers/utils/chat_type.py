from Powers.bot_class import Gojo
from pyrogram.types import Message
from pyrogram.enums import ChatType


async def chattype(m: Message):
    # To get chat type with message

    if m.chat.type == ChatType.CHANNEL:
        ct = "channel"

    if m.chat.type == ChatType.PRIVATE:
        ct = "private"

    if m.chat.type == ChatType.GROUP:
        ct = "group"

    if m.chat.type == ChatType.SUPERGROUP:
        ct = "supergroup"

    return ct


async def c_type(c: Gojo, chat_id):
    # To get chat type with chat id

    ch = await c.get_chat(chat_id)

    if ch.type == ChatType.CHANNEL:
        ct = "channel"

    if ch.type == ChatType.GROUP:
        ct = "group"

    if ch.type == ChatType.SUPERGROUP:
        ct = "supergroup"

    if ch.type == ChatType.PRIVATE:
        ct = "private"

    return ct

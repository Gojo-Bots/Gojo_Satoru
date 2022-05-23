import enum
from pyrogram.enums import ChatType
from pyrogram.types import Message


async def chattype(m: Message):
    if bool(m.chat and m.chat.type in {ChatType.CHANNEL}):
        ct = "channel"
    
    if bool(m.chat and m.chat.type in {ChatType.PRIVATE}):
        ct = "private"

    if bool(m.chat and m.chat.type in {ChatType.GROUP}):
        ct = "group"
    
    if bool(m.chat and m.chat.type in {ChatType.SUPERGROUP}):
        ct = "supergroup"

    if bool(m.chat and m.chat.type in {ChatType.SUPERGROUP}) and bool(m.chat and m.chat.type in {ChatType.GROUP}):
        ct = "supreme group"

    if bool(m.chat and m.chat.type in {ChatType.BOT}):
        ct ="bot"


    return ct

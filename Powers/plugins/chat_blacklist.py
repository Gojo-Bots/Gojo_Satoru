from traceback import format_exc

from pyrogram.enums import ChatType as CT
from pyrogram.errors import PeerIdInvalid, RPCError
from pyrogram.types import Message

from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.database.group_blacklist import GroupBlacklist
from Powers.utils.custom_filters import command

# initialise database
db = GroupBlacklist()


@Gojo.on_message(command("blchat", dev_cmd=True))
async def blacklist_chat(c: Gojo, m: Message):
    if len(m.text.split()) >= 2:
        chat_ids = m.text.split()[1:]
        replymsg = await m.reply_text(f"Adding {len(chat_ids)} chats to blacklist")
        for chat in chat_ids:
            try:
                get_chat = await c.get_chat(chat)
                chat_id = get_chat.id
                db.add_chat(chat_id)
            except PeerIdInvalid:
                await replymsg.edit_text(
                    "Haven't seen this group in this session, maybe try again later?",
                )
            except RPCError as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        await replymsg.edit_text(
            f"Added the following chats to Blacklist.\n<code>{', '.join(chat_ids)}</code>.",
        )
    elif m.chat.type == CT.PRIVATE:
        await m.reply_text("Use in groups")
    else:
        chat_id = m.chat.id
        db.add_chat(chat_id)
        await m.reply_text("Added this chat to blacklist chats")
    return


@Gojo.on_message(
    command(["rmblchat", "unblchat"], dev_cmd=True),
)
async def unblacklist_chat(c: Gojo, m: Message):
    if len(m.text.split()) >= 2:
        chat_ids = m.text.split()[1:]
        replymsg = await m.reply_text(f"Removing {len(chat_ids)} chats from blacklist")
        bl_chats = db.list_all_chats()
        for chat in chat_ids:
            try:
                get_chat = await c.get_chat(chat)
                chat_id = get_chat.id
                if chat_id not in bl_chats:
                    # If chat is not blaklisted, continue loop
                    continue
                db.remove_chat(chat_id)
            except PeerIdInvalid:
                await replymsg.edit_text(
                    "Haven't seen this group in this session, maybe try again later?",
                )
            except RPCError as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        await replymsg.edit_text(
            f"Removed the following chats to Blacklist.\n<code>{', '.join(chat_ids)}</code>.",
        )
    elif m.chat.type == CT.PRIVATE:
        await m.reply_text("Use in groups")
    else:
        chat_id = m.chat.id
        bl_chats = bl_chats = db.list_all_chats()
        if chat_id in bl_chats:
            await m.reply_text("Removed this chat from blacklist chats")
        else:
            await m.reply_text("This chat is not in my list of blacklisted chats")
    return


@Gojo.on_message(
    command(["blchatlist", "blchats"], dev_cmd=True),
)
async def list_blacklist_chats(_, m: Message):
    if bl_chats := db.list_all_chats():
        txt = (
            (
                    "These Chats are Blacklisted:\n"
                    + "\n".join(f"<code>{i}</code>" for i in bl_chats)
            ),
        )

    else:
        txt = "No chats are currently blacklisted!"
    await m.reply_text(txt)
    return


__PLUGIN__ = "Chat blacklist"

__HELP__ = """
**Chat blacklist**

**Dev commands:**
• /blchat [space separated id or username of chats]: Add chats to black list if given or the current chat.
• /rmblchat [space separated id or username of chats]: Remove chats from black list if given or the current chat.
• /blchats: Give the list of blacklisted chats
"""

from asyncio import sleep

from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message

from Powers import SUPPORT_GROUP
from Powers.bot_class import Gojo
from Powers.utils.custom_filters import admin_filter, command


@Gojo.on_message(command("purge") & admin_filter)
async def purge(c: Gojo, m: Message):

    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="Cannot purge messages in a basic group")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="Cannot delete all messages. The messages may be too old, I might not have delete rights, or this might not be a supergroup."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
            )

        count_del_msg = len(message_ids)

        z = await m.reply_text(text=f"Deleted <i>{count_del_msg}</i> messages")
        await sleep(3)
        await z.delete()
        return
    await m.reply_text("Reply to a message to start purge !")
    return


@Gojo.on_message(command("spurge") & admin_filter)
async def spurge(c: Gojo, m: Message):

    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="Cannot purge messages in a basic group")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="Cannot delete all messages. The messages may be too old, I might not have delete rights, or this might not be a supergroup."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
            )
        return
    await m.reply_text("Reply to a message to start spurge !")
    return


@Gojo.on_message(
    command("del") & admin_filter,
    group=9,
)
async def del_msg(c: Gojo, m: Message):

    if m.chat.type != ChatType.SUPERGROUP:
        return

    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="What do you wanna delete?")
    return


__PLUGIN__ = "purges"

__alt_name__ = ["purge", "del", "spurge"]

__HELP__ = """
**Purge**

• /purge: Deletes messages upto replied message.
• /spurge: Deletes messages upto replied message without a success message.
• /del: Deletes a single message, used as a reply to message."""

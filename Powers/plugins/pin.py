from html import escape as escape_html

from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import ChatAdminRequired, RightForbidden, RPCError
from pyrogram.filters import regex
from pyrogram.types import CallbackQuery, Message

from Powers import LOGGER, SUPPORT_GROUP
from Powers.bot_class import Gojo
from Powers.database.pins_db import Pins
from Powers.utils.custom_filters import admin_filter, command
from Powers.utils.kbhelpers import ikb
from Powers.utils.string import build_keyboard, parse_button


@Gojo.on_message(command("pin") & admin_filter)
async def pin_message(_, m: Message):
    pin_args = m.text.split(None, 1)
    if m.reply_to_message:
        try:
            disable_notification = True

            if len(pin_args) >= 2 and pin_args[1] in ["alert", "notify", "loud"]:
                disable_notification = False

            await m.reply_to_message.pin(
                disable_notification=disable_notification,
            )
            LOGGER.info(
                f"{m.from_user.id} pinned msgid-{m.reply_to_message.id} in {m.chat.id}",
            )

            if m.chat.username:
                # If chat has a username, use this format
                link_chat_id = m.chat.username
                message_link = f"https://t.me/{link_chat_id}/{m.reply_to_message.id}"
            elif (str(m.chat.id)).startswith("-100"):
                # If chat does not have a username, use this
                link_chat_id = (str(m.chat.id)).replace("-100", "")
                message_link = f"https://t.me/c/{link_chat_id}/{m.reply_to_message.id}"
            if not disable_notification:
                await m.reply_text(
                    text=f"I have Pinned and Notified [this message]({message_link})!",
                    disable_web_page_preview=True,
                )
            else:
                await m.reply_text(
                    text=f"I have Pinned [this message]({message_link})!",
                    disable_web_page_preview=True,
                )

        except ChatAdminRequired:
            await m.reply_text(text="I'm not admin or I don't have rights.")
        except RightForbidden:
            await m.reply_text(text="I don't have enough rights to pin messages.")
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
            )
            LOGGER.error(ef)
    else:
        await m.reply_text("Reply to a message to pin it!")

    return


@Gojo.on_message(command("unpin") & admin_filter)
async def unpin_message(c: Gojo, m: Message):
    try:
        if m.reply_to_message:
            await m.reply_to_message.unpin()
            LOGGER.info(
                f"{m.from_user.id} unpinned msgid: {m.reply_to_message.id} in {m.chat.id}",
            )
            await m.reply_text(text="Unpinned last message.")
        else:
            m_id = (await c.get_chat(m.chat.id)).pinned_message.id
            await c.unpin_chat_message(m.chat.id,m_id)
            await m.reply_text(text="Unpinned last pinned message!")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to unpin messages.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Gojo.on_message(command("unpinall") & admin_filter)
async def unpinall_message(_, m: Message):
    await m.reply_text(
        "Do you really want to unpin all messages in this chat?",
        reply_markup=ikb([[("Yes", "unpin_all_in_this_chat"), ("No", "close_admin")]]),
    )
    return


@Gojo.on_callback_query(regex("^unpin_all_in_this_chat$"))
async def unpinall_calllback(c: Gojo, q: CallbackQuery):
    user_id = q.from_user.id
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
        await q.answer(
            "You're not even an admin, don't try this explosive shit!",
            show_alert=True,
        )
        return
    if user_status != CMS.OWNER:
        await q.answer(
            "You're just an admin, not owner\nStay in your limits!",
            show_alert=True,
        )
        return
    try:
        await c.unpin_all_chat_messages(q.message.chat.id)
        LOGGER.info(f"{q.from_user.id} unpinned all messages in {q.message.chat.id}")
        await q.message.edit_text(text="Unpinned all messages in this chat.")
    except ChatAdminRequired:
        await q.message.edit_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await q.message.edit_text(text="I don't have enough rights to unpin messages.")
    except RPCError as ef:
        await q.message.edit_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
    return


@Gojo.on_message(command("antichannelpin") & admin_filter)
async def anti_channel_pin(_, m: Message):
    pinsdb = Pins(m.chat.id)

    if len(m.text.split()) == 1:
        status = pinsdb.get_settings()["antichannelpin"]
        await m.reply_text(text=f"Current AntiChannelPin status: {status}")
        return

    if len(m.text.split()) == 2:
        if m.command[1] in ("yes", "on", "true"):
            pinsdb.antichannelpin_on()
            LOGGER.info(f"{m.from_user.id} enabled antichannelpin in {m.chat.id}")
            msg = "Turned on AntiChannelPin, now all message pinned by channel will be unpinned automtically!"
        elif m.command[1] in ("no", "off", "false"):
            pinsdb.antichannelpin_off()
            LOGGER.info(f"{m.from_user.id} disabled antichannelpin in {m.chat.id}")
            msg = "Turned off AntiChannelPin, now all message pinned by channel will stay pinned!"
        else:
            await m.reply_text(
                text="Please check help on how to use this this command."
            )
            return

    await m.reply_text(msg)
    return


@Gojo.on_message(command("pinned") & admin_filter)
async def pinned_message(c: Gojo, m: Message):
    chat_title = m.chat.title
    chat = await c.get_chat(chat_id=m.chat.id)
    msg_id = m.reply_to_message.id if m.reply_to_message else m.id

    if chat.pinned_message:
        pinned_id = chat.pinned_message.id
        if m.chat.username:
            link_chat_id = m.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(m.chat.id)).startswith("-100"):
            link_chat_id = (str(m.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        await m.reply_text(
            f"The pinned message of {escape_html(chat_title)} is [here]({message_link}).",
            reply_to_message_id=msg_id,
            disable_web_page_preview=True,
        )
    else:
        await m.reply_text(f"There is no pinned message in {escape_html(chat_title)}.")


@Gojo.on_message(command("cleanlinked") & admin_filter)
async def clean_linked(_, m: Message):
    pinsdb = Pins(m.chat.id)

    if len(m.text.split()) == 1:
        status = pinsdb.get_settings()["cleanlinked"]
        await m.reply_text(text=f"Current AntiChannelPin status: {status}")
        return

    if len(m.text.split()) == 2:
        if m.command[1] in ("yes", "on", "true"):
            pinsdb.cleanlinked_on()
            LOGGER.info(f"{m.from_user.id} enabled CleanLinked in {m.chat.id}")
            msg = "Turned on CleanLinked! Now all the messages from linked channel will be deleted!"
        elif m.command[1] in ("no", "off", "false"):
            pinsdb.cleanlinked_off()
            LOGGER.info(f"{m.from_user.id} disabled CleanLinked in {m.chat.id}")
            msg = "Turned off CleanLinked! Messages from linked channel will not be deleted!"
        else:
            await m.reply_text(
                text="Please check help on how to use this this command."
            )
            return

    await m.reply_text(msg)
    return


@Gojo.on_message(command("permapin") & admin_filter)
async def perma_pin(_, m: Message):
    if m.reply_to_message or len(m.text.split()) > 1:
        LOGGER.info(f"{m.from_user.id} used permampin in {m.chat.id}")
        if m.reply_to_message:
            text = m.reply_to_message.text
        elif len(m.text.split()) > 1:
            text = m.text.split(None, 1)[1]
        teks, button = await parse_button(text)
        button = await build_keyboard(button)
        button = ikb(button) if button else None
        z = await m.reply_text(teks, reply_markup=button)
        await z.pin()
    else:
        await m.reply_text("Reply to a message or enter text to pin it.")
    await m.delete()
    return


__PLUGIN__ = "pins"

__alt_name__ = ["pin", "unpin"]

__HELP__ = """
**Pin**

Here you find find all help related to groups pins and how to manage them via me.

**Admin Cmds:**
• /pin: Silently pins the message replied to - add `loud`, `notify` or `alert` to give notificaton to users.
• /unpin: Unpins the last pinned message.
• /pinned: Gives the current pinned message of the chat.
• /unpinall: Unpins all the pinned message in the current chat.
• /antichannelpin `<on/off/yes/no>`: Toggle antichannelpin status. All the messages from linked channel will be unpinned if enabled!
• /cleanlinked `<on/off/yes/no>`: Toggle cleanlinked status. All the messages from linked channel will be deleted if enabled!
• /permapin `<text>`: Pin a custom messages via bot. This message can contain markdown, and can be used in replies to the media include additional buttons and text."""

from asyncio import sleep
from datetime import datetime, timedelta
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import MessageEntityType as MET
from pyrogram.enums import MessageServiceType as MST
from pyrogram.errors import (ChatAdminRequired, ChatNotModified, RPCError,
                             UserAdminInvalid)
from pyrogram.types import CallbackQuery, ChatPermissions, Message

from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.database.approve_db import Approve
from Powers.database.locks_db import LOCKS
from Powers.supports import get_support_staff
from Powers.utils.caching import ADMIN_CACHE, admin_cache_reload
from Powers.utils.custom_filters import command, restrict_filter
from Powers.utils.kbhelpers import ikb

l_t = """
**Lock Types:**
- `all` = Everything
- `msg` = Messages
- `media` = Media, such as Photo and Video.
- `polls` = Polls
- `invite` = Add users to Group
- `pin` = Pin Messages
- `info` = Change Group Info
- `webprev` = Web Page Previews
- `inlinebots`, `inline` = Inline bots
- `animations` = Animations
- `games` = Game Bots
- `stickers` = Stickers
- `anonchannel` = Send as chat will be locked
- `forwardall` = Forwarding from channel and user
- `forwardu` = Forwarding from user
- `forwardc` = Forwarding from channel
- `links | url` = Lock links
- `bot` = Adding bot will be forbidden
"""


@Gojo.on_message(command("locktypes"))
async def lock_types(_, m: Message):
    await m.reply_text(
        l_t
    )
    return


@Gojo.on_message(command("lock") & restrict_filter)
async def lock_perm(c: Gojo, m: Message):
    if len(m.text.split()) < 2:
        await m.reply_text("Please enter a permission to lock!")
        return
    lock_type = m.text.split(None, 1)[1]
    chat_id = m.chat.id

    if not lock_type:
        await m.reply_text(text="Specify a permission to lock!")
        return

    get_perm = m.chat.permissions

    msg = get_perm.can_send_messages
    media = get_perm.can_send_media_messages
    webprev = get_perm.can_add_web_page_previews
    polls = get_perm.can_send_polls
    info = get_perm.can_change_info
    invite = get_perm.can_invite_users
    pin = get_perm.can_pin_messages
    stickers = animations = games = inlinebots = None
    lock = LOCKS()

    if lock_type == "all":
        try:
            await c.set_chat_permissions(chat_id, ChatPermissions())
            lock.insert_lock_channel(m.chat.id, "all")
        except ChatNotModified:
            pass
        except ChatAdminRequired:
            await m.reply_text(text="I don't have permission to do that")
        await m.reply_text("🔒 " + "Locked <b>all</b> permission from this Chat!")
        await prevent_approved(m)
        return

    if lock_type == "msg":
        msg = False
        perm = "messages"

    elif lock_type == "media":
        media = False
        perm = "audios, documents, photos, videos, video notes, voice notes"

    elif lock_type == "stickers":
        stickers = False
        perm = "stickers"

    elif lock_type == "animations":
        animations = False
        perm = "animations"

    elif lock_type == "games":
        games = False
        perm = "games"

    elif lock_type in ("inlinebots", "inline"):
        inlinebots = False
        perm = "inline bots"

    elif lock_type == "webprev":
        webprev = False
        perm = "web page previews"

    elif lock_type == "polls":
        polls = False
        perm = "polls"

    elif lock_type == "info":
        info = False
        perm = "info"

    elif lock_type == "invite":
        invite = False
        perm = "invite"

    elif lock_type == "pin":
        pin = False
        perm = "pin"
    elif lock_type == "bot":
        curr = lock.insert_lock_channel(m.chat.id, "bot")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Restricted adding bots in the chat.")
        return
    elif lock_type in ["links", "url"]:
        curr = lock.insert_lock_channel(m.chat.id, "anti_links")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Locked links in the chat")
        return
    elif lock_type == "anonchannel":
        curr = lock.insert_lock_channel(m.chat.id, "anti_c_send")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Locked Send As Chat")
        return
    elif lock_type == "forwardall":
        curr = lock.insert_lock_channel(m.chat.id, "anti_fwd")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Locked Forward from user as well as channel")
        return
    elif lock_type == "forwardu":
        curr = lock.insert_lock_channel(m.chat.id, "anti_fwd_u")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Locked Forward message from user")
        return
    elif lock_type == "forwardc":
        curr = lock.insert_lock_channel(m.chat.id, "anti_fwd_c")
        if not curr:
            await m.reply_text("It is already on")
            return
        await m.reply_text("Locked Forward message from channel")
        return
    else:
        await m.reply_text(
            text=""" Invalid Lock Type!

Use /locktypes to get the lock types"""
        )
        return

    try:
        await c.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=msg,
                can_send_media_messages=media,
                can_send_other_messages=any(
                    [stickers, animations, games, inlinebots]),
                can_add_web_page_previews=webprev,
                can_send_polls=polls,
                can_change_info=info,
                can_invite_users=invite,
                can_pin_messages=pin,
            ),
        )
    except ChatNotModified:
        pass
    except ChatAdminRequired:
        await m.reply_text(text="I don't have permission to do that")
    await m.reply_text(f"🔒 Locked <b>{perm}</b> for this Chat.")
    await prevent_approved(m)
    return


@Gojo.on_message(command("locks") & restrict_filter)
async def view_locks(_, m: Message):
    chkmsg = await m.reply_text(text="Checking Chat permissions...")
    v_perm = m.chat.permissions

    async def convert_to_emoji(val: bool):
        return "✅" if val else "❌"

    lock = LOCKS()
    anon = lock.get_lock_channel(m.chat.id, "anti_c_send")
    anti_f = lock.get_lock_channel(m.chat.id, "anti_fwd")
    anti_f_u = lock.get_lock_channel(m.chat.id, "anti_fwd_u")
    anti_f_c = lock.get_lock_channel(m.chat.id, "anti_fwd_c")
    antil = lock.get_lock_channel(m.chat.id, "anti_links")
    bots = lock.get_lock_channel(m.chat.id, "bot")

    vmsg = await convert_to_emoji(v_perm.can_send_messages)
    vmedia = await convert_to_emoji(v_perm.can_send_media_messages)
    vother = await convert_to_emoji(v_perm.can_send_other_messages)
    vwebprev = await convert_to_emoji(v_perm.can_add_web_page_previews)
    vpolls = await convert_to_emoji(v_perm.can_send_polls)
    vinfo = await convert_to_emoji(v_perm.can_change_info)
    vinvite = await convert_to_emoji(v_perm.can_invite_users)
    vpin = await convert_to_emoji(v_perm.can_pin_messages)
    vanon = await convert_to_emoji(anon)
    vanti = await convert_to_emoji(anti_f)
    vantiu = await convert_to_emoji(anti_f_u)
    vantic = await convert_to_emoji(anti_f_c)
    vantil = await convert_to_emoji(antil)
    vantibot = await convert_to_emoji(bots)

    if v_perm is not None:
        try:
            permission_view_str = f"""<b>Chat Permissions:</b>

      <b>Send Messages:</b> {vmsg}
      <b>Send Media:</b> {vmedia}
      <b>Send Stickers:</b> {vother}
      <b>Send Animations:</b> {vother}
      <b>Can Play Games:</b> {vother}
      <b>Can Use Inline Bots:</b> {vother}
      <b>Webpage Preview:</b> {vwebprev}
      <b>Send Polls:</b> {vpolls}
      <b>Change Info:</b> {vinfo}
      <b>Invite Users:</b> {vinvite}
      <b>Pin Messages:</b> {vpin}
      <b>Send as chat:</b> {vanon}
      <b>Can forward:</b> {vanti}
      <b>Can forward from user:</b> {vantiu}
      <b>Can forward from channel and chats:</b> {vantic}
      <b>Can send links:</b> {vantil}
      <b>Can bot send messages:</b> {vantibot}
      """
            await chkmsg.edit_text(permission_view_str)
        except RPCError as e_f:
            await chkmsg.edit_text(text="Something went wrong!")
            await m.reply_text(e_f)
    return


@Gojo.on_message(command("unlock") & restrict_filter)
async def unlock_perm(c: Gojo, m: Message):
    if len(m.text.split()) < 2:
        await m.reply_text("Please enter a permission to unlock!")
        return
    unlock_type = m.text.split(None, 1)[1]
    chat_id = m.chat.id

    if not unlock_type:
        await m.reply_text(text="Specify a permission to unlock!")
        return

    lock = LOCKS()
    if unlock_type == "all":
        try:
            await c.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                ),
            )
            lock.remove_lock_channel(m.chat.id, "all")
        except ChatNotModified:
            pass
        except ChatAdminRequired:
            await m.reply_text(text="I don't have permission to do that")
        await m.reply_text("🔓 " + "Unlocked <b>all</b> permission from this Chat!")
        await prevent_approved(m)
        return

    get_uperm = m.chat.permissions

    umsg = get_uperm.can_send_messages
    umedia = get_uperm.can_send_media_messages
    uwebprev = get_uperm.can_add_web_page_previews
    upolls = get_uperm.can_send_polls
    uinfo = get_uperm.can_change_info
    uinvite = get_uperm.can_invite_users
    upin = get_uperm.can_pin_messages
    ustickers = uanimations = ugames = uinlinebots = None

    if unlock_type == "msg":
        umsg = True
        uperm = "messages"

    elif unlock_type == "media":
        umedia = True
        uperm = "audios, documents, photos, videos, video notes, voice notes"

    elif unlock_type == "stickers":
        ustickers = True
        uperm = "stickers"

    elif unlock_type == "animations":
        uanimations = True
        uperm = "animations"

    elif unlock_type == "games":
        ugames = True
        uperm = "games"

    elif unlock_type in ("inlinebots", "inline"):
        uinlinebots = True
        uperm = "inline bots"

    elif unlock_type == "webprev":
        uwebprev = True
        uperm = "web page previews"

    elif unlock_type == "polls":
        upolls = True
        uperm = "polls"

    elif unlock_type == "info":
        uinfo = True
        uperm = "info"

    elif unlock_type == "invite":
        uinvite = True
        uperm = "invite"

    elif unlock_type == "pin":
        upin = True
        uperm = "pin"
    elif unlock_type == "bot":
        curr = lock.remove_lock_channel(m.chat.id, "bot")
        if not curr:
            m.reply_text("User already can add bots in the chat")
            return
        await m.reply_text("User are now allowed to add bots in the chat.")
    elif unlock_type == "anonchannel":
        curr = lock.remove_lock_channel(m.chat.id, "anti_c_send")

        if not curr:
            await m.reply_text("Send as chat is not allowed in this chat")
            return
        await m.reply_text("Send as chat is now enabled for this chat")
        return
    elif unlock_type in ["links", "url"]:
        if curr := lock.remove_lock_channel(m.chat.id, "anti_links"):
            await m.reply_text("Sending link is now allowed")
        else:
            await m.reply_text("Sending link is not allowed")
        return
    elif unlock_type == "forwardall":
        curr = lock.remove_lock_channel(m.chat.id, "anti_fwd")

        if not curr:
            await m.reply_text("Forwarding content is not allowed in this chat")
            return
        await m.reply_text("Forwarding content is now enabled for this chat")
        return

    elif unlock_type == "forwardu":
        curr = lock.remove_lock_channel(m.chat.id, "anti_fwd_u")

        if not curr:
            await m.reply_text("Forwarding content from users is not allowed in this chat")
            return

        await m.reply_text("Forwarding content from users is now enabled for this chat")
        return

    elif unlock_type == "forwardc":
        curr = lock.remove_lock_channel(m.chat.id, "anti_fwd_c")

        if not curr:
            await m.reply_text("Forwarding content from channel is not allowed in this chat")
            return
        await m.reply_text("Forwarding content from channel is now enabled for this chat")
        return

    else:
        await m.reply_text(
            text="""Invalid Lock Type!

      Use /locktypes to get the lock types"""
        )
        return

    try:
        await c.set_chat_permissions(
            chat_id,
            ChatPermissions(
                can_send_messages=umsg,
                can_send_media_messages=umedia,
                can_send_other_messages=any(
                    [ustickers, uanimations, ugames, uinlinebots],
                ),
                can_add_web_page_previews=uwebprev,
                can_send_polls=upolls,
                can_change_info=uinfo,
                can_invite_users=uinvite,
                can_pin_messages=upin,
            ),
        )
    except ChatNotModified:
        pass
    except ChatAdminRequired:
        await m.reply_text(text="I don't have permission to do that")
    await m.reply_text(f"🔓 Unlocked <b>{uperm}</b> for this Chat.")
    await prevent_approved(m)
    return


async def delete_messages(c: Gojo, m: Message):
    try:
        await m.delete()
        return
    except RPCError as rp:
        LOGGER.error(rp)
        LOGGER.error(format_exc())
        return


async def is_approved_user(c: Gojo, m: Message):
    approved_users = Approve(m.chat.id).list_approved()
    ul = [user[0] for user in approved_users]
    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "lock")

    SUDO_LEVEL = get_support_staff("sudo_level")

    if m.forward_from:
        return bool(
            m.from_user
            and (
                    m.from_user.id in ul
                    or m.from_user.id in SUDO_LEVEL
                    or m.from_user.id in admins_group
                    or m.from_user.id == c.me.id
            )
        )
    elif m.forward_from_chat:
        if m.from_user and (
                m.from_user.id in ul or m.from_user.id in SUDO_LEVEL or m.from_user.id in admins_group or m.from_user.id == c.me.id):
            return True
        elif m.automatic_forward:
            return True
        else:
            return False
    elif m.from_user:
        return (
                m.from_user.id in ul
                or m.from_user.id in SUDO_LEVEL
                or m.from_user.id in admins_group
                or m.from_user.id == c.me.id
        )
    else:
        return False


@Gojo.on_message(filters.service & filters.group, 19)
async def servicess(c: Gojo, m: Message):
    if m.service != MST.NEW_CHAT_MEMBERS:
        return
    approved = await is_approved_user(c, m)
    if approved:
        return
    for i in m.new_chat_members:
        if i.is_bot:
            try:
                timee = datetime.now() + timedelta(minutes=5)
                await m.chat.ban_member(i.id, until_date=timee)
                sleep(1)
            except UserAdminInvalid:
                continue
            except Exception as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
    return


@Gojo.on_message(filters.group & ~filters.me, 3)
async def lock_del_mess(c: Gojo, m: Message):
    lock = LOCKS()
    chat_locks = lock.get_lock_channel(m.chat.id)
    if not chat_locks:
        return

    if (
            chat_locks["anti_channel"]
            and m.sender_chat
            and not m.forward_from_chat
            and not m.forward_from
    ):
        if m.chat.is_admin:
            return
        await delete_messages(c, m)
        return
    is_approved = await is_approved_user(c, m)
    if is_approved:
        return
    entity = m.entities if m.text else m.caption_entities
    if entity and chat_locks["anti_links"]:
        for i in entity:
            if i.type in [MET.URL or MET.TEXT_LINK]:
                await delete_messages(c, m)
                return
    elif any(chat_locks["anti_fwd"].values()) and (m.forward_from or m.forward_from_chat):
        if all(chat_locks["anti_fwd"].values()):
            await delete_messages(c, m)
            return
        elif chat_locks["anti_fwd"]["user"] and not m.forward_from_chat:
            await delete_messages(c, m)
            return
        elif chat_locks["anti_fwd"]["chat"] and m.forward_from_chat:
            await delete_messages(c, m)
            return


async def prevent_approved(m: Message):
    approved_users = Approve(m.chat.id).list_approved()
    ul = [user[0] for user in approved_users]
    for i in ul:
        try:
            await m.chat.unban_member(user_id=i)
        except (ChatAdminRequired, ChatNotModified, RPCError):
            continue
        await sleep(0.1)
    return


@Gojo.on_callback_query(filters.regex("^LOCK_TYPES"))
async def lock_types_callback(c: Gojo, q: CallbackQuery):
    data = q.data

    if data == "LOCK_TYPES":
        kb = ikb([[("Back", "LOCK_TYPES_back")]])
        await q.edit_message_caption(
            l_t,
            reply_markup=kb
        )
    else:
        kb = ikb([[("Lock Types", "LOCK_TYPES")]])
        await q.edit_message_caption(
            __HELP__,
            reply_markup=kb
        )

__PLUGIN__ = "locks"

__alt_name__ = ["grouplock", "lock", "grouplocks"]

__buttons__ = [
    [
        ("Lock Types", "LOCK_TYPES"),
    ], ]

__HELP__ = """
**Locks**

Use this to lock group permissions.
Allows you to lock and unlock permission types in the chat.

**Usage:**
• /lock `<type>`: Lock Chat permission.
• /unlock `<type>`: Unlock Chat permission.
• /locks: View Chat permission.
• /locktypes: Check available lock types!

**Example:**
`/lock media`: this locks all the media messages in the chat."""
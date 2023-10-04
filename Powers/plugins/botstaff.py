from pyrogram.errors import RPCError
from pyrogram.types import Message

from Powers import LOGGER, OWNER_ID, WHITELIST_USERS
from Powers.bot_class import Gojo
from Powers.supports import get_support_staff
from Powers.utils.custom_filters import command
from Powers.utils.parser import mention_html

DEV_USERS = get_support_staff("dev")
SUDO_USERS = get_support_staff("sudo")

@Gojo.on_message(command("botstaff", dev_cmd=True))
async def botstaff(c: Gojo, m: Message):
    try:
        owner = await c.get_users(OWNER_ID)
        reply = f"<b>🌟 Owner:</b> {(await mention_html(owner.first_name, OWNER_ID))} (<code>{OWNER_ID}</code>)\n"
    except RPCError:
        pass
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply += "\n<b>Developers ⚡️:</b>\n"
    if not true_dev:
        reply += "No Dev Users\n"
    else:
        for each_user in true_dev:
            user_id = int(each_user)
            try:
                user = await c.get_users(user_id)
                reply += f"• {(await mention_html(user.first_name, user_id))} (<code>{user_id}</code>)\n"
            except RPCError:
                pass
    true_sudo = list(set(SUDO_USERS) - set(DEV_USERS))
    reply += "\n<b>Sudo Users 🐉:</b>\n"
    if true_sudo == []:
        reply += "No Sudo Users\n"
    else:
        for each_user in true_sudo:
            user_id = int(each_user)
            try:
                user = await c.get_users(user_id)
                reply += f"• {(await mention_html(user.first_name, user_id))} (<code>{user_id}</code>)\n"
            except RPCError:
                pass
    reply += "\n<b>Whitelisted Users 🐺:</b>\n"
    if WHITELIST_USERS == []:
        reply += "No additional whitelisted users\n"
    else:
        for each_user in WHITELIST_USERS:
            user_id = int(each_user)
            try:
                user = await c.get_users(user_id)
                reply += f"• {(await mention_html(user.first_name, user_id))} (<code>{user_id}</code>)\n"
            except RPCError:
                pass
    await m.reply_text(reply)
    LOGGER.info(f"{m.from_user.id} fetched botstaff in {m.chat.id}")
    return

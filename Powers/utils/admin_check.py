from traceback import format_exc

from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, Message

from Powers import LOGGER, OWNER_ID
from Powers.supports import get_support_staff


async def admin_check(m: Message or CallbackQuery) -> bool:
    """Checks if user is admin or not."""
    if isinstance(m, Message):
        user_id = m.from_user.id
    if isinstance(m, CallbackQuery):
        user_id = m.message.from_user.id

    SUDO_LEVEL = get_support_staff("sudo_level")

    try:
        if user_id in SUDO_LEVEL:
            return True
    except Exception as ef:
        LOGGER.error(format_exc())

    user = await m.chat.get_member(user_id)
    admin_strings = (CMS.OWNER, CMS.ADMINISTRATOR)

    if user.status not in admin_strings:
        reply = "Nigga, you're not admin, don't try this explosive shit."
        try:
            await m.edit_text(reply)
        except Exception as ef:
            await m.reply_text(reply)
            LOGGER.error(ef)
            LOGGER.error(format_exc())
        return False

    return True


async def check_rights(m: Message or CallbackQuery, rights) -> bool:
    """Check Admin Rights"""
    if isinstance(m, Message):
        user_id = m.from_user.id
        chat_id = m.chat.id
        app = m._client
    if isinstance(m, CallbackQuery):
        user_id = m.message.from_user.id
        chat_id = m.message.chat.id
        app = m.message._client

    user = await app.get_chat_member(chat_id, user_id)
    if user.status == CMS.MEMBER:
        return False
    admin_strings = (CMS.OWNER, CMS.ADMINISTRATOR)
    if user.status in admin_strings:
        return bool(getattr(user, rights, None))
    return False


async def owner_check(m: Message or CallbackQuery) -> bool:
    """Checks if user is owner or not."""
    if isinstance(m, Message):
        user_id = m.from_user.id
    if isinstance(m, CallbackQuery):
        user_id = m.message.from_user.id
        m = m.message

    SUDO_LEVEL = get_support_staff("sudo_level")

    if user_id in SUDO_LEVEL:
        return True

    try:
        user = await m.chat.get_member(user_id)
    except Exception:
        return False

    if user.status != CMS.OWNER:
        if user.status == CMS.ADMINISTRATOR:
            reply = "Stay in your limits, or lose adminship too."
        else:
            reply = "You ain't even admin, what are you trying to do?"
        try:
            await m.edit_text(reply)
        except Exception as ef:
            await m.reply_text(reply)
            LOGGER.error(ef)
            LOGGER.error(format_exc())

        return False

    return True

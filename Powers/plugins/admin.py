from asyncio import sleep
from html import escape
from os import remove
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType
from pyrogram.errors import (ChatAdminInviteRequired, ChatAdminRequired,
                             FloodWait, RightForbidden, RPCError,
                             UserAdminInvalid)
from pyrogram.types import ChatPrivileges, Message

from Powers import LOGGER, OWNER_ID
from Powers.bot_class import Gojo
from Powers.database.approve_db import Approve
from Powers.database.reporting_db import Reporting
from Powers.supports import get_support_staff
from Powers.utils.caching import (ADMIN_CACHE, TEMP_ADMIN_CACHE_BLOCK,
                                  admin_cache_reload)
from Powers.utils.custom_filters import (admin_filter, command, owner_filter,
                                         promote_filter)
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html
from Powers.vars import Config

SUPPORT_STAFF = get_support_staff()
DEV_LEVEL = get_support_staff("dev_level")

@Gojo.on_message(command("adminlist"))
async def adminlist_show(_, m: Message):
    global ADMIN_CACHE
    if m.chat.type not in [ChatType.SUPERGROUP,ChatType.GROUP]:
        return await m.reply_text(
            text="This command is made to be used in groups only!",
        )
    try:
        try:
            admin_list = ADMIN_CACHE[m.chat.id]
            note = "<i>Note:</i> These are cached values!"
        except KeyError:
            admin_list = await admin_cache_reload(m, "adminlist")
            note = "<i>Note:</i> These are up-to-date values!"
        adminstr = f"Admins in <b>{m.chat.title}</b>:" + "\n\n"
        bot_admins = [i for i in admin_list if (i[1].lower()).endswith("bot")]
        user_admins = [i for i in admin_list if not (i[1].lower()).endswith("bot")]
        # format is like: (user_id, username/name,anonyamous or not)
        mention_users = [
            (
                admin[1]
                if admin[1].startswith("@")
                else (await mention_html(admin[1], admin[0]))
            )
            for admin in user_admins
            if not admin[2]  # if non-anonyamous admin
        ]
        mention_users.sort(key=lambda x: x[1])
        mention_bots = [
            (
                admin[1]
                if admin[1].startswith("@")
                else (await mention_html(admin[1], admin[0]))
            )
            for admin in bot_admins
        ]
        mention_bots.sort(key=lambda x: x[1])
        adminstr += "<b>User Admins:</b>\n"
        adminstr += "\n".join(f"- {i}" for i in mention_users)
        adminstr += "\n\n<b>Bots:</b>\n"
        adminstr += "\n".join(f"- {i}" for i in mention_bots)
        await m.reply_text(adminstr + "\n\n" + note)
        LOGGER.info(f"Adminlist cmd use in {m.chat.id} by {m.from_user.id}")
    except Exception as ef:
        if str(ef) == str(m.chat.id):
            await m.reply_text(text="Use /admincache to reload admins!")
        else:
            ef = str(ef) + f"{admin_list}\n"
            await m.reply_text(
                text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
            )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command("zombies") & admin_filter)
async def zombie_clean(c: Gojo, m: Message):
    zombie = 0
    wait = await m.reply_text("Searching ... and banning ...")
    async for member in c.get_chat_members(m.chat.id):
        if member.user.is_deleted:
            zombie += 1
            try:
                await c.ban_chat_member(m.chat.id, member.user.id)
            except UserAdminInvalid:
                zombie -= 1
            except FloodWait as e:
                await sleep(e.x)
    if zombie == 0:
        return await wait.edit_text("Group is clean!")
    return await wait.edit_text(
        text=f"<b>{zombie}</b> Zombies found and has been banned!",
    )


@Gojo.on_message(command("admincache"))
async def reload_admins(_, m: Message):
    global TEMP_ADMIN_CACHE_BLOCK
    if m.chat.type not in [ChatType.SUPERGROUP,ChatType.GROUP]:
        return await m.reply_text(
            "This command is made to be used in groups only!",
        )
    if (
        (m.chat.id in set(TEMP_ADMIN_CACHE_BLOCK.keys()))
        and (m.from_user.id not in SUPPORT_STAFF)
        and TEMP_ADMIN_CACHE_BLOCK[m.chat.id] == "manualblock"
    ):
        await m.reply_text("Can only reload admin cache once per 10 mins!")
        return
    try:
        await admin_cache_reload(m, "admincache")
        TEMP_ADMIN_CACHE_BLOCK[m.chat.id] = "manualblock"
        await m.reply_text(text="Reloaded all admins in this chat!")
        LOGGER.info(f"Admincache cmd use in {m.chat.id} by {m.from_user.id}")
    except RPCError as ef:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(filters.regex(r"^(?i)@admin(s)?") & filters.group)
async def tag_admins(_, m: Message):
    db = Reporting(m.chat.id)
    if not db.get_settings():
        return
    try:
        admin_list = ADMIN_CACHE[m.chat.id]
    except KeyError:
        admin_list = await admin_cache_reload(m, "adminlist")
    user_admins = [i for i in admin_list if not (i[1].lower()).endswith("bot")]
    mention_users = [(await mention_html("\u2063", admin[0])) for admin in user_admins]
    mention_users.sort(key=lambda x: x[1])
    mention_str = "".join(mention_users)
    await m.reply_text(
        (
            f"{(await mention_html(m.from_user.first_name, m.from_user.id))}"
            f" reported the message to admins!{mention_str}"
        ),
    )


@Gojo.on_message(command("fullpromote") & promote_filter)
async def fullpromote_usr(c: Gojo, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(
            text="I can't promote nothing! Give me an username or user id or atleast reply to that user"
        )
        return
    try:
        user_id, user_first_name, user_name = await extract_user(c, m)
    except Exception:
        return
    bot = await c.get_chat_member(m.chat.id, Config.BOT_ID)
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, how can I even promote myself?")
        return
    if not bot.privileges.can_promote_members:
        return await m.reply_text(
            "I don't have enough permissions!",
        )  # This should be here
    user = await c.get_chat_member(m.chat.id, m.from_user.id)
    if m.from_user.id != OWNER_ID and user.status != CMS.OWNER:
        return await m.reply_text("This command can only be used by chat owner.")
    # If user is alreay admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "promote_cache_update"))
        }
    if user_id in admin_list:
        await m.reply_text(
            "This user is already an admin, how am I supposed to re-promote them?",
        )
        return
    try:
        await m.chat.promote_member(user_id=user_id, privileges=bot.privileges)
        title = ""
        if m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            title = "Gojo"  # Default fullpromote title
            if len(m.text.split()) == 3 and not m.reply_to_message:
                title = " ".join(m.text.split()[2:16]) # trim title to 16 characters
            elif len(m.text.split()) >= 2 and m.reply_to_message:
                title = " ".join(m.text.split()[1:16]) # trim title to 16 characters

            try:
                await c.set_administrator_title(m.chat.id, user_id, title)
            except RPCError as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
        LOGGER.info(
            f"{m.from_user.id} fullpromoted {user_id} in {m.chat.id} with title '{title}'",
        )
        await m.reply_text(
            (
                "{promoter} promoted {promoted} in chat <b>{chat_title}</b> with full rights!"
            ).format(
                promoter=(await mention_html(m.from_user.first_name, m.from_user.id)),
                promoted=(await mention_html(user_first_name, user_id)),
                chat_title=f"{escape(m.chat.title)} title set to {title}"
                if title
                else f"{escape(m.chat.title)} title set to Default",
            ),
        )
        # If user is approved, disapprove them as they willbe promoted and get
        # even more rights
        if Approve(m.chat.id).check_approve(user_id):
            Approve(m.chat.id).remove_approve(user_id)
        # ----- Add admin to temp cache -----
        try:
            inp1 = user_name or user_first_name
            admins_group = ADMIN_CACHE[m.chat.id]
            admins_group.append((user_id, inp1))
            ADMIN_CACHE[m.chat.id] = admins_group
        except KeyError:
            await admin_cache_reload(m, "promote_key_error")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights......")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to promote this user.")
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as e:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{e}</code>"
        )
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command("promote") & promote_filter)
async def promote_usr(c: Gojo, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(
            text="I can't promote nothing!......reply to user to promote him/her...."
        )
        return
    try:
        user_id, user_first_name, user_name = await extract_user(c, m)
    except Exception:
        return
    bot = await c.get_chat_member(m.chat.id, Config.BOT_ID)
    if user_id == Config.BOT_ID:
        await m.reply_text("Huh, how can I even promote myself?")
        return
    if not bot.privileges.can_promote_members:
        return await m.reply_text(
            "I don't have enough permissions",
        )  # This should be here
    # If user is alreay admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "promote_cache_update"))
        }
    if user_id in admin_list:
        await m.reply_text(
            "This user is already an admin, how am I supposed to re-promote them?",
        )
        return
    try:
        await m.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.privileges.can_change_info,
                can_invite_users=bot.privileges.can_invite_users,
                can_delete_messages=bot.privileges.can_delete_messages,
                can_restrict_members=bot.privileges.can_restrict_members,
                can_pin_messages=bot.privileges.can_pin_messages,
                can_manage_chat=bot.privileges.can_manage_chat,
                can_manage_video_chats=bot.privileges.can_manage_video_chats,
            ),
        )
        title = ""
        if m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            title = "Itadori"  # Deafult title
            if len(m.text.split()) >= 3 and not m.reply_to_message:
                title = " ".join(m.text.split()[2:16]) # trim title to 16 characters
            elif len(m.text.split()) >= 2 and m.reply_to_message:
                title = " ".join(m.text.split()[1:16]) # trim title to 16 characters
            try:
                await c.set_administrator_title(m.chat.id, user_id, title)
            except RPCError as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
        LOGGER.info(
            f"{m.from_user.id} promoted {user_id} in {m.chat.id} with title '{title}'",
        )
        await m.reply_text(
            ("{promoter} promoted {promoted} in chat <b>{chat_title}</b>!").format(
                promoter=(await mention_html(m.from_user.first_name, m.from_user.id)),
                promoted=(await mention_html(user_first_name, user_id)),
                chat_title=f"{escape(m.chat.title)} title set to {title}"
                if title
                else f"{escape(m.chat.title)} title set to default",
            ),
        )
        # If user is approved, disapprove them as they willbe promoted and get
        # even more rights
        if Approve(m.chat.id).check_approve(user_id):
            Approve(m.chat.id).remove_approve(user_id)
        # ----- Add admin to temp cache -----
        try:
            inp1 = user_name or user_first_name
            admins_group = ADMIN_CACHE[m.chat.id]
            admins_group.append((user_id, inp1))
            ADMIN_CACHE[m.chat.id] = admins_group
        except KeyError:
            await admin_cache_reload(m, "promote_key_error")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to promote this user.")
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as e:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{e}</code>"
        )
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command("demote") & promote_filter)
async def demote_usr(c: Gojo, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't demote nothing.")
        return
    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return
    if user_id == Config.BOT_ID:
        await m.reply_text("Get an admin to demote me!")
        return
    # If user not already admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "demote_cache_update"))
        }
    if user_id not in admin_list:
        await m.reply_text(
            "This user is not an admin, how am I supposed to re-demote them?",
        )
        return
    try:
        await m.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(can_manage_chat=False),
        )
        LOGGER.info(f"{m.from_user.id} demoted {user_id} in {m.chat.id}")
        # ----- Remove admin from cache -----
        try:
            admin_list = ADMIN_CACHE[m.chat.id]
            user = next(user for user in admin_list if user[0] == user_id)
            admin_list.remove(user)
            ADMIN_CACHE[m.chat.id] = admin_list
        except (KeyError, StopIteration):
            await admin_cache_reload(m, "demote_key_stopiter_error")
        await m.reply_text(
            ("{demoter} demoted {demoted} in <b>{chat_title}</b>!").format(
                demoter=(
                    await mention_html(
                        m.from_user.first_name,
                        m.from_user.id,
                    )
                ),
                demoted=(await mention_html(user_first_name, user_id)),
                chat_title=m.chat.title,
            ),
        )
    except ChatAdminRequired:
        await m.reply_text("I am not admin aroung here.")
    except RightForbidden:
        await m.reply_text("I can't demote users here.")
    except UserAdminInvalid:
        await m.reply_text(
            "Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as ef:
        await m.reply_text(
            f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command("invitelink"))
async def get_invitelink(c: Gojo, m: Message):
    # Bypass the bot devs, sudos and owner
    if m.from_user.id not in DEV_LEVEL:
        user = await m.chat.get_member(m.from_user.id)
        if not user.privileges.can_invite_users and user.status != CMS.OWNER:
            await m.reply_text(text="You don't have rights to invite users....")
            return False
    try:
        link = await c.export_chat_invite_link(m.chat.id)
        await m.reply_text(
            text=f"Invite Link for Chat <b>{m.chat.id}</b>: {link}",
            disable_web_page_preview=True,
        )
        LOGGER.info(f"{m.from_user.id} exported invite link in {m.chat.id}")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except ChatAdminInviteRequired:
        await m.reply_text(text="I don't have permission for invite link!")
    except RightForbidden:
        await m.reply_text(text="You don't have permissions to invite users.")
    except RPCError as ef:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command("setgtitle") & admin_filter)
async def setgtitle(_, m: Message):
    user = await m.chat.get_member(m.from_user.id)
    if not user.privileges.can_change_info and user.status != CMS.OWNER:
        await m.reply_text(
            "You don't have enough permission to use this command!",
        )
        return False
    if len(m.command) < 1:
        return await m.reply_text("Please read /help for using it!")
    gtit = m.text.split(None, 1)[1]
    try:
        await m.chat.set_title(gtit)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed Group Title From {m.chat.title} To {gtit}",
    )

@Gojo.on_message(command("setgdes") & admin_filter)
async def setgdes(_, m: Message):
    user = await m.chat.get_member(m.from_user.id)
    if not user.privileges.can_change_info and user.status != CMS.OWNER:
        await m.reply_text(
            "You don't have enough permission to use this command!",
        )
        return False
    if len(m.command) < 1:
        return await m.reply_text("Please read /help for using it!")
    desp = m.text.split(None, 1)[1]
    try:
        await m.chat.set_description(desp)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed Group description From {m.chat.description} To {desp}",
    )


@Gojo.on_message(command("title") & admin_filter)
async def set_user_title(c: Gojo, m: Message):
    user = await m.chat.get_member(m.from_user.id)
    if not user.privileges.can_promote_members and user.status != CMS.OWNER:
        await m.reply_text(
            "You don't have enough permission to use this command!",
        )
        return False
    if len(m.text.split()) == 1 and not m.reply_to_message:
        return await m.reply_text("To whom??")
    if m.reply_to_message:
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return
    if not user_id:
        return await m.reply_text("Cannot find user!")
    if user_id == Config.BOT_ID:
        return await m.reply_text("Huh, why ?")
    if not reason:
        return await m.reply_text("Read /help please!")
    from_user = await c.get_users(user_id)
    title = reason
    try:
        await c.set_administrator_title(m.chat.id, from_user.id, title)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed {from_user.mention}'s Admin Title To {title}",
    )


@Gojo.on_message(command("setgpic") & admin_filter)
async def setgpic(c: Gojo, m: Message):
    user = await m.chat.get_member(m.from_user.id)
    if not user.privileges.can_change_info and user.status != CMS.OWNER:
        await m.reply_text(
            "You don't have enough permission to use this command!",
        )
        return False
    if not m.reply_to_message:
        return await m.reply_text("Reply to a photo to set it as chat photo")
    if not m.reply_to_message.photo and not m.reply_to_message.document:
        return await m.reply_text("Reply to a photo to set it as chat photo")
    photo = await m.reply_to_message.download()
    is_vid = False
    if m.reply_to_message.video:
        is_vid = True
    try:
        await m.chat.set_photo(photo,video=is_vid)
    except Exception as e:
        remove(photo)
        return await m.reply_text(f"Error: {e}")
    await m.reply_text("Successfully Changed Group Photo!")
    remove(photo)


__PLUGIN__ = "admin"
__alt_name__ = [
    "admins",
    "promote",
    "demote",
    "adminlist",
    "setgpic",
    "title",
    "setgtitle",
    "fullpromote",
    "invitelink",
    "setgdes",
    "zombies",
]
__HELP__ = """
**Admin**

**User Commands:**
• /adminlist: List all the admins in the Group.

**Admin only:**
• /invitelink: Gets chat invitelink.
• /promote: Promotes the user replied to or tagged (supports with title).
• /fullpromote: Fully Promotes the user replied to or tagged (supports with title).
• /demote: Demotes the user replied to or tagged.
• /setgpic: Set group picture.
• /admincache: Reloads the List of all the admins in the Group.
• /zombies: Bans all the deleted accounts. (owner only)
• /title: sets a custom title for an admin that the bot promoted.
• /disable <commandname>: Stop users from using "commandname" in this group.
• /enable <item name>: Allow users from using "commandname" in this group.
• /disableable: List all disableable commands.
• /disabledel <yes/off>: Delete disabled commands when used by non-admins.
• /disabled: List the disabled commands in this chat.
• /enableall: enable all disabled commands.

**Example:**
`/promote @username`: this promotes a user to admin."""



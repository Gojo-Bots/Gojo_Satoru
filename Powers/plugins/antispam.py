from datetime import datetime
from io import BytesIO
from traceback import format_exc

from pyrogram.errors import MessageTooLong, PeerIdInvalid, UserIsBlocked
from pyrogram.types import Message

from Powers import LOGGER, MESSAGE_DUMP, SUPPORT_GROUP, TIME_ZONE
from Powers.bot_class import Gojo
from Powers.database.antispam_db import GBan
from Powers.database.users_db import Users
from Powers.supports import get_support_staff
from Powers.utils.clean_file import remove_markdown_and_html
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html
from Powers.vars import Config

# Initialize
db = GBan()
SUPPORT_STAFF = get_support_staff()

@Gojo.on_message(command(["gban", "globalban"], sudo_cmd=True))
async def gban(c: Gojo, m: Message):
    if len(m.text.split()) == 1:
        await m.reply_text(
            text="<b>How to gban?</b> \n <b>Answer:</b> <code>/gban user_id reason</code>"
        )
        return

    if len(m.text.split()) == 2 and not m.reply_to_message:
        await m.reply_text(text="Please enter a reason to gban user!")
        return

    user_id, user_first_name, _ = await extract_user(c, m)

    if m.reply_to_message:
        gban_reason = m.text.split(None, 1)[1]
    else:
        gban_reason = m.text.split(None, 2)[2]

    if user_id in SUPPORT_STAFF:
        await m.reply_text(text="This user is part of my Support!, Can't ban our own!")
        return

    if user_id == Config.BOT_ID:
        await m.reply_text(
            text="You don't dare use that command on me again nigga! \n Go straight and fuck your self......"
        )
        return

    if db.check_gban(user_id):
        db.update_gban_reason(user_id, gban_reason)
        await m.reply_text(text="Updated Gban reason to: <code>{gban_reason}</code>.")
        return

    db.add_gban(user_id, gban_reason, m.from_user.id)
    await m.reply_text(
        (
            f"Added {user_first_name} to GBan List. \n They will now be banned in all groups where I'm admin!"
        )
    )
    LOGGER.info(f"{m.from_user.id} gbanned {user_id} from {m.chat.id}")
    date = datetime.utcnow().strftime("%H:%M - %d-%m-%Y")
    log_msg = f"#GBAN \n <b>Originated from:</b> {m.chat.id} \n <b>Admin:</b> {await mention_html(m.from_user.first_name, m.from_user.id)} \n <b>Gbanned User:</b> {await mention_html(user_first_name, user_id)} \n <b>Gbanned User ID:</b> {user_id} \\ n<b>Event Stamp:</b> {date}"
    await c.send_message(MESSAGE_DUMP, log_msg)
    try:
        # Send message to user telling that he's gbanned
        await c.send_message(
            user_id,
            f"You have been added to my global ban list! \n <b>Reason:</b> <code>{gban_reason}</code> \n <b>Appeal Chat:</b> @{SUPPORT_GROUP}",
        )
    except UserIsBlocked:
        LOGGER.error("Could not send PM Message, user blocked bot")
    except PeerIdInvalid:
        LOGGER.error(
            "Haven't seen this user anywhere, mind forwarding one of their messages to me?",
        )
    except Exception as ef:  # TO DO: Improve Error Detection
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(
    command(["ungban", "unglobalban", "globalunban"], sudo_cmd=True),
)
async def ungban(c: Gojo, m: Message):
    if len(m.text.split()) == 1:
        await m.reply_text(text="Pass a user id or username as an argument!")
        return

    user_id, user_first_name, _ = await extract_user(c, m)

    if user_id in SUPPORT_STAFF:
        await m.reply_text(text="This user is part of my Support!, Can't ban our own!")
        return

    if user_id == Config.BOT_ID:
        await m.reply_text(
            text="""You can't gban me nigga!
        Fuck yourself.......!"""
        )
        return

    if db.check_gban(user_id):
        db.remove_gban(user_id)
        await m.reply_text(text=f"Removed {user_first_name} from Global Ban List.")
        time = ((datetime.utcnow().strftime("%H:%M - %d-%m-%Y")),)
        LOGGER.info(f"{m.from_user.id} ungbanned {user_id} from {m.chat.id}")
        log_msg = f"""#UNGBAN
        <b>Originated from:</b> {m.chat.id}
        <b>Admin:</b> {(await mention_html(m.from_user.first_name, m.from_user.id))}
        <b>UnGbanned User:</b> {(await mention_html(user_first_name, user_id))}
        <b>UnGbanned User ID:</b> {user_id}
        <b>Event Stamp:</b> {time}"""
        await c.send_message(MESSAGE_DUMP, log_msg)
        try:
            # Send message to user telling that he's ungbanned
            await c.send_message(
                user_id,
                text="You have been removed from my global ban list!.....Be careful it takes few seconds to add you again...",
            )
        except Exception as ef:  # TODO: Improve Error Detection
            LOGGER.error(ef)
            LOGGER.error(format_exc())
        return

    await m.reply_text(text="User is not gbanned!")
    return


@Gojo.on_message(
    command(["numgbans", "countgbans", "gbancount", "gbanscount"], sudo_cmd=True),
)
async def gban_count(_, m: Message):
    await m.reply_text(
        text=f"Number of people gbanned: <code>{(db.count_gbans())}</code>"
    )
    LOGGER.info(f"{m.from_user.id} counting gbans in {m.chat.id}")
    return


@Gojo.on_message(
    command(["gbanlist", "globalbanlist"], sudo_cmd=True),
)
async def gban_list(_, m: Message):
    banned_users = db.load_from_db()

    if not banned_users:
        await m.reply_text(text="There aren't any gbanned users...!")
        return

    banfile = "Here are all the globally banned geys!\n\n"
    for user in banned_users:
        banfile += f"[x] <b>{Users.get_user_info(user['_id'])['name']}</b> - <code>{user['_id']}</code>\n"
        if user["reason"]:
            banfile += f"<b>Reason:</b> {user['reason']}\n"

    try:
        await m.reply_text(banfile)
    except MessageTooLong:
        with BytesIO(str.encode(await remove_markdown_and_html(banfile))) as f:
            f.name = "gbanlist.txt"
            await m.reply_document(
                document=f, caption="Here are all the globally banned geys!\n\n"
            )

    LOGGER.info(f"{m.from_user.id} exported gbanlist in {m.chat.id}")

    return

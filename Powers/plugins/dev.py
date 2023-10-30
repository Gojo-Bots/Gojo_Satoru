import subprocess as subp
import sys
from asyncio import create_subprocess_shell, sleep, subprocess
from io import BytesIO, StringIO
from os import execvp
from sys import executable
from time import gmtime, strftime, time
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (ChannelInvalid, ChannelPrivate, ChatAdminRequired,
                             EntityBoundsInvalid, FloodWait, MessageTooLong,
                             PeerIdInvalid, RPCError)
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import (BOT_TOKEN, LOG_DATETIME, LOGFILE, LOGGER, MESSAGE_DUMP,
                    OWNER_ID, UPTIME)
from Powers.bot_class import Gojo
from Powers.database import MongoDB
from Powers.database.chats_db import Chats
from Powers.database.support_db import SUPPORTS
from Powers.database.users_db import Users
from Powers.plugins.scheduled_jobs import clean_my_db
from Powers.supports import get_support_staff
from Powers.utils.clean_file import remove_markdown_and_html
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_markdown


def can_change_type(curr, to_user):
    if curr == "dev" and to_user in ["whitelist","sudo"]:
        return True
    elif curr == "sudo" and to_user == "whitelist":
        return True
    else:
        return False

@Gojo.on_message(command(["addsupport"]))
async def add_support(c: Gojo, m:Message):
    support = SUPPORTS()
    curr_user = support.get_support_type(m.from_user.id)
    if not curr_user:
        await m.reply_text("Stay in you limit")
        return
    split = m.command
    reply_to = m.reply_to_message
    if reply_to:
        try:
            userr = reply_to.from_user.id
        except Exception:
            await m.reply_text("Reply to an user")
            return
        curr = support.get_support_type(userr)
        try:
            to = split[1].lower()
        except IndexError:
            await m.reply_text("**USAGE**\n/addsupport [reply to message | user id] [dev | sudo | whitelist]")
            return
        if to not in ["dev","sudo","whitelist"]:
            await m.reply_text("**USAGE**\n/addsupport [reply to message | user id] [dev | sudo | whitelist]")
            return
        if m.from_user.id == int(OWNER_ID):
            if to == curr:
                await m.reply_text(f"This user is already in {to} users")
                return
            elif curr:
                kb = IKM(
                    [
                        [
                            IKB("Yes",f"change_support_type:{to}"),
                            IKB("No","change_support_type:no")
                        ]
                    ]
                )
                await m.reply_text(f"This is user is already in {curr} users\nDo you want to make him {to} user?",reply_markup=kb)
                return
            else:
                support.insert_support_user(userr,to)
                await m.reply_text(f"This user is now a {to} user")
                return
        can_do = can_change_type(curr_user,to)
        if can_do:
            if to == curr:
                await m.reply_text(f"This user is already in {to} users")
                return
            elif curr:
                kb = IKM(
                    [
                        [
                            IKB("Yes",f"change_support_type:{to}"),
                            IKB("No","change_support_type:no")
                        ]
                    ]
                )
                await m.reply_text(f"This is user is already in {curr} users\nDo you want to make him {to} user?",reply_markup=kb)
                return
            else:
                support.insert_support_user(userr,to)
                await m.reply_text(f"This user is now a {to} user")
                return
        else:
            await m.reply_text("Sorry you can't do it")
            return
    elif len(split) >= 3:
        user = split[1]
        try:
            userr,_,_ = extract_user(user)
        except Exception:
            await m.reply_text("Tell the user to start me first")
            return
        curr = support.get_support_type(userr)
        try:
            to = m.command[2].lower()
        except IndexError:
            await m.reply_text("**USAGE**\n/addsupport [reply to message | user id | username] [dev | sudo | whitelist]")
            return
        if to not in ["dev","sudo","whitelist"]:
            await m.reply_text("**USAGE**\n/addsupport [reply to message | user id] [dev | sudo | whitelist]")
            return
        if m.from_user.id == int(OWNER_ID):
            if to == curr:
                await m.reply_text(f"This user is already in {to} users")
                return
            elif curr:
                kb = IKM(
                    [
                        [
                            IKB("Yes",f"change_support_type:{to}"),
                            IKB("No","change_support_type:no")
                        ]
                    ]
                )
                await m.reply_text(f"This is user is already in {curr} users\nDo you want to make him {to} user?",reply_markup=kb)
                return
            else:
                support.insert_support_user(userr,to)
                await m.reply_text(f"This user is now a {to} user")
                return
        can_do = can_change_type(curr_user,to)
        if can_do:
            if to == curr:
                await m.reply_text(f"This user is already in {to} users")
                return
            elif curr:
                kb = IKM(
                    [
                        [
                            IKB("Yes",f"change_support_type:{to}"),
                            IKB("No","change_support_type:no")
                        ]
                    ]
                )
                await m.reply_text(f"This is user is already in {curr} users\nDo you want to make him {to} user?",reply_markup=kb)
                return
            else:
                support.insert_support_user(userr,to)
                await m.reply_text(f"This user is now a {to} user")
                return
        else:
            await m.reply_text("Sorry you can't do it")
            return

@Gojo.on_message(command("rmsupport"))
async def rm_support(c: Gojo, m: Message):
    support = SUPPORTS()
    curr_user = support.get_support_type(m.from_user.id)
    if not curr_user:
        await m.reply_text("Stay in you limit")
        return
    split = m.command
    reply_to = m.reply_to_message

    if reply_to:
        try:
            curr = reply_to.from_user.id
        except Exception:
            await m.reply_text("Reply to an user")
            return
    elif len(split) >= 2:
        try:
            curr,_,_ = extract_user(m)
        except Exception:
            await m.reply_text("Dunno who u r talking abt")
            return
    else:
        await m.reply_text("**USAGE**\n/rmsupport [reply to user | user id | username]")
        return
    to_user = support.get_support_type(curr)
    can_user = can_change_type(curr_user,to_user)
    if m.from_user.id == int(OWNER_ID) or can_user:
        support.delete_support_user(curr)
        await m.reply_text("Done! User now no longer belongs to the support staff")
    else:
        await m.reply_text("Sorry you can't do that...")
    return

@Gojo.on_message(command("ping", sudo_cmd=True))
async def ping(_, m: Message):
    LOGGER.info(f"{m.from_user.id} used ping cmd in {m.chat.id}")
    start = time()
    replymsg = await m.reply_text(text="Pinging...", quote=True)
    delta_ping = time() - start
    await replymsg.edit_text(f"<b>Pong!</b>\n{delta_ping * 1000:.3f} ms")
    return


@Gojo.on_message(command("logs", dev_cmd=True))
async def send_log(c: Gojo, m: Message):
    replymsg = await m.reply_text("Sending logs...!")
    await c.send_message(
        MESSAGE_DUMP,
        f"#LOGS\n\n**User:** {(await mention_markdown(m.from_user.first_name, m.from_user.id))}",
    )
    # Send logs
    with open(LOGFILE) as f:
        raw = ((f.read()))[1]
    await m.reply_document(
        document=LOGFILE,
        quote=True,
    )
    await replymsg.delete()
    return


@Gojo.on_message(command("neofetch", dev_cmd=True))
async def neofetch_stats(_, m: Message):
    cmd = "neofetch --stdout"

    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "No Error"
    OUTPUT = stdout.decode()
    if not OUTPUT:
        OUTPUT = "No Output"

    try:
        await m.reply_text(OUTPUT, quote=True)
    except MessageTooLong:
        with BytesIO(str.encode(await remove_markdown_and_html(OUTPUT))) as f:
            f.name = "neofetch.txt"
            await m.reply_document(document=f, caption="neofetch result")
        await m.delete()
    return

HARMFUL = [
    "base64",
    "bash",
    "get_me()",
    "phone",
    "os.system",
    "sys.stdout",
    "sys.stderr",
    "subprocess",
    "DB_URI",
    "DB_URI",
    "BOT_TOKEN",
    "API_HASH",
    "APP_ID",
    "SSH_CLIENT",
    "SSH_CONNECTION"
    "SSH"
    
]


@Gojo.on_message(command(["eval", "py"], dev_cmd=True))
async def evaluate_code(c: Gojo, m: Message):
    protect = BOT_TOKEN.split(":")
    initial = protect[0]
    end = protect[1][-5:]
    if len(m.text.split()) == 1:
        await m.reply_text(text="Please execute the code correctly!")
        return
    sm = await m.reply_text("`Processing...`")
    cmd = m.text.split(None, maxsplit=1)[1]
    if "while True:" in cmd:
        await sm.delete()
        await m.reply_text("BSDK SPAM NI")
        await c.send_message(
            MESSAGE_DUMP,
            f"@{m.from_user.username} TREID TO USE `while True` \n userid = {m.from_user.id}"
            )
        return
    if m.reply_to_message and m.reply_to_message.document:
        if m.reply_to_message.document.mime_type.split("/")[1] == "x-python" or m.reply_to_message.document.file_name.endswith("py"):
            await sm.delete()
            await m.reply_text("Loading external plugin is prohibited")
            return
    reply_to_id = m.id
    if m.reply_to_message:
        reply_to_id = m.reply_to_message.id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, c, m)
    except Exception as ef:
        LOGGER.error(ef)
        exc = format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    for i in evaluation.split(None):
        ev = i.strip()
        if (
            (ev.startswith(initial) or ev.endswith(end))
            or (BOT_TOKEN in ev)
        ) and m.from_user.id != OWNER_ID:
            evaluation = "Bhaag ja bsdk"
            await c.send_message(
                MESSAGE_DUMP,
                f"@{m.from_user.username} TREID TO FETCH ENV OF BOT \n userid = {m.from_user.id}",
            )
    for j in HARMFUL:
        if j in evaluation.split() or j in cmd:
            if m.from_user.id != OWNER_ID:
                evaluation = "Bhaag ja bsdk"
                await c.send_message(
                    MESSAGE_DUMP,
                    f"@{m.from_user.username} TREID TO FETCH ENV OF BOT \n userid = {m.from_user.id}")
    for i in evaluation.split():
        for j in i.split("="):
            if j and j[0] in HARMFUL:
                if m.from_user.id != OWNER_ID:
                    evaluation = "Bhaag ja bsdk"
                    await c.send_message(
                        MESSAGE_DUMP,
                        f"@{m.from_user.username} TREID TO FETCH ENV OF BOT \n userid = {m.from_user.id}"
                    )
      

    try:
        final_output = f"**EVAL**: ```python\n{cmd}```\n\n<b>OUTPUT</b>:\n```python\n{evaluation}```</code> \n"
        await sm.edit(final_output)
    except MessageTooLong:
        final_output = f"<b>EVAL</b>: <code>{cmd}</code>\n\n<b>OUTPUT</b>:\n<code>{evaluation}</code> \n"
        with BytesIO(str.encode(await remove_markdown_and_html(final_output))) as f:
            f.name = "py.txt"
            await m.reply_document(
                document=f,
                caption=cmd,
                disable_notification=True,
                reply_to_message_id=reply_to_id,
            )
        await sm.delete()

    return


async def aexec(code, c, m):
    exec("async def __aexec(c, m): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](c, m)




@Gojo.on_message(command(["exec", "sh"], dev_cmd=True))
async def execution(c: Gojo, m: Message):
    protect = BOT_TOKEN.split(":")
    initial = protect[0]
    end = protect[1][-5:]
    if len(m.text.split()) == 1:
        await m.reply_text(text="Please execute the code correctly!")
        return
    sm = await m.reply_text("`Processing...`\n")
    cmd = m.text.split(maxsplit=1)[1]

    reply_to_id = m.id
    if m.reply_to_message:
        reply_to_id = m.reply_to_message.id

    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode().strip()
    if not e:
        e = "No Error"
    o = stdout.decode().strip()
    if not o:
        o = "No Output"
    out = o
    xxx = o.split()
    for OwO in xxx:
      if OwO.startswith(initial) or OwO.endswith(end):
          out = "You can't access them"
          break
    for x in xxx:
        xx = x.split("=")
        if xx and xx[0] in HARMFUL:
            if m.from_user.id != OWNER_ID:
                out = "You can't access them"
                await c.send_message(
                    MESSAGE_DUMP,
                    f"@{m.from_user.username} TREID TO FETCH ENV OF BOT \n userid = {m.from_user.id}",
                )
            else:
                pass
        else:
            pass
    for x in HARMFUL:
        if x in out:
            if m.from_user.id != OWNER_ID:
                out = "You can't access them"
                await c.send_message(
                    MESSAGE_DUMP,
                    f"@{m.from_user.username} TREID TO FETCH ENV OF BOT \n userid = {m.from_user.id}",
                )
            else:
                pass
        else:
            pass
    

    OUTPUT = ""
    OUTPUT += f"<b>QUERY:</b>\n<u>Command:</u>\n<code>{cmd}</code> \n"
    OUTPUT += f"<u>PID</u>: <code>{process.pid}</code>\n\n"
    OUTPUT += f"<b>stderr</b>: \n<code>{e}</code>\n\n"
    OUTPUT += f"<b>stdout</b>: \n<code>{out}</code>"

    try:
        await sm.edit_text(OUTPUT)
    except (MessageTooLong, EntityBoundsInvalid):
        with BytesIO(str.encode(await remove_markdown_and_html(OUTPUT))) as f:
            f.name = "sh.txt"
            await m.reply_document(
                document=f,
                caption=cmd,
                disable_notification=True,
                reply_to_message_id=reply_to_id,
            )
        await sm.delete()
    return

async def stop_and_send_logger(c:Gojo,is_update=False):
    runtime = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    LOGGER.info("Uploading logs before stopping...!\n")
        # Send Logs to MESSAGE_DUMP and LOG_CHANNEL
    await c.send_document(
            MESSAGE_DUMP,
            document=LOGFILE,
            caption=(
                f"{'Updating and Restarting'if is_update else 'Restarting'} The Bot !\n\n" f"Uptime: {runtime}\n" f"<code>{LOG_DATETIME}</code>"
            ),
        )
    if MESSAGE_DUMP:
        # LOG_CHANNEL is not necessary
        await c.send_document(
                MESSAGE_DUMP,
                document=LOGFILE,
                caption=f"Uptime: {runtime}",
            )
    MongoDB.close()
    LOGGER.info(
            f"""Bot Stopped.
            Logs have been uploaded to the MESSAGE_DUMP Group!
            Runtime: {runtime}s\n
        """,
        )
    return

@Gojo.on_message(command(["restart", "update"], owner_cmd=True),group=-100)
async def restart_the_bot(c:Gojo,m:Message):
    try:
        cmds = m.command
        await m.reply_text(f"Restarting{' and updating ' if cmds[0] == 'update' else ' '}the bot...\nType `/ping` after few minutes")
        if cmds[0] == "update":
            try:
                out = subp.check_output(["git", "pull"]).decode("UTF-8")
                if "Already up to date." in str(out):
                    return await m.reply_text("Its already up-to date!")
                await m.reply_text(f"```{out}```")
            except Exception as e:
                return await m.reply_text(str(e))
            m = await m.reply_text("**Updated with main branch, restarting now.**")
            await stop_and_send_logger(c,True)
        if cmds[0] == "restart":
            await stop_and_send_logger(c)
        execvp(executable, [executable, "-m", "Powers"])
    except Exception as e:
        await m.reply_text(f"Failed to restart the bot due to\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

@Gojo.on_message(command("chatlist", dev_cmd=True))
async def chats(c: Gojo, m: Message):
    exmsg = await m.reply_text(text="Exporting Charlist...")
    await c.send_message(
        MESSAGE_DUMP,
        f"#CHATLIST\n\n**User:** {(await mention_markdown(m.from_user.first_name, m.from_user.id))}",
    )
    all_chats = (Chats.list_chats_full()) or {}
    chatfile = """List of chats in my database.

        <b>Chat name | Chat ID | Members count</b>"""
    P = 1
    for chat in all_chats:
        try:
            chat_info = await c.get_chat(chat["_id"])
            chat_members = chat_info.members_count
            try:
                invitelink = chat_info.invite_link
            except KeyError:
                invitelink = "No Link!"
            chatfile += f"{P}. {chat['chat_name']} | {chat['_id']} | {chat_members} | {invitelink}\n"
            P += 1
        except ChatAdminRequired:
            pass
        except (ChannelPrivate, ChannelInvalid):
            Chats.remove_chat(chat["_id"])
        except PeerIdInvalid:
            LOGGER.warning(f"Peer not found {chat['_id']}")
        except FloodWait as ef:
            LOGGER.error("FloodWait required, Sleeping for 60s")
            LOGGER.error(ef)
            sleep(60)
        except RPCError as ef:
            LOGGER.error(ef)
            await m.reply_text(f"**Error:**\n{ef}")

    with BytesIO(str.encode(await remove_markdown_and_html(chatfile))) as f:
        f.name = "chatlist.txt"
        await m.reply_document(
            document=f,
            caption="Here is the list of chats in my Database.",
        )
    await exmsg.delete()
    return


@Gojo.on_message(command("uptime", dev_cmd=True))
async def uptime(_, m: Message):
    up = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    await m.reply_text(text=f"<b>Uptime:</b> <code>{up}</code>", quote=True)
    return


@Gojo.on_message(command("leavechat", dev_cmd=True))
async def leave_chat(c: Gojo, m: Message):
    if len(m.text.split()) != 2:
        await m.reply_text("Supply a chat id which I should leave!", quoet=True)
        return

    chat_id = m.text.split(None, 1)[1]

    replymsg = await m.reply_text(f"Trying to leave chat {chat_id}...", quote=True)
    try:
        await c.leave_chat(chat_id)
        await replymsg.edit_text(f"Left <code>{chat_id}</code>.")
    except PeerIdInvalid:
        await replymsg.edit_text("Haven't seen this group in this session!")
    except RPCError as ef:
        LOGGER.error(ef)
        await replymsg.edit_text(f"Failed to leave chat!\nError: <code>{ef}</code>.")
    return


@Gojo.on_message(command("chatbroadcast", dev_cmd=True))
async def chat_broadcast(c: Gojo, m: Message):
    if m.reply_to_message:
        msg = m.reply_to_message.text.markdown
    else:
        await m.reply_text("Reply to a message to broadcast it")
        return

    exmsg = await m.reply_text("Started broadcasting!")
    all_chats = (Chats.list_chats_by_id()) or {}
    err_str, done_broadcast = "", 0

    for chat in all_chats:
        try:
            await c.send_message(chat, msg, disable_web_page_preview=True)
            done_broadcast += 1
            await sleep(0.1)
        except RPCError as ef:
            LOGGER.error(ef)
            err_str += str(ef)
            continue

    await exmsg.edit_text(
        f"Done broadcasting ✅\nSent message to {done_broadcast} chats",
    )

    if err_str:
        with BytesIO(str.encode(await remove_markdown_and_html(err_str))) as f:
            f.name = "error_broadcast.txt"
            await m.reply_document(
                document=f,
                caption="Broadcast Error",
            )

    return

@Gojo.on_message(command(["forward","fwd"],dev_cmd=True))
async def forward_type_broadcast(c: Gojo, m: Message):
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Please reply to message to broadcast it")
        return
    split = m.command
    
    chat = Chats.list_chats_by_id()
    user = [i["_id"] for i in Users.list_users()]
    alll = chat + user
    if len(split) != 2:
        tag = "all"
    else:
        try:
            if split[0].lower() == "-u":
                tag = "user"
            elif split[0].lower() == "-c":
                tag = "chat"
            else:
                tag = "all"
        except IndexError:
            pass
    if tag == "chat":
        peers = chat
    elif tag == "user":
        peers = user
    else:
        peers = alll
    
    xx = await m.reply_text("Broadcasting...")

    failed = 0
    total = len(peers)
    for peer in peers:
        try:
            await repl.forward(int(peer))
            await sleep(0.1)
        except Exception:
            failed += 1
            pass
    txt = f"Broadcasted message to {total-failed} peers out of {total}\nFailed to broadcast message to {failed} peers"
    if not failed:
        txt = f"Broadcasted message to {total} peers"
    await m.reply_text(txt)
    try:
        await xx.delete()
    except Exception:
        pass
    return


@Gojo.on_message(command(["cleandb","cleandatabase"],sudo_cmd=True))
async def cleeeen(c:Gojo,m:Message):
    x = await m.reply_text("Cleaning the database...")
    try:
        z = await clean_my_db(c,True,m.from_user.id)
        try:
            await x.delete()
        except Exception:
            pass
        await m.reply_text(z)
        return
    except Exception as e:
        await m.reply_text(e)
        await x.delete()
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

__PLUGIN__ = "devs"


__HELP__ = """
**DEV and SUDOERS commands**

**Owner's commands:**
• /restart : Restart the bot
• /update : To update the bot with the main stream repo

**Dev's commands:**
• /addsupport [dev | sudo | whitelist] : Reply to message or give me user id or username
• /logs : Return the logs of bot.
• /neofetch : Fetch neo.
• /eval : Evaluate the given python code.
• /exec : Execute the given code.
• /chatlist : Return the list of chats present in database
• /uptime : Return the uptime of the bot.
• /leavechat : Bot will leave the provided chat.
• /chatbroadcast : Broadcast the messge to chats.
• /forward (/fwd) [tag] : Forward message to peers according to tag. Default to all
    Available tags:
     `-u` : For users
     `-c` : For chats
     `-all` : For all

**Sudoer's command:**
• /ping : return the ping of the bot.
• /cleandb : Delete useless junks from database (Automatically start cleaning it at 3:00:00 AM)

**Example:**
/ping
"""

import json
import re
from io import BytesIO
from os import remove

import aiofiles
from gpytranslate import Translator
from pyrogram import enums, filters
from pyrogram.errors import MessageTooLong, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError

from Powers import *
from Powers.bot_class import Gojo
from Powers.database.users_db import Users
from Powers.supports import get_support_staff
from Powers.utils.clean_file import remove_markdown_and_html
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Powers.utils.http_helper import *
from Powers.utils.parser import mention_html


@Gojo.on_message(command("wiki"))
async def wiki(_, m: Message):

    if len(m.text.split()) <= 1:
        return await m.reply_text(
            text="Please check help on how to use this this command."
        )

    search = m.text.split(None, 1)[1]
    try:
        res = summary(search)
    except DisambiguationError as de:
        return await m.reply_text(
            f"Disambiguated pages found! Adjust your query accordingly.\n<i>{de}</i>",
            parse_mode=enums.ParseMode.HTML,
        )
    except PageError as pe:
        return await m.reply_text(f"<code>{pe}</code>", parse_mode=enums.ParseMode.HTML)
    if res:
        result = f"<b>{search}</b>\n\n"
        result += f"<i>{res}</i>\n"
        result += f"""<a href="https://en.wikipedia.org/wiki/{search.replace(" ", "%20")}">Read more...</a>"""
        try:
            return await m.reply_text(
                result,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except MessageTooLong:
            with BytesIO(str.encode(await remove_markdown_and_html(result))) as f:
                f.name = "result.txt"
                return await m.reply_document(
                    document=f,
                    quote=True,
                    parse_mode=enums.ParseMode.HTML,
                )
    await m.stop_propagation()


@Gojo.on_message(command("gdpr"))
async def gdpr_remove(_, m: Message):
    if m.from_user.id in get_support_staff():
        await m.reply_text(
            "You're in my support staff, I cannot do that unless you are no longer a part of it!",
        )
        return

    Users(m.from_user.id).delete_user()
    await m.reply_text(
        "Your personal data has been deleted.\n"
        "Note that this will not unban you from any chats, as that is telegram data, not Gojo data."
        " Flooding, warns, and gbans are also preserved, as of "
        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/),"
        " which clearly states that the right to erasure does not apply 'for the performance of a task carried out in the public interest', "
        "as is the case for the aforementioned pieces of data.",
        disable_web_page_preview=True,
    )
    await m.stop_propagation()

@Gojo.on_message(
    command("lyrics") & (filters.group | filters.private),
)
async def get_lyrics(_, m: Message):
    if not is_genius_lyrics:
        await m.reply_text("Genius lyrics api is missing")
        return
    if len(m.text.split()) <= 1:
        await m.reply_text(text="Please check help on how to use this this command.")
        return

    query = m.text.split(None, 1)[1]
    artist = m.text.split("-")[-1].strip()
    song = ""
    if not query:
        await m.edit_text(text="You haven't specified which song to look for!")
        return
    song_name = query
    em = await m.reply_text(text=f"Finding lyrics for <code>{song_name}<code>...")
    try:
        if artist:
            song = genius_lyrics.search_song(query,artist)
        else:
            song = genius_lyrics.search_song(query)
    except Exception as e:
        await em.delete()
        await m.reply_text("Connection error try again after sometime")
        return
        
    if song:
        if song.lyrics:
            reply = song.lyrics
            reply = reply.split("\n",1)[1]
            if not artist:
                artist = song.artist
            else:
                artist = artist
        else:
            reply = "Couldn't find any lyrics for that song!"
    else:
        reply = "Song not found!"
    try:
        await em.edit_text(f"**{query.capitalize()} by {artist}**\n`{reply}`")
    except MessageTooLong:
        header = f"{query.capitalize()} by {artist}"
        with BytesIO(str.encode(await remove_markdown_and_html(reply))) as f:
            f.name = "lyrics.txt"
            await m.reply_document(
                document=f,
                caption=header
            )
        await em.delete()
    return



@Gojo.on_message(
    command("id") & (filters.group | filters.private),
)
async def id_info(c: Gojo, m: Message):

    ChatType = enums.ChatType
    user_id, _, _ = await extract_user(c, m)
    try:
        if user_id and len(m.text.split()) == 2:
            txt = f"Given user's id: <code>{user_id}</code>"
            await m.reply_text(txt, parse_mode=enums.ParseMode.HTML)
            return
        elif m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP] and not m.reply_to_message:
            await m.reply_text(text=f"This Group's ID is <code>{m.chat.id}</code>\nYour ID <code>{m.from_user.id}</code>")
            return

        elif m.chat.type == ChatType.PRIVATE and not m.reply_to_message:
            await m.reply_text(text=f"Your ID is <code>{m.chat.id}</code>.")
            return
    except Exception as e:
        await m.reply_text(e)
        return
    if user_id:
        if m.reply_to_message and m.reply_to_message.forward_from:
            user1 = m.reply_to_message.from_user
            user2 = m.reply_to_message.forward_from
            orig_sender = await mention_html(user2.first_name, user2.id)
            orig_id = f"<code>{user2.id}</code>"
            fwd_sender = await mention_html(user1.first_name, user1.id)
            fwd_id = f"<code>{user1.id}</code>"
            await m.reply_text(
                text=f"""Original Sender - {orig_sender} (<code>{orig_id}</code>)
Forwarder - {fwd_sender} (<code>{fwd_id}</code>)""",
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            try:
                user = await c.get_users(user_id)
            except PeerIdInvalid:
                await m.reply_text(
                    text="""Failed to get user
      Peer ID invalid, I haven't seen this user anywhere earlier, maybe username would help to know them!"""
                )
                return

            await m.reply_text(
                f"{(await mention_html(user.first_name, user.id))}'s ID is <code>{user.id}</code>.",
                parse_mode=enums.ParseMode.HTML,
            )
    elif m.chat.type == ChatType.PRIVATE:
        text=f"Your ID is <code>{m.chat.id}</code>."
        if m.reply_to_message:
            if m.forward_from:
                text+=f"Forwarded from user ID <code>{m.forward_from.id}</code>."
            elif m.forward_from_chat:
                text+=f"Forwarded from user ID <code>{m.forward_from_chat.id}</code>."
        await m.reply_text(text)
    else:
        text=f"Chat ID <code>{m.chat.id}</code>\nYour ID <code>{m.from_user.id}</code>"
        await m.reply_text(text)
    return


@Gojo.on_message(
    command("gifid") & (filters.group | filters.private),
)
async def get_gifid(_, m: Message):
    if m.reply_to_message and m.reply_to_message.animation:
        LOGGER.info(f"{m.from_user.id} used gifid cmd in {m.chat.id}")
        await m.reply_text(
            f"Gif ID:\n<code>{m.reply_to_message.animation.file_id}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        await m.reply_text(text="Please reply to a gif to get it's ID.")
    return


@Gojo.on_message(
    command(["github", "git"]) & (filters.group | filters.private),
)
async def github(_, m: Message):
    if len(m.text.split()) == 2:
        username = m.text.split(maxsplit=1)[1]
        LOGGER.info(f"{m.from_user.id} used github cmd in {m.chat.id}")
    else:
        await m.reply_text(
            f"Usage: <code>/github username</code>",
        )
        return
    username = username.split("/")[-1].strip("@")
    URL = f"https://api.github.com/users/{username}"
    try:
        r = resp_get(URL, timeout=5)
    except requests.exceptions.ConnectTimeout:
        return await m.reply_text("request timeout")
    except Exception as e:
        return await m.reply_text(f"ERROR:\n`{e}`")
    if r.status_code != 200:
        await m.reply_text(f"{username} this user is not available on github\nMake sure you have given correct username")
        return
    r = r.json()
    avtar = r.get("avatar_url", None)
    if avtar:
        avtar = avtar.rsplit("=",1)
        avtar.pop(-1)
        avtar.append("5")
        avtar = "=".join(avtar)
    url = r.get("html_url", None)
    name = r.get("name", None)
    company = r.get("company", None)
    followers = r.get("followers", 0)
    following = r.get("following", 0)
    public_repos = r.get("public_repos", 0)
    bio = r.get("bio", None)
    created_at = r.get("created_at", "NA").replace("T", " ").replace("Z","")
    location = r.get("location", None)
    email = r.get("email", None)
    updated_at = r.get("updated_at", "NA").replace("T", " ").replace("Z","")
    blog = r.get("blog", None)
    twitter = r.get("twitter_username", None)

    REPLY = ""
    if name:
        REPLY += f"<b>🧑‍💻 GitHub Info of {name}:</b>"
    if url:
        REPLY += f"\n<b>📎 URL:</b> <a href='{url}'>{username}</a>"
    REPLY += f"\n<b>🔑 Public Repos:</b> {public_repos}"
    REPLY += f"\n<b>🧲 Followers:</b> {followers}"
    REPLY += f"\n<b>✨ Following:</b> {following}"
    if email:
        REPLY += f"\n<b>✉️ Email:</b> <code>{email}</code>"
    if company:
        org_url = company.strip("@")
        REPLY += f"\n<b>™️ Organization:</b> <a href='https://github.com/{org_url}'>{company}</a>"
    if blog:
        bname = blog.split(".")[-2]
        bname = bname.split("/")[-1]
        REPLY += f"\n<b>📝 Blog:</b> <a href={blog}>{bname}</a>"
    if twitter:
        REPLY += f"\n<b>⚜️ Twitter:</b> <a href='https://twitter.com/{twitter}'>{twitter}</a>"
    if location:
        REPLY += f"\n<b>🚀 Location:</b> <code>{location}</code>"
    if created_at != "NA":
        REPLY += f"\n<b>💫 Created at:</b> <code>{created_at}</code>"
    if updated_at != "NA":
        REPLY += f"\n<b>⌚️ Updated at:</b> <code>{updated_at}</code>"
    if bio:
        REPLY += f"\n\n<b>🎯 Bio:</b> {bio}"

    kb = InlineKeyboardMarkup(
        [
            InlineKeyboardButton("")
        ]
    )

    if avtar:
        return await m.reply_photo(photo=f"{avtar}", caption=REPLY)
    await m.reply_text(REPLY)
    return


pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")
BASE = "https://pasty.lus.pm/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
}

def paste(content: str):
    data = {"content": content}
    resp = resp_post(f"{BASE}api/v1/pastes", data=json.dumps(data), headers=headers)
    if not resp.ok:
        return
    resp = resp.json()
    return BASE + resp['id']


@Gojo.on_message(command("paste"))
async def paste_func(_, message: Message):
    r = message.reply_to_message
    m = await message.reply_text("Pasting...")

    if not r:
        content = message.text.split(None, 1)[1]

    if r:
        if not r.text and not r.document:
            return await m.edit("Only text and documents are supported")

        if r.text:
            content = r.text
            exe = "txt"
        if r.document:
            if r.document.file_size > 40000:
                return await m.edit("You can only paste files smaller than 40KB.")

            if not pattern.search(r.document.mime_type):
                return await m.edit("Only text files can be pasted.")

            doc = await message.reply_to_message.download()
            exe = doc.rsplit(".",1)[-1]
            async with aiofiles.open(doc, mode="r") as f:
                fdata = await f.read()
                content = fdata

            remove(doc)
    try:
        link = paste(content)
    except Exception as e:
        await m.edit_text(e)
        return
    if not link:
        await m.edit_text("Failed to post!")
        return
    kb = [[InlineKeyboardButton(text="📍 Paste 📍", url=link + f".{exe}")]]
    await m.delete()
    try:
        await message.reply_text("Here's your paste", reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        if link:
            return await message.reply_text(f"Here's your paste:\n [link]({link + f'.{exe}'})",)
        return await message.reply_text(f"Failed to post. Due to following error:\n{e}")


@Gojo.on_message(command("tr"))
async def tr(_, message):
    trl = Translator()
    if message.reply_to_message and (
        message.reply_to_message.text or message.reply_to_message.caption
    ):
        if len(message.text.split()) == 1:
            target_lang = "en"
        else:
            target_lang = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "Provide lang code.\n[Available options](https://telegra.ph/Lang-Codes-02-22).\n<b>Usage:</b> <code>/tr en</code>",
            )
            return
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    detectlang = await trl.detect(text)
    try:
        tekstr = await trl(text, targetlang=target_lang)
    except ValueError as err:
        await message.reply_text(f"Error: <code>{str(err)}</code>")
        return
    return await message.reply_text(
        f"<b>Translated:</b> from {detectlang} to {target_lang} \n<code>``{tekstr.text}``</code>",
    )

@Gojo.on_message(command("bug"))
async def reporting_query(c: Gojo, m: Message):
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Please reply to a message to report it as bug")
        return
    if not repl.text:
        await m.reply_text("Please reply to a text message.")
        return
    txt = "#BUG\n"
    txt += repl.text.html
    txt += f"\nReported by: {m.from_user.id} ({m.from_user.mention})"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Update channel",url=f"https://t.me/{SUPPORT_GROUP}")],[InlineKeyboardButton("Report on github",url="https://github.com/Gojo-Bots/Gojo_Satoru/issues/new/choose")]])
    try:
        z = await c.send_message(MESSAGE_DUMP,txt,parse_mode=enums.ParseMode.HTML)
    except Exception:
        txt = repl.text.html
        z = await c.send_message(MESSAGE_DUMP,txt,parse_mode=enums.ParseMode.HTML)
        await z.reply_text(f"#BUG\nReported by: {m.from_user.id} ({m.from_user.mention})")
    await repl.delete()
    await m.reply_photo(photo="./extras/Fire.jpg",caption="Successfully reported your bug",reply_markup=kb)
    ppost = z.link
    await c.send_message(OWNER_ID,f"New bug report\n{ppost}",disable_web_page_preview=True)
    return

__PLUGIN__ = "utils"
_DISABLE_CMDS_ = ["paste", "wiki", "id", "gifid", "tr", "github", "git", "bug"]
__alt_name__ = ["util", "misc", "tools"]

__HELP__ = """
**Utils**

Some utils provided by bot to make your tasks easy!

• /id: Get the current group id. If used by replying to a message, get that user's id.
• /info: Get information about a user.
• /gifid: Reply to a gif to me to tell you its file ID.
• /lyrics `<song name>`-`<artist name>` : Find your song and give the lyrics of the song
• /wiki: `<query>`: wiki your query.
• /tr `<language>`: Translates the text and then replies to you with the language you have specifed, works as a reply to message.
• /git `<username>`: Search for the user using github api!
• /weebify `<text>` or `<reply to message>`: To weebify the text.
• /bug <reply to text message> : To report a bug

**Example:**
`/git iamgojoof6eyes`: this fetches the information about a user from the database."""

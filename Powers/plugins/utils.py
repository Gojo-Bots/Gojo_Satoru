from io import BytesIO
from os import remove
import re
import aiofiles
from search_engine_parser import GoogleSearch
from datetime import datetime
from aiohttp import ClientSession
from tswift import Song
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from traceback import format_exc

from gpytranslate import Translator
from pyrogram import filters
from pyrogram.errors import MessageTooLong, PeerIdInvalid, RPCError
from pyrogram.types import Message,InlineKeyboardButton, InlineKeyboardMarkup


from Powers import *
from Powers.bot_class import Gojo
from Powers.database.antispam_db import GBan
from Powers.database.users_db import Users
from Powers.utils.clean_file import remove_markdown_and_html
from Powers.utils.custom_filters import command
from Powers.utils.chat_type import chattype
from Powers.utils.http_helper import *
from Powers.utils.kbhelpers import ikb
from Powers.utils.parser import mention_html
from Powers.utils.extract_user import extract_user
from Powers.vars import Config

gban_db = GBan()


@Gojo.on_message(command("wiki"))
async def wiki(_, m: Message):

    if len(m.text.split()) <= 1:
        return await m.reply_text(text="Please check help on how to use this this command.")

    search = m.text.split(None, 1)[1]
    try:
        res = summary(search)
    except DisambiguationError as de:
        return await m.reply_text(
            f"Disambiguated pages found! Adjust your query accordingly.\n<i>{de}</i>",
            parse_mode="html",
        )
    except PageError as pe:
        return await m.reply_text(f"<code>{pe}</code>", parse_mode="html")
    if res:
        result = f"<b>{search}</b>\n\n"
        result += f"<i>{res}</i>\n"
        result += f"""<a href="https://en.wikipedia.org/wiki/{search.replace(" ", "%20")}">Read more...</a>"""
        try:
            return await m.reply_text(
                result,
                parse_mode="html",
                disable_web_page_preview=True,
            )
        except MessageTooLong:
            with BytesIO(str.encode(await remove_markdown_and_html(result))) as f:
                f.name = "result.txt"
                return await m.reply_document(
                    document=f,
                    quote=True,
                    parse_mode="html",
                )
    await m.stop_propagation()


@Gojo.on_message(command("gdpr"))
async def gdpr_remove(_, m: Message):
    if m.from_user.id in SUPPORT_STAFF:
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
    if len(m.text.split()) <= 1:
        await m.reply_text(text="Please check help on how to use this this command.")
        return

    query = m.text.split(None, 1)[1]
    song = ""
    if not query:
        await m.edit_text(text="You haven't specified which song to look for!")
        return
    song_name=query
    em = await m.reply_text(
        text=f"Finding lyrics for <code>{song_name}<code>...")
    song = Song.find_song(query)
    if song:
        if song.lyrics:
            reply = song.format()
        else:
            reply = "Couldn't find any lyrics for that song!"
    else:
        reply = "Song not found!"
    try:
        await em.edit_text(reply)
    except MessageTooLong:
        with BytesIO(str.encode(await remove_markdown_and_html(reply))) as f:
            f.name = "lyrics.txt"
            await m.reply_document(
                document=f,
            )
        await em.delete()
    return


@Gojo.on_message(
    command("id") & (filters.group | filters.private),
)
async def id_info(c: Gojo, m: Message):

    chat_type = await chattype(m)
    if chat_type == "supergroup" and not m.reply_to_message:
        await m.reply_text(text=f"This Group's ID is <code>{m.chat.id}</code>")
        return

    if chat_type == "private" and not m.reply_to_message:
        await m.reply_text(text=f"Your ID is <code>{m.chat.id}</code>.")
        return

    user_id, _, _ = await extract_user(c, m)
    if user_id:
        if m.reply_to_message and m.reply_to_message.forward_from:
            user1 = m.reply_to_message.from_user
            user2 = m.reply_to_message.forward_from
            orig_sender=(await mention_html(user2.first_name, user2.id)),
            orig_id=f"<code>{user2.id}</code>",
            fwd_sender=(await mention_html(user1.first_name, user1.id)),
            fwd_id=f"<code>{user1.id}</code>",
            await m.reply_text(
                text=f"""Original Sender - {orig_sender} (<code>{orig_id}</code>)
        Forwarder - {fwd_sender} (<code>{fwd_id}</code>)""",
                parse_mode="HTML",
            )
        else:
            try:
                user = await c.get_users(user_id)
            except PeerIdInvalid:
                await m.reply_text(text="""Failed to get user
      Peer ID invalid, I haven't seen this user anywhere earlier, maybe username would help to know them!""")
                return

            await m.reply_text(
                f"{(await mention_html(user.first_name, user.id))}'s ID is <code>{user.id}</code>.",
                parse_mode="HTML",
            )
    elif chat_type == "private":
        await m.reply_text(
            text=f"Your ID is <code>{m.chat.id}</code>."    
        )
    else:
        await m.reply_text(
            text=f"This Group's ID is <code>{m.chat.id}</code>"
        )
    return


@Gojo.on_message(
    command("gifid") & (filters.group | filters.private),
)
async def get_gifid(_, m: Message):
    if m.reply_to_message and m.reply_to_message.animation:
        LOGGER.info(f"{m.from_user.id} used gifid cmd in {m.chat.id}")
        await m.reply_text(
            f"Gif ID:\n<code>{m.reply_to_message.animation.file_id}</code>",
            parse_mode="html",
        )
    else:
        await m.reply_text(text="Please reply to a gif to get it's ID.")
    return


@Gojo.on_message(
    command("github") & (filters.group | filters.private),
)
async def github(_, message):
    try:
        if len(message.command) < 2:
            await message.reply_text('"/github" Needs An Argument')
            return
        gett = message.text.split(None, 1)[1]
        text = gett + ' "site:github.com"'
        gresults = await GoogleSearch().async_search(text, 1)
        result = ""
        for i in range(4):
            try:
                title = gresults["titles"][i].replace("\n", " ")
                source = gresults["links"][i]
                description = gresults["descriptions"][i]
                result += f"[{title}]({source})\n"
                result += f"`{description}`\n\n"
            except IndexError:
                pass
        await message.reply_text(result, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(str(e))
        LOGGER.error(e)
        LOGGER.error(format_exc())

#paste here
session = ClientSession()
pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")
BASE = "https://batbin.me/"

async def post(url: str, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data

async def paste(content: str):
    resp = await post(f"{BASE}api/v2/paste", data=content)
    if not resp["success"]:
        return
    return BASE + resp["message"]


@Gojo.on_message(command("paste"))
async def paste_func(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply To A Message With `/paste`")
   
    r = message.reply_to_message

    if not r.text and not r.document:
        return await message.reply_text("Only text and documents are supported")

    m = await message.reply_text("Pasting...")

    if r.text:
        content = str(r.text)
    elif r.document:
        if r.document.file_size > 40000:
            return await m.edit("You can only paste files smaller than 40KB.")

        if not pattern.search(r.document.mime_type):
            return await m.edit("Only text files can be pasted.")

        doc = await message.reply_to_message.download()

        async with aiofiles.open(doc, mode="r") as f:
            content = await f.read()

        remove(doc)

    link = await paste(content)
    kb = [[InlineKeyboardButton(text="Paste Link ", url=link)]]
    try:
        if m.from_user.is_bot:
            await message.reply_photo(
                photo=link,
                quote=False,
                caption="Pasted",
                reply_markup=InlineKeyboardMarkup(kb),
            )
        else:
            await message.reply_photo(
                photo=link,
                quote=False,
                caption="Pasted",
                reply_markup=InlineKeyboardMarkup(kb),
            )
        await m.delete()
    except Exception:
        await m.edit("Here is the link of the document....", reply_markup=InlineKeyboardMarkup(kb))


@Gojo.on_message(command("tr"))
async def tr(_, message):
    trl = Translator()
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
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




__PLUGIN__ = "utils"
_DISABLE_CMDS_ = [
    "paste",
    "wiki",
    "id",
    "gifid",
    "lyrics",
    "tr",
    "github",
]
__alt_name__ = ["util", "misc", "tools"]

__HELP__ = """
***Utils***

Some utils provided by bot to make your tasks easy!

* /id: Get the current group id. If used by replying to a message, get that user's id.
* /info: Get information about a user.
* /gifid: Reply to a gif to me to tell you its file ID.
* /wiki: `<query>`: wiki your query.
* /tr `<language>`: Translates the text and then replies to you with the language you have specifed, works as a reply to message.
* /github `<username>`: Search for the user using github api!
* /lyrics `<song>`: Get the lyrics of the song you specify!
* /weebify `<text>` or `<reply to message>`: To weebify the text.

**Example:**
`/github @iamgojoof6eyes`: this fetches the information about a user from the database."""

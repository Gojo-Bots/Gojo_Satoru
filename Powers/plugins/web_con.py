import asyncio
import os
from traceback import format_exc

from pyrogram import filters
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import (LOGGER, RMBG, Audd, genius_lyrics, is_audd,
                    is_genius_lyrics, is_rmbg)
from Powers.bot_class import Gojo
from Powers.utils.custom_filters import command
from Powers.utils.http_helper import *
from Powers.utils.sticker_help import toimage
from Powers.utils.web_helpers import *

# @Gojo.on_message(command(["songname","insong","songinfo","whichsong","rsong","reversesong"]))
# • /whichsong (/songname, /songinfo, /insong, /rsong, /reversesong) : Reply to file to get the song playing in it.
# async def get_song_info(c: Gojo, m: Message):
#     if not is_audd:
#         await m.reply_text("Audd api is missing add it to use this command")
#         return
#     reply = m.reply_to_message
#     if not reply:
#         await m.reply_text("Reply to a video or audio file")
#         return
#     elif reply.text:
#         await m.reply_text("Reply to a video or audio file")
#         return
#     elif not (reply.video or reply.audio or reply.video_note or reply.document and (reply.document.mime_type.split("/")[0] in ["video","audio"])):
#         await m.reply_text("Reply to a video or audio file")
#         return
#     try:
#         XnX = await m.reply_text("⏳")
#         URL = "https://api.audd.io/"
#         sizee = (await get_file_size(reply)).split()
#         if (int(sizee[0]) <= 30 and sizee[1] == "mb") or sizee[1] == "kb":
#             fpath = await reply.download()
#             files = {
#                 "file" : open(fpath,"rb")
#             }
#             BASE_AUDD = {
#                 "api_token":Audd,
#                 "return": "spotify"
#             }
#             result = resp_post(URL,data=BASE_AUDD, files=files)
#         # elif int(sizee[0]) > 15 or int(sizee[0]) <= 30 and sizee[1] == "mb":
#         #     BASE_AUDD = {
#         #         "api_token":Audd,
#         #         "url": f'{reply.link}',
#         #         "return": "spotify"
#         #     }
#         #    result = resp_post(URL,data=BASE_AUDD)
#         else:
#             await XnX.edit_text("File size too big\nI can only fetch file of size upto 30 mbs for now")
#             return
#         if result.status_code != 200:
#             await XnX.edit_text(f"{result.status_code}:{result.text}")
#             return
#         result = result.json()
#         data = result["result"]
#         Artist = data["artist"]
#         Title = data["title"]
#         Release_date = data["release_date"]
#         web_slink = data["song_link"]
#         SPOTIFY = data["spotify"]
#         spotify_url = SPOTIFY["external_urls"]
#         album_url = SPOTIFY["album"]["external_urls"]
#         Album = SPOTIFY["album"]["name"]
#         photo = SPOTIFY["images"][0]["url"]
#         artist_url = SPOTIFY["artists"]["external_urls"]
#         cap = f"""
#     Song name: {Title} 
#     Artist: {Artist}
#     Album: {Album}
#     Release data: {Release_date}
#     """
#         youtube_link = (await song_search(Title))[1]["link"]
#         kb = [
#             [
#                 IKB("🗂 Album", url=album_url),
#                 IKB("🎨 Artist",url=artist_url)
#             ],
#             [
#                 IKB("🎵 Spotify song link",url=spotify_url),
#                 IKB("▶️ Youtube",url=youtube_link)
#             ],
#             [IKB("♾ More links", url=web_slink)]
#         ]
#         if is_genius_lyrics:
#             g_k = [IKB("📝 Lyrics",f"lyrics_{Title}:{Artist}")]
#             kb.append(g_k)
#         await XnX.delete()
#         os.remove(fpath)
#         await m.reply_photo(photo,caption=cap,reply_markup=IKM(kb))
#     except Exception as e:
#         await XnX.delete()
#         await m.reply_text(f"Error\n{e}")
#         try:
#             os.remove(fpath)
#         except Exception:
#             pass
#     return

songs = dict()

@Gojo.on_callback_query(filters.regex("^lyrics_"))
async def lyrics_for_song(c: Gojo, q: CallbackQuery):
    data = q.data.split("_")[1].split(":")
    song = songe = data[0]
    try:
        artist = data[1]
    except IndexError:
        artist = None
    if artist:
        song = genius_lyrics.search_song(song,artist)
    elif not artist:
        song = genius_lyrics.search_song(song)
        artist = song.artist
    if not song.lyrics:
        await q.answer("‼️ No lyrics found ‼️",True)
        return
    header = f"{songe.capitalize()} by {artist}"
    if song.lyrics:
        await q.answer("Fetching lyrics")
        reply = song.lyrics.split("\n",1)[1]
    if len(reply) >= 4096:
        cap = f"{header}\n{reply[0:4080]}..."
        if artist:
            songs[f"{songe}"][f"{artist}"] = reply
            art = '_'+artist
        else:
            songs[f"{songe}"] = reply
            art = ''
        new_kb = [
            [
                IKB("Next",f"lyrics_next_{songe}{art}")
            ]
            [
                IKB("Close","f_close")
            ]
        ]
    else:
        cap = f"{header}\n{reply}"
        new_kb = [
            [
                IKB("Close","f_close")
            ]
        ]
    await q.message.reply_to_message.reply_text(cap,reply_markup=new_kb)
    await q.message.delete()
    return

@Gojo.on_callback_query(filters.regex("^lyrics_next_") | filters.regex("^lyrics_prev_"))
async def lyrics_for_song_next(c: Gojo, q: CallbackQuery):
    split = q.data.split("_")
    song = split[2]
    todo = split[1]
    try:
        artist = split[3]
        header = f"{song.capitalize()} by {artist}"
        art = '_'+artist
    except IndexError:
        artist = False
        header = f"{song.capitalize()}"
        art = ''
    try:
        if artist:
            songe = songs[song][artist]
        else:
            songe = songs[song]
    except KeyError:
        if artist:
            songe = genius_lyrics.search_song(song,artist)
        elif not artist:
            songe = genius_lyrics.search_song(song)
        if todo == "next":
            next_part = songe[4080:]
        else:
            next_part = songe[:4080]
    next_part = f"{header}\n{next_part}"
    new_kb = [
            [
                IKB("Next",f"lyrics_prev_{song}{art}")
            ]
            [
                IKB("Close","f_close")
            ]
        ]
    await q.edit_message_text(next_part, reply_markup=new_kb)


@Gojo.on_message(command(["removebackground","removebg","rmbg"]))
async def remove_background(c: Gojo, m: Message):
    if not is_rmbg:
        await m.reply_text("Add rmbg api to use this command")
        return
    
    reply = m.reply_to_message
    if not reply:
        await m.reply_text("Reply to image/sticker to remove it's background")
        return
    elif not (reply.photo or (reply.document and reply.document.mime_type.split("/")[0] == "image") or reply.sticker):
        await m.reply_text("Reply to image/sticker to remove it's background")
        return
    elif reply.sticker and (reply.sticker.is_video or reply.sticker.is_animated):
        await m.reply_text("Reply to normal sticker to remove it's background")
        return
    XnX = await m.reply_text("⏳")
    URL = "https://api.remove.bg/v1.0/removebg"
    if reply.sticker:
        filee = await reply.download()
        file = toimage(filee)
    else:
        file = await reply.download()
    finfo = {'image_file':open(file,'rb')}
    Data = {'size':'auto'}
    Headers = {'X-Api-Key':RMBG}
    result = resp_post(URL,files=finfo,data=Data,headers=Headers)
    await XnX.delete()
    contentType = result.headers.get("content-type")
    if result.status_code != 200:
        await m.reply_text(f"{result.status_code}:{result.text}")
        os.remove(file)
        return
    elif "image" not in contentType:
        await m.reply_text(f"Error\n{result.content.decode('UTF-8')}")
        os.remove(file)
        return
    to_path = "./downloads"
    if reply.sticker:
        to_path = f'{to_path}/no-bg.webp'
    else:
        to_path = f'{to_path}/no-bg.png'
    with open(to_path,'wb') as out:
        out.write(result.content)
    if reply.sticker:
        await m.reply_sticker(to_path)
    else:
        await m.reply_photo(to_path)
    try:
        os.remove(file)
        os.remove(to_path)
    except PermissionError:
        await asyncio.sleep(5)
    return

@Gojo.on_message(command(["song","yta"]))
async def song_down_up(c: Gojo, m: Message):
    try:
        splited = m.text.split(None,1)[1].strip()
    except IndexError:
        await m.reply_text("**USAGE**\n /song [song name | link]")
        return
    if splited.startswith("https://youtube.com"):
        is_direct = True
        query = splited.split("?")[0]
    else:
        is_direct = False
        query = splited
    XnX = await m.reply_text("⏳")
    try:
        await youtube_downloader(c,m,query,is_direct,"a")
        await XnX.delete()
        return
    except KeyError:
        await XnX.edit_text(f"Failed to find any result")
        return
    except Exception as e:
        await XnX.edit_text(f"Got an error\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

@Gojo.on_message(command(["vsong","ytv"]))
async def video_down_up(c: Gojo, m: Message):
    try:
        splited = m.text.split(None,1)[1].strip()
    except IndexError:
        await m.reply_text("**USAGE**\n /vsong [song name | link]")
        return
    if splited.startswith("https://youtube.com"):
        is_direct = True
        query = splited.split("?")[0]
    else:
        is_direct = False
        query = splited
    XnX = await m.reply_text("⏳")
    try:
        await youtube_downloader(c,m,query,is_direct,"v")
        await XnX.delete()
        return
    except KeyError:
        await XnX.edit_text(f"Failed to find any result")
        return
    except Exception as e:
        await XnX.edit_text(f"Got an error\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

@Gojo.on_message(command(["ig","instagram","insta"]))
async def download_instareels(c: Gojo, m: Message):
    try:
        reel_ = m.command[1]
    except IndexError:
        await m.reply_text("Give me an link to download it...")
        return
    if not reel_.startswith("https://www.instagram.com/reel/"):
        await m.reply_text("In order to obtain the requested reel, a valid link is necessary. Kindly provide me with the required link.")
        return
    OwO = reel_.split(".",1)
    Reel_ = ".dd".join(OwO)
    try:
        await m.reply_video(Reel_)
        return
    except Exception:
        try:
            await m.reply_photo(Reel_)
            return
        except Exception:
            try:
                await m.reply_document(Reel_)
                return
            except Exception:
                await m.reply_text("I am unable to reach to this reel.")
                return

__PLUGIN__ = "web support"

__HELP__ = """
**Available commands**
• /rmbg (/removebg, /removebackground) : Reply to image file or sticker of which you want to remove background
• /song (/yta) <songname or youtube link> : Download audio only from provided youtube url
• /vsong (/ytv) <songname or youtube link> : Download video from provided youtube url
• /ig (/instagram , /insta) <reel's url> : Download reel from it's url

**Bot will not download any song or video having duration greater than 10 minutes (to reduce the load on bot's server)**
"""

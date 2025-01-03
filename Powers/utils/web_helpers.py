import math
import os
import time
from traceback import format_exc

from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message
from pytube import YouTube, extract
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL

from Powers import youtube_dir
from Powers.bot_class import LOGGER, Gojo
from Powers.utils.sticker_help import resize_file_to_sticker_size
from Powers.utils.web_scrapper import SCRAP_DATA

backUP = "https://artfiles.alphacoders.com/160/160160.jpeg"


def readable_time(seconds: int) -> str:
    count = 0
    out_time = ""
    time_list = []
    time_suffix_list = ["secs", "mins", "hrs", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]

    if len(time_list) == 4:
        out_time += f"{time_list.pop()}, "

    time_list.reverse()
    out_time += " ".join(time_list)

    return out_time or "0 secs"


def humanbytes(size: int):
    if not size:
        return ""
    power = 2 ** 10
    number = 0
    dict_power_n = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        number += 1
    return f"{str(round(size, 2))} {dict_power_n[number]}B"


async def progress(
        current: int, total: int, message: Message, start: float, process: str
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        complete_time = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + complete_time
        progress_str = "**[{0}{1}] : {2}%\n**".format(
            "".join(["●" for _ in range(math.floor(percentage / 10))]),
            "".join(["○" for _ in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        msg = (
                progress_str
                + "__{0}__ **𝗈𝖿** __{1}__\n**𝖲𝗉𝖾𝖾𝖽:** __{2}/s__\n**𝖤𝖳𝖠:** __{3}__".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            readable_time(estimated_total_time / 1000),
        )
        )
        await message.edit_text(f"**{process} ...**\n\n{msg}")


async def get_file_size(file: Message):
    if file.photo:
        size = file.photo.file_size / 1024
    elif file.document:
        size = file.document.file_size / 1024
    elif file.video:
        size = file.video.file_size / 1024
    elif file.audio:
        size = file.audio.file_size / 1024
    elif file.sticker:
        size = file.sticker.file_size / 1024
    elif file.animation:
        size = file.animation.file_size / 1024
    elif file.voice:
        size = file.voice.file_size / 1024
    elif file.video_note:
        size = file.video_note.file_size / 1024

    if size <= 1024:
        return f"{round(size)} kb"
    size = size / 1024
    if size <= 1024:
        return f"{round(size)} mb"
    elif size > 1024:
        size = size / 1024
        return f"{round(size)} gb"


def get_video_id(url):
    try:
        _id = extract.video_id(url)
        return _id or None
    except Exception:
        return None


def get_duration_in_sec(dur: str):
    duration = dur.split(":")
    return (
        (int(duration[0]) * 60) + int(duration[1])
        if len(duration) == 2
        else int(duration[0])
    )


# Gets yt result of given query.


async def song_search(query, max_results=1):
    yt_dict = {}
    try:
        videos = VideosSearch(query, max_results)
        results = await videos.next()
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return {0: e}
    nums = 1
    for i in results["result"]:
        durr = i['duration'].split(":")
        if len(durr) == 3:
            hour_to_sec = int(durr[0]) * 60 * 60
            minutes_to_sec = int(durr[1]) * 60
            total = hour_to_sec + minutes_to_sec + int(durr[2])
        if len(durr) == 2:
            minutes_to_sec = int(durr[0]) * 60
            total = minutes_to_sec + int(durr[1])
        if total <= 600:
            dict_form = {
                "link": i["link"],
                "title": i["title"],
                "views": i["viewCount"]["short"],
                "channel": i["channel"]["link"],
                "duration": i["accessibility"]['duration'],
                "DURATION": i["duration"],
                "published": i["publishedTime"],
            }
            try:
                dict_form["uploader"] = i["channel"]["name"]
            except Exception:
                dict_form["uploader"] = "Captain D. Ezio"
            try:
                thumb = {"thumbnail": i["thumbnails"][0]["url"]}
            except Exception:
                thumb = {"thumbnail": None}
            dict_form.update(thumb)
            yt_dict[nums] = dict_form
            nums += 1
    return yt_dict


song_opts = {
    "format": "bestaudio",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "480",
        }
    ],
    "outtmpl": "%(id)s",
    "quiet": True,
    "logtostderr": False,
}

video_opts = {
    "format": "best",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }
    ],
    "outtmpl": "%(id)s.mp4",
    "quiet": True,
    "logtostderr": False,
}


async def youtube_downloader(c: Gojo, m: Message, query: str, type_: str):
    if type_ == "a":
        opts = song_opts
        video = False
        song = True
        ext = "mp3"
    elif type_ == "v":
        opts = video_opts
        video = True
        song = False
        ext = "mp4"
    # ydl = yt_dlp.YoutubeDL(opts)
    dicti = await song_search(query, 1)
    if err := dicti.get(0, None):
        await m.reply_text(err)
        return
    if not dicti and type(dicti) != str:
        await m.reply_text("File with duration less than or equals to 10 minutes is allowed only")
    elif type(dicti) == str:
        await m.reply_text(dicti)
        return
    try:
        query = dicti[1]['link']
    except KeyError:
        return
    yt = YouTube(query)
    if yt.age_restricted:
        await m.reply_text("This video is age restricted")
        return
    dicti = dicti[1]
    f_name = dicti["title"]
    views = dicti["views"]
    up_url = dicti["channel"]
    uploader = dicti["uploader"]
    dura = dicti["duration"]
    thumb = dicti["thumbnail"]
    vid_dur = get_duration_in_sec(dicti["DURATION"])
    published_on = dicti["published"]
    if thumb:
        try:
            thumb = SCRAP_DATA(thumb).get_images()
            thumb = await resize_file_to_sticker_size(thumb[0], 320, 320)
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error(format_exc())
            LOGGER.info("Using back up image as thumbnail")
            thumb = SCRAP_DATA(backUP).get_images()
            thumb = await resize_file_to_sticker_size(thumb[0], 320, 320)

    else:
        thumb = SCRAP_DATA(backUP).get_images()
        thumb = await resize_file_to_sticker_size(thumb[0], 320, 320)

    # FILE = ydl.extract_info(query,download=video)
    url = query
    cap = f"""
⤷ Name: `{f_name}`
⤷ Duration: `{dura}`
⤷ Views: `{views}`
⤷ Published: `{published_on}`

Downloaded by: @{c.me.username}
"""
    upload_text = f"**⬆️ 𝖴𝗉𝗅𝗈𝖺𝖽𝗂𝗇𝗀 {'audio' if song else 'video'}** \\**⚘ 𝖳𝗂𝗍𝗅𝖾:** `{f_name[:50]}`\n*⚘ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅:** `{uploader}`"
    kb = IKM(
        [
            [IKB(f"✘ {uploader.capitalize()} ✘", url=f"{up_url}")],
            [IKB("✘ Youtube url ✘", url=f"{url}")],
        ]
    )

    def get_my_file(opts, ext):
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([query])
                info = ydl.extract_info(query, False)
            file_name = ydl.prepare_filename(info)
            if len(file_name.rsplit(".", 1)) != 2:
                file_name = f"{file_name}.{ext}"
            new = info['title'].replace('/', '|').replace('\\', '|')
            new_file = f"{youtube_dir}{new}.{ext}"
            os.rename(file_name, new_file)
            return True, new_file
        except Exception as e:
            return False, str(e)

    if song:
        success, file_path = get_my_file(opts, ext)
        if not success:
            await m.reply_text(file_path)
            return
        msg = await m.reply_text(upload_text)
        await m.reply_audio(file_path, caption=cap, reply_markup=kb, duration=vid_dur, thumb=thumb, title=f_name,
                            performer=uploader, progress=progress, progress_args=(msg, time.time(), upload_text))
        await msg.delete()
        os.remove(file_path)
        return
    elif video:
        success, file_path = get_my_file(opts, ext)
        if not success:
            await m.reply_text(file_path)
            return
        msg = await m.reply_text(upload_text)
        await m.reply_video(file_path, caption=cap, reply_markup=kb, duration=vid_dur, thumb=thumb, progress=progress,
                            progress_args=(msg, time.time(), upload_text))
        await msg.delete()
        os.remove(file_path)
        return

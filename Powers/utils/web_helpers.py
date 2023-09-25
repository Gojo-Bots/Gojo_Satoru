import json
import os
from traceback import format_exc
from urllib import parse

import yt_dlp
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message
from youtubesearchpython.__future__ import Video, VideosSearch

from Powers.bot_class import LOGGER, MESSAGE_DUMP, Gojo
from Powers.utils.http_helper import *


async def get_file_size(file: Message):
    if file.photo:
        size = file.photo.file_size/1024
    elif file.document:
        size = file.document.file_size/1024
    elif file.video:
        size = file.video.file_size/1024
    elif file.audio:
        size = file.audio.file_size/1024
    elif file.sticker:
        size = file.sticker.file_size/1024
        
    if size <= 1024:
        return f"{round(size)} kb"
    elif size > 1024:
        size = size/1024
        if size <= 1024:
            return f"{round(size)} mb"
        elif size > 1024:
            size = size/1024
            return f"{round(size)} gb"



# Gets yt result of given query.
async def song_search(query, is_direct, max_results=1):
    yt_dict = {}
    try:
        if is_direct:
            vid = Video.getInfo(query)
            query = vid["title"]
        else:
            query = query
        videos = VideosSearch(query,max_results)
        results = await videos.next()
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return e
           
    nums = 1
    for i in results["result"]:
        durr = i['duration'].split(":")
        if len(durr) == 3:
            hour_to_sec = int(durr[0])*60*60
            minutes_to_sec = int(durr[1])*60
            total = hour_to_sec + minutes_to_sec + int(durr[2])
        if len(durr) == 2:
            minutes_to_sec = int(durr[0])*60
            total = minutes_to_sec + int(durr[1])
        if not (total > 600):
            dict_form = {
                "link": i["link"],
                "title": i["title"],
                "views": i["viewCount"]["short"],
                "channel": i["channel"]["link"],
                "duration": i["accessibility"]['duration'],
                "thumbnail": i["richThumbnail"],
                "published": i["publishedTime"],
                "uploader": i ["channel"]["name"]
                }
            yt_dict.update({nums: dict_form})
            nums += 1
        else:
            pass
    return yt_dict

song_opts = {
    "format": "bestaudio",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
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
    "outtmpl": "%(id)s.mp3",
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
    "logtostderr": False,
    "quiet": True,
}



async def youtube_downloader(c:Gojo,m:Message,query:str,is_direct:bool,type_:str):
    if type_ == "a":
        opts = song_opts
        video = False
        song = True
    elif type_ == "v":
        opts = video_opts
        video = True
        song = False
    ydl = yt_dlp.YoutubeDL(opts)
    dicti = await song_search(query, is_direct,1)
    if not dicti and type(dicti) != str:
        await m.reply_text("File with duration less than or equals to 5 minutes is allowed only")
    elif type(dicti) == str:
        await m.reply_text(dicti)
        return
    try:
        query = dicti[1]['link']
    except KeyError:
        z = "KeyError"
        return z
    
    f_name = dicti["title"]
    views = dicti["views"]
    up_url = dicti["channel"]
    uploader = dicti["uploader"]
    thumb = dicti["thumbnail"]
    published_on = dicti["publishedON"]

    FILE = ydl.extract_info(query,download=video)
    url = query
    thumb_ = await c.send_photo(MESSAGE_DUMP, thumb)
    thumb = await thumb_.download()
    await thumb_.delete()
    if song:
        f_down = ydl.prepare_filename(FILE)
        f_path = f"{f_down}.mp3"
        ydl.download([query])
        ext = ".mp3"
    elif video:
        f_path = open(f"{FILE['id']}.mp4","rb")
        ext = ".mp4"
    cap = f"""
⤷ Name: `{f_name}`
⤷ Views: `{views}`
⤷ Published date: `{published_on}`
"""
    kb = IKM(
        [
            [
                IKB(f"✘ {uploader.capitalize()} ✘",url=f"{up_url}")
            ],
            [
                IKB(f"✘ Youtube url ✘", url=f"{url}")
            ]
        ]
    )

    file_path = f_name.strip() + ext
    os.rename(f_path,file_path)


    if video:
        await m.reply_video(file_path,caption=cap,reply_markup=kb,duration=int(FILE['duration']))
        os.remove(file_path)
        os.remove(thumb)
        return
    elif song:
        await m.reply_audio(file_path,caption=cap,reply_markup=kb,duration=int(FILE['duration']),thumb=thumb,title=f_name)
        os.remove(f_path)
        os.remove(thumb)
        return



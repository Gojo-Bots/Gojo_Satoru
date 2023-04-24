import json
import os
from urllib import parse

import yt_dlp
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message
from telegraph import upload_file

from Powers import telegraph
from Powers.bot_class import Gojo
from Powers.utils.http_helper import *


async def get_file_size(file: Message):
    if file.photo:
        size = file.photo.file_size/1024
    elif file.document:
        size = file.document.file_size/1024
    elif file.video:
        size = file.video.file_size/1024

    if size <= 1024:
        return f"{round(size,3)} kb"
    elif size > 1024:
        size = size/1024
        if size <= 1024:
            return f"{round(size,3)} mb"
        elif size > 1024:
            size = size/1024
            return f"{round(size,3)} gb"

async def telegraph_up(file:Message=None,name=None,content=None):
    if not name:
        name = "Captain_Ezio_Gojo_Bots"
    if content:
        page = telegraph.create_page(name,html_content=content)
        if page:
            return page['url']
        else:
            return
    if file.text:
        to_upload = file.text.html
        page = telegraph.create_page(name,html_content=to_upload)
        if page:
            return page['url']
        else:
            return
    doc = await file.download()
    media_url = upload_file(doc)
    tg_url = f"https://telegra.ph/{media_url[0]}"
    os.remove(doc)
    if tg_url:
        return tg_url
    else:
        return

class GOJO_YTS:
    """
    A class to fetch link of from youtube using the name provided
    Creadit: Hellbot
    """
    def __init__(self, search_terms: str, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = self._search()

    def _search(self):
        encoded_search = parse.quote_plus(self.search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = get(url).text
        while "ytInitialData" not in response:
            response = get(url).text
        results = self._parse_html(response)
        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]
        return results

    def _parse_html(self, response):
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos:
            res = {}
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})
                res["id"] = video_data.get("videoId", None)
                res["thumbnails"] = [
                    thumb.get("url", None)
                    for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])
                ]
                res["title"] = (
                    video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
                )
                res["long_desc"] = (
                    video_data.get("descriptionSnippet", {})
                    .get("runs", [{}])[0]
                    .get("text", None)
                )
                res["channel"] = (
                    video_data.get("longBylineText", {})
                    .get("runs", [[{}]])[0]
                    .get("text", None)
                )
                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                res["publish_time"] = video_data.get("publishedTimeText", {}).get(
                    "simpleText", 0
                )
                res["url_suffix"] = (
                    video_data.get("navigationEndpoint", {})
                    .get("commandMetadata", {})
                    .get("webCommandMetadata", {})
                    .get("url", None)
                )
                results.append(res)
        return results

    def to_dict(self, clear_cache=True):
        result = self.videos
        if clear_cache:
            self.videos = ""
        return result

    def to_json(self, clear_cache=True):
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = ""
        return result


# Gets yt result of given query.
async def song_search(query, max_results=1):
    try:
        results = json.loads(GOJO_YTS(query, max_results=max_results).to_json())
    except KeyError:
        return 
    yt_dict = {}
    if not (i['duration'] > 300):       
        nums = 1
        for i in results["videos"]:
            dict_form = {
                "link": f"https://www.youtube.com{i['url_suffix']}",
                "title": i['title'],
                "views": i['views'],
                "channel": i['channel'],
                "duration": i['duration'],
                "thumbnail": i['thumbnails'][0]
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
    if is_direct:
        query = query
    else:
        dicti = await song_search(query, 1)
        if not dicti:
            await m.reply_text("File with duration less than or equals to 5 minutes is allowed only")
            return
        query = dicti['link']
    FILE = ydl.extract_info(query,download=False)
    if FILE['duration'] > 300:
        await m.reply_text("File with duration less than or equals to 5 minutes is allowed only")
        return 
    f_name = FILE['title']
    uploader = FILE['uploader']
    up_url = FILE['uploader_url']
    views = FILE['view_count']
    url = f"https://www.youtube.com/watch?v={FILE['id']}"
    f_path = ydl.prepare_filename(FILE)
    ydl.download([query])
    cap = f"""
✘ Name: `{f_name}`
✘ Views: `{views}` 
"""
    kb = IKM(
        [
            [
                IKB(f"✘ {uploader.capitalize()} ✘",url=f"{up_url}"),
                IKB(f"✘ Youtube url ✘", url=f"{url}")
            ]
        ]
    )
    if video:
        m.reply_video(f_path,caption=cap,reply_markup=kb)
        os.remove(f_path)
        return
    elif song:
        m.reply_audio(f_path,caption=cap,reply_markup=kb)
        os.remove(f_path)
        return



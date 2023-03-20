#Add pyrogram, requests, beautifulsoup4, youtubesearchpython, youtube_dl, deezer-python these in requirements.txt
import pyrogram
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
from youtubesearchpython import SearchVideos
from youtube_dl import YoutubeDL
from deezer import Deezer
from Powers.bot_class import Gojo as app

def download_yt_song(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        ydl.download([url])
    return video_title + '.mp3'


@app.on_message(filters.command("song"))
def get_song(client: Client, message: Message):
    text = message.text.split(" ", 1)[1]
    if text.startswith("https://www.youtube.com/"):
        # If YouTube link is provided, download and upload the song
        video_title = download_yt_song(text)
        audio_file = video_title
        title = video_title[:-4]
        with open(audio_file, 'rb') as f:
            client.send_audio(
                chat_id=message.chat.id,
                audio=f,
                caption=title,
                title=title,
                duration=60,
            )
        os.remove(audio_file)
    else:
        deezer = Deezer()
        song = deezer.search(text)
        song_url = song[0]['preview']
        response = requests.get(song_url)
        audio_file = song[0]['title'] + '.mp3'
        with open(audio_file, 'wb') as f:
            f.write(response.content)
        with open(audio_file, 'rb') as f:
            client.send_audio(
                chat_id=message.chat.id,
                audio=f,
                caption=song[0]['title'] + ' - ' + song[0]['artist']['name'],
                title=song[0]['title'],
                duration=int(song[0]['duration'] / 1000),
            )
        os.remove(audio_file)

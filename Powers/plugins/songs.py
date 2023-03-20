from pyrogram import Client, filters
import os
import youtube_dl
from Powers.bot_class import Gojo as app

@app.on_message(filters.command('song', prefixes='/'))
def download_and_upload_song(client, message):
    query = message.text.split(' ', 1)[1]
    url = f'https://youtube.com/results?search_query={query}'
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.mp3',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(url, download=False)['entries']

    if not search_results:
        message.reply_text('Sorry, I could not find that song on YouTube.')
        return
    video = search_results[0]
    message.reply_audio(audio='song.mp3', caption=f'{video.get("title")}\nDuration: {video.get("duration")} seconds\nViews: {video.get("view_count")}')

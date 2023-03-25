# Add instagrapi & pytube in requirements.txt
from pyrogram import Client, filters
import urllib.request
from instagrapi import Client as InstaClient
from pytube import YouTube
from Powers.bot_class import Gojo as app

insta_client = InstaClient()

@app.on_message(filters.command("download"))
def download_media(client, message):
    chat_id = message.chat.id
    platform = message.text.split()[1]
    client.send_message(chat_id, "Enter your choice 1 for Instagram 2 For YouTube:")
    if platform == "1":
        client.send_message(chat_id, "Please enter the Instagram post or story URL:")
        insta_link = message.text.split()[2]

        media = insta_client.media_info(insta_link)

        video_url = media.video_versions[0].url
        urllib.request.urlretrieve(video_url, "video.mp4")

        client.send_video(chat_id, video="video.mp4")

    elif platform == "2":
        client.send_message(chat_id, "Please enter the YouTube link:")
        yt_link = message.text.split()[2]

        yt = YouTube(yt_link)
        stream = yt.streams.get_highest_resolution()

        stream.download(output_path="./", filename="video.mp4")

        client.send_video(chat_id, video="video.mp4")

    else:
        client.send_message(chat_id, "Invalid platform choice. Please enter 1 for Instagram or 2 for YouTube.")

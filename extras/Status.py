import time
import psutil
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler


# TeamUltroid/Ultroid
def time_formatter(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (((str(weeks) + "w:") if weeks else "") +
           ((str(days) + "d:") if days else "") +
           ((str(hours) + "h:") if hours else "") +
           ((str(minutes) + "m:") if minutes else "") +
           ((str(seconds) + "s") if seconds else ""))
    if not tmp:
        return "0s"
    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp


class PyroClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()
        self.add_handler(MessageHandler(
            self.status, filters=filters.private & filters.command("statusbot")))

    @staticmethod
    async def status(client, message):
        uptime = time_formatter((time.time() - client.start_time) * 1000)
        cpu = psutil.cpu_percent()
        TEXT = f"UPTIME: {uptime} | CPU: {cpu}%"
        await message.reply(TEXT)

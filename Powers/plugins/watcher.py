from Powers.bot_class import Gojo
from pyrogram.types import Message
from pyrogram import filters

try:
  from RiZoeLX.functions import Red7_Watch
except:
  import os
  os.system("pip3 install pyRiZoeLX")
  from RiZoeLX.functions import Red7_Watch

@Gojo.on_message(filters.new_chat_members)
async def Red7_Scanner(_, message: Message):
    await Red7_Watch(Gojo, message)

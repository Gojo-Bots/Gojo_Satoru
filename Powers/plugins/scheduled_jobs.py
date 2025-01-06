from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client

from Powers import BDB_URI, TIME_ZONE
from Powers.database.chats_db import Chats

# from Powers.database.users_db import Users
if BDB_URI:
    from Powers.plugins import bday_cinfo, bday_info

from datetime import datetime, time
from random import choice

from pyrogram.enums import ChatMemberStatus

from Powers.utils.extras import birthday_wish


def give_date(date, form="%d/%m/%Y"):
    return datetime.strptime(date, form).date()


scheduler = AsyncIOScheduler()
scheduler.timezone = TIME_ZONE
scheduler_time = time(0, 0, 0)


async def send_wishish(JJK: Client):
    c_list = Chats.list_chats_by_id()
    blist = list(bday_info.find())
    curr = datetime.now(TIME_ZONE).date()
    cclist = list(bday_cinfo.find())
    for i in blist:
        dob = give_date(i["dob"])
        if dob.month == curr.month and dob.day == curr.day:
            for j in c_list:
                if cclist and (j in cclist):
                    return
                try:
                    agee = ""
                    if i["is_year"]:
                        agee = curr.year - dob.year
                        if int(agee / 10) == 1:
                            suf = "th"
                        else:
                            suffix = {1: 'st', 2: 'nd', 3: 'rd'}
                            suffix.get((agee % 10), "th")
                        agee = f"{agee}{suf}"
                    U = await JJK.get_chat_member(chat_id=j, user_id=i["user_id"])
                    if U.user.is_deleted:
                        bday_info.delete_one({"user_id": i["user_id"]})
                        continue
                    wish = choice(birthday_wish)
                    if U.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                        xXx = await JJK.send_message(j, f"Happy {agee} birthday {U.user.mention}🥳\n{wish}")
                        try:
                            await xXx.pin()
                        except Exception:
                            pass
                except Exception:
                    pass


""""
from datetime import date, datetime

#form = 
num = "18/05/2005"
st = "18 May 2005"
timm = datetime.strptime(num,"%d/%m/%Y").date()
x = datetime.now().date()
if timm.month < x.month:
    next_b = date(x.year + 1, timm.month, timm.day)
    days_left = (next_b - x).days
else:
    timmm = date(x.year, timm.month, timm.day)
    days_left = (timmm - x).days
print(days_left)
print(x.year - timm.year)
"""

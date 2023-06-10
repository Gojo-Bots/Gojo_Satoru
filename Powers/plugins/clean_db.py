import time
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
#from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus as CMS

from Powers import LOGGER, MESSAGE_DUMP, TIME_ZONE
from Powers.bot_class import Gojo
from Powers.database.approve_db import Approve
from Powers.database.blacklist_db import Blacklist
from Powers.database.chats_db import Chats
from Powers.database.disable_db import Disabling
from Powers.database.filters_db import Filters
from Powers.database.flood_db import Floods
from Powers.database.greetings_db import Greetings
from Powers.database.notes_db import Notes, NotesSettings
from Powers.database.pins_db import Pins
from Powers.database.reporting_db import Reporting
from Powers.database.users_db import Users
from Powers.database.warns_db import Warns, WarnSettings
from Powers.utils.custom_filters import command
from Powers.vars import Config

scheduler = AsyncIOScheduler()
scheduler.timezone = TIME_ZONE

async def clean_my_db(c:Gojo,is_cmd=False, id=None):
    to_clean = list()
    all_userss = Users.list_users()
    chats_list = Chats.list_chats_by_id()
    to_clean.clear()
    start = time.time()
    for chats in chats_list:
        try:
            stat = await c.get_chat_member(chat_id=chats,user_id=Config.BOT_ID)
            if stat.status not in [CMS.MEMBER, CMS.ADMINISTRATOR, CMS.OWNER]:
                to_clean.append(chats)
        except Exception:
            to_clean.append(chats)
    for i in to_clean:
        Approve(i).clean_approve()
        Blacklist(i).clean_blacklist()
        Chats.remove_chat(i)
        Disabling(i).clean_disable()
        Filters().rm_all_filters(i)
        Floods().rm_flood(i)
        Greetings(i).clean_greetings()
        Notes().rm_all_notes(i)
        NotesSettings().clean_notes(i)
        Pins(i).clean_pins()
        Reporting(i).clean_reporting()
        Warns(i).clean_warn()
        WarnSettings(i).clean_warns()
    x = len(to_clean)
    txt = f"#INFO\n\nCleaned db:\nTotal chats removed: {x}"
    to_clean.clear()
    LOGGER.info("Sleeping for 60 seconds")
    await sleep(60)
    LOGGER.info("Continuing the cleaning process")
    all_users = [i["_id"] for i in all_userss]
    for i in all_users:
        try:
            infos = await c.get_users(int(i))
        except Exception:
            try:
                inn = await c.resolve_peer(int(i))
                infos = await c.get_users(inn.user_id)
            except Exception:
                to_clean.append(i)
                Users(i).delete_user()
        try:
            if infos.is_deleted:
                to_clean.append(infos.id)
                Users(infos.id).delete_user()
            else:
                pass
        except Exception:
            pass
            
    txt += f"\nTotal users removed: {len(to_clean)}"
    to_clean.clear()
    if is_cmd:
        txt += f"\nClean type: Forced\nInitiated by: {(await c.get_users(user_ids=id)).mention}"
        await c.send_message(chat_id=MESSAGE_DUMP,text=txt)
        return txt
    else:
        txt += f"\nClean type: Auto\n\tTook {time.time()-start-60} seconds to complete the process"
        await c.send_message(chat_id=MESSAGE_DUMP,text=txt)
        return
    

scheduler.add_job(clean_my_db,'cron',[Gojo],hour=3,minute=0,second=0)
scheduler.start()
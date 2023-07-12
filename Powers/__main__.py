import uvloop  # Comment it out if using on windows
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Powers import BDB_URI, TIME_ZONE
from Powers.bot_class import Gojo
from Powers.plugins.birthday import send_wishish
from Powers.plugins.clean_db import clean_my_db

scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

if __name__ == "__main__":
    uvloop.install() # Comment it out if using on windows
    Gojo().run()
    scheduler.add_job(clean_my_db,'cron',[Gojo()],hour=3,minute=0,second=0)
    if BDB_URI:
        scheduler.add_job(send_wishish,'cron',[Gojo()],hour=0,minute=0,second=0)
    scheduler.start()

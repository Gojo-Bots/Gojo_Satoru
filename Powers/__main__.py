import uvloop  # Comment it out if using on windows
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Powers import BDB_URI, TIME_ZONE
from Powers.bot_class import Gojo

if __name__ == "__main__":
    uvloop.install() # Comment it out if using on windows
    Gojo().run()
    
    

import os
from platform import system

from Powers import LOGGER
from Powers.bot_class import Gojo

if __name__ == "__main__":
    if system() == "Windows":
        LOGGER.info("Windows system detected thus not installing uvloop")
    else:
        LOGGER.info("Attempting to install uvloop")
        try:
            os.system("pip3 install uvloop")
            import uvloop
            uvloop.install()
            LOGGER.info("Installed uvloop continuing the process")
        except:
            LOGGER.info("Failed to install uvloop continuing the process")
    Gojo().run()

async def all_plugins():
    # This generates a list of plugins in this folder for the * in __main__ to
    # work.

    from glob import glob
    from os.path import basename, dirname, isfile

    mod_paths = glob(dirname(__file__) + "/*.py")
    all_plugs = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return sorted(all_plugs)

from sys import exit as exiter

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from Powers import BDB_URI, LOGGER

if BDB_URI:
    try:
        BIRTHDAY_DB = MongoClient(BDB_URI)
    except PyMongoError as f:
        LOGGER.error(f"Error in Mongodb2: {f}")
        exiter(1)
    Birth_main_db = BIRTHDAY_DB["birthdays"]

    bday_info = Birth_main_db['users_bday']
    bday_cinfo = Birth_main_db["chat_bday"]

from datetime import datetime


def till_date(date):
    form = "%Y-%m-%d %H:%M:%S"
    z = datetime.strptime(date,form)
    return z

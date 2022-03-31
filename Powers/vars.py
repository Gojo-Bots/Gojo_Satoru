from os import getcwd
import os

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

#env_file = f"{getcwd()}/.env"
#config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])



class Config:
    """Config class for variables."""

    LOGGER = True
    BOT_TOKEN = environ.get("BOT_TOKEN", default=None)
    API_ID = int(environ.get("API_ID", default=None))
    API_HASH = environ.get("API_HASH", default=None)
    OWNER_ID = int(environ.get("OWNER_ID", default=1344569458))
    MESSAGE_DUMP = int(environ.get("MESSAGE_DUMP", default=-100))
    DEV_USERS = [int(i) for i in environ.get("DEV_USERS", default="1432756163 1344569458 1355478165 1789859817 1777340882").split(" ")]
    SUDO_USERS = [int(i) for i in environ.get("SUDO_USERS", default="1432756163 1344569458 1355478165 1789859817 1777340882").split(" ")]
    WHITELIST_USERS = [int(i) for i in environ.get("WHITELIST_USERS", default="1432756163 1344569458 1355478165 1789859817 1777340882").split(" ")]
    DB_URI = environ.get("DB_URI", default="")
    DB_NAME = environ.get("DB_NAME", default="Power_robot")
    NO_LOAD = environ.get("NO_LOAD", default="").split()
    PREFIX_HANDLER = environ.get("PREFIX_HANDLER", default="/").split()
    SUPPORT_GROUP = environ.get("SUPPORT_GROUP", default="HellBot_Network")
    SUPPORT_CHANNEL = environ.get("SUPPORT_CHANNEL", default="gojo_updates")
    ENABLED_LOCALES = [str(i) for i in environ.get("ENABLED_LOCALES", default="en").split()]
    VERSION = environ.get("VERSION", default="v2.0")
    WORKERS = int(environ.get("WORKERS", default=16))
    BOT_USERNAME = ""
    BOT_ID = ""
    BOT_NAME = ""


class Development:
    """Development class for variables."""

    # Fill in these vars if you want to use Traditional method of deploying
    LOGGER = True
    BOT_TOKEN = "YOUR BOT_TOKEN"
    API_ID = 12345  # Your APP_ID from Telegram
    API_HASH = "YOUR API HASH"  # Your APP_HASH from Telegram
    OWNER_ID = 1344569458  # Your telegram user id
    MESSAGE_DUMP = -100  # Your Private Group ID for logs
    DEV_USERS = []
    SUDO_USERS = []
    WHITELIST_USERS = []
    DB_URI = "postgres://username:password@postgresdb:5432/database_name"
    DB_NAME = "Power_robot"
    NO_LOAD = []
    PREFIX_HANDLER = ["!", "/"]
    SUPPORT_GROUP = "SUPPORT_GROUP"
    SUPPORT_CHANNEL = "SUPPORT_CHANNEL"
    ENABLED_LOCALES = ["ENABLED_LOCALES"]
    VERSION = "VERSION"
    WORKERS = 8

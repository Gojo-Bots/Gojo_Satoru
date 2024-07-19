from os import getcwd

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Config:
    """Config class for variables."""

    LOGGER = True
    BOT_TOKEN = config("BOT_TOKEN", default="6924002790:AAHaWLtKzjzPBLo6ZovJvBdh6C1I2tLz1d4")
    API_ID = int(config("API_ID", default="24269862"))
    API_HASH = config("API_HASH", default="5b1a646f8c8ed40f15af84c9b2dfa9e8")
    OWNER_ID = int(config("OWNER_ID", default="5154912723"))
    MESSAGE_DUMP = int(config("MESSAGE_DUMP"))
    DEV_USERS = [
        int(i)
        for i in config(
            "DEV_USERS",
            default="",
        ).split("5154912723")
    ]
    SUDO_USERS = [
        int(i)
        for i in config(
            "SUDO_USERS",
            default="",
        ).split(None)
    ]
    WHITELIST_USERS = [
        int(i)
        for i in config(
            "WHITELIST_USERS",
            default="",
        ).split(None)
    ]
    GENIUS_API_TOKEN = config("GENIUS_API",default=None)
    AuDD_API = config("AuDD_API",default=None)
    RMBG_API = config("RMBG_API",default="W6KWsRHiQCxedSEvfSLY2Mex")
    DB_URI = config("DB_URI", default="mongodb+srv://yumlanulmi:hii121itsk@cluster0.gbperk3.mongodb.net/?retryWrites=true&w=majority")
    DB_NAME = config("DB_NAME", default="Management")
    BDB_URI = config("BDB_URI",default=None)
    NO_LOAD = config("NO_LOAD", default="").split()
    PREFIX_HANDLER = config("PREFIX_HANDLER", default="/").split()
    SUPPORT_GROUP = config("SUPPORT_GROUP", default="lundlelobsdkmera")
    SUPPORT_CHANNEL = config("SUPPORT_CHANNEL", default="lundlelobsdk")
    WORKERS = int(config("WORKERS", default=16))
    TIME_ZONE = config("TIME_ZONE",default='Asia/Kolkata')
    BOT_USERNAME = ""
    BOT_ID = ""
    BOT_NAME = ""
    owner_username = ""


class Development:
    """Development class for variables."""

    # Fill in these vars if you want to use Traditional method of deploying
    LOGGER = True
    BOT_TOKEN = "6924002790:AAHaWLtKzjzPBLo6ZovJvBdh6C1I2tLz1d4"
    API_ID = 24269862  # Your APP_ID from Telegram
    API_HASH = "5b1a646f8c8ed40f15af84c9b2dfa9e8"  # Your APP_HASH from Telegram
    OWNER_ID = 5154912723  # Your telegram user id defult to mine
    MESSAGE_DUMP = -1002122149322  # Your Private Group ID for logs
    DEV_USERS = [5154912723]
    SUDO_USERS = []
    WHITELIST_USERS = []
    DB_URI = "mongodb+srv://yumlanulmi:hii121itsk@cluster0.gbperk3.mongodb.net/?retryWrites=true&w=majority
    "  # Your mongo DB URI
    DB_NAME = "Management"  # Your DB name
    NO_LOAD = []
    GENIUS_API_TOKEN = ""
    RMBG_API = "W6KWsRHiQCxedSEvfSLY2Mex"
    PREFIX_HANDLER = ["!", "/","$"]
    SUPPORT_GROUP = "lundlelobsdkmera"
    SUPPORT_CHANNEL = "lundlelobsdk"
    VERSION = "VERSION"
    TIME_ZONE = 'Asia/Kolkata'
    BDB_URI = "mongodb+srv://b7604190:hii121itsk@cluster0.vtt1cxt.mongodb.net/?retryWrites=true&w=majority"
    WORKERS = 8

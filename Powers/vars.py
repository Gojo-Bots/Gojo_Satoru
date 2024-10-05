from os import getcwd

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Config:
    """Config class for variables."""

    LOGGER = True
    BOT_TOKEN = "hajsfhuhj:123455...."
    API_ID = 12345  # Your APP_ID from Telegram
    API_HASH = "asjhfuahf7572hjgkaghdf"  # Your APP_HASH from Telegram
    OWNER_ID = 1344569458  # Your telegram user id defult to mine
    MESSAGE_DUMP = -100845454887  # Your Private Group ID for logs
    DEV_USERS = [123456667]
    SUDO_USERS = [2345123123]
    WHITELIST_USERS = [12314134]
    DB_URI = "mongodb+srv://User:testdb.m14k3kx.mongodb.net/?retryWrites=true&w=majority"  # Your mongo DB URI
    DB_NAME = "MYDB"  # Your DB name
    NO_LOAD = []
    GENIUS_API_TOKEN = "" # Your genius API token or leave it as it is
    RMBG_API = "" # Your rmbg API token or leave it as it is
    PREFIX_HANDLER = ["!", "/","$"]
    SUPPORT_GROUP = "gojo_bots_network" #Username without @
    SUPPORT_CHANNEL = "gojo_bots_network" #Username without @
    VERSION = "VERSION" #Leave it as it is
    TIME_ZONE = 'Asia/Kolkata'
    BDB_URI = "" #If you want your birthday module to work pass mongo db uri u can use same URI but I prefer passing a new one
    WORKERS = 8
    TIME_ZONE = 'Asia/Kolkata'
    BOT_USERNAME = ""
    BOT_ID = ""
    BOT_NAME = ""
    owner_username = ""


class Development:
    """Development class for variables."""

    # Fill in these vars if you want to use Traditional method of deploying
    LOGGER = True
    BOT_TOKEN = "6924002790:AAEDDX81bKuilEc7rMyQROZguCPgWCR_22k"
    API_ID = 24269862  # Your APP_ID from Telegram
    API_HASH = "5b1a646f8c8ed40f15af84c9b2dfa9e8"  # Your APP_HASH from Telegram
    OWNER_ID = 5154912723  # Your telegram user id defult to mine
    MESSAGE_DUMP = -1002052189895  # Your Private Group ID for logs
    DEV_USERS = [5154912723]
    SUDO_USERS = [5154912723]
    WHITELIST_USERS = [5154912723]
    DB_URI = "mongodb+srv://yumlanulmi:hii121itsk@cluster0.gbperk3.mongodb.net/?retryWrites=true&w=majority"  # Your mongo DB URI
    DB_NAME = "Management"  # Your DB name
    NO_LOAD = []
    GENIUS_API_TOKEN = "" # Your genius API token or leave it as it is
    RMBG_API = "mL1mJVeYSgRpQpUoPewHykgh" # Your rmbg API token or leave it as it is
    PREFIX_HANDLER = ["!", "/","$"]
    SUPPORT_GROUP = "NoxBots" #Username without @
    SUPPORT_CHANNEL = "Lundlelobsdkmera" #Username without @
    VERSION = "VERSION" #Leave it as it is
    TIME_ZONE = 'Asia/Kolkata'
    BDB_URI = "mongodb+srv://b7604190:hii121itsk@cluster0.vtt1cxt.mongodb.net/?retryWrites=true&w=majority" #If you want your birthday module to work pass mongo db uri u can use same URI but I prefer passing a new one
    WORKERS = 8

from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    LOGGER = True

    API_ID = int(getenv("API_ID", 6))
    API_HASH = getenv("API_HASH", None)
    ARQ_API_KEY = "PMPTTD-HOMLMF-SRBHNH-RZMWXL-ARQ"
    SPAMWATCH_API = None
    TOKEN = getenv("TOKEN", None)
    OWNER_ID = int(getenv("OWNER_ID", 5938660179))
    OWNER_USERNAME = getenv("OWNER_USERNAME", "AshokShau")
    SUPPORT_CHAT = getenv("SUPPORT_CHAT", "AbishnoiMF")
    LOGGER_ID = int(getenv("LOGGER_ID", "-1001819078701"))
    MONGO_URI = getenv(
        "MONGO_DB_URI",
        "mongodb+srv://public:abishnoimf@cluster0.rqk6ihd.mongodb.net/?retryWrites=true&w=majority",
    )
    DB_NAME = getenv("DB_NAME", "ExonRobot")

class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True

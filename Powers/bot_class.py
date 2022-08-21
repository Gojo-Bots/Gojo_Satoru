from threading import RLock
from Powers.vars import Config
from aiohttp import ClientSession
from pyrogram.raw.all import layer
from Powers.database import MongoDB
from platform import python_version
from Powers.plugins import all_plugins
from time import time, gmtime, strftime
from pyrogram import Client, __version__
from Powers import (
    API_ID, LOGGER, UPTIME, LOGFILE, NO_LOAD, WORKERS, API_HASH, BOT_TOKEN,
    LOG_DATETIME, MESSAGE_DUMP, load_cmds)


INITIAL_LOCK = RLock()

# Check if MESSAGE_DUMP is correct
if MESSAGE_DUMP == -100 or not str(MESSAGE_DUMP).startswith("-100"):
    raise Exception(
        "Please enter a vaild Supergroup ID, A Supergroup ID starts with -100",
    )

aiohttpsession = ClientSession()


class Gojo(Client):
    """Starts the Pyrogram Client on the Bot Token when we do 'python3 -m Powers'"""

    def __init__(self):
        # name = Powers

        super().__init__(
            "Gojo_Satarou",
            bot_token=BOT_TOKEN,
            plugins=dict(root="Powers.plugins", exclude=NO_LOAD),
            api_id=API_ID,
            api_hash=API_HASH,
            workers=WORKERS,
        )

    async def start(self):
        """Start the bot."""
        await super().start()

        meh = await self.get_me()  # Get bot info from pyrogram client
        LOGGER.info("Starting bot...")
        Config.BOT_ID = meh.id
        Config.BOT_NAME = meh.first_name
        Config.BOT_USERNAME = meh.username

        startmsg = await self.send_message(MESSAGE_DUMP, "<i>Starting Bot...</i>")

        # Show in Log that bot has started
        LOGGER.info(
            f"Pyrogram v{__version__} (Layer - {layer}) started on {meh.username}",
        )
        LOGGER.info(f"Python Version: {python_version()}\n")

        # Get cmds and keys
        cmd_list = await load_cmds(await all_plugins())

        LOGGER.info(f"Plugins Loaded: {cmd_list}")

        # Send a message to MESSAGE_DUMP telling that the
        # bot has started and has loaded all plugins!
        await startmsg.edit_text(
            (
                f"<b><i>@{meh.username} started on Pyrogram v{__version__} (Layer - {layer})</i></b>\n"
                f"\n<b>Python:</b> <u>{python_version()}</u>\n"
                "\n<b>Loaded Plugins:</b>\n"
                f"<i>{cmd_list}</i>\n"
            ),
        )

        LOGGER.info("Bot Started Successfully!\n")

    async def stop(self):
        """Stop the bot and send a message to MESSAGE_DUMP telling that the bot has stopped."""
        runtime = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
        LOGGER.info("Uploading logs before stopping...!\n")
        # Send Logs to MESSAGE_DUMP and LOG_CHANNEL
        await self.send_document(
            MESSAGE_DUMP,
            document=LOGFILE,
            caption=(
                "Bot Stopped!\n\n" f"Uptime: {runtime}\n" f"<code>{LOG_DATETIME}</code>"
            ),
        )
        if MESSAGE_DUMP:
            # LOG_CHANNEL is not necessary
            await self.send_document(
                MESSAGE_DUMP,
                document=LOGFILE,
                caption=f"Uptime: {runtime}",
            )
        await super().stop()
        MongoDB.close()
        LOGGER.info(
            f"""Bot Stopped.
            Logs have been uploaded to the MESSAGE_DUMP Group!
            Runtime: {runtime}s\n
        """,
        )

from random import choice
from Powers.vars import Config
from Powers.bot_class import Gojo
from pyrogram import enums, filters
from Powers.utils.kbhelpers import ikb
from Powers import LOGGER, HELP_COMMANDS
from Powers.utils.extras import StartPic
from Powers.utils.chat_type import chattype
from Powers.utils.custom_filters import command
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import UserIsBlocked, QueryIdInvalid, MessageNotModified
from Powers.utils.start_utils import (
    gen_cmds_kb, gen_start_kb, get_help_msg, get_private_note,
    get_private_rules)


@Gojo.on_message(
    command("donate") & (filters.group | filters.private),
)
async def donate(_, m: Message):
    cpt = """
Hey Thanks for your thought of donating me!
When you donate, all the fund goes towards my development which makes on fast and responsive.
Your donation might also me get me a new feature or two, which I wasn't able to get due to server limitations.

All the fund would be put into my services such as database, storage and hosting!

You can donate by contacting my owner: [Captain Ezio](http://t.me/iamgojoof6eyes)
     """

    LOGGER.info(f"{m.from_user.id} fetched donation text in {m.chat.id}")
    await m.reply_photo(photo=choice(StartPic), caption=cpt)
    return


@Gojo.on_callback_query(filters.regex("^close_admin$"))
async def close_admin_callback(_, q: CallbackQuery):
    user_id = q.from_user.id
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
        await q.answer(
            "You're not even an admin, don't try this explosive shit!",
            show_alert=True,
        )
        return
    if user_status != CMS.OWNER:
        await q.answer(
            "You're just an admin, not owner\nStay in your limits!",
            show_alert=True,
        )
        return
    await q.message.edit_text("Closed!")
    await q.answer("Closed menu!", show_alert=True)
    return


@Gojo.on_message(
    command("start") & (filters.group | filters.private),
)
async def start(c: Gojo, m: Message):
    chat_type = await chattype(m)
    if chat_type == "private":
        if len(m.text.split()) > 1:
            help_option = (m.text.split(None, 1)[1]).lower()

            if help_option.startswith("note") and (
                help_option not in ("note", "notes")
            ):
                await get_private_note(c, m, help_option)
                return
            if help_option.startswith("rules"):
                LOGGER.info(f"{m.from_user.id} fetched privaterules in {m.chat.id}")
                await get_private_rules(c, m, help_option)
                return

            help_msg, help_kb = await get_help_msg(m, help_option)

            if not help_msg:
                return

            await m.reply_photo(
                photo=choice(StartPic),
                caption=help_msg,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=ikb(help_kb),
                quote=True,
            )
            return
        try:
            cpt = f"""
Hey [{m.from_user.first_name}](http://t.me/{m.from_user.username})! My self Gojo ✨.
I'm here to help you manage your groups!
Hit /help to find out more about how to use me in my full potential!

Join my [News Channel](https://t.me/gojo_updates) to get information on all the latest updates."""

            await m.reply_photo(
                photo=choice(StartPic),
                caption=cpt,
                reply_markup=(await gen_start_kb(m)),
                quote=True,
            )
        except UserIsBlocked:
            LOGGER.warning(f"Bot blocked by {m.from_user.id}")
    else:
        kb = ikb(
            [
                [
                    (
                        "Connect me to pm",
                        f"https://t.me/{Config.BOT_USERNAME}?start=start",
                        "url",
                    )
                ]
            ]
        )
        await m.reply_photo(
            photo=choice(StartPic),
            caption="I'm alive :3",
            reply_markup=kb,
            quote=True,
        )
    return


@Gojo.on_callback_query(filters.regex("^start_back$"))
async def start_back(_, q: CallbackQuery):
    try:
        cpt = f"""
Hey [{q.from_user.first_name}](http://t.me/{q.from_user.username})! My name is Gojo ✨.
I'm here to help you manage your groups!
Hit /help to find out more about how to use me in my full potential!

Join my [News Channel](http://t.me/gojo_updates) to get information on all the latest updates."""

        await q.edit_message_caption(
            caption=cpt,
            reply_markup=(await gen_start_kb(q.message)),
        )
    except MessageNotModified:
        pass
    await q.answer()
    return


@Gojo.on_callback_query(filters.regex("^commands$"))
async def commands_menu(_, q: CallbackQuery):
    keyboard = ikb(
        [
            *(await gen_cmds_kb(q)),
            [(f"« Back", "start_back")],
        ],
    )
    try:
        cpt = f"""
Hey **[{q.from_user.first_name}](http://t.me/{q.from_user.username})**! My name is Gojo✨.
I'm here to help you manage your groups!
Commands available:
* /start: Start the bot
* /help: Give's you this message."""

        await q.edit_message_caption(
            caption=cpt,
            reply_markup=keyboard,
        )
    except MessageNotModified:
        pass
    except QueryIdInvalid:
        await q.message.reply_photo(
            photo=choice(StartPic), caption=cpt, reply_markup=keyboard
        )

    await q.answer()
    return


@Gojo.on_message(command("help"))
async def help_menu(_, m: Message):
    if len(m.text.split()) >= 2:
        help_option = (m.text.split(None, 1)[1]).lower()
        help_msg, help_kb = await get_help_msg(m, help_option)

        if not help_msg:
            LOGGER.error(f"No help_msg found for help_option - {help_option}!!")
            return

        LOGGER.info(
            f"{m.from_user.id} fetched help for '{help_option}' text in {m.chat.id}",
        )
        chat_type = await chattype(m)
        if chat_type == "private":
            if len(help_msg) >= 1026:
                await m.reply_text(
                    help_msg, parse_mode=enums.ParseMode.MARKDOWN, quote=True
                )
            await m.reply_photo(
                photo=choice(StartPic),
                caption=help_msg,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=ikb(help_kb),
                quote=True,
            )
        else:

            await m.reply_photo(
                photo=choice(StartPic),
                caption=f"Press the button below to get help for <i>{help_option}</i>",
                reply_markup=ikb(
                    [
                        [
                            (
                                "Help",
                                f"t.me/{Config.BOT_USERNAME}?start={help_option}",
                                "url",
                            ),
                        ],
                    ],
                ),
            )
    else:
        chat_type = await chattype(m)
        if chat_type == "private":
            keyboard = ikb(
                [
                    *(await gen_cmds_kb(m)),
                    [("« Back", "start_back")],
                ],
            )
            msg = f"""
Hey **[{m.from_user.first_name}](http://t.me/{m.from_user.username})**!My name is Gojo✨.
I'm here to help you manage your groups!
Commands available:
* /start: Start the bot
* /help: Give's you this message."""
        else:
            keyboard = ikb(
                [[("Help", f"t.me/{Config.BOT_USERNAME}?start=help", "url")]],
            )
            msg = "Contact me in PM to get the list of possible commands."

        await m.reply_photo(
            photo=choice(StartPic),
            caption=msg,
            reply_markup=keyboard,
        )

    return


@Gojo.on_callback_query(filters.regex("^get_mod."))
async def get_module_info(_, q: CallbackQuery):
    module = q.data.split(".", 1)[1]

    help_msg = (f"**{str(module)}:**\n\n" + HELP_COMMANDS[module]["help_msg"],)

    help_kb = HELP_COMMANDS[module]["buttons"] + [
        [("« " + "Back", "commands")],
    ]
    await q.edit_message_caption(
        caption=help_msg,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=ikb(help_kb),
    )
    await q.answer()
    return

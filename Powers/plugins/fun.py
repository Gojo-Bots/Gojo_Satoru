from html import escape
from random import choice

from pyrogram import enums
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.supports import get_support_staff
from Powers.utils import extras
from Powers.utils.custom_filters import command
from Powers.utils.extras import NOWYES as NO
from Powers.utils.extras import YESWNO as YES

DEV_USERS = get_support_staff("dev")

@Gojo.on_message(command("shout"))
async def fun_shout(_, m: Message):
    if len(m.text.split()) == 1:
        await m.reply_text(
            text="Please check help on how to use this this command.",
            quote=True,
        )
        return
    try:
        text = " ".join(m.text.split(None, 1)[1])
        result = [" ".join(list(text))]
        for pos, symbol in enumerate(text[1:]):
            result.append(symbol + " " + "  " * pos + symbol)
        result = list("\n".join(result))
        result[0] = text[0]
        result = "".join(result)
        msg = "```\n" + result + "```"
        await m.reply_text(msg, parse_mode=enums.ParseMode.MARKDOWN)
        LOGGER.info(f"{m.from_user.id} shouted in {m.chat.id}")
        return
    except MessageTooLong as e:
        await m.reply_text(f"Error: {e}")
        return


@Gojo.on_message(command("runs"))
async def fun_run(_, m: Message):
    await m.reply_text(choice(extras.RUN_STRINGS))
    LOGGER.info(f"{m.from_user.id} runed in {m.chat.id}")
    return


@Gojo.on_message(command("slap"))
async def fun_slap(c: Gojo, m: Message):
    me = await c.get_me()

    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text

    curr_user = escape(m.from_user.first_name)
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user
    user_id = user.id
    
    if user_id == me.id:
        temp = choice(extras.SLAP_GOJO_TEMPLATES)
    else:
        temp = choice(extras.SLAP_TEMPLATES)

    if user_id != m.from_user.id:
        user1 = curr_user
        user2 = user.first_name
        
    else:
        user1 = me.first_name
        user2 = curr_user

    item = choice(extras.ITEMS)
    hit = choice(extras.HIT)
    throw = choice(extras.THROW)

    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)
    await reply_text(reply)
    LOGGER.info(f"{m.from_user.id} slaped in {m.chat.id}")
    return


@Gojo.on_message(command("roll"))
async def fun_roll(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(choice(range(1, 7)))
    LOGGER.info(f"{m.from_user.id} roll in {m.chat.id}")
    return


@Gojo.on_message(command("toss"))
async def fun_toss(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(choice(extras.TOSS))
    LOGGER.info(f"{m.from_user.id} tossed in {m.chat.id}")
    return


@Gojo.on_message(command("insult"))
async def insult(c: Gojo, m: Message):
    if not m.reply_to_message:
        await m.reply_text("You want to insult yourself such a foolish person.\nYou are not even worth insulting")
        return
    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name
    if user_id in DEV_USERS:
        await m.reply_text("Sorry! I can't insult my devs....")
        return LOGGER.info(
            f"{m.from_user.id} tried to insult {user_first_name} in {m.chat.id}"
        )
    else:
        Insult_omp = choice(extras.INSULT_STRINGS)
        await m.reply_to_message.reply_text(Insult_omp)
        LOGGER.info(f"{m.from_user.id} insulted {user_first_name} in {m.chat.id}")


@Gojo.on_message(command("yes"))
async def yesw(c: Gojo, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    rtext = YES[0]
    await reply_text(rtext)
    LOGGER.info(f"{m.from_user.id} said YES or may be NO in {m.chat.id}")
    return


@Gojo.on_message(command("no"))
async def now(c: Gojo, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    rtext = NO[0]
    await reply_text(rtext)
    LOGGER.info(f"{m.from_user.id} said NO or may be YES in {m.chat.id}")
    return


@Gojo.on_message(command("shrug"))
async def fun_shrug(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(r"¯\_(ツ)_/¯")
    LOGGER.info(f"{m.from_user.id} shruged in {m.chat.id}")
    return


@Gojo.on_message(command("bluetext"))
async def fun_bluetext(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(
        "|| /BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS ||",
    )
    LOGGER.info(f"{m.from_user.id} bluetexted in {m.chat.id}")
    return


@Gojo.on_message(command("decide"))
async def fun_decide(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(choice(extras.DECIDE))
    LOGGER.info(f"{m.from_user.id} decided in {m.chat.id}")
    return


@Gojo.on_message(command("react"))
async def fun_table(_, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(choice(extras.REACTIONS))
    LOGGER.info(f"{m.from_user.id} reacted in {m.chat.id}")
    return


@Gojo.on_message(command("weebify"))
async def weebify(_, m: Message):
    if len(m.text.split()) >= 2:
        args = m.text.split(None, 1)[1]
    elif m.reply_to_message and len(m.text.split()) == 1:
        args = m.reply_to_message.text
    else:
        await m.reply_text(
            "Please reply to a message or enter text after command to weebify it.",
        )
        return
    if not args:
        await m.reply_text(text="What am I supposed to Weebify?")
        return

    # Use split to convert to list
    # Not using list itself becuase black changes it to long format...
    normiefont = "a b c d e f g h i j k l m n o p q r s t u v w x y z".split()
    weebyfont = "卂 乃 匚 刀 乇 下 厶 卄 工 丁 长 乚 从 𠘨 口 尸 㔿 尺 丂 丅 凵 リ 山 乂 丫 乙".split()

    string = "  ".join(args).lower()
    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)

    await m.reply_text(
        text=f"""<b>Weebified String:</b>
        <code>{string}</code>"""
    )
    LOGGER.info(f"{m.from_user.id} weebified '{args}' in {m.chat.id}")
    return


__PLUGIN__ = "fun"

_DISABLE_CMDS_ = [
    "weebify",
    "decide",
    "react",
    "bluetext",
    "toss",
    "yes",
    "no",
    "roll",
    "slap",
    "runs",
    "shout",
    "insult",
    "shrug",
]

__HELP__ = """
**Fun**

• /runs: reply a random string from an array of replies.
• /slap: slap a user, or get slapped if not a reply.
• /insult: to insult a user, or get insulted if not a reply
• /shrug : get shrug XD.
• /decide : Randomly answers yes/no/maybe
• /toss : Tosses A coin
• /yes : check urself :V
• /no : check urself :V
• /bluetext : check urself :V
• /roll : Roll a dice.
• /react : Random Reaction
• /shout `<keyword>`: write anything you want to give loud shout."""

from datetime import date, datetime
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import BDB_URI, LOGGER, TIME_ZONE
from Powers.bot_class import Gojo
from Powers.database.chats_db import Chats

if BDB_URI:
    from Powers.plugins import bday_cinfo, bday_info

from Powers.utils.custom_filters import command


def give_date(date,form = "%d/%m/%Y"):
    datee = datetime.strptime(date,form).date()
    return datee

@Gojo.on_message(command("remember"))
async def remember_me(c: Gojo, m: Message):
    if not BDB_URI:
        await m.reply_text("BDB_URI is not configured")
        return
    splited = m.text.split()
    if len(splited) == 1:
        await m.reply_text("**USAGE**:\n/remember [username or user id or reply to user] [DOB]\nDOB should be in format of dd/mm/yyyy\nYear is optional it is not necessary to pass it")
        return
    if len(splited) != 2 and m.reply_to_message:
        await m.reply_text("**USAGE**:\n/remember [username or user id or reply to user] [DOB]\nDOB should be in format of dd/mm/yyyy\nYear is optional it is not necessary to pass it")
        return
    DOB = splited[1] if len(splited) == 2 else splited[2]
    if len(splited) == 2 and m.reply_to_message:
        user = m.reply_to_message.from_user.id
    elif not m.reply_to_message:
        user = m.from_user.id
    else:
        try:
            u_id = int(splited[1])
        except ValueError:
            pass
        try:
            user = await c.get_users(u_id)
        except Exception:
            u_u = await c.resolve_peer(u_id)
            try:
                user = (await c.get_users(u_u.user_id)).id
            except KeyError:
                await m.reply_text("Unable to find the user")
                return
    DOB = DOB.split("/")
    if len(DOB) != 3 and len(DOB) != 2:
        await m.reply_text("DOB should be in format of dd/mm/yyyy\nYear is optional it is not necessary to pass it")
        return
    is_correct = False
    if len(DOB) == 3:
        is_correct = (len(DOB[2]) == 4)
    if len(DOB[0]) != 2 and len(DOB[1]) !=2 and not is_correct:
        await m.reply_text("DOB should be in format of dd/mm/yyyy\nYear is optional it is not necessary to pass it")
        return
    try:
        date = int(DOB[0])
        month = int(DOB[1])
        if is_correct:
            year = int(DOB[2])
            is_year = 1
        else:
            year = "1900"
            is_year = 0
        DOB = f"{str(date)}/{str(month)}/{str(year)}"
    except ValueError:
        await m.reply_text("DOB should be numbers only")
        return

    data = {"user_id":user,"dob":DOB,"is_year":is_year}
    try:
        result = bday_info.find_one({"user_id":user})
        if result:
            await m.reply_text("User is already in my database")
            return
    except Exception as e:
        await m.reply_text(f"Got an error\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return
    try:
        bday_info.insert_one(data)
        await m.reply_text("Your birthday is now registered in my database")
    except Exception as e:
        await m.reply_text(f"Got an error\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

@Gojo.on_message(command(["removebday","rmbday"]))
async def who_are_you_again(c: Gojo, m: Message):
    if not BDB_URI:
        await m.reply_text("BDB_URI is not configured")
        return
    user = m.from_user.id
    try:
        result = bday_info.find_one({"user_id":user})
        if not result:
            await m.reply_text("User is not in my database")
            return
        elif result:
            bday_info.delete_one({"user_id":user})
            await m.reply_text("Removed your birthday")
            return
    except Exception as e:
        await m.reply_text(f"Got an error\n{e}")
        return

@Gojo.on_message(command(["nextbdays","nbdays","birthdays","bdays"]))
async def who_is_next(c: Gojo, m: Message):
    if not BDB_URI:
        await m.reply_text("BDB_URI is not configured")
        return
    blist = list(bday_info.find())
    if m.chat.type == ChatType.PRIVATE:
        await m.reply_text("Use it in group")
        return
    curr = datetime.now(TIME_ZONE).date()
    xx = await m.reply_text("📆")
    users = []
    if blist:
        for i in blist:
            if Chats(m.chat.id).user_is_in_chat(i["user_id"]):
                dob = give_date(i["dob"])
                if dob.month >= curr.month:
                    if (dob.month == curr.month and not dob.day < curr.day) or dob.month >= curr.month:
                        users.append(i)         
                elif dob.month < curr.month:
                    pass
            if len(users) == 10:
                break
    if not users:
        await xx.delete()
        await m.reply_text("There are no upcoming birthdays of any user in this chat:/\nEither all the birthdays are passed or no user from this chat have registered their birthday")
        return
    txt = "🎊 Upcomming Birthdays Are 🎊\n"
    for i in users:
        DOB = give_date(i["dob"])
        dete = date(curr.year, DOB.month, DOB.day)
        leff = (dete - curr).days
        txt += f"`{i['user_id']}` : {leff} days left"
    txt += "\n\nYou can use /info [user id] to get info about the user"
    await xx.delete()
    await m.reply_text(txt)
    return

@Gojo.on_message(command(["getbday","gbday","mybirthday","mybday"]))
async def cant_recall_it(c: Gojo, m: Message):
    if not BDB_URI:
        await m.reply_text("BDB_URI is not configured")
        return
    user = m.from_user.id
    men = m.from_user.mention
    if m.reply_to_message:
        user = m.reply_to_message.from_user.id
        men = m.reply_to_message.from_user.mention
    try:
        result = bday_info.find_one({"user_id":user})
        if not result:
            await m.reply_text("User is not in my database")
            return
    except Exception as e:
        await m.reply_text(f"Got an error\n{e}")
        return
    
    curr = datetime.now(TIME_ZONE).date() 
    u_dob = give_date(result["dob"])
    formatted = str(u_dob.strftime('%d' + '%B %Y'))[2:-5]
    day = int(result["dob"].split('/')[0])
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day if day < 20 else day % 10, 'th')
    bday_on = f"{day}{suffix} {formatted}"
    if u_dob.month < curr.month:
        next_b = date(curr.year + 1, u_dob.month, u_dob.day)
        days_left = (next_b - curr).days
        txt = f"{men} 's birthday is passed 🫤\nDays left until next one {days_left}"
        txt += f"\nBirthday on: {bday_on}"
        txt += f"\n\nDate of birth: {result['dob']}"
    else:
        u_dobm = date(curr.year, u_dob.month, u_dob.day)
        days_left = (u_dobm - curr).days
        txt = f"User's birthday is coming🥳\nDays left : {days_left}"
        txt += f"\nBirthday on: {bday_on}"
        txt += f"\n\nDate of birth: {result['dob']}"
    txt+= "\n\n**NOTE**:\nDOB may be wrong if user haven't entered his/her birth year"
    await m.reply_text(txt)
    return

@Gojo.on_message(command(["settingbday","sbday"]))
async def chat_birthday_settings(c: Gojo, m: Message):
    if not BDB_URI:
        await m.reply_text("BDB_URI is not configured")
        return
    if m.chat.type == ChatType.PRIVATE:
        await m.reply_text("Use in groups")
        return
    chats = m.chat.id
    c_in = bday_cinfo.find_one({"chat_id":chats})
    kb = IKM(
        [
            [
                IKB(f"{'Yes' if not c_in else 'No'}",f"switchh_{'yes' if not c_in else 'no'}"),
                IKB("Close", "f_close")
            ]
        ]
    )
    await m.reply_text("Do you want to wish members for their birthday in the group?",reply_markup=kb)
    return

@Gojo.on_callback_query(filters.regex("^switchh_"))
async def switch_on_off(c:Gojo, q: CallbackQuery):
    user = (await q.message.chat.get_member(q.from_user.id)).status
    await q.message.chat.get_member(q.from_user.id)
    if user not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await q.answer("...")
        return
    data = q.data.split("_")[1]
    chats = q.message.chat.id
    xXx = {"chat_id":chats}
    if data == "yes":
        bday_cinfo.delete_one(xXx)
    elif data == "no":
        bday_cinfo.insert_one(xXx)
    await q.edit_message_text(f"Done! I will {'wish' if data == 'yes' else 'not wish'}",reply_markup=IKM([[IKB("Close", "f_close")]]))
    return



__PLUGIN__ = "birthday"

__HELP__ = """
• /remember [reply to user] [DOB] : To registers user date of birth in my database. If not replied to user then the DOB givien will be treated as yours
• /nextbdays (/nbdays,/brithdays,/bdays) : Return upcoming birthdays of 10 users
• /removebday (/rmbday) : To remove birthday from database (One can only remove their data from database not of others)
• /settingbday (/sbday) : To configure the settings for wishing and all for the chat
• /getbday (/gbday,/mybirthday,/mybday) [reply to user] : If replied to user get the replied user's birthday else returns your birthday

DOB should be in format of dd/mm/yyyy
Year is optional it is not necessary to pass it
"""

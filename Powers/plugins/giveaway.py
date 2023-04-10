import os
from asyncio import sleep
from datetime import datetime, timedelta
from random import choice
from traceback import format_exc

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType as CT
from pyrogram.enums import MessageMediaType as MMT
from pyrogram.errors import UserNotParticipant
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.database.giveaway_db import GIVEAWAY
from Powers.utils.custom_filters import command
from Powers.vars import Config

user_entry = {} # {c_id :  {participants_id : 0}}} dict be like
voted_user = {} # {c_id : [voter_ids]}} dict be like
total_entries = {} # {c_id : [user_id]} dict be like for participants
left_deduct = {} # {c_id:{u_id:p_id}} u_id = user who have voted, p_id = participant id. Will deduct vote from participants account if user leaves
rejoin_try = {} # store the id of the user who lefts the chat while giveaway under-process {c_id:[]}
is_start_vote = [] # store id of chat where voting is started

@Gojo.on_message(command(["startgiveaway", "startga"]))
async def start_give_one(c: Gojo, m: Message):
    uWu = True
    try:
        if m.chat.type != CT.PRIVATE:
            await m.reply_text("**USAGE**\n/startgiveaway\nMeant to be used in private")
            return
        GA = GIVEAWAY()
        g_id = await c.ask(text="Send me number of giveaway", chat_id = m.chat.id, filters=filters.text)
        give_id = g_id.text.markdown
        curr = GA.give_info(u_id=m.from_user.id)
        if curr:
            gc_id = curr["chat_id"]
            c_id = curr["where"]
            if curr["is_give"]:
                await m.reply_text("One giveaway is already in progress")
                return
            while True:
                con = await c.ask(text="You info is already present in my database do you want to continue\nYes : To start the giveaway with previous configurations\nNo: To create one",chat_id = m.chat.id,filters=filters.text)
                if con.text.lower() == "/cancel":
                    await m.reply_text("cancelled")
                    return
                if con.text.lower() == "yes":
                    await c.send_message(m.chat.id,"Done")
                    while True:
                        yes_no = await c.ask(text="Ok.\nDo you want to allow old member of the channel can vote in this giveaway.\n**Yes: To allow**\n**No: To don't allow**\nNote that old mean user who is present in the chat for more than 48 hours",chat_id = m.from_user.id,filters=filters.text)
                        if yes_no.text.lower() == "/cancel":
                            await m.reply_text("cancelled")
                            return
                        if yes_no.text.lower() == "yes":
                            is_old = 0
                            break
                        elif yes_no.text.lower() == "no":
                            is_old = 1
                            break
                        else:
                            await c.send_message(m.chat.id,"Type yes or no only")
                    f_c_id = gc_id
                    s_c_id = c_id
                    is_old = is_old
                    GA.update_is_old(m.from_user.id, is_old)
                    GA.stop_entries(m.from_user.id, entries = 1) # To start entries
                    GA.stop_give(m.from_user.id, is_give=1) # To start giveaway
                    link = await c.export_chat_invite_link(s_c_id)
                    uWu = False
                    await c.send_message(m.chat.id,"Done")
                    break
                elif con.text.lower() == "no":
                    uWu = True
                    break
                else:
                    await c.send_message(m.chat.id,"Type yes or no only")
        if uWu:
            while True:
                channel_id = await c.ask(text="OK....send me id of the channel and make sure I am admin their. If you don't have id forward a post from your chat.\nType /cancel cancel the current process",chat_id = m.chat.id,filters=filters.text)
                if channel_id.text:
                    if str(channel_id.text).lower() == "/cancel":        
                        await c.send_message(m.from_user.id, "Cancelled")
                        return
                    try:
                        c_id = int(channel_id.text)
                        try:
                            bot_stat = (await c.get_chat_member(c_id,Config.BOT_ID)).status
                            if bot_stat in [CMS.ADMINISTRATOR,CMS.OWNER]:
                                break
                            else:
                                await c.send_message(m.chat.id,f"Looks like I don't have admin privileges in the chat {c_id}\n Make me admin and then send me channel id again")
                        except UserNotParticipant:
                            await c.send_message(m.chat.id,f"Looks like I am not part of the chat {c_id}\n")
                        
                                
                    except ValueError:
                        await c.send_message(m.chat.id,"Channel id should be integer type")
                    
                else:
                    if channel_id.forward_from_chat:
                        try:
                            bot_stat = (await c.get_chat_member(c_id,Config.BOT_ID)).status
                            if bot_stat in [CMS.ADMINISTRATOR,CMS.OWNER]:
                                break
                            else:
                                await c.send_message(m.chat.id,f"Looks like I don't have admin privileges in the chat {c_id}\n Make me admin and then send me channel id again")
                        except UserNotParticipant:
                            await c.send_message(m.chat.id,f"Looks like I am not part of the chat {c_id}\n")
                    else:
                        await c.send_message(m.chat.id,f"Forward me content from chat where you want to start giveaway")
            f_c_id = c_id 
            await c.send_message(m.chat.id,"Channel id received")
            while True:
                chat_id = await c.ask(text="Sende me id of the chat and make sure I am admin their. If you don't have id go in the chat and type /id.\nType /cancel to cancel the current process",chat_id = m.chat.id,filters=filters.text)
                if chat_id.text:
                    if str(chat_id.text).lower() == "/cancel":
                        await c.send_message(m.from_user.id, "Cancelled")
                        return
                    try:
                        cc_id = int(chat_id.text)               
                        try:
                            cc_id = (await c.get_chat(cc_id)).id
                            s_c_id = cc_id
                            break
                        except Exception:
                            try:
                                cc_id = await c.resolve_peer(cc_id)
                                cc_id = (await c.get_chat(cc_id.channel_id)).id
                                s_c_id = cc_id
                                break
                            except Exception as e:
                                await c.send_message(m.chat.id,f"Looks like chat doesn't exist{e}")
                    except ValueError:
                        await c.send_message(m.chat.id,"Chat id should be integer type")
                    try:
                        bot_stat = (await c.get_chat_member(s_c_id,Config.BOT_ID)).status
                        if bot_stat in [CMS.ADMINISTRATOR,CMS.OWNER]:
                            break
                        else:
                            await c.send_message(m.chat.id,f"Looks like I don't have admin privileges in the chat {s_c_id}\n Make me admin and then send me channel id again")
                    except UserNotParticipant:
                        await c.send_message(m.chat.id,f"Looks like I am not part of the chat {s_c_id}\n")
                
            await c.send_message(m.chat.id,"Chat id received")
                
            link = await c.export_chat_invite_link(cc_id)

            yes_no = await c.ask(text="Do you want to allow old member of the channel can vote in this giveaway.\n**Yes: To allow**\n**No: To don't allow**\nNote that old mean user who is present in the chat for more than 48 hours",chat_id = m.from_user.id,filters=filters.text)
            if yes_no.text.lower() == "yes":
                is_old = 0
            elif yes_no.text.lower() == "no":
                is_old = 1
            curr = GA.save_give(f_c_id, s_c_id, m.from_user.id, is_old, force_c=True)               
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return   

    reply = m.reply_to_message
    giveaway_text = f"""
**#Giveaway {give_id} 》**
➖➖➖➖➖➖➖➖➖➖➖
__To win this logo giveaway__
__participate in the contest__,
__Comment /enter to begin__

Bot should be started!!
➖➖➖➖➖➖➖➖➖➖➖
**Status : Entries open**
"""

    kb = IKM([[IKB("Join the chat", url=link)],[IKB("Start the bot", url=f"https://{Config.BOT_USERNAME}.t.me/")]])
    try:
        if reply and (reply.media in [MMT.VIDEO, MMT.PHOTO] or (reply.document.mime_type.split("/")[0]=="image")):
            if reply.photo:
                pin = await c.send_photo(f_c_id, reply.photo.file_id, giveaway_text, reply_markup=kb)
            elif reply.video:
                pin = await c.send_video(f_c_id, reply.video.file_id, giveaway_text, reply_markup=kb)
            elif reply.document:
                download = await reply.download()
                pin = await c.send_photo(f_c_id, download, giveaway_text, reply_markup=kb)
                os.remove(download)
        else:
            pin = await c.send_message(f_c_id,giveaway_text, reply_markup=kb, disable_web_page_preview=True)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        await m.reply_text(f"Failed to send message to channel due to\n{e}")
        return
    c_in = await c.get_chat(f_c_id)
    name = c_in.title
    await m.reply_text(f"✨ Giveaway post has been sent to [{name}]({c_in.invite_link})", disable_web_page_preview=True, reply_markup=IKM([[IKB("Go To Post", url=pin.link)]]))


async def message_editor(c:Gojo, m: Message, c_id):
    txt = f"""
**#Giveaway 》**
➖➖➖➖➖➖➖➖➖➖➖
__To win this logo giveaway__
__participate in the contest__,
__Comment /enter to begin__

Note: Bot should be started!!
➖➖➖➖➖➖➖➖➖➖➖
**Status : Entries closed**
**Total entries : {len(total_entries[c_id])}**
"""
    try:
        m_id = int(m.text.split(None)[1].split("/")[-1])
    except ValueError:
        await m.reply_text("The link doesn't contain any message id")
        return False
    try:
        mess = await c.get_messages(c_id,m_id)
    except Exception as e:
        await m.reply_text(f"Failed to get message form the chat id {c_id}. Due to following error\n{e}")
        return False
    try:
        if mess.caption:    
            await mess.edit_caption(txt)
        else:
            await mess.edit_text(txt)
        return True
    except Exception as e:
        await m.reply_text(f"Failed to update the message due to following error\n{e}")
        await m.reply_text(f"Here is the text you can edit the message by your self\n`{txt}`\nSorry for inconvenience")
        return False

        
@Gojo.on_message(command("stopentry"))
async def stop_give_entry(c:Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id
    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("You have not started any giveaway yeat.")
        return
    if not curr["entries"]:
        await m.reply_text("You have not started any giveaway yeat.")
        return
    user = curr["user_id"]
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    c_id = curr["chat_id"]
    if len(m.text.split(None)) != 2:
        await m.reply_text("**Usage**\n`/stopentry <post link>`")
        return
    GA.stop_entries(u_id)
    z = await message_editor(c,m,c_id)
    if not z:
        return
    await m.reply_text("Stopped the further entries")
    return

def clean_values(c_id):
    try:
        rejoin_try[c_id].clear()
    except KeyError:
        pass
    try:
        user_entry[c_id].clear()
    except KeyError:
        pass
    try:
        left_deduct[c_id].clear()
    except KeyError:
        pass
    try:
        total_entries[c_id].clear()
    except KeyError:
        pass
    try:    
        is_start_vote.remove(c_id)   
    except ValueError:
        pass
    try:
        voted_user[c_id].clear()
    except KeyError:
        pass
    return

@Gojo.on_message(command(["stopgiveaway","stopga"]))
async def stop_give_away(c:Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id
    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("You have not started any giveaway yet")
        return
    if not curr["is_give"]:
        await m.reply_text("You have not started any giveaway yet")
        return
    user = curr["user_id"]
    c_id = curr["chat_id"]
    
    GA.stop_entries(u_id)
    GA.start_vote(u_id,0)
    try:
        if not len(total_entries[c_id]):
            await m.reply_text("No entires found")
            GA.stop_give(u_id)
            clean_values(c_id)
            await m.reply_text("Stopped the giveaway")
            return
    except KeyError:
        await m.reply_text("No entires found")
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("Stopped the giveaway")
        return
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    try:
        if not len(user_entry[c_id]):
            await m.reply_text("No entries found")
            GA.stop_give(u_id)
            clean_values(c_id)
            await m.reply_text("Stopped the giveaway")
            return
    except KeyError:
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("Stopped the giveaway")
        return
    GA.stop_give(u_id)
    try:
        if not len(voted_user[c_id]):
            clean_values(c_id)
            await m.reply_text("No voters found")
            GA.stop_give(u_id)
            await m.reply_text("Stopped the giveaway")
            return
    except KeyError:
        GA.stop_give(u_id)
        clean_values(c_id)
        await m.reply_text("Stopped the giveaway")
        return
    # highest = max(user_entry[c_id], key=lambda k:user_entry[c_id][k])
    # high = user_entry[c_id][highest]
    max_value = max(user_entry[c_id].values())
    max_user = []
    for k,v in user_entry[c_id].items():
        if v == max_value:
            max_user.append(k)
    if len(max_user) == 1:
        
        high = max_value
        user_high = (await c.get_users(max_user[0])).mention
        txt = f"""
**Giveaway complete** ✅
➖➖➖➖➖➖➖➖➖➖➖
≡ Total participants: {len(total_entries[c_id])}
≡ Total number of votes: {len(voted_user[c_id])}

≡ Winner 🏆 : {user_high}
≡ Vote got 🗳 : `{high}` votes
➖➖➖➖➖➖➖➖➖➖➖
>>>Thanks for participating
"""
    else:
        to_key = ["Jai hind", "Jai Jawaan","Jai Bharat", "Jai shree ram", "Jai shree shyam", "Jai shree Krishn", "Jai shree radhe", "Radhe radhe", "Sambhu", "Jai mata di", "Jai mahakaal", "Jai bajarangbali"]
        key = choice(to_key)
        high = max_value
        user_h = [i.mention for i in await c.get_users(max_user)]
        txt = f"""
**Giveaway complete** ✅
➖➖➖➖➖➖➖➖➖➖➖
≡ Total participants: {len(total_entries[c_id])}
≡ Total number of votes: {len(voted_user[c_id])}

≡ It's a tie between following users:
{", ".join(user_h)}
≡ They each got 🗳 : `{high}` votes
➖➖➖➖➖➖➖➖➖➖➖
>>>Thanks for participating

The user who will comment the code will win
Code: `{key}`
"""
    await c.send_message(c_id, txt)
    clean_values(c_id)
    await m.reply_text("Stopped giveaway")

@Gojo.on_message(command("startvote"))
async def start_the_vote(c: Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id
    curr = GA.give_info(u_id=m.from_user.id)
    if not curr:
        await m.reply_text("You have not started any giveaway yet")
        return
    if not curr["is_give"]:
        await m.reply_text("You have not started any giveaway yet")
        return
    c_id = curr["chat_id"]
    user = curr["user_id"]
    if len(is_start_vote):
        if m.chat.id in is_start_vote:
            await m.reply_text("Voting is already started for this chat")
            return
    if len(m.text.split(None)) == 2:
        await message_editor(c,m,c_id)
    else:
        await m.reply_text("No message link provided to update status to closed")
    GA.stop_entries(u_id)
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    try:
        if not len(total_entries[c_id]):
            clean_values(c_id)
            await m.reply_text("No entires found")
            return
    except KeyError:
        clean_values(c_id)
        await m.reply_text("No entires found")
        return
    users = await c.get_users(total_entries[c_id])
    c_link = await c.export_chat_invite_link(c_id)
    for user in users:
        u_id = user.id
        full_name = user.first_name
        if user.last_name and user.first_name:
            full_name = user.first_name +" "+ user.last_name
        u_name = user.username if user.username else user.mention
        txt = f"""
**Participant's info:** 🔍  》
➖➖➖➖➖➖➖➖➖➖➖
≡ Participant's name : {full_name}
≡ Participant's ID : `{u_id}`
≡ Participant's {'username' if user.username else "mention"} : {'@'if user.username else ""}{u_name}
➖➖➖➖➖➖➖➖➖➖➖
>>>Thanks for participating
"""     
        if not len(user_entry):
            user_entry[c_id] = {u_id:0}
        else:
            try:
                user_entry[c_id][u_id] = 0
            except KeyError:
                user_entry[c_id] = {u_id:0}
        vote_kb = IKM([[IKB("❤️", f"vote_{c_id}_{u_id}")]])
        um = await c.send_message(c_id, txt, reply_markup=vote_kb)
        if m.chat.username and not c_link:
            c_link = f"https://t.me/{m.chat.username}"
        join_channel_kb = IKM([[IKB("Giveaway Channel", url=c_link)]])
        txt_ib = f"Voting has been started 》\n\n>>>Here is your vote link :\nHere is your vote message link {um.link}.\n\n**Things to keep in mind**\n■ If user lefts the chat after voting your vote count will be deducted.\n■ If an user left and rejoins the chat he will not be able to vote.\n■ If an user is not part of the chat then he'll not be able to vote"
        await c.send_message(u_id, txt_ib, reply_markup=join_channel_kb,disable_web_page_preview=True)
        await sleep(5) # To avoid flood
    GA.start_vote(u_id)
    is_start_vote.append(c_id)
    await m.reply_text("Started the voting")
    return


@Gojo.on_message(command(["enter","register","participate"]))
async def register_user(c: Gojo, m: Message):
    GA = GIVEAWAY()
    curr = GA.is_vote(m.chat.id)
    if not curr:
        await m.reply_text("No giveaway to participate in.\nOr may be entries are closed now")
        return
    curr = GA.give_info(m.chat.id)
    if not curr["is_give"]:
        await m.reply_text("No giveaway to participate in. Wait for the next one")
        return
    elif not curr["entries"]:
        await m.reply_text("You are late,\nentries are closed 🫤\nTry again in next giveaway")
        return
    c_id = curr["chat_id"]
    if len(total_entries):
        try:
            if m.from_user.id in total_entries[c_id]:
                await m.reply_text("You are already registered")
                return
        except KeyError:
            pass
    try:
        await c.send_message(m.from_user.id, "Thanks for participating in the giveaway")
    except Exception:
        await m.reply_text("Start the bot first\nAnd try again",reply_markup=IKM([[IKB("Star the bot", url=f"https://{Config.BOT_USERNAME}.t.me/")]]))
        return
    curr = GA.give_info(m.chat.id)
    c_id = curr["chat_id"]
    if not len(total_entries):
        total_entries[c_id] = [m.from_user.id]
    else:
        try:
            if m.from_user.id not in total_entries[c_id]:
                total_entries[c_id].append(m.from_user.id)
            else:
                pass
        except KeyError:
            total_entries[c_id] = [m.from_user.id]
    await m.reply_text("You are registered successfully\n**Don't block the bot because you are going to get info about giveaway via bot**")
    return

def get_curr_votes(p_id,c_id):
    votess = []
    if votess:
        votess.clear()
    if not len(left_deduct[c_id]):
        votes = 0
        return 0
    for i,j in left_deduct[c_id].items():
        if j == p_id:
            votess.append(i)
    votes = len(votess)
    return votes

@Gojo.on_callback_query(filters.regex("^vote_"))
async def vote_increment(c: Gojo, q: CallbackQuery):
    GA = GIVEAWAY()
    data = q.data.split("_")
    c_id = int(data[1])
    u_id = int(data[2])
    curr = GA.give_info(c_id)
    if not curr["is_give"]:
        await q.answer("Voting is closed")
        return
    if not curr:
        return
    if len(rejoin_try):
        try:
            if q.from_user.id in rejoin_try[c_id]:
                await q.answer("You can't vote. Because your rejoined the chat during giveaway")
                return
        except KeyError:
            pass
    is_old = curr["is_new"]
    can_old = False
    if is_old:
        can_old = datetime.now() - timedelta(days=2)
    try:
        is_part = await c.get_chat_member(c_id,q.from_user.id)
    except UserNotParticipant:
        await q.answer("Join the channel to vote", True)
        return
    if is_part.status not in [CMS.MEMBER, CMS.OWNER, CMS.ADMINISTRATOR]:
        await q.answer("Join the channel to vote", True)
        return
    if can_old and can_old < is_part.joined_date:
        await q.answer("Old member can't vote", True)
        return
    if not len(voted_user):
        voted_user[c_id] = [q.from_user.id]
    elif len(voted_user):
        try:
            if q.from_user.id in voted_user[c_id]:
                await q.answer("You have already voted once", True)
                return
            voted_user[c_id].append(q.from_user.id)
        except KeyError:
            voted_user[c_id] = [q.from_user.id]
    try:
        left_deduct[c_id][q.from_user.id] = u_id
    except KeyError:
        left_deduct[c_id] = {q.from_user.id:u_id}
    votes = get_curr_votes(u_id,c_id)
    try:
        user_entry[c_id][u_id] += 1
        new_vote = IKM([[IKB(f"❤️ {votes}", f"vote_{c_id}_{u_id}")]])
        await q.answer("Voted.")
        await q.edit_message_reply_markup(new_vote)
    except KeyError:
        await q.answer("Voting has been closed for this giveaway",True)
        return
    except Exception as e:  
        LOGGER.error(e)
        LOGGER.error(format_exc())


@Gojo.on_message(filters.left_chat_member)
async def rejoin_try_not(c:Gojo, m: Message):
    user = m.left_chat_member
    if not user:
        return
    GA = GIVEAWAY()
    Ezio = GA.give_info(m.chat.id)
    if not Ezio:
        return
    Captain = user.id
    if len(voted_user):
        if Captain in voted_user[m.chat.id]:
            GB = int(left_deduct[m.chat.id][Captain])
            user_entry[m.chat.id][GB] -= 1
            await c.send_message(GB,f"One user who have voted you left the chat so his vote is reduced from your total votes.\nNote that he will not able to vote if he rejoins the chat\nLeft user : {Captain}")
            try:
                rejoin_try[m.chat.id].append(Captain)
            except KeyError:
                rejoin_try[m.chat.id] = [Captain]
    else:
        try:
            rejoin_try[m.chat.id].append(Captain)
        except KeyError:
            rejoin_try[m.chat.id] = [Captain]
        return


__PLUGIN__ = "giveaway"

__alt_name__ = [
    "giveaway",
    "events"
]

__HELP__ = """
**Giveaway**
• /enter (/register, /participate): To participate in giveaway. Make sure the bot is started to get registered.

**Admin commands:**
• /startgiveaway (/startga) : Start the giveaway. Reply to media to send giveaway start message with tagged media (Will only wrok in bot ib).

**User dependent commands**
• /stopentry <post link>: Stop the further entries. Channel for which you want to stop the entries. Pass the post link of the post you want to edit the msg and set it as closed message
• /stopgiveaway (/stopga) : Stop the giveaway. Channel for which you want to stop the giveaway. Will also close voting at same time.
• /startvote <post link>: Start uploading all the user info and will start voting. Pass the post link of the post you want to edit the msg and set it as closed message. Not necessary to give post link.

**Post link (For Channels) = Message link (For chats)**

**All the above command (except `/startgiveaway`) can only be valid iff the user who started the giveaway gives them**

**TO USE THE ADMIN COMMANDS YOU MUST BE ADMIN IN BOTH CHANNEL AS WELL AS CHAT**

**USER DEPENDENT COMMANDS ARE THOSE COMMANDS WHICH CAN ONLY BE USED BY THE USER WHO HAVE GIVEN `/startgiveaway` COMMAND

**Example:**
`/enter`

**NOTE**
Bot should be admin where you are doing giveaway and where you are taking entries.
"""
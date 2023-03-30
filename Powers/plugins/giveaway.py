import os
from datetime import datetime, timedelta
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
from Powers.utils.custom_filters import admin_filter, command
from Powers.vars import Config

user_entry = {} # {c_id :  {participants_id : 0}}} dict be like
voted_user = {} # {c_id : [voter_ids]}} dict be like
total_entries = {} # {c_id : [user_id]} dict be like for participants
left_deduct = {} # {u_id:p_id} u_id = user who have voted, p_id = participant id. Will deduct vote from participants account if user leaves
rejoin_try = {} # store the id of the user who lefts the chat while giveaway under-process {c_id:[]}

async def start_give_one_help(c: Gojo, m: Message):
        while True:
            channel_id = await c.ask(text="Sende me id of the channel and make sure I am admin their. If you don't have id forward a post from your chat.\nType /cancel cancel the current process",chat_id = m.chat.id,filters=filters.text)
            if channel_id.text:
                if str(channel_id.text).lower() == "/cancel":
                    
                    await c.send_message(m.from_user.id, "Cancelled")
                    return None, None, None, None, None
                try:
                    c_id = int(channel_id.text)
                    try:
                        um = await c.send_message(c_id, "Test")
                        await um.pin()
                        await um.unpin()
                        await um.delete()
                        c_id = c_id
                        break
                    except Exception:
                        await c.send_message(m.chat.id,f"Looks like I don't have admin privileges in the chat {c_id}")
                        
                except ValueError:
                    await c.send_message(m.chat.id,"Channel id should be integer type")
            
            else:
                if channel_id.forward_from_chat:
                    try:
                        c_id = channel_id.forward_from_chat.id
                        um = await c.send_message(c_id, "Test")
                        await um.pin()
                        await um.unpin()
                        await um.delete()
                        c_id = c_id
                        break
                    except Exception:
                        await c.send_message(m.chat.id,f"Looks like I don't have admin privileges in the chat {c_id}")
                        
                else:
                    await c.send_message(m.chat.id,f"Forward me content from chat where you want to start giveaway")
        f_c_id = c_id 
        await c.send_message(m.chat.id,"Channel id received")
        while True:
            chat_id = await c.ask(text="Sende me id of the chat and make sure I am admin their. If you don't have id go in the chat and type /id.\nType /cancel to cancel the current process",chat_id = m.chat.id,filters=filters.text)
            if chat_id.text:
                if str(chat_id.text).lower() == "/cancel":
                    await c.send_message(m.from_user.id, "Cancelled")
                    return None, None, None, None, None
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
        
        await c.send_message(m.chat.id,"Chat id received")
        
        link = await c.export_chat_invite_link(cc_id)

        yes_no = await c.ask(text="Do you want to allow old member of the channel can vote in this giveaway.\n**Yes: To allow**\n**No: To don't allow**\nNote that old mean user who is present in the chat for more than 48 hours",chat_id = m.from_user.id,filters=filters.text)
        if yes_no.text.lower() == "yes":
            is_old = 0
        elif yes_no.text.lower() == "no":
            is_old = 1
        return f_c_id, s_c_id, m.from_user.id, is_old, link

@Gojo.on_message(command("startgiveaway"))
async def start_give_one(c: Gojo, m: Message):
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
            con = await c.ask(text="You info is already present in my database do you want to continue\nYes : To start the giveaway with previous configurations\nNo: To create one",chat_id = m.chat.id,filters=filters.text)
            await c.send_message(m.chat.id,"Done")
            if con.text.lower == "yes":
                yes_no = await c.ask(text="Ok.\nDo you want to allow old member of the channel can vote in this giveaway.\n**Yes: To allow**\n**No: To don't allow**\nNote that old mean user who is present in the chat for more than 48 hours",chat_id = m.from_user.id,filters=filters.text)
                await c.send_message(m.chat.id,"Done")
                if yes_no.text.lower() == "yes":
                    is_old = 0
                elif yes_no.text.lower() == "no":
                    is_old = 1
                f_c_id = c_id
                s_c_id = gc_id
                is_old = is_old
                GA.update_is_old(c_id, is_old)
                link = await c.export_chat_invite_link(s_c_id)
        else:
            f_c_id, s_c_id, m.from_user.id, is_old, link = await start_give_one_help(c, m)
            if not f_c_id:
                return
            user_s1 = (await c.get_chat_member(f_c_id,m.from_user.id)).status
            user_s2 = (await c.get_chat_member(s_c_id,m.from_user.id)).status
            if user_s1 not in [CMS.OWNER, CMS.ADMINISTRATOR] and user_s2 not in user_s1 not in [CMS.OWNER, CMS.ADMINISTRATOR]:
                await m.reply_text("You have to be owner or admin in the chat of which you have provided id")
                return
            curr = GA.save_give(f_c_id, s_c_id, m.from_user.id, is_old, force_c=True)               
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return   
    
    if not curr:
        await m.reply_text("One giveaway is already in progress")
        return
    reply = m.reply_to_message
    giveaway_text = f"""
#Giveaway {give_id} ⟩⟩
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
If you want {'this' if reply else "you custom made logo"} logo
How to participate:
• Start the bot by pressing on **Start the bot**
• [Join the chat]({link}) by presseing on **Join the chat** and type `/enter`
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
Status : Entries open
"""

    kb = IKM([[IKB("Join the chat", url=link)],[IKB("Start the bot", url=f"https://{Config.BOT_USERNAME}.t.me/")]])
    try:
        if reply and (reply.media in [MMT.VIDEO, MMT.PHOTO] or (reply.document.mime_type.split("/")[0]=="image")):
            if reply.photo:
                pin = await c.send_photo(f_c_id, reply.photo.file_id,giveaway_text, reply_markup=kb)
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
    await m.reply_text(f"Giveaway is started now in [{name}]({c_in.invite_link})\nHere is the post link {pin.link}")
    await pin.pin()
    

        
@Gojo.on_message(command("stopentry"))
async def stop_give_entry(c:Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id
    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("No current giveaway with the given channel id and giveaway id registered")
        return
    user = curr["user_id"]
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    c_id = curr["chat_id"]
    GA.stop_entries(c_id)
    txt = f"""
Giveaway is closed!
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
Total number of entries registered {len(total_entries[c_id])}
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
Status : Entries closed
"""
    await m.reply_text("Stopped the further entries")
    x = await c.send_message(c_id, txt)
    await x.pin()
    return

@Gojo.on_message(command("stopgiveaway"))
async def stop_give_away(c:Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id

    curr = GA.give_info(u_id=u_id)
    if not curr:
        await m.reply_text("No current giveaway with the given channel id and giveaway id registered")
        return
    user = curr["user_id"]
    c_id = curr["chat_id"]
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    try:
        if not len(user_entry[c_id]):
            await m.reply_text("No entries found")
            GA.stop_give(c_id)
            await m.reply_text("Stopped the giveaway")
            return
    except KeyError:
        GA.stop_give(c_id)
        await m.reply_text("Stopped the giveaway")
        return
    GA.stop_give(c_id)
    GA.stop_entries(c_id)
    await m.reply_text("Stopped the giveaway")
    highest = max(user_entry[c_id], key=lambda k:user_entry[c_id][k])
    high = user_entry[c_id][highest]
    user_high = (await c.get_users(highest)).mention
    txt = f"""
Giveaway is closed!
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
≡ Total participants: {len(total_entries[c_id])}
≡ Total number of votes: {len(voted_user[c_id])}

≡ Winner 🏆 : {user_high}
≡ Vote got 🗳 : `{high}` votes
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
Thanks for participating
"""
    x = await c.send_message(c_id, txt)
    await x.pin()
    try:
        rejoin_try[c_id].clear()
        voted_user[c_id].clear()
        user_entry[c_id].clear()
        left_deduct.clear()
        await m.reply_text("Stopped giveaway")
    except KeyError:
        pass
    return

@Gojo.on_message(command("startvote"))
async def start_the_vote(c: Gojo, m: Message):
    GA = GIVEAWAY()
    u_id = m.from_user.id
    curr = GA.give_info(u_id)
    c_id = curr["chat_id"]
    if not curr:
        await m.reply_text("No current giveaway with the given channel id and giveaway id registered")
        return
    user = curr["user_id"]
    if u_id != user:
        await m.reply_text("You are not the one who have started the giveaway")
        return
    if not len(total_entries[c_id]):
        await m.reply_text("No entires found")
        return
    users = await c.get_users(total_entries[c_id])
    for user in users:
        u_id = user.id
        full_name = user.first_name
        if user.last_name and user.first_name:
            full_name = user.first_name +" "+ user.last_name
        u_name = user.username if user.username else user.mention
        txt = f"""
Participant's info:

≡ Participant's ID : `{u_id}`
≡ Participant's name : {full_name}
≡ Participant's {'username' if user.username else "mention"} : {'@'if user.username else ""}{u_name}
"""     
        if not len(user_entry):
            user_entry[c_id] = {u_id:0}
        else:
            try:
                user_entry[c_id][u_id] = 0
            except KeyError:
                user_entry[c_id] = {u_id:0}
        vote_kb = IKM([[IKB("❤️", f"vote_{c_id}_{u_id}_0")]])
        um = await c.send_message(c_id, txt, reply_markup=vote_kb)
        c_link = um.chat.username
        if not c_link:
            c_link = um.chat.invite_link
        txt_ib = f"Voting is now started\nHere is your vote message link {um.link}.\nHere is chat's {'join link' if not um.chat.username else 'username'} {'@' if um.chat.username else ''}{c_link}\n\n**Thing to keep in mind**\nIf user lefts the chat after voting your vote count will be deducted.\nIf an user left and rejoins the chat he will not be able to vote.\nIf an user is not part of the chat then he'll not be able to vote"
        await c.send_message(u_id, txt_ib, disable_web_page_preview=True)
    await m.reply_text("Started the voting")
    return

@Gojo.on_message(command("enter"))
async def register_user(c: Gojo, m: Message):
    GA = GIVEAWAY()
    curr = GA.is_vote(m.chat.id)
    if not curr:
        await m.reply_text("No giveaway to participate in.\nOr may be entries are closed now")
        return
    curr = GA.give_info(m.chat.id)
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

@Gojo.on_callback_query(filters.regex("^vote_"))
async def vote_increment(c: Gojo, q: CallbackQuery):
    GA = GIVEAWAY()
    data = q.data.split("_")
    c_id = int(data[1])
    u_id = int(data[2])
    votes = int(data[3])
    curr = GA.give_info(c_id)
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
    left_deduct[q.from_user.id] = u_id
    try:
        user_entry[c_id][u_id] += 1
        new_vote = IKM([[IKB(f"❤️ {votes+1}", f"vote_{c_id}_{u_id}_{votes+1}")]])
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
            GB = int(left_deduct[Captain])
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
• /enter : To participate in giveaway. Make sure the bot is started to get registered.

**Admin commands:**
• /startgiveaway : Start the giveaway. Reply to media to send giveaway start message with tagged media (Will only wrok in bot ib).
• /stopentry : Stop the further entries. Channel for which you want to stop the entries.
• /stopgiveaway : Stop the giveaway. Channel for which you want to stop the giveaway. Will also close voting at same time.
• /startvote : Start uploading all the user info and will start voting.

**All the above command (except `/startgiveaway`) can only be valid iff the user who started the giveaway gives them**

**USE ALL THE USER DEPENDENT COMMAND IN PRIVATE**

**Example:**
`/enter`

**NOTE**
Bot should be admin where you are doing giveaway and where you are taking entries
"""
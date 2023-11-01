import os
from asyncio import gather
from random import choice
from traceback import format_exc

from pyrogram.errors import (PeerIdInvalid, ShortnameOccupyFailed,
                             StickerEmojiInvalid, StickerPngDimensions,
                             StickerPngNopng, StickerTgsNotgs,
                             StickerVideoNowebm, UserIsBlocked)
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import LOGGER
from Powers.bot_class import Gojo
from Powers.utils.custom_filters import command
from Powers.utils.sticker_help import *
from Powers.utils.web_helpers import get_file_size
from Powers.vars import Config


@Gojo.on_message(command(["stickerinfo","stinfo"]))
async def give_st_info(c: Gojo , m: Message):
    if not m.reply_to_message:
        await m.reply_text("Reply to a sticker")
        return
    elif not m.reply_to_message.sticker:
        await m.reply_text("Reply to a sticker")
        return
    st_in = m.reply_to_message.sticker
    st_type = "Normal"
    if st_in.is_animated:
        st_type = "Animated"
    elif st_in.is_video:
        st_type = "Video"
    st_to_gib = f"""[Sticker]({m.reply_to_message.link}) info:
File ID : `{st_in.file_id}`
File name : {st_in.file_name}
File unique ID : `{st_in.file_unique_id}`
Date and time sticker created : `{st_in.date}`
Sticker type : `{st_type}`
Emoji : {st_in.emoji}
Pack name : {st_in.set_name}
"""
    kb = IKM([[IKB("➕ Add sticker to pack", url=f"https://t.me/addstickers/{st_in.set_name}")]])
    await m.reply_text(st_to_gib,reply_markup=kb)
    return

@Gojo.on_message(command(["stickerid","stid"]))
async def sticker_id_gib(c: Gojo, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Reply to a sticker")
        return
    elif not m.reply_to_message.sticker:
        await m.reply_text("Reply to a sticker")
        return
    st_in = m.reply_to_message.sticker
    await m.reply_text(f"Sticker id: `{st_in.file_id}`\nSticker unique ID : `{st_in.file_unique_id}`")
    return


@Gojo.on_message(command(["kang", "steal"]))
async def kang(c:Gojo, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("Reply to a sticker or image to kang it.")
    elif not (m.reply_to_message.animation or m.reply_to_message.sticker or m.reply_to_message.photo or (m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0]in["image","video"])):
        return await m.reply_text("Reply to a sticker or image to kang it.")
    if not m.from_user:
        return await m.reply_text("You are anon admin, kang stickers in my pm.")
    msg = await m.reply_text("Kanging Sticker..")
    is_requ = False
    if m.reply_to_message.sticker:
        if m.reply_to_message.sticker.is_animated or m.reply_to_message.sticker.is_video:
            is_requ = True
    # Find the proper emoji
    args = m.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif m.reply_to_message.sticker:
        try:
          sticker_emoji = m.reply_to_message.sticker.emoji
        except Exception:
          ran = ["🤣", "😑", "😁", "👍", "🔥", "🙈", "🙏", "😍", "😘", "😱", "☺️", "🙃", "😌", "🤧", "😐", "😬", "🤩", "😀", "🙂", "🥹", "🥺", "🫥", "🙄", "🫡", "🫠", "🤫", "😓", "🥵", "🥶", "😤", "😡", "🤬", "🤯", "🥴", "🤢", "🤮", "💀", "🗿", "💩", "🤡", "🫶", "🙌", "👐", "✊", "👎", "🫰", "🤌", "👌", "👀", "💃", "🕺", "👩‍❤️‍💋‍👩", "👩‍❤️‍💋‍👨","👨‍❤️‍👨", "💑", "👩‍❤️‍👩", "👩‍❤️‍👨", "💏", "👨‍❤️‍💋‍👨", "😪", "😴", "😭", "🥸", "🤓", "🫤", "😮", "😧", "😲", "🥱", "😈", "👿", "🤖", "👾", "🙌", "🥴", "🥰", "😇", "🤣" ,"😂", "😜", "😎"]
          sticker_emoji = choice(ran)
    else:
        edit = await msg.reply_text("No emoji provided choosing a random emoji")
        ran = ["🤣", "😑", "😁", "👍", "🔥", "🙈", "🙏", "😍", "😘", "😱", "☺️", "🙃", "😌", "🤧", "😐", "😬", "🤩", "😀", "🙂", "🥹", "🥺", "🫥", "🙄", "🫡", "🫠", "🤫", "😓", "🥵", "🥶", "😤", "😡", "🤬", "🤯", "🥴", "🤢", "🤮", "💀", "🗿", "💩", "🤡", "🫶", "🙌", "👐", "✊", "👎", "🫰", "🤌", "👌", "👀", "💃", "🕺", "👩‍❤️‍💋‍👩", "👩‍❤️‍💋‍👨","👨‍❤️‍👨", "💑", "👩‍❤️‍👩", "👩‍❤️‍👨", "💏", "👨‍❤️‍💋‍👨", "😪", "😴", "😭", "🥸", "🤓", "🫤", "😮", "😧", "😲", "🥱", "😈", "👿", "🤖", "👾", "🙌", "🥴", "🥰", "😇", "🤣" ,"😂", "😜", "😎"]
        sticker_emoji = choice(ran)
        await edit.delete()
    await msg.edit_text(f"Makeing a sticker with {sticker_emoji} emoji")

    # Get the corresponding fileid, resize the file if necessary
    try:
        if is_requ or m.reply_to_message.animation or m.reply_to_message.video or m.reply_to_message.photo or (m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] in ["video","image"]):
            # telegram doesn't allow animated and video sticker to be kanged as we do for normal stickers
            if m.reply_to_message.animation or m.reply_to_message.video or (m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] == "video"):
                path = await Vsticker(c, m.reply_to_message)
                SIZE = os.path.getsize(path)
                if SIZE > 261120:
                    await m.reply_text("File is too big")
                    os.remove(path)
                    return
            elif is_requ:
                path = await m.reply_to_message.download() 
            else:
                sizee = (await get_file_size(m.reply_to_message)).split()
                if (sizee[1] == "mb" and int(sizee[0]) > 10) or sizee[1] == "gb":
                    await m.reply_text("File size is too big")
                    return
                path = await m.reply_to_message.download()
                path = await resize_file_to_sticker_size(path)
            sticker = await create_sticker(
                await upload_document(
                    c, path, m.chat.id
                ),
                sticker_emoji
            )
            os.remove(path)
        elif m.reply_to_message.sticker and not is_requ:
            sticker = await create_sticker(
                await get_document_from_file_id(
                    m.reply_to_message.sticker.file_id
                ),
                sticker_emoji
            )
        else:
          await m.reply_text("Unsupported media file...")
          return
    except ShortnameOccupyFailed:
        await m.reply_text("Change Your Name Or Username")
        return

    except Exception as e:
        await m.reply_text(str(e))
        e = format_exc()
        LOGGER.error(e)
        LOGGER.error(format_exc())

    # Find an available pack & add the sticker to the pack; create a new pack if needed
    # Would be a good idea to cache the number instead of searching it every single time...
    kang_lim = 120
    st_in = m.reply_to_message.sticker 
    st_type = "norm"
    is_anim = is_vid = False
    if st_in:
        if st_in.is_animated:
            st_type = "ani"
            kang_lim = 50
            is_anim = True
        elif st_in.is_video:
            st_type = "vid"
            kang_lim = 50
            is_vid = True
    elif m.reply_to_message.document:
        if m.reply_to_message.document.mime_type in ["application/x-bad-tgsticker", "application/x-tgsticker"]:
            st_type = "ani"
            kang_lim = 50
            is_anim = True
        elif m.reply_to_message.document.mime_type == "video/webm":
            st_type = "vid"
            kang_lim = 50
            is_vid = True
    elif m.reply_to_message.video or m.reply_to_message.animation or (m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] == "video"):
        st_type = "vid"
        kang_lim = 50
        is_vid = True
    packnum = 0
    limit = 0
    volume = 0
    packname_found = False
    
    try:
        while not packname_found:
            packname = f"CE{str(m.from_user.id)}{st_type}{packnum}_by_{Config.BOT_USERNAME}"
            kangpack = f"{('@'+m.from_user.username) if m.from_user.username else m.from_user.first_name[:10]} {st_type} {('vOl '+str(volume)) if volume else ''} by @{Config.BOT_USERNAME}"
            if limit >= 50: # To prevent this loop from running forever
                await m.reply_text("Failed to kang\nMay be you have made more than 50 sticker packs with me try deleting some")
                return
            sticker_set = await get_sticker_set_by_name(c,packname)
            if not sticker_set:
                sticker_set = await create_sticker_set(
                    client=c,
                    owner=m.from_user.id,
                    title=kangpack,
                    short_name=packname,
                    stickers=[sticker],
                    animated=is_anim,
                    video=is_vid
                )
            elif sticker_set.set.count >= kang_lim:
                packnum += 1
                limit += 1
                volume += 1
                continue
            else:
                try:
                    await add_sticker_to_set(c,sticker_set,sticker)
                except StickerEmojiInvalid:
                    return await msg.edit("[ERROR]: INVALID_EMOJI_IN_ARGUMENT")
            limit += 1
            packname_found = True
        kb = IKM(
            [
                [
                    IKB("➕ Add Pack ➕",url=f"t.me/addstickers/{packname}")
                ]
            ]
        )
        await msg.delete()
        await m.reply_text(
            f"Kanged the sticker\nPack name: `{kangpack}`\nEmoji: {sticker_emoji}",
            reply_markup=kb
        )
    except (PeerIdInvalid, UserIsBlocked):
        keyboard = IKM(
            [[IKB("Start me first", url=f"t.me/{Config.BOT_USERNAME}")]]
        )
        await msg.delete()
        await m.reply_text(
            "You Need To Start A Private Chat With Me.",
            reply_markup=keyboard,
        )
    except StickerPngNopng:
        await msg.delete()
        await m.reply_text(
            "Stickers must be png files but the provided image was not a png"
        )
    except StickerPngDimensions:
        await msg.delete()
        await m.reply_text("The sticker png dimensions are invalid.")
    except StickerTgsNotgs:
        await msg.delete()
        await m.reply_text("Sticker must be tgs file but the provided file was not tgs")
    except StickerVideoNowebm:
        await msg.delete()
        await m.reply_text("Sticker must be webm file but the provided file was not webm")
    except Exception as e:
        await msg.delete()
        await m.reply_text(f"Error occured\n{e}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command(["mmfb","mmfw","mmf"]))
async def memify_it(c: Gojo, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Invalid type.")
        return
    rep_to = m.reply_to_message
    if not (rep_to.sticker or rep_to.photo or (rep_to.document and "image" in rep_to.document.mime_type.split("/"))):
        await m.reply_text("I only support memifying of normal sticker and photos for now")
        return
    if rep_to.sticker and (rep_to.sticker.is_animated or rep_to.sticker.is_video):
        await m.reply_text("I only support memifying of normal sticker and photos for now")
        return
    kb = IKM(
        [
            [
                IKB("Join for memes",url="https://t.me/memesofdank")
            ]
        ]
    )
    if len(m.command) == 1:
        await m.reply_text("Give me something to write")
        return
    filll = m.command[0][-1]
    if filll == "b":
        fiil = "black"
    else:
        fiil = "white"
    x = await m.reply_text("Memifying...")
    meme = m.text.split(None,1)[1].strip()
    name = f"@memesofdank_{m.id}.png"
    path = await rep_to.download(name)
    is_sticker = False
    if rep_to.sticker:
        is_sticker = True
    output = await draw_meme(path,meme,is_sticker,fiil)
    await x.delete()
    xNx = await m.reply_photo(output[0],reply_markup=kb)
    await xNx.reply_sticker(output[1],reply_markup=kb)
    try:
        os.remove(output[0])
        os.remove(output[1])
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return

@Gojo.on_message(command(["getsticker","getst"]))
async def get_sticker_from_file(c: Gojo, m: Message):
    Caption = f"Converted by:\n@{Config.BOT_USERNAME}"
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Reply to a sticker or file")
        return
    to_vid = False
    if not (repl.animation or repl.video or repl.sticker or repl.photo or (repl.document and repl.document.mime_type.split("/")[0] in ["image","video"])):
        await m.reply_text("I only support conversion of plain stickers, images, videos and animation for now")
        return
    if repl.animation or repl.video or (repl.document and repl.document.mime_type.split("/")[0]=="video"):
        to_vid = True
    x = await m.reply_text("Converting...")
    if repl.sticker:
        if repl.sticker.is_animated:
            upp = await repl.download()
            up = tgs_to_gif(upp,True)
            await x.delete()
            await m.reply_animation(up,caption=Caption)
            os.remove(up)
            return
        elif repl.sticker.is_video:
            upp = await repl.download()
            up = await webm_to_gif(upp)
            await x.delete()
            await m.reply_animation(up,caption=Caption)
            os.remove(up)
            return
        else:
            upp = await repl.download()
            up = toimage(upp,is_direc=True)
            await x.delete()
            await m.reply_photo(up,caption=Caption)
            os.remove(up)
            return
    elif repl.photo:
        upp = await repl.download()
        up = tosticker(upp,is_direc=True)
        await x.delete()
        await m.reply_sticker(up)
        os.remove(up)
        return
    
    elif to_vid:
        up = await Vsticker(c,repl)
        await x.delete()
        await m.reply_sticker(up)
        os.remove(up)
        return

        
__PLUGIN__ = "sticker"
__alt_name__ = [
    "sticker",
    "kang"
]
__HELP__ = """
**User Commands:**
• /kang (/steal) <emoji>: Reply to a sticker or any supported media
• /stickerinfo (/stinfo) : Reply to any sticker to get it's info
• /getsticker (/getst) : Get sticker as photo, gif or vice versa.
• /stickerid (/stid) : Reply to any sticker to get it's id
• /mmf <your text>: Reply to a normal sticker or a photo or video file to memify it. If you want to right text at bottom use `;right your message`
    ■ For e.g. 
    ○ /mmf Hello freinds : this will add text to the top
    ○ /mmf Hello ; freinds : this will add Hello to the top and freinds at the bottom
    ○ /mmf ; Hello friends : this will add text at the bottom
    ○ /mmfb <text>: To fill text with black colour
    ○ /mmfw or /mmf <text>: To fill it with white colour

**Note**
mmf and getsticker only support photo and normal stickers for now.

"""

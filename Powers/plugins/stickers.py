from random import choice
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (PeerIdInvalid, ShortnameOccupyFailed,
                             StickerEmojiInvalid, StickerPngDimensions,
                             StickerPngNopng, StickerTgsNotgs,
                             StickerVideoNowebm, UserIsBlocked)
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Powers import LOGGER
from Powers.utils.custom_filters import command
from Powers.utils.sticker_help import *
from Powers.utils.string import encode_decode
from Powers.utils.web_helpers import get_file_size


@Gojo.on_message(command(["stickerinfo", "stinfo"]))
async def give_st_info(c: Gojo, m: Message):
    if not m.reply_to_message or not m.reply_to_message.sticker:
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
    await m.reply_text(st_to_gib, reply_markup=kb)
    return


@Gojo.on_message(command(["stickerid", "stid"]))
async def sticker_id_gib(c: Gojo, m: Message):
    if not m.reply_to_message or not m.reply_to_message.sticker:
        await m.reply_text("Reply to a sticker")
        return
    st_in = m.reply_to_message.sticker
    await m.reply_text(f"Sticker id: `{st_in.file_id}`\nSticker unique ID : `{st_in.file_unique_id}`")
    return


@Gojo.on_message(command(["kang", "steal"]))
async def kang(c: Gojo, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("Reply to a sticker or image to kang it.")
    elif not (m.reply_to_message.animation or m.reply_to_message.sticker or m.reply_to_message.photo or (
            m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] in ["image", "video"])):
        return await m.reply_text("Reply to a sticker or image to kang it.")
    if not m.from_user:
        return await m.reply_text("You are anon admin, kang stickers in my pm.")
    msg = await m.reply_text("Kanging Sticker..")
    is_requ = bool(
        m.reply_to_message.sticker
        and (
            m.reply_to_message.sticker.is_animated
            or m.reply_to_message.sticker.is_video
        )
    )
    # Find the proper emoji
    args = m.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif m.reply_to_message.sticker:
        try:
            sticker_emoji = m.reply_to_message.sticker.emoji
            if not sticker_emoji:
                ran = ["🤣", "😑", "😁", "👍", "🔥", "🙈", "🙏", "😍", "😘", "😱", "☺️", "🙃", "😌", "🤧", "😐", "😬", "🤩", "😀", "🙂",
                       "🥹", "🥺", "🫥", "🙄", "🫡", "🫠", "🤫", "😓", "🥵", "🥶", "😤", "😡", "🤬", "🤯", "🥴", "🤢", "🤮", "💀", "🗿",
                       "💩", "🤡", "🫶", "🙌", "👐", "✊", "👎", "🫰", "🤌", "👌", "👀", "💃", "🕺", "👩‍❤️‍💋‍👩", "👩‍❤️‍💋‍👨",
                       "👨‍❤️‍👨", "💑", "👩‍❤️‍👩", "👩‍❤️‍👨", "💏", "👨‍❤️‍💋‍👨", "😪", "😴", "😭", "🥸", "🤓", "🫤", "😮", "😧", "😲",
                       "🥱", "😈", "👿", "🤖", "👾", "🙌", "🥴", "🥰", "😇", "🤣", "😂", "😜", "😎"]
                sticker_emoji = choice(ran)
        except Exception:
            ran = ["🤣", "😑", "😁", "👍", "🔥", "🙈", "🙏", "😍", "😘", "😱", "☺️", "🙃", "😌", "🤧", "😐", "😬", "🤩", "😀", "🙂", "🥹",
                   "🥺", "🫥", "🙄", "🫡", "🫠", "🤫", "😓", "🥵", "🥶", "😤", "😡", "🤬", "🤯", "🥴", "🤢", "🤮", "💀", "🗿", "💩", "🤡",
                   "🫶", "🙌", "👐", "✊", "👎", "🫰", "🤌", "👌", "👀", "💃", "🕺", "👩‍❤️‍💋‍👩", "👩‍❤️‍💋‍👨", "👨‍❤️‍👨", "💑",
                   "👩‍❤️‍👩", "👩‍❤️‍👨", "💏", "👨‍❤️‍💋‍👨", "😪", "😴", "😭", "🥸", "🤓", "🫤", "😮", "😧", "😲", "🥱", "😈", "👿", "🤖",
                   "👾", "🙌", "🥴", "🥰", "😇", "🤣", "😂", "😜", "😎"]
            sticker_emoji = choice(ran)
    else:
        edit = await msg.reply_text("No emoji provided choosing a random emoji")
        ran = ["🤣", "😑", "😁", "👍", "🔥", "🙈", "🙏", "😍", "😘", "😱", "☺️", "🙃", "😌", "🤧", "😐", "😬", "🤩", "😀", "🙂", "🥹", "🥺",
               "🫥", "🙄", "🫡", "🫠", "🤫", "😓", "🥵", "🥶", "😤", "😡", "🤬", "🤯", "🥴", "🤢", "🤮", "💀", "🗿", "💩", "🤡", "🫶", "🙌",
               "👐", "✊", "👎", "🫰", "🤌", "👌", "👀", "💃", "🕺", "👩‍❤️‍💋‍👩", "👩‍❤️‍💋‍👨", "👨‍❤️‍👨", "💑", "👩‍❤️‍👩", "👩‍❤️‍👨",
               "💏", "👨‍❤️‍💋‍👨", "😪", "😴", "😭", "🥸", "🤓", "🫤", "😮", "😧", "😲", "🥱", "😈", "👿", "🤖", "👾", "🙌", "🥴", "🥰",
               "😇", "🤣", "😂", "😜", "😎"]
        sticker_emoji = choice(ran)
        await edit.delete()
    await msg.edit_text(f"Makeing a sticker with {sticker_emoji} emoji")

    # Get the corresponding fileid, resize the file if necessary
    try:
        if is_requ or m.reply_to_message.animation or m.reply_to_message.video or m.reply_to_message.photo or (
                m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] in ["video",
                                                                                                        "image"]):
            # telegram doesn't allow animated and video sticker to be kanged as we do for normal stickers
            if m.reply_to_message.animation or m.reply_to_message.video or (
                    m.reply_to_message.document and m.reply_to_message.document.mime_type.split("/")[0] == "video"):
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
        elif m.reply_to_message.sticker:
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
    packnum = 0
    limit = 0
    volume = 0
    packname_found = False

    try:
        while not packname_found:
            packname = f"CE{m.from_user.id}{packnum}_by_{c.me.username}"
            kangpack = f"{f'@{m.from_user.username}' if m.from_user.username else m.from_user.first_name[:10]} {f'vOl {str(volume)}' if volume else ''} by @{c.me.username}"
            if limit >= 50:  # To prevent this loop from running forever
                await m.reply_text(
                    "Failed to kang\nMay be you have made more than 50 sticker packs with me try deleting some")
                return
            sticker_set = await get_sticker_set_by_name(c, packname)
            if not sticker_set:
                try:
                    sticker_set = await create_sticker_set(
                        client=c,
                        owner=m.from_user.id,
                        title=kangpack,
                        short_name=packname,
                        stickers=[sticker]
                    )
                except StickerEmojiInvalid:
                    return await msg.edit("[ERROR]: INVALID_EMOJI_IN_ARGUMENT")
            elif sticker_set.set.count >= kang_lim:
                packnum += 1
                limit += 1
                volume += 1
                continue
            try:
                await add_sticker_to_set(c, sticker_set, sticker)
                packname_found = True
            except StickerEmojiInvalid:
                return await msg.edit("[ERROR]: INVALID_EMOJI_IN_ARGUMENT")
        kb = IKM(
            [
                [
                    IKB("➕ Add Pack ➕", url=f"t.me/addstickers/{packname}")
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
            [[IKB("Start me first", url=f"t.me/{c.me.username}")]]
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


@Gojo.on_message(command(["rmsticker", "removesticker"]))
async def remove_sticker_from_pack(c: Gojo, m: Message):
    if not m.reply_to_message or not m.reply_to_message.sticker:
        return await m.reply_text(
            "Reply to a sticker to remove it from the pack."
        )

    sticker = m.reply_to_message.sticker

    to_modify = await m.reply_text("Removing the sticker from your pack")
    sticker_set = await get_sticker_set_by_name(c, sticker.set_name)

    if not sticker_set:
        await to_modify.edit_text("This sticker is not part for your pack")
        return

    try:
        await remove_sticker(c, sticker.file_id)
        await to_modify.edit_text(
            f"Successfully removed [sticker]({m.reply_to_message.link}) from {sticker_set.set.title}")
    except Exception as e:
        await to_modify.delete()
        await m.reply_text(f"Failed to remove sticker due to:\n{e}\nPlease report this bug using `/bug`")
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command(["mmfb", "mmfw", "mmf"]))
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
                IKB("You might like", url="https://t.me/me_and_ghost")
            ]
        ]
    )
    if len(m.command) == 1:
        await m.reply_text("Give me something to write")
        return
    filll = m.command[0][-1]
    fiil = "black" if filll == "b" else "white"
    x = await m.reply_text("Memifying...")
    meme = m.text.split(None, 1)[1].strip()
    name = f"@memesofdank_{m.id}.png"
    path = await rep_to.download(name)
    is_sticker = bool(rep_to.sticker)
    output = await draw_meme(path, meme, is_sticker, fiil)
    await x.delete()
    xNx = await m.reply_photo(output[0], reply_markup=kb)
    await xNx.reply_sticker(output[1], reply_markup=kb)
    try:
        os.remove(output[0])
        os.remove(output[1])
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return


@Gojo.on_message(command(["getsticker", "getst"]))
async def get_sticker_from_file(c: Gojo, m: Message):
    Caption = f"Converted by:\n@{c.me.username}"
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Reply to a sticker or file")
        return
    if (
            not repl.animation
            and not repl.video
            and not repl.sticker
            and not repl.photo
            and (
            not repl.document
            or repl.document.mime_type.split("/")[0] not in ["image", "video"]
    )
    ):
        await m.reply_text("I only support conversion of plain stickers, images, videos and animation for now")
        return
    to_vid = bool(
        repl.animation
        or repl.video
        or (repl.document and repl.document.mime_type.split("/")[0] == "video")
    )
    x = await m.reply_text("Converting...")
    if repl.sticker:
        if repl.sticker.is_animated:
            upp = await repl.download()
            up = await tgs_to_gif(upp, True)
            await x.delete()
            await m.reply_animation(up, caption=Caption)
        elif repl.sticker.is_video:
            upp = await repl.download()
            up = await webm_to_gif(upp)
            await x.delete()
            await m.reply_animation(up, caption=Caption)
        else:
            upp = await repl.download()
            up = toimage(upp, is_direc=True)
            await x.delete()
            await m.reply_document(up, caption=Caption)
        os.remove(up)
        return
    elif repl.photo:
        upp = await repl.download()
        up = tosticker(upp, is_direc=True)
        await x.delete()
        await m.reply_sticker(up)
        os.remove(up)
        return

    elif to_vid:
        up = await Vsticker(c, repl)
        await x.delete()
        await m.reply_sticker(up)
        os.remove(up)
        return


@Gojo.on_message(command(["rmsticker", "rmst", "removesticker"]))
async def remove_from_MY_pack(c: Gojo, m: Message):
    if not m.reply_to_message or not m.reply_to_message.sticker:
        await m.reply_text("Please reply to a sticker to remove it from your pack")
        return

    sticker = m.reply_to_message.sticker
    sticker_set = await get_sticker_set_by_name(c, sticker.set_name)

    if not sticker_set:
        await m.reply_text("This sticker is not part of your pack")
        return

    try:
        await remove_sticker(c, sticker.file_id)
        await m.reply_text(f"Deleted [this]({m.reply_to_message.link}) from pack: {sticker_set.et.title}")
        return
    except Exception as e:
        await m.reply_text(f"Error\n{e}\nReport it using /bug")
        LOGGER.error(e)
        LOGGER.error(format_exc(e))
        return


@Gojo.on_message(command(["getmypacks", "mypacks", "mysets", "stickerset", "stset"]))
async def get_my_sticker_sets(c: Gojo, m: Message):
    to_del = await m.reply_text("Please wait while I fetch all the sticker set I have created for you.")

    txt, kb = await get_all_sticker_packs(c, m.from_user.id)

    await to_del.delete()
    if not txt:
        await m.reply_text("Looks like you haven't made any sticker using me...")
        return
    await m.reply_text(txt, reply_markup=kb)


@Gojo.on_message(command(["q", "ss"]))
async def quote_the_msg(_, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Reply to a message to quote it")
        return

    to_edit = await m.reply_text("Genrating quote...")

    if len(m.command) > 1 and m.command[1].lower() == "r":
        reply_msg = m.reply_to_message.reply_to_message
        if not reply_msg or not reply_msg.text:
            reply_message = {}
        else:
            to_edit = await to_edit.edit_text("Genrating quote with reply to the message...")
            replied_name = reply_msg.from_user.first_name
            if reply_msg.from_user.last_name:
                replied_name += f" {reply_msg.from_user.last_name}"

            reply_message = {
                "chatId": reply_msg.from_user.id,
                "entities": get_msg_entities(reply_msg),
                "name": replied_name,
                "text": reply_msg.text,
            }
    else:
        reply_message = {}
    name = m.reply_to_message.from_user.first_name
    if m.reply_to_message.from_user.last_name:
        name += f" {m.reply_to_message.from_user.last_name}"

    emoji_status = None
    if m.reply_to_message.from_user.emoji_status:
        emoji_status = str(m.reply_to_message.from_user.emoji_status.custom_emoji_id)

    msg_data = [
        {
            "entities": get_msg_entities(m.reply_to_message),
            "avatar": True,
            "from": {
                "id": m.reply_to_message.from_user.id,
                "name": name,
                "emoji_status": emoji_status,
            },
            "text": m.reply_to_message.text,
            "replyMessage": reply_message,
        }
    ]
    status, path = quotify(msg_data)

    if not status:
        await to_edit.edit_text(path)
        return

    await m.reply_sticker(path)
    await to_edit.delete()
    os.remove(path)


@Gojo.on_callback_query(filters.regex(r"^stickers_.*"))
async def sticker_callbacks(c: Gojo, q: CallbackQuery):
    data = q.data.split("_")
    decoded = await encode_decode(data[-1], "decode")
    user = int(decoded.split("_")[-1])
    if q.from_user.id != user:
        await q.answer("This is not for you")
    else:
        offset = int(decoded.split("_")[0])

        txt, kb = await get_all_sticker_packs(c, q.from_user.id, offset)
        if not txt:
            await q.answer("No sticker pack found....")
        else:
            await q.answer("Showing your sticker set")
            await q.edit_message_text(txt, reply_markup=kb)

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
• /mypacks : Get all of your current sticker pack you have made via me.
• /q(/ss) <reply to message> : Will quote the replied message
• /q(/ss) r <reply to message> : Will quote the replied message and message it was replied to.
• /mmf <your text>: Reply to a normal sticker or a photo or video file to memify it. If you want to right text at bottom use `;right your message`
    ■ For e.g. 
    ○ /mmfb <text>: To fill text with black colour
    ○ /mmfw or /mmf <text>: To fill it with white colour

**Note**
mmf and getsticker only support photo and normal stickers for now.

"""

import asyncio
import math
import os
import shlex
import textwrap
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from pyrogram import errors, raw
from pyrogram.file_id import FileId
from pyrogram.types import Message

from Powers.bot_class import Gojo


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

async def get_sticker_set_by_name(
    client: Gojo, name: str
) -> raw.base.messages.StickerSet:
    try:
        return await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name),
                hash=0,
            )
        )
    except errors.exceptions.not_acceptable_406.StickersetInvalid:
        return None



async def create_sticker_set(
    client: Gojo,
    owner: int,
    title: str,
    short_name: str,
    stickers: List[raw.base.InputStickerSetItem],
    animated:bool=False,
    video:bool=False
) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.CreateStickerSet(
            user_id=await client.resolve_peer(owner),
            title=title,
            short_name=short_name,
            stickers=stickers,
            animated=animated,
            videos=video
        )
    )


async def add_sticker_to_set(
    client: Gojo,
    stickerset: raw.base.messages.StickerSet,
    sticker: raw.base.InputStickerSetItem,
) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.AddStickerToSet(
            stickerset=raw.types.InputStickerSetShortName(
                short_name=stickerset.set.short_name
            ),
            sticker=sticker,
        )
    )


async def create_sticker(
    sticker: raw.base.InputDocument, emoji: str
) -> raw.base.InputStickerSetItem:
    return raw.types.InputStickerSetItem(document=sticker, emoji=emoji)



STICKER_DIMENSIONS = (512, 512)


async def resize_file_to_sticker_size(file_path: str,length:int=512,width:int=512) -> str:
    im = Image.open(file_path)
    if (im.width, im.height) < STICKER_DIMENSIONS:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = length / size1
            size1new = length
            size2new = size2 * scale
        else:
            scale = width / size2
            size1new = size1 * scale
            size2new = width
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(STICKER_DIMENSIONS)

    file_pathh = "./downloads/resized.png"
    im.save(file_pathh)
    os.remove(file_path)
    return file_pathh

async def tgs_to_gif(file, tgs=False, video=False):
    if tgs:
        cmd = f"lottie_convert.py '{file}' 'gojo_satoru.gif'"
    elif video:
        cmd = f"ffmpeg -i '{file}' -c copy 'gojo_satoru.gif'"
    await runcmd(cmd)
    os.remove(file)
    return 'gojo_satoru.gif'

async def webm_to_gif(file):
    cmd = f"ffmpeg -i '{file}' 'goJo.gif'"
    await runcmd(cmd)
    os.remove(file)
    return "goJo.gif"
        
async def Vsticker(c: Gojo, file: Message):
    if file.animation:
        file = file.animation
    elif file.video:
        file = file.video
    _width_ = file.width
    _height_ = file.height
    if _height_ > _width_:
        _height_, _width_ = (512, -1)
    else:
        _height_, _width_ = (-1, 512)
    file = await c.download_media(file)
    await runcmd(
        f"ffmpeg -to 00:00:02.900 -i '{file}' -vf scale={_width_}:{_height_} -c:v libvpx-vp9 -crf 30 -b:v 560k -maxrate 560k -bufsize 256k -an 'VideoSticker.webm'"
    )
    os.remove(file)
    return "VideoSticker.webm"


async def upload_document(
    client: Gojo, file_path: str, chat_id: int
) -> raw.base.InputDocument:
    media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=await client.resolve_peer(chat_id),
            media=raw.types.InputMediaUploadedDocument(
                mime_type=client.guess_mime_type(file_path) or "application/zip",
                file=await client.save_file(file_path),
                attributes=[
                    raw.types.DocumentAttributeFilename(
                        file_name=os.path.basename(file_path)
                    )
                ],
                force_file=True,
            ),
        )
    )
    return raw.types.InputDocument(
        id=media.document.id,
        access_hash=media.document.access_hash,
        file_reference=media.document.file_reference,
    )


async def get_document_from_file_id(
    file_id: str,
) -> raw.base.InputDocument:
    decoded = FileId.decode(file_id)
    return raw.types.InputDocument(
        id=decoded.media_id,
        access_hash=decoded.access_hash,
        file_reference=decoded.file_reference,
    )


async def draw_meme(image_path: str, text: str, sticker: bool, fiill: str) -> list:
    _split = text.split(";", 1)
    if len(_split) == 2:
        lower_text = _split[1]
        upper_text = _split[0]
    else:
        upper_text = text
        lower_text = ""

    image = Image.open(image_path)
    width, height = image.size

    font_size = int(width / 11)
    font = ImageFont.truetype("./extras/comic.ttf", font_size)

    draw = ImageDraw.Draw(image)

    upper_text_width, _ = draw.textsize(upper_text, font=font)
    lower_text_width, lower_text_height = draw.textsize(lower_text, font=font)

    upper_text_position = ((width - upper_text_width) // 2, height // 10)
    lower_text_position = ((width - lower_text_width) // 2, height - lower_text_height - (height // 10))

    draw.text(upper_text_position, upper_text, font=font, fill=fiill)
    draw.text(lower_text_position, lower_text, font=font, fill=fiill)

    if sticker:
        stick_path = image_path
    else:
        stick_path = await resize_file_to_sticker_size(image_path)

    image1 = image_path
    image2 = tosticker(stick_path,"@memesofdank_memer_hu_vai.webp")

    image.save(image1)
    image.save(image2)

    image.close()

    return [image1, image2]


# async def draw_meme(image_path, text:str,stick):
#     """Hellbot se churaya hai hue hue hue..."""
#     img = Image.open(image_path)
#     i_width, i_height = img.size
#     m_font = ImageFont.truetype(
#         "./extras/comic.ttf", int(i_width / 11)
#     )
#     if ";" in text:
#         upper_text, lower_text = text.split(";")
#     else:
#         upper_text = text
#         lower_text = ""
#     draw = ImageDraw.Draw(img)
#     current_h, pad = 10, 5
#     if upper_text:
#         for u_text in textwrap.wrap(upper_text,width=15,subsequent_indent=" "):
#             u_width, u_height = draw.textsize(u_text, font=m_font)
#             draw.text(
#                 xy=(((i_width - u_width) / 2) - 1, int((current_h / 640) * i_width)),
#                 text=u_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(((i_width - u_width) / 2) + 1, int((current_h / 640) * i_width)),
#                 text=u_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 1),
#                 text=u_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 1),
#                 text=u_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
#                 text=u_text,
#                 font=m_font,
#                 fill=(255, 255, 255),
#             )
#             current_h += u_height + pad
#     if lower_text:
#         for l_text in textwrap.wrap(upper_text,width=15,subsequent_indent=" "):
#             u_width, u_height = draw.textsize(l_text, font=m_font)
#             draw.text(
#                 xy=(
#                     ((i_width - u_width) / 2) - 1,
#                     i_height - u_height - int((20 / 640) * i_width),
#                 ),
#                 text=l_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(
#                     ((i_width - u_width) / 2) + 1,
#                     i_height - u_height - int((20 / 640) * i_width),
#                 ),
#                 text=l_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(
#                     (i_width - u_width) / 2,
#                     (i_height - u_height - int((20 / 640) * i_width)) - 1,
#                 ),
#                 text=l_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(
#                     (i_width - u_width) / 2,
#                     (i_height - u_height - int((20 / 640) * i_width)) + 1,
#                 ),
#                 text=l_text,
#                 font=m_font,
#                 fill=(0, 0, 0),
#             )
#             draw.text(
#                 xy=(
#                     (i_width - u_width) / 2,
#                     i_height - u_height - int((20 / 640) * i_width),
#                 ),
#                 text=l_text,
#                 font=m_font,
#                 fill=(255, 255, 255),
#             )
#             current_h += u_height + pad

#     hue = image_path
#     if stick:
#         stick_path = image_path
#     else:
#         stick_path = await resize_file_to_sticker_size(hue)
#     mee = tosticker(stick_path,"@memesofdank_memer_hu_vai.webp")
#     img.save(hue)
#     img.save(mee)
#     return hue, mee

def toimage(image, filename=None, is_direc=False):
    filename = filename if filename else "gojo.jpg"
    if is_direc:
        os.rename(image,filename)
        return filename
    img = Image.open(image)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(filename, "jpeg")
    os.remove(image)
    return filename


def tosticker(response, filename=None, is_direc=False):
    filename = filename if filename else "gojo.webp"
    if is_direc:
        os.rename(response,filename)
        return filename
    image = Image.open(response)
    if image.mode != "RGB":
        image.convert("RGB")
    image.save(filename, "webp")
    os.remove(response)
    return filename
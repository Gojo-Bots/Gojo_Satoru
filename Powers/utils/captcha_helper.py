from random import choice, randint, randrange

import qrcode
from captcha.image import ImageCaptcha
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM

from Powers.database.captcha_db import CAPTCHA_DATA
from Powers.utils.string import encode_decode
from Powers.vars import Config

initial = f"t.me/{Config.BOT_USERNAME}?start=qrcaptcha_"
captchaa = CAPTCHA_DATA()

async def get_qr_captcha(chat,user):
    encode = f"{chat}:{user}"
    encoded = encode_decode(encode)
    final = initial+encoded
    qr = qrcode.make(final)
    name = f"captcha_verification{chat}_{user}.png"
    qr.save(name)
    return name

def genrator():
    alpha = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    rand_alpha = choice(alpha)
    if_ = randint(0,1)
    
    if if_:
        new_alpha = rand_alpha.upper()
    else:
        new_alpha = rand_alpha

    list_ = [new_alpha]
    while len(list_) != 4:
        xXx = randrange(0,9)
        list_.append(xXx)

    str_ = ""
    while len(str_) != 4:
        OwO = choice(list_)
        str_ += OwO 
    return str_

async def get_image_captcha(chat,user):
    str_ = genrator()
    captchaa.load_cap_data(chat,user,str_)
    name = f"captcha_img_{chat}_{user}.png"
    image = ImageCaptcha(280,90)

    cap = image.generate(str_)
    image.write(str_,name)

    return name, str_



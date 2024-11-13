from random import choice, randint, randrange

import qrcode
from captcha.image import ImageCaptcha

from Powers.database.captcha_db import CAPTCHA_DATA
from Powers.utils.string import encode_decode

captchaa = CAPTCHA_DATA()


async def get_qr_captcha(chat, user, username):
    initial = f"t.me/{username}?start=qr_"
    encode = f"{chat}:{user}"
    encoded = await encode_decode(encode)
    final = initial + encoded
    qr = qrcode.make(final)
    name = f"captcha_verification{chat}_{user}.png"
    qr.save(name)
    return name


def genrator():
    alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
             "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    rand_alpha = choice(alpha)
    if_ = randint(0, 1)

    new_alpha = rand_alpha.upper() if if_ else rand_alpha
    list_ = [new_alpha]
    while len(list_) != 4:
        xXx = randrange(0, 9)
        list_.append(xXx)

    str_ = ""
    while len(str_) != 4:
        OwO = choice(list_)
        str_ += str(OwO)
    return str_


async def get_image_captcha(chat, user):
    str_ = genrator()
    captchaa.load_cap_data(chat, user, str_)
    name = f"captcha_img_{chat}_{user}.png"
    image = ImageCaptcha(280, 90)

    cap = image.generate(str_)
    image.write(str_, name)

    return name, str_

from re import findall
from pyrogram.types import InlineKeyboardButton as kb
from pykeyboard import InlineKeyboard

# CREDIT WILLIAM BUTCHER BOT

def is_url(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, str(text))]

def keyboard(buttons_list, row_width: int = 2):
    """
    Buttons builder, pass buttons in a list and it will
    return pyrogram.types.IKB object
    Ex: keyboard([["click here", "https://google.com"]])
    if theres, a url, it will make url button, else callback button
    """
    buttons = InlineKeyboard(row_width=row_width)
    data = [
        (
            kb(text=str(i[0]), callback_data=str(i[1]))
            if not is_url(i[1])
            else kb(text=str(i[0]), url=str(i[1]))
        )
        for i in buttons_list
    ]
    buttons.add(*data)
    return buttons


def ikb(data: dict, row_width: int = 2):
    """
    Converts a dict to pyrogram buttons
    Ex: dict_to_keyboard({"click here": "this is callback data"})
    """
    return keyboard(data.items(), row_width=row_width)

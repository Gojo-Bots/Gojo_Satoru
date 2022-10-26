from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ikb(rows=None, back=False):
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = []
        for button in row:
            btn_text = button.split(".")[1].upper()
            button = btn(btn_text, button)  # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    if back:
        back_btn = [(btn("Back", "start_back"))]
        lines.append(back_btn)
    return InlineKeyboardMarkup(inline_keyboard=lines)


def btn(text, value, type="callback_data"):
    return InlineKeyboardButton(text, **{type: value})

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu(is_manager: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="/today"), KeyboardButton(text="/limits")],
        [KeyboardButton(text="/add_expense"), KeyboardButton(text="/add_income")],
        [KeyboardButton(text="/goals"), KeyboardButton(text="/debts")],
        [KeyboardButton(text="/build"), KeyboardButton(text="/week"), KeyboardButton(text="/month")],
        [KeyboardButton(text="/decision"), KeyboardButton(text="/settings")],
    ]
    if is_manager:
        rows.append([KeyboardButton(text="/approve")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

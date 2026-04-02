from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu(is_manager: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="/today Сегодня"), KeyboardButton(text="/limits Лимиты")],
        [KeyboardButton(text="/add_expense Добавить расход"), KeyboardButton(text="/add_income Добавить доход")],
        [KeyboardButton(text="/goals Цели"), KeyboardButton(text="/debts Долги")],
        [KeyboardButton(text="/build Бюджет стройки"), KeyboardButton(text="/week Неделя"), KeyboardButton(text="/month Месяц")],
        [KeyboardButton(text="/decision Вопрос по трате"), KeyboardButton(text="/settings Настройки")],
    ]
    if is_manager:
        rows.append([KeyboardButton(text="/approve Согласование")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

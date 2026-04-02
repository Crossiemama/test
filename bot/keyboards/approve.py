from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def approval_kb(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{expense_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{expense_id}"),
            ]
        ]
    )

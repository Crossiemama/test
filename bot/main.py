from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import load_settings
from bot.db.session import Database
from bot.handlers.commands import router
from bot.services.bootstrap import init_db, seed_data
from bot.services.scheduler import build_scheduler


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()

    db = Database(settings.database_url)
    await init_db(db.engine)
    async with db.session() as session:
        await seed_data(session, settings)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await bot.set_my_commands([
        BotCommand(command="start", description="Меню"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="today", description="Сегодня"),
        BotCommand(command="add_expense", description="Добавить расход"),
        BotCommand(command="add_income", description="Добавить доход"),
        BotCommand(command="limits", description="Лимиты"),
        BotCommand(command="goals", description="Цели"),
        BotCommand(command="debts", description="Долги"),
        BotCommand(command="build", description="Бюджет стройки"),
        BotCommand(command="week", description="Неделя"),
        BotCommand(command="month", description="Месяц"),
        BotCommand(command="approve", description="Согласование"),
        BotCommand(command="decision", description="Вопрос по трате"),
        BotCommand(command="settings", description="Настройки"),
    ])
    dp = Dispatcher(storage=MemoryStorage())

    dp["session_maker"] = db.session
    dp["settings"] = settings
    dp.include_router(router)

    scheduler = build_scheduler(bot, db.session, settings.timezone)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

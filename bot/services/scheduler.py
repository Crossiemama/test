from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from bot.repositories import FinanceRepository, SettingsRepository, UserRepository
from bot.services.reporting import ReportingService


def build_scheduler(bot: Bot, session_maker, timezone: str) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone)

    async def send_weekly_report():
        async with session_maker() as session:
            users = await UserRepository(session).list_all()
            report = await ReportingService(FinanceRepository(session), SettingsRepository(session)).week_report(datetime.utcnow())
            for user in users:
                await bot.send_message(user.telegram_id, report, parse_mode="Markdown")

    async def send_distribution_day_reminder():
        async with session_maker() as session:
            users = await UserRepository(session).list_all()
            text = "Напоминание: сегодня день распределения денег. Проверьте лимиты, долги и фонд дома."
            for user in users:
                await bot.send_message(user.telegram_id, text)

    scheduler.add_job(send_weekly_report, CronTrigger(day_of_week="sun", hour=19, minute=0))
    scheduler.add_job(send_distribution_day_reminder, CronTrigger(day="10,25", hour=10, minute=0))
    return scheduler

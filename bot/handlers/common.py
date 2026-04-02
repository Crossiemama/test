from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import UserRole
from bot.repositories import UserRepository


async def resolve_user(session: AsyncSession, message: Message):
    repo = UserRepository(session)
    user = await repo.get_by_telegram_id(message.from_user.id)
    if not user:
        user = await repo.create(
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
            role=UserRole.USER.value,
        )
    return user


async def send_to_manager(bot: Bot, manager_id: int | None, text: str, **kwargs) -> None:
    if manager_id:
        await bot.send_message(manager_id, text, **kwargs)

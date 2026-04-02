from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from bot.config import Settings
from bot.models import Base, Debt, Goal, Limit, SystemSetting, User, UserRole


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data(session: AsyncSession, settings: Settings) -> None:
    async def _exists(stmt) -> bool:
        return (await session.execute(stmt)).first() is not None

    if settings.manager_telegram_id and not await _exists(select(User.id).where(User.telegram_id == settings.manager_telegram_id)):
        session.add(User(telegram_id=settings.manager_telegram_id, name=settings.manager_name, role=UserRole.MANAGER.value))
    if settings.user_telegram_id and not await _exists(select(User.id).where(User.telegram_id == settings.user_telegram_id)):
        session.add(User(telegram_id=settings.user_telegram_id, name=settings.user_name, role=UserRole.USER.value))

    default_limits = [
        ("Кафе", Decimal("10000")),
        ("Маркетплейсы", Decimal("12000")),
        ("Спонтанное", Decimal("8000")),
        ("Подарки/мелкие переводы", Decimal("5000")),
    ]
    for category, amount in default_limits:
        if not await _exists(select(Limit.id).where(Limit.category == category)):
            session.add(Limit(category=category, amount=amount))

    default_goals = [
        ("Переезд в дом", Decimal("1580000"), "HOME"),
        ("Подушка", Decimal("1500000"), "RESERVE"),
        ("Закрытие малого кредита", Decimal("266205.71"), "REQUIRED"),
        ("Закрытие большого кредита", Decimal("1551840.44"), "REQUIRED"),
    ]
    for title, target_amount, contour in default_goals:
        if not await _exists(select(Goal.id).where(Goal.title == title)):
            session.add(Goal(title=title, target_amount=target_amount, saved_amount=Decimal("0"), contour=contour))

    default_debts = [
        Debt(title="Ипотека", balance=Decimal("2200000"), monthly_payment=Decimal("22424.50"), interest_rate=Decimal("10.5"), priority=1),
        Debt(title="Кредит 1", balance=Decimal("1551840.44"), monthly_payment=Decimal("50400"), interest_rate=Decimal("16.99"), priority=2),
        Debt(title="Кредит 2", balance=Decimal("266205.71"), monthly_payment=Decimal("17780"), interest_rate=None, end_date=date(2028, 7, 19), priority=1),
        Debt(title="Строители", balance=Decimal("730000"), monthly_payment=None, interest_rate=None, priority=3),
        Debt(title="Материалы", balance=Decimal("450000"), monthly_payment=None, interest_rate=None, priority=3),
    ]
    for debt in default_debts:
        if not await _exists(select(Debt.id).where(Debt.title == debt.title)):
            session.add(debt)

    default_settings = [
        ("approval_threshold", str(settings.approval_threshold)),
        ("plan_income", "250000"),
        ("plan_expense", "200000"),
        ("underfunded_build_delta", str(settings.underfunded_build_delta)),
    ]
    for key, value in default_settings:
        if not await _exists(select(SystemSetting.id).where(SystemSetting.key == key)):
            session.add(SystemSetting(key=key, value=value))

    await session.commit()

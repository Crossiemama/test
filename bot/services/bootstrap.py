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
    users_count = (await session.execute(select(User))).scalars().first()
    if not users_count:
        if settings.manager_telegram_id:
            session.add(User(telegram_id=settings.manager_telegram_id, name=settings.manager_name, role=UserRole.MANAGER.value))
        if settings.user_telegram_id:
            session.add(User(telegram_id=settings.user_telegram_id, name=settings.user_name, role=UserRole.USER.value))

        session.add_all([
            Limit(category="Кафе", amount=Decimal("10000")),
            Limit(category="Маркетплейсы", amount=Decimal("12000")),
            Limit(category="Спонтанное", amount=Decimal("8000")),
            Limit(category="Подарки/мелкие переводы", amount=Decimal("5000")),
        ])
        session.add_all([
            Goal(title="Переезд в дом", target_amount=Decimal("1580000"), saved_amount=Decimal("0"), contour="HOME"),
            Goal(title="Подушка", target_amount=Decimal("1500000"), saved_amount=Decimal("0"), contour="RESERVE"),
            Goal(title="Закрытие малого кредита", target_amount=Decimal("266205.71"), saved_amount=Decimal("0"), contour="REQUIRED"),
            Goal(title="Закрытие большого кредита", target_amount=Decimal("1551840.44"), saved_amount=Decimal("0"), contour="REQUIRED"),
        ])
        session.add_all([
            Debt(title="Ипотека", balance=Decimal("2200000"), monthly_payment=Decimal("22424.50"), interest_rate=Decimal("10.5"), priority=1),
            Debt(title="Кредит 1", balance=Decimal("1551840.44"), monthly_payment=Decimal("50400"), interest_rate=Decimal("16.99"), priority=2),
            Debt(title="Кредит 2", balance=Decimal("266205.71"), monthly_payment=Decimal("17780"), interest_rate=None, end_date=date(2028, 7, 19), priority=1),
            Debt(title="Строители", balance=Decimal("730000"), monthly_payment=None, interest_rate=None, priority=3),
            Debt(title="Материалы", balance=Decimal("450000"), monthly_payment=None, interest_rate=None, priority=3),
        ])
        session.add_all([
            SystemSetting(key="approval_threshold", value=str(settings.approval_threshold)),
            SystemSetting(key="plan_income", value="250000"),
            SystemSetting(key="plan_expense", value="200000"),
            SystemSetting(key="underfunded_build_delta", value=str(settings.underfunded_build_delta)),
        ])
        await session.commit()

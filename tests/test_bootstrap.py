import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import Settings
from bot.models import Debt
from bot.services.bootstrap import init_db, seed_data


def test_seed_data_is_idempotent(tmp_path) -> None:
    db_file = tmp_path / "seed.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    settings = Settings(bot_token="123456:ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    async def _run() -> None:
        await init_db(engine)
        async with session_factory() as session:
            await seed_data(session, settings)
        async with session_factory() as session:
            await seed_data(session, settings)
            debt_count = await session.scalar(select(func.count()).select_from(Debt))
            assert debt_count == 5
        await engine.dispose()

    asyncio.run(_run())


def test_seed_data_adds_missing_records_without_duplicates(tmp_path) -> None:
    db_file = tmp_path / "seed_partial.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    settings = Settings(bot_token="123456:ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    async def _run() -> None:
        await init_db(engine)
        async with session_factory() as session:
            session.add(Debt(title="Ипотека", balance=1, monthly_payment=None, interest_rate=None, priority=1))
            await session.commit()

        async with session_factory() as session:
            await seed_data(session, settings)
            debt_count = await session.scalar(select(func.count()).select_from(Debt))
            assert debt_count == 5
        await engine.dispose()

    asyncio.run(_run())

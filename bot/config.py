from __future__ import annotations

from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    bot_token: str
    database_url: str = "sqlite+aiosqlite:///./finance_bot.db"
    approval_threshold: int = 10000
    timezone: str = "Europe/Moscow"
    manager_telegram_id: int | None = None
    manager_name: str = "Юлия"
    user_telegram_id: int | None = None
    user_name: str = "Антон"
    underfunded_build_delta: int = 50000



def load_settings() -> Settings:
    load_dotenv()
    token = getenv("BOT_TOKEN", "")
    if not token:
        raise ValueError("BOT_TOKEN не задан в .env")

    return Settings(
        bot_token=token,
        database_url=getenv("DATABASE_URL", "sqlite+aiosqlite:///./finance_bot.db"),
        approval_threshold=int(getenv("APPROVAL_THRESHOLD", "10000")),
        timezone=getenv("TIMEZONE", "Europe/Moscow"),
        manager_telegram_id=int(getenv("MANAGER_TELEGRAM_ID")) if getenv("MANAGER_TELEGRAM_ID") else None,
        manager_name=getenv("MANAGER_NAME", "Юлия"),
        user_telegram_id=int(getenv("USER_TELEGRAM_ID")) if getenv("USER_TELEGRAM_ID") else None,
        user_name=getenv("USER_NAME", "Антон"),
        underfunded_build_delta=int(getenv("UNDERFUNDED_BUILD_DELTA", "50000")),
    )

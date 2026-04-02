from sqlalchemy import select

from bot.models.entities import SystemSetting
from bot.repositories.base import BaseRepository


class SettingsRepository(BaseRepository):
    async def get(self, key: str, default: str | None = None) -> str | None:
        res = await self.session.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = res.scalar_one_or_none()
        return setting.value if setting else default

    async def set(self, key: str, value: str) -> None:
        res = await self.session.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = res.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            self.session.add(SystemSetting(key=key, value=value))
        await self.session.commit()

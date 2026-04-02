from sqlalchemy import select

from bot.models import User
from bot.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        res = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return res.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        res = await self.session.execute(select(User))
        return list(res.scalars().all())

    async def create(self, telegram_id: int, name: str, role: str) -> User:
        user = User(telegram_id=telegram_id, name=name, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

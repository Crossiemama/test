from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, func, select

from bot.models import Debt, Expense, Goal, Income, Limit
from bot.repositories.base import BaseRepository


class FinanceRepository(BaseRepository):
    async def add_income(self, **kwargs) -> Income:
        entity = Income(**kwargs)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def add_expense(self, **kwargs) -> Expense:
        entity = Expense(**kwargs)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def list_pending_expenses(self) -> list[Expense]:
        res = await self.session.execute(select(Expense).where(Expense.approval_status == "pending").order_by(Expense.created_at))
        return list(res.scalars().all())

    async def update_expense_status(self, expense_id: int, status: str, approved_by: int | None = None) -> Expense | None:
        res = await self.session.execute(select(Expense).where(Expense.id == expense_id))
        exp = res.scalar_one_or_none()
        if not exp:
            return None
        exp.approval_status = status
        exp.approved_by = approved_by
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def month_income_total(self, start: datetime, end: datetime) -> Decimal:
        res = await self.session.execute(select(func.coalesce(func.sum(Income.amount), 0)).where(and_(Income.created_at >= start, Income.created_at < end)))
        return Decimal(res.scalar_one())

    async def month_expense_total(self, start: datetime, end: datetime, approved_only: bool = True) -> Decimal:
        stmt = select(func.coalesce(func.sum(Expense.amount), 0)).where(and_(Expense.created_at >= start, Expense.created_at < end))
        if approved_only:
            stmt = stmt.where(Expense.approval_status == "approved")
        res = await self.session.execute(stmt)
        return Decimal(res.scalar_one())

    async def expense_by_category(self, start: datetime, end: datetime) -> dict[str, Decimal]:
        res = await self.session.execute(
            select(Expense.category, func.coalesce(func.sum(Expense.amount), 0))
            .where(and_(Expense.created_at >= start, Expense.created_at < end, Expense.approval_status == "approved"))
            .group_by(Expense.category)
        )
        return {row[0]: Decimal(row[1]) for row in res.all()}

    async def list_limits(self) -> list[Limit]:
        res = await self.session.execute(select(Limit))
        return list(res.scalars().all())

    async def list_goals(self) -> list[Goal]:
        res = await self.session.execute(select(Goal).order_by(Goal.id))
        return list(res.scalars().all())

    async def list_debts(self) -> list[Debt]:
        res = await self.session.execute(select(Debt).order_by(Debt.priority, Debt.id))
        return list(res.scalars().all())

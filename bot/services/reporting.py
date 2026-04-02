from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from bot.repositories import FinanceRepository, SettingsRepository
from bot.services.business_rules import BusinessRulesService
from bot.utils.dates import month_bounds, week_bounds
from bot.utils.formatting import money


class ReportingService:
    def __init__(self, finance_repo: FinanceRepository, settings_repo: SettingsRepository):
        self.finance_repo = finance_repo
        self.settings_repo = settings_repo
        self.rules = BusinessRulesService()

    async def today_summary(self, now: datetime) -> str:
        start, end = month_bounds(now)
        income = await self.finance_repo.month_income_total(start, end)
        expense = await self.finance_repo.month_expense_total(start, end)
        free_flow = income - expense
        lines = [
            f"*Сегодня / месяц:* {now:%m.%Y}",
            f"Доходы: *{money(income)}*",
            f"Расходы: *{money(expense)}*",
            f"Свободный поток: *{money(free_flow)}*",
        ]

        limits = await self._limits_block(start, end)
        goals = await self._goals_short_block()
        debts = await self.finance_repo.list_debts()
        nearest_debts = ", ".join(d.title for d in debts[:2]) if debts else "нет"
        lines.extend([
            "\n*Лимиты в риске:*",
            limits,
            f"\n*Ближайшие обязательства:* {nearest_debts}",
            "\n*Цели:*",
            goals,
        ])
        return "\n".join(lines)

    async def limits_report(self, now: datetime) -> str:
        start, end = month_bounds(now)
        spent_map = await self.finance_repo.expense_by_category(start, end)
        lines = ["*Лимиты на месяц:*"]
        for limit in await self.finance_repo.list_limits():
            spent = spent_map.get(limit.category, Decimal("0"))
            percent, status = self.rules.category_limit_status(spent, limit.amount)
            lines.append(
                f"• {limit.category}: лимит {money(limit.amount)}, потрачено {money(spent)}, остаток {money(limit.amount-spent)}, {percent:.1f}% — *{status}*"
            )
        return "\n".join(lines)

    async def goals_report(self) -> str:
        lines = ["*Финансовые цели:*"]
        for goal in await self.finance_repo.list_goals():
            left = goal.target_amount - goal.saved_amount
            status = "В процессе" if left > 0 else "Достигнута"
            deadline = goal.deadline.isoformat() if goal.deadline else "—"
            lines.append(
                f"• {goal.title}: цель {money(goal.target_amount)}, накоплено {money(goal.saved_amount)}, осталось {money(left)}, дедлайн {deadline}, статус *{status}*"
            )
        return "\n".join(lines)

    async def debts_report(self) -> str:
        lines = ["*Долги:*"]
        for debt in await self.finance_repo.list_debts():
            lines.append(
                f"• {debt.title}: остаток {money(debt.balance)}, платеж {money(debt.monthly_payment or Decimal('0'))}, ставка {debt.interest_rate or '-'}%, окончание {debt.end_date or '-'}, приоритет {debt.priority}"
            )
        return "\n".join(lines)

    async def build_report(self) -> str:
        goals = await self.finance_repo.list_goals()
        home_goal = next((g for g in goals if "дом" in g.title.lower() or "переезд" in g.title.lower()), None)
        if not home_goal:
            return "Цель фонда дома не найдена."
        left = home_goal.target_amount - home_goal.saved_amount
        return (
            "*Фонд дома:*\n"
            f"Цель: {money(home_goal.target_amount)}\n"
            f"Накоплено: {money(home_goal.saved_amount)}\n"
            f"Остаток: {money(left)}\n"
            f"Статус: {'Риск недофинансирования' if left > 0 else 'Норма'}"
        )

    async def week_report(self, now: datetime) -> str:
        start, end = week_bounds(now)
        income = await self.finance_repo.month_income_total(start, end)
        expense = await self.finance_repo.month_expense_total(start, end)
        lines = [
            "*Недельный отчет:*",
            f"Доходы недели: {money(income)}",
            f"Расходы недели: {money(expense)}",
            f"Отклонение: {money(income-expense)}",
            "Рекомендация: держать расходы категорий Кафе и Маркетплейсы под контролем.",
        ]
        return "\n".join(lines)

    async def month_report(self, now: datetime) -> str:
        start, end = month_bounds(now)
        plan_income = Decimal(await self.settings_repo.get("plan_income", "250000"))
        plan_expense = Decimal(await self.settings_repo.get("plan_expense", "200000"))
        fact_income = await self.finance_repo.month_income_total(start, end)
        fact_expense = await self.finance_repo.month_expense_total(start, end)
        plan_flow = plan_income - plan_expense
        fact_flow = fact_income - fact_expense
        status = self.rules.month_status(plan_flow, fact_flow)
        return (
            "*Месячный отчет:*\n"
            f"Доход план/факт: {money(plan_income)} / {money(fact_income)}\n"
            f"Расход план/факт: {money(plan_expense)} / {money(fact_expense)}\n"
            f"Свободный поток: {money(fact_flow)}\n"
            f"Отклонение: {money(fact_flow-plan_flow)}\n"
            f"Статус месяца: *{status}*\n"
            "Ключевые риски: перерасход лимитов и недофинансирование дома."
        )

    async def _goals_short_block(self) -> str:
        goals = await self.finance_repo.list_goals()
        if not goals:
            return "целей пока нет"
        return "\n".join([f"• {g.title}: {money(g.saved_amount)}/{money(g.target_amount)}" for g in goals[:3]])

    async def _limits_block(self, start: datetime, end: datetime) -> str:
        spent_map = await self.finance_repo.expense_by_category(start, end)
        chunks = []
        for limit in await self.finance_repo.list_limits():
            spent = spent_map.get(limit.category, Decimal("0"))
            percent, status = self.rules.category_limit_status(spent, limit.amount)
            if status in {"Риск", "Стоп"}:
                chunks.append(f"• {limit.category}: {percent:.1f}% ({status})")
        return "\n".join(chunks) if chunks else "нет"

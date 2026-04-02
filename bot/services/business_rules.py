from decimal import Decimal

from bot.utils.formatting import limit_status


class BusinessRulesService:
    """Pure business rules used by handlers and reports."""

    @staticmethod
    def needs_approval(amount: Decimal, threshold: Decimal) -> bool:
        return amount > threshold

    @staticmethod
    def category_limit_status(spent: Decimal, limit_amount: Decimal) -> tuple[Decimal, str]:
        if limit_amount == 0:
            return Decimal("0"), "Норма"
        percent = (spent / limit_amount) * Decimal("100")
        return percent, limit_status(percent)

    @staticmethod
    def month_status(plan_flow: Decimal, actual_flow: Decimal) -> str:
        if plan_flow == 0:
            return "желтый"
        diff = (plan_flow - actual_flow) / plan_flow
        if diff > Decimal("0.15"):
            return "красный"
        if diff > Decimal("0.05"):
            return "желтый"
        return "зеленый"

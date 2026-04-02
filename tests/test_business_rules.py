from decimal import Decimal

from bot.services.business_rules import BusinessRulesService


rules = BusinessRulesService()


def test_needs_approval_threshold():
    assert rules.needs_approval(Decimal("10000.01"), Decimal("10000")) is True
    assert rules.needs_approval(Decimal("10000"), Decimal("10000")) is False


def test_limit_status_boundaries():
    p, status = rules.category_limit_status(Decimal("7000"), Decimal("10000"))
    assert p == Decimal("70")
    assert status == "Внимание"

    _, status2 = rules.category_limit_status(Decimal("9500"), Decimal("10000"))
    assert status2 == "Риск"

    _, status3 = rules.category_limit_status(Decimal("10000"), Decimal("10000"))
    assert status3 == "Стоп"


def test_month_status():
    assert rules.month_status(Decimal("100000"), Decimal("83000")) == "красный"
    assert rules.month_status(Decimal("100000"), Decimal("93000")) == "желтый"
    assert rules.month_status(Decimal("100000"), Decimal("98000")) == "зеленый"

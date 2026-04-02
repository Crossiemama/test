from decimal import Decimal


def money(value: Decimal) -> str:
    return f"{value:,.2f}".replace(",", " ") + " ₽"


def limit_status(percent: Decimal) -> str:
    if percent >= Decimal("100"):
        return "Стоп"
    if percent >= Decimal("90"):
        return "Риск"
    if percent >= Decimal("70"):
        return "Внимание"
    return "Норма"

from enum import Enum


class _StrEnum(str, Enum):
    """Py3.10-compatible replacement for StrEnum."""


class UserRole(_StrEnum):
    MANAGER = "manager"
    USER = "user"


class MoneyContour(_StrEnum):
    OPERATING = "OPERATING"
    REQUIRED = "REQUIRED"
    HOME = "HOME"
    RESERVE = "RESERVE"
    CAPITAL = "CAPITAL"


class ExpenseCategory(_StrEnum):
    PRODUCTS = "Продукты"
    CHILD = "Ребенок"
    CAFE = "Кафе"
    MARKETPLACE = "Маркетплейсы"
    IMPULSE = "Спонтанное"
    HOME = "Дом"
    DEBTS = "Долги"
    RENT = "Аренда"
    CUSHION = "Подушка"
    INVESTMENTS = "Инвестиции"
    OTHER = "Прочее"
    GIFTS = "Подарки/мелкие переводы"


class ApprovalStatus(_StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

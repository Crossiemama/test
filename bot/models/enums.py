from enum import Enum


class StrEnum(str, Enum):
    """Python 3.10-compatible replacement for enum.StrEnum."""


class UserRole(StrEnum):
    MANAGER = "manager"
    USER = "user"


class MoneyContour(StrEnum):
    OPERATING = "OPERATING"
    REQUIRED = "REQUIRED"
    HOME = "HOME"
    RESERVE = "RESERVE"
    CAPITAL = "CAPITAL"


class ExpenseCategory(StrEnum):
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


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

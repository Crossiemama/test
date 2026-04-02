from aiogram.fsm.state import State, StatesGroup


class AddExpenseState(StatesGroup):
    category = State()
    contour = State()
    amount = State()
    comment = State()
    spender = State()


class AddIncomeState(StatesGroup):
    member = State()
    income_type = State()
    amount = State()
    source = State()
    comment = State()


class DecisionState(StatesGroup):
    text = State()
    reason = State()
    valid_until = State()
    comment = State()

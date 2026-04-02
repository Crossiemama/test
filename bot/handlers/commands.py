from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.common import resolve_user
from bot.handlers.states import AddExpenseState, AddIncomeState, DecisionState
from bot.keyboards.approve import approval_kb
from bot.keyboards.main import main_menu
from bot.models import ApprovalStatus, Decision
from bot.repositories import FinanceRepository, SettingsRepository
from bot.services.reporting import ReportingService

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message, session_maker):
    async with session_maker() as session:
        user = await resolve_user(session, message)
        await message.answer(
            f"Привет, {user.name}! Я бот семейных финансов. Выберите команду в меню.",
            reply_markup=main_menu(user.role == "manager"),
        )


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Доступные команды: /today /add_expense /add_income /limits /goals /debts /build /week /month /approve /decision /settings"
    )


@router.message(Command("today"))
async def today_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.today_summary(datetime.utcnow()), parse_mode="Markdown")


@router.message(Command("limits"))
async def limits_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.limits_report(datetime.utcnow()), parse_mode="Markdown")


@router.message(Command("goals"))
async def goals_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.goals_report(), parse_mode="Markdown")


@router.message(Command("debts"))
async def debts_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.debts_report(), parse_mode="Markdown")


@router.message(Command("build"))
async def build_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.build_report(), parse_mode="Markdown")


@router.message(Command("week"))
async def week_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.week_report(datetime.utcnow()), parse_mode="Markdown")


@router.message(Command("month"))
async def month_cmd(message: Message, session_maker):
    async with session_maker() as session:
        service = ReportingService(FinanceRepository(session), SettingsRepository(session))
        await message.answer(await service.month_report(datetime.utcnow()), parse_mode="Markdown")


@router.message(Command("add_expense"))
async def add_expense_start(message: Message, state: FSMContext):
    await state.set_state(AddExpenseState.category)
    await message.answer("Категория? (например: Кафе, Маркетплейсы, Продукты)")


@router.message(AddExpenseState.category)
async def add_expense_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddExpenseState.contour)
    await message.answer("Контур? (OPERATING/REQUIRED/HOME/RESERVE/CAPITAL)")


@router.message(AddExpenseState.contour)
async def add_expense_contour(message: Message, state: FSMContext):
    await state.update_data(contour=message.text)
    await state.set_state(AddExpenseState.amount)
    await message.answer("Сумма?")


@router.message(AddExpenseState.amount)
async def add_expense_amount(message: Message, state: FSMContext):
    await state.update_data(amount=message.text.replace(",", "."))
    await state.set_state(AddExpenseState.comment)
    await message.answer("Комментарий? (или '-' )")


@router.message(AddExpenseState.comment)
async def add_expense_comment(message: Message, state: FSMContext):
    await state.update_data(comment=None if message.text == "-" else message.text)
    await state.set_state(AddExpenseState.spender)
    await message.answer("Кто потратил?")


@router.message(AddExpenseState.spender)
async def add_expense_finish(message: Message, state: FSMContext, session_maker, bot, settings):
    from decimal import Decimal

    data = await state.get_data()
    async with session_maker() as session:
        user = await resolve_user(session, message)
        repo = FinanceRepository(session)
        srepo = SettingsRepository(session)
        threshold = Decimal(await srepo.get("approval_threshold", str(settings.approval_threshold)))
        amount = Decimal(data["amount"])
        approval_status = ApprovalStatus.PENDING.value if amount > threshold else ApprovalStatus.APPROVED.value

        expense = await repo.add_expense(
            user_id=user.id,
            category=data["category"],
            contour=data["contour"],
            amount=amount,
            comment=data["comment"],
            spender_name=message.text,
            approval_status=approval_status,
        )

        if approval_status == ApprovalStatus.PENDING.value:
            await message.answer("Расход сохранён и отправлен на согласование менеджеру.")
            if settings.manager_telegram_id:
                await bot.send_message(
                    settings.manager_telegram_id,
                    f"Нужна проверка расхода #{expense.id}: {expense.category}, {expense.amount} ₽, {expense.comment or '-'}",
                    reply_markup=approval_kb(expense.id),
                )
        else:
            await message.answer("Расход сохранён ✅")

    await state.clear()


@router.message(Command("add_income"))
async def add_income_start(message: Message, state: FSMContext):
    await state.set_state(AddIncomeState.member)
    await message.answer("Кто получил доход?")


@router.message(AddIncomeState.member)
async def add_income_member(message: Message, state: FSMContext):
    await state.update_data(member=message.text)
    await state.set_state(AddIncomeState.income_type)
    await message.answer("Тип дохода? (зарплата/аванс/больничный/премия/соцвыплата/прочее)")


@router.message(AddIncomeState.income_type)
async def add_income_type(message: Message, state: FSMContext):
    await state.update_data(income_type=message.text)
    await state.set_state(AddIncomeState.amount)
    await message.answer("Сумма?")


@router.message(AddIncomeState.amount)
async def add_income_amount(message: Message, state: FSMContext):
    await state.update_data(amount=message.text.replace(",", "."))
    await state.set_state(AddIncomeState.source)
    await message.answer("Источник?")


@router.message(AddIncomeState.source)
async def add_income_source(message: Message, state: FSMContext):
    await state.update_data(source=message.text)
    await state.set_state(AddIncomeState.comment)
    await message.answer("Комментарий? (или '-')")


@router.message(AddIncomeState.comment)
async def add_income_finish(message: Message, state: FSMContext, session_maker):
    from decimal import Decimal

    data = await state.get_data()
    async with session_maker() as session:
        user = await resolve_user(session, message)
        repo = FinanceRepository(session)
        await repo.add_income(
            user_id=user.id,
            income_type=data["income_type"],
            amount=Decimal(data["amount"]),
            source=data["source"],
            comment=None if message.text == "-" else message.text,
        )
    await message.answer("Доход сохранён ✅")
    await state.clear()


@router.message(Command("approve"))
async def approve_cmd(message: Message, session_maker):
    async with session_maker() as session:
        user = await resolve_user(session, message)
        if user.role != "manager":
            await message.answer("Команда доступна только manager.")
            return
        pending = await FinanceRepository(session).list_pending_expenses()
        if not pending:
            await message.answer("Нет расходов на согласование.")
            return
        for exp in pending:
            await message.answer(
                f"#{exp.id} | {exp.category} | {exp.amount} ₽ | {exp.spender_name}",
                reply_markup=approval_kb(exp.id),
            )


@router.callback_query(F.data.startswith("approve:") | F.data.startswith("reject:"))
async def approve_callback(callback: CallbackQuery, session_maker):
    action, expense_id_s = callback.data.split(":")
    expense_id = int(expense_id_s)
    async with session_maker() as session:
        user = await resolve_user(session, callback.message)
        if user.role != "manager":
            await callback.answer("Недостаточно прав", show_alert=True)
            return
        repo = FinanceRepository(session)
        status = "approved" if action == "approve" else "rejected"
        exp = await repo.update_expense_status(expense_id, status=status, approved_by=user.id)
        await callback.message.edit_text(f"Расход #{expense_id}: {status}")
        await callback.answer("Готово")


@router.message(Command("decision"))
async def decision_start(message: Message, state: FSMContext):
    await state.set_state(DecisionState.text)
    await message.answer("Текст управленческого решения:")


@router.message(DecisionState.text)
async def decision_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(DecisionState.reason)
    await message.answer("Причина:")


@router.message(DecisionState.reason)
async def decision_reason(message: Message, state: FSMContext):
    await state.update_data(reason=message.text)
    await state.set_state(DecisionState.valid_until)
    await message.answer("Срок действия (YYYY-MM-DD) или '-':")


@router.message(DecisionState.valid_until)
async def decision_until(message: Message, state: FSMContext):
    await state.update_data(valid_until=None if message.text == "-" else message.text)
    await state.set_state(DecisionState.comment)
    await message.answer("Комментарий (или '-'):")


@router.message(DecisionState.comment)
async def decision_finish(message: Message, state: FSMContext, session_maker):
    from datetime import date

    data = await state.get_data()
    async with session_maker() as session:
        user = await resolve_user(session, message)
        valid_until = date.fromisoformat(data["valid_until"]) if data["valid_until"] else None
        session.add(
            Decision(
                author_id=user.id,
                text=data["text"],
                reason=data["reason"],
                valid_until=valid_until,
                comment=None if message.text == "-" else message.text,
            )
        )
        await session.commit()
    await message.answer("Решение сохранено ✅")
    await state.clear()


@router.message(Command("settings"))
async def settings_cmd(message: Message, session_maker):
    async with session_maker() as session:
        srepo = SettingsRepository(session)
        threshold = await srepo.get("approval_threshold", "10000")
        underfund = await srepo.get("underfunded_build_delta", "50000")
        await message.answer(
            "*Настройки:*\n"
            f"Порог согласования: {threshold} ₽\n"
            "Напоминания: 10 и 25 числа в 10:00\n"
            "Недельный отчёт: воскресенье 19:00\n"
            f"Допустимое недофинансирование дома: {underfund} ₽\n"
            "Для изменения в MVP используйте редактирование SystemSetting в БД.",
            parse_mode="Markdown",
        )

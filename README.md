# MVP Telegram-бот семейных финансов

Практичный MVP-бот на **Python 3.11+ / aiogram 3.x / SQLite / SQLAlchemy** для контроля доходов/расходов, лимитов, целей, долгов и фонда дома.

## Что реализовано в MVP

- Роли: `manager`, `user`.
- Сущности: `User`, `Income`, `Expense`, `Limit`, `Goal`, `Debt`, `Decision`, `SystemSetting`, `NotificationLog`.
- Команды: `/start`, `/help`, `/today`, `/add_expense`, `/add_income`, `/limits`, `/goals`, `/debts`, `/build`, `/week`, `/month`, `/approve`, `/decision`, `/settings`.
- Мастер добавления расхода/дохода (FSM).
- Согласование трат выше порога (`approval_threshold`, по умолчанию 10000).
- Авто-отчеты по расписанию:
  - воскресенье 19:00 — недельный отчет;
  - 10 и 25 числа в 10:00 — напоминание о распределении денег.
- Автосоздание таблиц при первом запуске + seed-данные.
- Базовые тесты бизнес-логики.

## Важные MVP-упрощения

Чтобы сохранить надежность и скорость внедрения:

1. В `/settings` настройки пока отображаются; изменение значений — через БД (`SystemSetting`).
2. Прогнозная дата достижения целей и рекомендованный план по долгам в простом виде (без сложной финансовой модели).
3. Формы ввода в командах используют короткий текстовый ввод, но ключевые действия (меню + согласование) уже через кнопки.

## Архитектура

```text
bot/
  db/
    session.py
  handlers/
    commands.py
    common.py
    states.py
  keyboards/
    approve.py
    main.py
  models/
    base.py
    entities.py
    enums.py
  repositories/
    base.py
    finance_repo.py
    settings_repo.py
    user_repo.py
  services/
    bootstrap.py
    business_rules.py
    reporting.py
    scheduler.py
  utils/
    dates.py
    formatting.py
  config.py
  main.py
tests/
  test_business_rules.py
.env.example
requirements.txt
```

## Быстрый старт

### 1) Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Настройка окружения

```bash
cp .env.example .env
```

Заполните минимум `BOT_TOKEN`.
Указывайте токен **без кавычек и пробелов** (как выдал `@BotFather`), иначе запуск завершится ошибкой валидации токена.

### 3) Запуск

```bash
python -m bot.main
```

При первом запуске:
- таблицы в SQLite создаются автоматически;
- сидируются стартовые данные (лимиты, цели, долги, настройки, пользователи если указаны telegram id).

## Seed-данные

### Лимиты
- Кафе = 10000
- Маркетплейсы = 12000
- Спонтанное = 8000
- Подарки/мелкие переводы = 5000

### Цели
- Переезд в дом = 1580000
- Подушка = 1500000
- Закрытие малого кредита = 266205.71
- Закрытие большого кредита = 1551840.44

### Долги
- Ипотека = 2200000, платеж 22424.50, ставка 10.5
- Кредит 1 = 1551840.44, платеж 50400, ставка 16.99
- Кредит 2 = 266205.71, платеж 17780, дата окончания 2028-07-19
- Строители = 730000
- Материалы = 450000

## Точки расширения (заложены)

1. **Google Sheets интеграция**
   - добавить `services/integrations/google_sheets.py`
   - вызывать из `reporting.py` и/или фоновых задач.
2. **Импорт CSV/банковских выписок**
   - добавить `services/importers/csv_importer.py`
   - сохранять через `FinanceRepository`.
3. **Аналитика капитала**
   - добавить модуль `services/analytics/capital.py`
   - подключить отдельную команду `/capital`.
4. **Мобильный клиент / API**
   - вынести бизнес-логику в отдельный application-слой;
   - добавить FastAPI поверх текущих repository/service.

## Тесты

```bash
pytest
```

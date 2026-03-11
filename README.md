# TZ Pipeline

Набор утилит для:
1. Сбора и нормализации данных из источников (ATS Energo / SO-UPS / NP SR и др.).
2. Подготовки DOCX-документа из ТЗ в markdown с оформлением, приближенным к ГОСТ 7.32-2017.

## Установка

```bash
pip install -e .
```

или

```bash
pip install -r requirements.txt
```

## Сбор и обработка данных

Подготовьте YAML-конфиг на основе `config/sources.example.yaml`.

```bash
tz-pipeline collect --config config/sources.example.yaml --output artifacts/collected.csv
```

Что делает команда:
- запускает коллекторы по каждому источнику;
- объединяет данные по `datetime`;
- нормализует временную сетку;
- выполняет безопасную импутацию (`ffill/bfill`);
- оставляет только рабочие дни (`workday_only: true`).

## Формирование DOCX

```bash
tz-pipeline build-docx --input-md technical_specification_ru.md --output-docx artifacts/technical_specification_ru.docx
```

Что делает команда:
- читает markdown-файл ТЗ;
- применяет параметры оформления (Times New Roman 14, межстрочный 1.5, поля 3/1.5/2/2 см);
- сохраняет документ в `.docx`.

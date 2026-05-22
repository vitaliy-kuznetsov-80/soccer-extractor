# soccer-extractor

Инструмент парсинга коэффициентов для ставок на футбол. Собирает данные с букмекерского сайта через Selenium, экспортирует в Excel.

## Запуск

```bash
pip3 install -r requirements.txt

python run_europe.py    # Европа
python run_america.py   # Америка
python run_asia.py      # Азия
python main_results.py  # Результаты матчей
python run_scheduler.py # Запуск по расписанию (все регионы)
```

## Архитектура

```
main.py              — точка входа (принимает RegionEnum)
main_results.py      — сбор результатов вчерашних матчей
run_scheduler.py     — планировщик (schedule library)
src/
  dto/               — модели данных (GameDto, LineDto, RegionEnum и др.)
  parcer/            — парсеры страниц
    lines_parser.py  — список линий (матчей) региона
    games_parser.py  — коэффициенты по каждой игре
    results_parser.py — парсер результатов игр 
    Outcome/         — исходы 1X2
    Total/           — тоталы
    IndividualTotal/ — индивидуальные тоталы
    BothWillScore/   - обе забьют
    DoubleOutcome/   — двойной исход
    Goals/
  utils/
    config.py        — загрузка appsettings.json
    excel_manager.py — генерация .xls (xlwt)
    logger.py
  page.py            — обёртка над Selenium WebDriver
config/
  appsettings.json       — основной конфиг
  appsettings.local.json — локальные переопределения (в .gitignore)
assets/
  template.xls           — шаблон Excel
  europe/america/asia.txt — whitelist линий
  ignore-soccer.txt       — исключения
  europe.json             — матрица золотых коэффициентов
```

## Конфигурация (appsettings.json)

| Ключ | Описание |
|------|----------|
| `general.page_load_timeout` | Таймаут загрузки страницы (сек) |
| `general.element_load_timeout` | Таймаут ожидания элемента (сек) |
| `general.retry_count` | Число повторных попыток |
| `general.retry_period` | Интервал между попытками (сек) |
| `debug.LOG_IN_CONSOLE` | true — в консоль, false — в файл |
| `debug.LINES_LIMIT` | Лимит линий (0 = без лимита) |
| `debug.ONLY_LINE_ID` | Запустить одну линию по ID |
| `debug.ONLY_GAME_ID` | Запустить одну игру по ID |
| `scheduler.day_offset` | Сдвиг часов для имени файла Excel |
| `scheduler.europe/america/asia` | Время запуска по расписанию |

`appsettings.local.json` перезатирает значения из `appsettings.json`.

## Стек

- **Python 3.6+**
- **Selenium 4.41** — браузерная автоматизация (Chrome)
- **xlwt / xlrd / xlutils** — работа с `.xls`
- **schedule** — планировщик задач
- **json5** — конфиг с поддержкой комментариев

## Соглашения

- Код и комментарии на русском языке
- DTO-классы в `src/dto/`, парсеры в `src/parcer/`
- Логи пишутся в папку `logs/`, результаты в `results/`
- Версия отслеживается в `history.md`
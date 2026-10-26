# Pokemon Battle — API-автотесты на Pytest + Requests

Учебный проект по автоматизации тестирования API веб-приложения [«Битва Покемонов»](https://pokemonbattle.ru) — тренажёра для QA-инженеров. Тесты написаны во время прохождения курса по автоматизации на Python.

Проект покрывает два сервиса:

- **API покемонов** (`api.pokemonbattle.ru/v2`): тренеры, покемоны, битвы, достижения;
- **Лавка** (`lavka.pokemonbattle.ru`): покупка подписки Pokemon Premium по карте.

## Стек

| Инструмент | Для чего используется |
|---|---|
| [Python 3.12+](https://www.python.org/) | Язык тестов (в коде есть f-строки с вложенными кавычками одного типа, а они работают только с 3.12) |
| [Pytest](https://docs.pytest.org/) | Тестовый раннер, фикстуры, параметризация, маркеры |
| [Requests](https://requests.readthedocs.io/) | HTTP-клиент, общая `Session` с заголовком авторизации |
| [jsonschema](https://python-jsonschema.readthedocs.io/) + [PyYAML](https://pyyaml.org/) | Валидация ответов по JSON-схемам, описанным в YAML |
| [DeepDiff](https://zepworks.com/deepdiff/) | Сравнение тела ответа с эталонной структурой с исключением динамических полей |
| [pytest-check](https://pypi.org/project/pytest-check/) | Мягкие проверки: тест не падает на первом несовпадении |
| [pytest-dotenv](https://pypi.org/project/pytest-dotenv/) + [python-dotenv](https://pypi.org/project/python-dotenv/) | Загрузка токена и тестовых данных из `.env` при старте pytest |
| [Allure](https://allurereport.org/docs/pytest/) (`allure-pytest`) | Отчёты: шаги `allure.step`, заголовки, сьюты, вложения с запросами и ответами |

## Структура проекта

```
.
├── config/
│   └── api_config.py          # базовые URL: api.pokemonbattle.ru/v2 и lavka.pokemonbattle.ru
├── data/
│   └── api_endpoints.py       # эндпоинты: /trainers, /pokemons, /battle, /achievements, /payments
├── fixtures/
│   └── api_fixures.py         # API-сессия, подготовка данных для битвы, CRUD и премиума
├── helpers/
│   ├── api_helpers.py         # обёртка ApiSession: логирование в Allure и обход rate limiter
│   └── file_helpers.py        # загрузка JSON-схем из папки schemas/
├── schemas/
│   ├── achievements.yml       # схема ответа GET /achievements
│   └── battles.yml            # схема ответа GET /battle
├── tests/
│   ├── test_api_lavka_premium.py
│   ├── test_api_pokemon_achievements.py
│   ├── test_api_pokemon_battle.py
│   ├── test_api_pokemon_crud.py
│   └── test_api_pokemon_trainers.py
├── .env                       # токен тренера и тестовые данные карт
├── conftest.py                # подключение плагина с фикстурами
├── index.zip                  # пример сгенерированного Allure-отчёта (single file)
├── pytest.ini                 # addopts и маркеры
└── requirements.txt
```

## Архитектура и подходы

- **Обёртка над сессией.** Все запросы идут через `ApiSession` (`helpers/api_helpers.py`) с методами `get` / `post` / `patch`. Каждый вызов оформлен как шаг Allure, а к отчёту прикладываются URL, заголовки и тела запроса и ответа.
- **Обход rate limiter.** Если тренажёр отвечает `400` с сообщением «Лимит запросов превышен», `ApiSession` повторяет запрос раз в секунду в течение 5 секунд, а потом падает с понятной ошибкой.
- **Одна сессия на прогон.** Фикстура `api_session` (scope `session`) создаёт `requests.Session` с заголовком `trainer_token` из `.env`, и её переиспользуют все тесты.
- **Подготовка и очистка данных через API:**
  - `knockout_trainer_pokemons` отправляет в нокаут всех живых покемонов тренера и проверяет, что их статус стал `0`;
  - `create_pokemon` после очистки создаёт нового покемона для CRUD-тестов;
  - `prepare_and_clear_battle` ищет покемона тренера в покеболе. Если такого нет, сажает в покебол живого покемона или создаёт нового. После теста отправляет его в нокаут;
  - `check_and_cancel_premium` через `GET /me` проверяет, есть ли у тренера премиум, и при необходимости отменяет его через `POST /cancel_premium`. Так тренер остаётся в исходном состоянии и до теста, и после.
- **Валидация схем.** Ответы `/achievements` и `/battle` проверяются `jsonschema` по YAML-схемам с `additionalProperties: false`, поэтому лишнее поле в ответе тоже уронит тест.
- **Сравнение с эталоном.** Список достижений сравнивается с шаблоном через `DeepDiff`, а динамическое поле `is_reached` исключено регуляркой.
- **Параметризация.** Негативные сценарии покупки премиума запускаются одним тестом с разными невалидными полями, а заголовки кейсов в Allure задаются через `allure.dynamic.title`.
- **Вынесенные константы.** URL и эндпоинты лежат отдельно от тестов, в `config/` и `data/`.

## Покрытые сценарии

### Тренеры — `test_api_pokemon_trainers.py`

| Тест | Маркер | Что проверяет |
|---|---|---|
| `test_get_trainers_by_city_success` | `smoke` | `GET /trainers?city=Subotica`: статус 200, город тренера в ответе совпадает с запрошенным |
| `test_get_trainer_by_id_success` | `smoke` | `GET /trainers?trainer_id=...`: статус 200, ID тренера совпадает |
| `test_get_trainers_by_id_sorted_level_desc_success` | `regress` | `GET /trainers?city=Moscow&sort=desc_level`: все тренеры из Москвы, уровни отсортированы по убыванию |

### Покемоны — `test_api_pokemon_crud.py`

| Тест | Маркер | Что проверяет |
|---|---|---|
| `test_patch_pokemon_success` | `smoke` | `PATCH /pokemons/{id}`: смена имени созданного покемона, статус 200 и сообщение «Информация о покемоне обновлена» |
| `test_get_updated_pokemon_success` | — | `GET /pokemons/{id}`: имя обновилось (сейчас под `skip`) |

### Битвы — `test_api_pokemon_battle.py`

| Тест | Маркер | Что проверяет |
|---|---|---|
| `test_get_battles_success` | `smoke` | `GET /battle`: статус 200, ответ соответствует схеме `battles.yml` |
| `test_run_battle_successfully` | — | Полный флоу битвы: поиск чужого покемона в покеболе → `POST /battle` → проверка статуса своего покемона. После поражения покемон в нокауте и вне покебола, после победы остаётся активным в покеболе |

### Достижения — `test_api_pokemon_achievements.py`

| Тест | Маркер | Что проверяет |
|---|---|---|
| `test_get_achievements_success` | `smoke` | `GET /achievements`: статус 200, валидация по схеме `achievements.yml`, состав достижений совпадает с эталоном |
| `test_get_achievements_negative` | `negative` | `GET /achievements?is_reached=ololo`: статус 422, `status: error` и сообщение об ошибке валидации |

### Pokemon Premium — `test_api_lavka_premium.py`

| Тест | Маркер | Что проверяет |
|---|---|---|
| `test_buy_premium_success` | `positive` | `POST /payments` на 15 дней: статус 200, сообщение «Транзакция успешна», число дней. Затем через `GET /me` проверяется, что у тренера появился премиум |
| `test_buy_premium_fail` | `negative` | Параметризованный: невалидный код подтверждения из SMS и CVV карты без средств. Ожидается статус 400 (тренажёр на любую ошибку оплаты отвечает 400, а не 402) |

## Установка

```bash
git clone <url-репозитория>
cd pokemonbattle_api_tests

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Переменные окружения

Тестам нужен файл `.env` в корне проекта. Его подхватывает `pytest-dotenv` при запуске pytest:

```dotenv
# тренер
USER_TRAINER_TOKEN=  # API-токен тренера (заголовок trainer_token)
TRAINER_ID=          # ID тренера

# тестовые карты
SECURE_CODE=         # код подтверждения из SMS
DUE_DATE=            # срок действия, формат MM/YY
VISA=                # номер карты для оплаты
MASTERCARD=
CARD_NAME=           # имя держателя карты
SUCCESS_CVV=         # CVV для успешной оплаты
FAIL_CVV=            # CVV карты с недостаточным балансом
```

## Запуск тестов

```bash
# все тесты
pytest

# по маркерам
pytest -m smoke
pytest -m regress
pytest -m negative
pytest -m positive

# отдельный модуль
pytest tests/test_api_lavka_premium.py
```

Маркеры описаны в `pytest.ini`. Тесты тренеров, CRUD-тесты и `knockout_trainer_pokemons` используют захардкоженный ID тренера `64411`, поэтому под другим тренером эти значения нужно поменять.

## Allure-отчёт

Результаты пишутся в `allure-results/` автоматически: опция `--alluredir=allure-results` прописана в `pytest.ini`.

```bash
pytest
allure serve allure-results
```

Для `allure serve` нужен установленный [Allure CLI](https://allurereport.org/docs/install/). В архиве `index.zip` лежит пример готового отчёта одним HTML-файлом.

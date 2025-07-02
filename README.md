# AI Task Bot

AI Task Bot — Telegram-бот, преобразующий текстовые сообщения в обычные задачи и события календаря. Бот через API OpenAI (или совместимый сервис) извлекает из текста структурированные данные и может генерировать `.ics`-файлы для импорта в любой календарь.

## Основные возможности

- Автоматическое вычленение событий и задач из письменных обращений;
- Генерация импортируемых `.ics`-файлов;
- Минималистичные логи на русском языке;
- Поддержка запуска в Docker.

Бота можно добавлять в групповые чаты. Для вызова команд в группе используйте
формат `/command@BotName`.

## Требования

- Python 3.11+
- Зависимости из `requirements.txt`

## Быстрый запуск

1. Клонируйте репозиторий и создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Скопируйте `.env.example` в `.env` и заполните переменные:
   - `BOT_TOKEN` — токен вашего бота
   - `ADMINS` — идентификаторы админов
   - `AI_API_KEY` — ключ доступа к AI
   - `AI_API_MODEL` — модель для обработки
   - `AI_API_URL` — адрес сервиса
   - `AI_PROXY_URL` — прокси при необходимости, например `socks5://user:pass@1.1.1.1:1234`
4. Запустите бота:
   ```bash
   python main.py
   ```

После запуска в чате можно использовать команды `/start`, `/help` и `/create`.

## Запуск в Docker

Для упрощенного развертывания можно воспользоваться Docker:

```bash
docker-compose up -d
```

Папка `storage` монтируется для хранения базы данных.

## Управление доступом

По умолчанию бот недоступен для всех пользователей, кроме ID, указанных в
переменной `ADMINS`. Администраторы могут выдавать и отзывать доступ прямо из
админ-меню. Аналогичным образом можно разрешать или запрещать использование бота в групповых чатах. Состояние доступа сохраняется в SQLite базе `storage/main.db`.

## Настройка и обновление

- Файлы `config/system_prompt.txt`, `config/user_prompt.txt` и `config/schema.json` позволяют менять логику бота под свои задачи;
- Перед коммитом рекомендуется проверить код:
  ```bash
  python -m py_compile $(git ls-files '*.py')
  ```
- Если появятся тесты, запускайте `pytest`.

## Тестирование

Для запуска тестов используйте:

```bash
pytest
```

Пример простого теста (см. `tests/test_ics.py`):

```python
from ics.creator import ICSCreator

def test_create_ics_basic():
    creator = ICSCreator()
    tasks = {
        "events_tasks": [
            {"type": "event", "title": "Test", "date": "2025-07-01", "time": "12:00"}
        ]
    }
    filename = creator.create_ics(tasks)
    assert filename and filename.endswith('.ics')
```

## Пример .env

```env
BOT_TOKEN=your-telegram-bot-token
ADMINS=123456789,987654321
AI_API_KEY=your-openai-key
AI_API_MODEL=gpt-3.5-turbo
AI_API_URL=https://api.openai.com/v1
AI_PROXY_URL=
```

## Структура проекта

- `ai/` — работа с моделью AI;
- `handlers/` — телеграм-команды и форматы ответов;
- `ics/` — формирование `.ics`-файлов;
- `storage/` — простая база SQLite для хранения запросов.

## Лицензия

Проект распространяется по лицензии BSD-3-Clause.

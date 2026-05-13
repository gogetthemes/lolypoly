# LolyPoly Trading Bot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Роботизированная система копирования торговых сделок между торговыми счетами на Pooymarket.

## Особенности

- 📋 **Управление счетами**: Создавайте и управляйте несколькими торговыми счетами
- 🔄 **Копирование сделок**: Автоматическое копирование сделок от одного счета на другие
- 🎯 **Фильтры**: Гибкие фильтры для выборочного копирования:
  - Диапазон размеров сделок (min/max)
  - Множители размера
  - Толерантность к проскальзыванию
  - Фильтр по времени выполнения
- 📊 **Аналитика**: Статистика по счетам и сделкам
- 🌐 **REST API**: Полнофункциональный API для управления ботом
- 🔌 **WebSocket**: Поддержка WebSocket для мониторинга в реальном времени
- 🐘 **PostgreSQL**: Надежное хранилище данных

## Установка

### Требования

- Python 3.11+
- PostgreSQL 12+
- Docker (опционально)

### Быстрый старт

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/ThemesMonsters/lolypoly.git
cd lolypoly
```

2. **Создайте виртуальное окружение**:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\\Scripts\\activate
```

3. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

4. **Установите переменные окружения**:
```bash
cp .env.example .env
# Отредактируйте .env с вашими параметрами
```

5. **Инициализируйте базу данных**:
```bash
python -c "from src.database.database import init_db; init_db()"
```

6. **Запустите приложение**:
```bash
python -m src.main
```

API будет доступен на `http://localhost:8000`

### Docker

```bash
docker build -t lolypoly .
docker run -d -p 8000:8000 --env-file .env lolypoly
```

## Использование

### Создание счета

```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Trading Account",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "account_type": "source",
    "enabled": true
  }'
```

### Создание стратегии

```bash
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Copy All Trades",
    "source_account_id": "acc_xxxxx",
    "target_accounts": ["acc_yyyyy"],
    "copy_mode": "full",
    "enabled": true
  }'
```

### Получение статистики

```bash
curl http://localhost:8000/api/trades/stats
```

## Структура проекта

```
lolyopoly/
├── src/
│   ├── accounts/          # Управление счетами
│   ├── strategies/        # Управление стратегиями
│   ├── trading/          # Торговая логика
│   ├── analytics/        # Аналитика и статистика
│   ├── api/              # REST API
│   ├── database/         # Модели БД и сессии
│   ├── utils/            # Утилиты
│   ├── config.py         # Конфигурация
│   └── main.py           # Точка входа
├── tests/                # Тесты
├── config/               # Примеры конфигов
├── requirements.txt      # Python зависимости
├── Dockerfile            # Docker конфигурация
└── README.md             # Этот файл
```

## API Endpoints

### Счета
- `GET /api/accounts` - Список счетов
- `POST /api/accounts` - Создать счет
- `GET /api/accounts/{id}` - Получить счет
- `PUT /api/accounts/{id}` - Обновить счет
- `DELETE /api/accounts/{id}` - Удалить счет

### Стратегии
- `GET /api/strategies` - Список стратегий
- `POST /api/strategies` - Создать стратегию
- `GET /api/strategies/{id}` - Получить стратегию
- `PUT /api/strategies/{id}` - Обновить стратегию
- `DELETE /api/strategies/{id}` - Удалить стратегию

### Аналитика
- `GET /api/trades/stats` - Статистика всех счетов
- `GET /api/trades/stats/{account_id}` - Статистика счета
- `GET /api/status` - Статус бота

## Примеры стратегий

См. папку `config/` для примеров конфигураций:
- `strategies.json.example` - Примеры стратегий
- `accounts.json.example` - Примеры конфигов счетов

## Тестирование

```bash
python -m pytest tests/
```

## Логирование

Логи сохраняются в `logs/bot.log` и выводятся в консоль.

Уровень логирования можно установить через переменную `LOG_LEVEL`:
- `debug`
- `info` (по умолчанию)
- `warning`
- `error`

## Лицензия

MIT License - см. LICENSE файл

## Контакты

- GitHub: [@ThemesMonsters](https://github.com/ThemesMonsters)
- Email: themesmonsterscom@gmail.com

## Благодарности

Спасибо за использование LolyPoly! 🚀

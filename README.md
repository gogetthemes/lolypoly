# LolyPoly - Trading Copy Bot

Автоматизированный бот для копирования сделок с нескольких аккаунтов Pooymarket с поддержкой гибких стратегий фильтрации и анализа.

## Возможности

✅ **Управление аккаунтами**
- Добавление и отслеживание нескольких аккаунтов
- Настройка прав доступа и API ключей
- Ведение статистики по каждому аккаунту

✅ **Стратегии копирования**
- Полное копирование сделок
- Выборочное копирование с фильтрами
- Изменение объёма сделок (процент, коэффициент)
- Фильтры по сумме сделки (от/до)
- Установка проскальзывания
- Фильтры по времени завершения (часы, дни, месяцы)
- Включение/отключение копирования в реальном времени

✅ **Технология**
- WebSocket для отслеживания сделок в реальном времени
- REST API для аналитики
- SQLite/PostgreSQL для хранения данных
- Асинхронная архитектура
- Логирование и мониторинг

## Структура проекта

```
lolypoly/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа приложения
│   ├── config.py              # Конфигурация
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy модели
│   │   ├── database.py        # Инициализация БД
│   │   └── migrations.py      # Миграции
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── manager.py         # Управление аккаунтами
│   │   └── models.py          # Модели аккаунтов
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── manager.py         # Управление стратегиями
│   │   ├── filters.py         # Фильтры для копирования
│   │   └── models.py          # Модели стратегий
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── copier.py          # Основной копировщик сделок
│   │   ├── ws_client.py       # WebSocket клиент
│   │   └── pooymarket_api.py  # API интеграция
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── stats.py           # Статистика
│   │   └── reports.py         # Отчёты
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # API маршруты
│   │   └── schemas.py         # Pydantic схемы
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Логирование
│       └── validators.py      # Валидация
├── config/
│   ├── accounts.json          # Конфигурация аккаунтов
│   └── strategies.json        # Конфигурация стратегий
├── database/
│   └── schema.sql             # SQL схема БД
├── tests/
│   ├── __init__.py
│   ├── test_accounts.py
│   ├── test_strategies.py
│   └── test_copier.py
├── logs/                       # Логи приложения
├── .env.example               # Пример окружения
├── .gitignore                 # Git ignore
├── requirements.txt           # Python зависимости
├── docker-compose.yml         # Docker конфигурация
├── Dockerfile                 # Docker образ
└── README.md                  # Документация
```

## Установка

### Локальное тестирование

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/ThemesMonsters/lolypoly.git
cd lolypoly
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Скопируйте конфиг:**
```bash
cp .env.example .env
```

5. **Отредактируйте .env файл:**
```bash
nano .env
```

6. **Инициализируйте базу данных:**
```bash
python -m src.database.migrations
```

7. **Запустите приложение:**
```bash
python -m src.main
```

### Развёртывание на VPS

1. **Подготовьте сервер:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql postgresql-contrib -y
```

2. **Клонируйте репозиторий:**
```bash
git clone https://github.com/ThemesMonsters/lolypoly.git
cd lolypoly
```

3. **Настройте systemd сервис:**
```bash
sudo nano /etc/systemd/system/lolypoly.service
```

4. **Запустите сервис:**
```bash
sudo systemctl enable lolypoly
sudo systemctl start lolypoly
sudo systemctl status lolypoly
```

## Использование

### API Endpoints

```
GET  /api/accounts              - Список аккаунтов
POST /api/accounts              - Добавить аккаунт
GET  /api/accounts/{id}         - Информация об аккаунте
PUT  /api/accounts/{id}         - Обновить аккаунт
DELETE /api/accounts/{id}       - Удалить аккаунт

GET  /api/strategies            - Список стратегий
POST /api/strategies            - Создать стратегию
GET  /api/strategies/{id}       - Информация о стратегии
PUT  /api/strategies/{id}       - Обновить стратегию
DELETE /api/strategies/{id}     - Удалить стратегию

GET  /api/trades                - История сделок
GET  /api/trades/stats          - Статистика сделок
GET  /api/trades/stats/{account_id}  - Статистика по аккаунту

GET  /api/status                - Статус бота
```

### Конфигурация аккаунтов

Файл `config/accounts.json`:
```json
{
  "accounts": [
    {
      "id": "acc_001",
      "name": "Главный трейдер",
      "api_key": "your_api_key",
      "api_secret": "your_api_secret",
      "account_type": "source",
      "enabled": true
    },
    {
      "id": "copy_001",
      "name": "Копирующий аккаунт",
      "api_key": "another_api_key",
      "api_secret": "another_secret",
      "account_type": "target",
      "enabled": true
    }
  ]
}
```

### Конфигурация стратегий

Файл `config/strategies.json`:
```json
{
  "strategies": [
    {
      "id": "strat_001",
      "name": "Агрессивная копия",
      "source_account": "acc_001",
      "target_accounts": ["copy_001"],
      "enabled": true,
      "copy_mode": "selective",
      "filters": {
        "min_amount": 100,
        "max_amount": 5000,
        "amount_multiplier": 0.5,
        "slippage_percent": 0.5,
        "real_time": true,
        "completion_time": {
          "type": "hours",
          "value": 24
        }
      }
    }
  ]
}
```

## Фильтры копирования

### Доступные фильтры

- **min_amount** - Минимальная сумма сделки для копирования
- **max_amount** - Максимальная сумма сделки для копирования
- **amount_multiplier** - Коэффициент изменения суммы (0.1 = 10% от оригинала)
- **amount_percent** - Процент от суммы (альтернатива multiplier)
- **slippage_percent** - Проскальзывание в процентах
- **real_time** - Копировать только сделки в реальном времени
- **completion_time** - Фильтр по времени завершения:
  - `type`: "minutes", "hours", "days", "weeks", "months"
  - `value`: числовое значение

## Логирование

Логи сохраняются в `logs/lolypoly.log` и выводятся в консоль.

Уровни логирования:
- DEBUG - Детальная информация
- INFO - Информационные сообщения
- WARNING - Предупреждения
- ERROR - Ошибки
- CRITICAL - Критические ошибки

## Разработка

### Запуск тестов

```bash
pytest tests/ -v
```

### Docker развёртывание

```bash
docker-compose up -d
```

## Безопасность

⚠️ **Важно:**
- Никогда не коммитьте .env файл с реальными API ключами
- Используйте переменные окружения для чувствительных данных
- Регулярно ротируйте API ключи
- Используйте приватный репозиторий

## Лицензия

Private

## Поддержка

Для вопросов и предложений открывайте Issues в репозитории.

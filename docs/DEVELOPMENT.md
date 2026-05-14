# LolyPoly Development Guide

## Architecture Overview

LolyPoly использует многоуровневую архитектуру:

```
HTTP Request
    ↓
API Routes (FastAPI)
    ↓
Managers (Business Logic)
    ↓
Database Models (SQLAlchemy)
    ↓
Pooymarket API / WebSocket
```

## Module Breakdown

### accounts/
Упразляет торговыми счетами:
- Создание/чтение/обновление/удаление счетов
- Управление типами счетов (источник/цель)
- Управление активным статусом

### strategies/
Управляет стратегиями копирования:
- Создание/обновление стратегий
- Применение фильтров к сделкам
- Связь между источниками и целевыми счетами

### trading/
Основная логика копирования:
- `copier.py` - главная логика копирования сделок
- `pooymarket_api.py` - HTTP клиент для API
- `ws_client.py` - WebSocket клиент для реал-тайм данных

### analytics/
Расчет статистики:
- Статистика по счетам
- Анализ прибыльности
- Ежедневные отчеты

### api/
REST API endpoints:
- `routes.py` - все API endpoints
- `schemas.py` - Pydantic модели для валидации

### database/
Слой данных:
- `models.py` - ORM модели
- `database.py` - сессии и инициализация

### utils/
Вспомогательные функции:
- `logger.py` - логирование
- `validators.py` - валидация данных

## Data Flow

### Копирование сделки

1. WebSocket получает обновление о новой сделке от Pooymarket
2. Стратегия проверяет фильтры на сделку
3. Если сделка проходит фильтры:
   - Создается запись в БД (Trade)
   - Сделка выполняется на целевом счете
   - Обновляется статус сделки
4. Статистика пересчитывается

## Adding New Features

### Добавление нового endpoint API

1. Создайте schema в `api/schemas.py`
2. Добавьте route в `api/routes.py`
3. Добавьте бизнес-логику в `accounts/manager.py` или другой manager
4. Добавьте тесты в `tests/`

### Добавление нового фильтра

1. Добавьте параметр в `strategies/filters.py`
2. Реализуйте логику проверки в `should_copy()`
3. Добавьте валидацию в `utils/validators.py`
4. Добавьте тесты

## Database Schema

### accounts
```sql
CREATE TABLE accounts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    account_type ENUM('source', 'target', 'both'),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### strategies
```sql
CREATE TABLE strategies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    source_account_id VARCHAR(50) FOREIGN KEY,
    target_accounts TEXT[],
    copy_mode ENUM('full', 'selective'),
    filters JSON,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### trades
```sql
CREATE TABLE trades (
    id VARCHAR(50) PRIMARY KEY,
    strategy_id VARCHAR(50) FOREIGN KEY,
    source_account_id VARCHAR(50) FOREIGN KEY,
    target_account_id VARCHAR(50),
    symbol VARCHAR(20),
    trade_type VARCHAR(20),
    original_amount FLOAT,
    copied_amount FLOAT,
    original_price FLOAT,
    actual_price FLOAT,
    status VARCHAR(20),
    source_opened_at TIMESTAMP,
    copied_at TIMESTAMP,
    meta_data JSON,
    created_at TIMESTAMP
);
```

## Common Tasks

### Добавление поля в модель

1. Обновите модель в `database/models.py`
2. Обновите schema в `api/schemas.py`
3. Создайте migration (если используется Alembic)
4. Обновите документацию

### Добавление логирования

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")
logger.error("Error message")
```

### Добавление новой зависимости

1. Установите пакет: `pip install package_name`
2. Добавьте в `requirements.txt`
3. Обновите документацию если необходимо

## Testing

```bash
# Запустить все тесты
python -m pytest

# Запустить с coverage
python -m pytest --cov=src tests/

# Запустить конкретный тест
python -m pytest tests/test_accounts.py::TestAccountManager::test_create_account

# Запустить с verbose выводом
python -m pytest -v
```

## Performance Tips

1. Используйте connection pooling для БД
2. Кэшируйте часто запрашиваемые данные
3. Используйте batch операции где возможно
4. Избегайте N+1 queries с помощью joins

## Security Considerations

1. Никогда не логируйте API ключи
2. Используйте переменные окружения для secrets
3. Валидируйте все входные данные
4. Используйте HTTPS в production
5. Реализуйте rate limiting

## Deployment

См. `docker-compose.yml` для локального deployment

```bash
docker-compose up -d
```

Для production:
1. Используйте managed PostgreSQL
2. Настройте HTTPS/SSL
3. Используйте environment-specific конфигурацию
4. Настройте мониторинг и алерты
5. Регулярно делайте backup БД

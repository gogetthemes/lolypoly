# LolyPoly API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
API использует Bearer token авторизацию (для будущих версий).

## Endpoints

### Accounts

#### Получить все счета
```http
GET /api/accounts?enabled_only=false
```

**Query Parameters:**
- `enabled_only` (boolean, optional) - показывать только активные счета

**Response:** Array of Account objects

#### Создать счет
```http
POST /api/accounts
Content-Type: application/json

{
  "name": "My Trading Account",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "account_type": "source",
  "enabled": true
}
```

**Response:** Account object

#### Получить счет по ID
```http
GET /api/accounts/{account_id}
```

**Response:** Account object

#### Обновить счет
```http
PUT /api/accounts/{account_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "enabled": true
}
```

**Response:** Account object

#### Удалить счет
```http
DELETE /api/accounts/{account_id}
```

**Response:** {"message": "Account deleted"}

---

### Strategies

#### Получить все стратегии
```http
GET /api/strategies?enabled_only=false
```

**Response:** Array of Strategy objects

#### Создать стратегию
```http
POST /api/strategies
Content-Type: application/json

{
  "name": "Copy All Trades",
  "source_account_id": "acc_xxxxx",
  "target_accounts": ["acc_yyyyy", "acc_zzzzz"],
  "copy_mode": "full",
  "filters": {
    "min_amount": 100,
    "max_amount": 5000,
    "amount_multiplier": 1.0,
    "slippage_percent": 0.5
  },
  "enabled": true
}
```

**Copy Modes:**
- `full` - копировать все сделки
- `selective` - копировать только отфильтрованные сделки

**Response:** Strategy object

#### Получить стратегию по ID
```http
GET /api/strategies/{strategy_id}
```

**Response:** Strategy object

#### Обновить стратегию
```http
PUT /api/strategies/{strategy_id}
Content-Type: application/json

{
  "name": "Updated Strategy",
  "copy_mode": "selective",
  "filters": {
    "min_amount": 200,
    "max_amount": 3000
  },
  "enabled": true
}
```

**Response:** Strategy object

#### Удалить стратегию
```http
DELETE /api/strategies/{strategy_id}
```

**Response:** {"message": "Strategy deleted"}

---

### Analytics

#### Получить статистику всех счетов
```http
GET /api/trades/stats
```

**Response:**
```json
[
  {
    "account_id": "acc_xxxxx",
    "account_name": "Account Name",
    "total_trades": 100,
    "successful_trades": 85,
    "failed_trades": 15,
    "win_rate": "85.00%",
    "total_profit": 1250.50,
    "avg_slippage": "0.2500%",
    "updated_at": "2026-05-13T12:00:00"
  }
]
```

#### Получить статистику счета
```http
GET /api/trades/stats/{account_id}
```

**Response:** Account stats object

#### Получить статус бота
```http
GET /api/status
```

**Response:**
```json
{
  "status": "running",
  "running": true,
  "timestamp": "2026-05-13T12:00:00",
  "version": "0.1.0"
}
```

#### Health check
```http
GET /health
```

**Response:** {"status": "ok"}

---

## Data Models

### Account
```json
{
  "id": "acc_xxxxx",
  "name": "Trading Account",
  "account_type": "source",
  "enabled": true,
  "created_at": "2026-05-13T10:00:00",
  "updated_at": "2026-05-13T10:00:00"
}
```

### Strategy
```json
{
  "id": "strat_xxxxx",
  "name": "Copy Strategy",
  "source_account_id": "acc_source",
  "target_accounts": ["acc_target1", "acc_target2"],
  "copy_mode": "full",
  "filters": {},
  "enabled": true,
  "created_at": "2026-05-13T10:00:00",
  "updated_at": "2026-05-13T10:00:00"
}
```

### Trade
```json
{
  "id": "trade_xxxxx",
  "strategy_id": "strat_xxxxx",
  "source_account_id": "acc_source",
  "target_account_id": "acc_target",
  "symbol": "BTC/USDT",
  "trade_type": "BUY",
  "original_amount": 1000.0,
  "copied_amount": 500.0,
  "original_price": 50000.0,
  "actual_price": 50100.0,
  "status": "completed",
  "source_opened_at": "2026-05-13T10:00:00",
  "copied_at": "2026-05-13T10:00:01",
  "created_at": "2026-05-13T10:00:01"
}
```

---

## Error Responses

Все ошибки возвращаются в формате:
```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Examples

### Пример 1: Создание стратегии копирования

```bash
# 1. Создать исходящий счет
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Source Trading",
    "api_key": "your_source_key",
    "api_secret": "your_source_secret",
    "account_type": "source"
  }'

# 2. Создать целевой счет
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Copy Trading",
    "api_key": "your_target_key",
    "api_secret": "your_target_secret",
    "account_type": "target"
  }'

# 3. Создать стратегию
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Copy All Trades",
    "source_account_id": "acc_source_id",
    "target_accounts": ["acc_target_id"],
    "copy_mode": "full"
  }'
```

### Пример 2: Селективное копирование

```bash
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conservative Copy",
    "source_account_id": "acc_source_id",
    "target_accounts": ["acc_target_id"],
    "copy_mode": "selective",
    "filters": {
      "min_amount": 100,
      "max_amount": 5000,
      "amount_multiplier": 0.5,
      "slippage_percent": 0.3,
      "real_time": true,
      "completion_time": {
        "type": "hours",
        "value": 24
      }
    }
  }'
```

### Пример 3: Получение статистики

```bash
# Получить статистику всех счетов
curl http://localhost:8000/api/trades/stats

# Получить статистику конкретного счета
curl http://localhost:8000/api/trades/stats/acc_xxxxx
```

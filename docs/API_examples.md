# Примеры использования API

## Аутентификация

### Регистрация нового пользователя
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "Иван Иванов"
  }'
```

### Вход в систему (получение токена)
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=yourpassword"
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Работа с данными

### Получить список всех пилотов
```bash
curl -X GET "http://localhost:8000/api/drivers?skip=0&limit=10"
```

### Получить информацию о конкретном пилоте
```bash
curl -X GET "http://localhost:8000/api/drivers/1"
```

### Создать нового пилота (требуется админ)
```bash
curl -X POST "http://localhost:8000/api/drivers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "driver_ref": "hamilton",
    "forename": "Lewis",
    "surname": "Hamilton",
    "code": "HAM",
    "number": 44,
    "nationality": "British"
  }'
```

## Аналитика

### Статистика пилота за всю карьеру
```bash
curl -X GET "http://localhost:8000/api/analytics/driver-stats/1"
```

### Турнирная таблица сезона
```bash
curl -X GET "http://localhost:8000/api/analytics/season-standings/2020"
```

### Топ пилотов всех времен
```bash
curl -X GET "http://localhost:8000/api/analytics/driver-statistics"
```

### История выступлений на трассе
```bash
curl -X GET "http://localhost:8000/api/analytics/circuit-history/1?limit=10"
```

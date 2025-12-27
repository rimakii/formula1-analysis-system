# F1 Analytics System 

Информационная система для анализа и статистики гоночных команд Формулы 1.

## Описание проекта

Система предназначена для сбора, хранения и анализа данных о пилотах, командах, гоночных уик-эндах и их результатах.

**Курсовая работа** по дисциплине "Базы данных"  
**Датасет**: [Formula 1 World Championship (1950-2020)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)

## Технологии

- **База данных**: PostgreSQL 16
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Аутентификация**: JWT с ролями (admin/user)
- **Контейнеризация**: Docker Compose

## Роли пользователей

### User (Обычный пользователь)
- Просмотр всех данных
- Доступ к аналитическим отчетам

### Admin (Администратор)
- Все права пользователя
- **Создание, изменение и удаление данных**
- Батчевая загрузка данных
- Управление пользователями

## Быстрый старт

### 1. Создайте файл .env
```bash
cp .env.example .env
```

 **Отредактируйте .env**: измените `SECRET_KEY` и `POSTGRES_PASSWORD`

### 2. Скачайте датасет Kaggle

Скачайте CSV файлы с [Kaggle](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020/data) и поместите в `database/data/kaggle_dataset/`:
- circuits.csv
- constructors.csv
- drivers.csv
- races.csv
- results.csv
- status.csv

### 3. Запустите систему
```bash
docker-compose up -d
```

### 4. Создайте администратора
```bash
docker-compose exec backend python scripts/create_admin.py
```

### 5. Загрузите данные (если CSV файлы размещены)
```bash
docker-compose exec backend python scripts/load_kaggle_data.py
```

### 6. Откройте Swagger UI

Перейдите: **http://localhost:8000/docs**

## Использование API

### Аутентификация в Swagger

1. Используйте `POST /api/auth/login` для получения токена
2. Нажмите кнопку "Authorize" 
3. Введите: `Bearer YOUR_ACCESS_TOKEN`
4. Нажмите "Authorize"

### Основные эндпоинты

**Аутентификация:**
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущий пользователь

**Данные:**
- `GET /api/drivers` - Список пилотов
- `POST /api/drivers` - Создать пилота (admin)
- `GET /api/constructors` - Список команд
- `GET /api/races` - Список гонок
- `GET /api/results` - Результаты

**Аналитика:**
- `GET /api/analytics/driver-stats/{id}` - Статистика пилота
- `GET /api/analytics/season-standings/{year}` - Турнирная таблица
- `GET /api/analytics/driver-statistics` - Топ-50 пилотов
- `GET /api/analytics/constructor-statistics` - Топ-50 команд

## База данных

### Таблицы (12 шт)
- drivers, constructors, circuits, races
- results (>25,000 записей), qualifying, lap_times, pit_stops
- driver_standings, constructor_standings
- users, audit_log

### SQL функции (11 шт)
**Скалярные:**
- calculate_driver_total_points
- calculate_driver_wins
- calculate_driver_podiums
- calculate_constructor_total_points
- calculate_constructor_wins
- calculate_average_lap_time

**Табличные:**
- get_season_driver_standings
- get_season_constructor_standings
- get_driver_career_stats
- get_constructor_season_results
- get_circuit_history

### Представления (VIEW)
- v_driver_statistics
- v_constructor_statistics
- v_race_results_detailed

### Триггеры
- Аудит изменений (INSERT/UPDATE/DELETE)
- Автообновление updated_at

## Оптимизация

35+ индексов для быстрых запросов:
- Поиск результатов: **19x быстрее**
- Поиск пилота: **14x быстрее**
- Статистика сезона: **12x быстрее**

## Структура проекта

```
f1-analytics-system/
├── database/init/        # SQL скрипты (6 файлов)
├── backend/
│   ├── main.py          # FastAPI приложение
│   ├── app/             # Модели, схемы, роутеры
│   └── scripts/         # Утилиты
└── docs/                # Документация
```

## Безопасность

Пароли хэшируются (bcrypt)  
JWT токены для аутентификации  
Роли PostgreSQL (app_admin, app_user)  
Параметризованные SQL запросы  
Секреты в .env файле  

## Полезные команды

```bash
# Просмотр логов
docker-compose logs -f backend

# Остановка
docker-compose stop

# Удаление с данными
docker-compose down -v

# Подключение к БД
docker-compose exec postgres psql -U f1admin -d f1_analytics
```


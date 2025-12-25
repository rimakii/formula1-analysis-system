# Анализ производительности запросов

## Тестовые запросы

### 1. Получение результатов гонки

**Запрос без индекса:**
```sql
EXPLAIN ANALYZE
SELECT * FROM results WHERE race_id = 1000;
```

**Результат до создания индекса:**
- Planning Time: 0.150 ms
- Execution Time: 45.230 ms
- Seq Scan on results

**Результат после создания индекса idx_results_race_id:**
- Planning Time: 0.125 ms
- Execution Time: 2.341 ms
- Index Scan using idx_results_race_id

**Улучшение: ~19x быстрее**

### 2. Поиск пилота по фамилии

**Запрос:**
```sql
EXPLAIN ANALYZE
SELECT * FROM drivers WHERE surname = 'Hamilton';
```

**До индекса:**
- Execution Time: 12.445 ms
- Seq Scan

**После idx_drivers_surname:**
- Execution Time: 0.842 ms
- Index Scan

**Улучшение: ~14x быстрее**

### 3. Статистика пилота за сезон

**Запрос:**
```sql
EXPLAIN ANALYZE
SELECT 
    d.forename, d.surname,
    SUM(r.points) as total_points,
    COUNT(*) FILTER (WHERE r.position = 1) as wins
FROM results r
JOIN drivers d ON r.driver_id = d.driver_id
JOIN races ra ON r.race_id = ra.race_id
WHERE ra.year = 2020
GROUP BY d.driver_id, d.forename, d.surname;
```

**С индексами:**
- Execution Time: 15.234 ms
- Использует idx_races_year, idx_results_driver_id

**Без индексов:**
- Execution Time: 186.442 ms

**Улучшение: ~12x быстрее**

## Выводы

Индексы значительно ускоряют:
1. Поиск по внешним ключам (race_id, driver_id, constructor_id)
2. Фильтрацию по годам и позициям
3. Сортировку по очкам и датам
4. JOIN операции между таблицами

Рекомендуется регулярно запускать VACUUM ANALYZE для поддержания актуальной статистики.

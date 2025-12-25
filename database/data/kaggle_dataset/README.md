# Kaggle F1 Dataset

Скачайте CSV файлы с Kaggle и поместите их в эту директорию:

https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020/data

## Необходимые файлы:

- circuits.csv
- constructors.csv
- constructor_results.csv (опционально)
- constructor_standings.csv
- drivers.csv
- driver_standings.csv
- lap_times.csv
- pit_stops.csv
- qualifying.csv
- races.csv
- results.csv
- seasons.csv (опционально)
- sprint_results.csv (опционально)
- status.csv

## Автоматическая загрузка

После размещения файлов, запустите:

```bash
docker-compose exec backend python scripts/load_kaggle_data.py
```

Скрипт автоматически загрузит данные в PostgreSQL.

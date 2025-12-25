import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Driver, Constructor, Circuit, Race, Result, Status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BatchLoader:
    """
    Сервис для батчевой загрузки данных из CSV файлов.
    Включает логирование ошибок и обработку исключений.
    """

    def __init__(self, db: Session):
        self.db = db
        self.errors = []

    def load_drivers(self, df: pd.DataFrame) -> dict:
        """Загрузить пилотов из DataFrame"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Начало загрузки {len(df)} пилотов...")

        for index, row in df.iterrows():
            try:
                driver = Driver(
                    driver_id=row.get('driverId'),
                    driver_ref=row['driverRef'],
                    number=row.get('number') if pd.notna(row.get('number')) else None,
                    code=row.get('code') if pd.notna(row.get('code')) else None,
                    forename=row['forename'],
                    surname=row['surname'],
                    dob=pd.to_datetime(row['dob']).date() if pd.notna(row.get('dob')) else None,
                    nationality=row.get('nationality'),
                    url=row.get('url')
                )
                self.db.merge(driver)
                success_count += 1

                if success_count % 100 == 0:
                    self.db.commit()
                    logger.info(f"Загружено {success_count} пилотов...")

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {index}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                continue

        self.db.commit()
        logger.info(f"Загрузка пилотов завершена. Успешно: {success_count}, Ошибок: {error_count}")

        return {
            "success": success_count,
            "failed": error_count,
            "errors": errors
        }

    def load_constructors(self, df: pd.DataFrame) -> dict:
        """Загрузить команды из DataFrame"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Начало загрузки {len(df)} команд...")

        for index, row in df.iterrows():
            try:
                constructor = Constructor(
                    constructor_id=row.get('constructorId'),
                    constructor_ref=row['constructorRef'],
                    name=row['name'],
                    nationality=row.get('nationality'),
                    url=row.get('url')
                )
                self.db.merge(constructor)
                success_count += 1

                if success_count % 50 == 0:
                    self.db.commit()

            except Exception as e:
                error_count += 1
                errors.append(f"Строка {index}: {str(e)}")
                logger.error(f"Ошибка загрузки команды в строке {index}: {e}")
                continue

        self.db.commit()
        logger.info(f"Загрузка команд завершена. Успешно: {success_count}, Ошибок: {error_count}")

        return {
            "success": success_count,
            "failed": error_count,
            "errors": errors
        }

    def load_circuits(self, df: pd.DataFrame) -> dict:
        """Загрузить трассы из DataFrame"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Начало загрузки {len(df)} трасс...")

        for index, row in df.iterrows():
            try:
                circuit = Circuit(
                    circuit_id=row.get('circuitId'),
                    circuit_ref=row['circuitRef'],
                    name=row['name'],
                    location=row.get('location'),
                    country=row.get('country'),
                    lat=row.get('lat') if pd.notna(row.get('lat')) else None,
                    lng=row.get('lng') if pd.notna(row.get('lng')) else None,
                    alt=row.get('alt') if pd.notna(row.get('alt')) else None,
                    url=row.get('url')
                )
                self.db.merge(circuit)
                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Строка {index}: {str(e)}")
                continue

        self.db.commit()
        logger.info(f"Загрузка трасс завершена. Успешно: {success_count}")

        return {
            "success": success_count,
            "failed": error_count,
            "errors": errors
        }

    def load_results(self, df: pd.DataFrame) -> dict:
        """
        Загрузить результаты гонок из DataFrame.
        Транзакционная таблица с >5000 записей.
        """
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"Начало загрузки {len(df)} результатов...")

        for index, row in df.iterrows():
            try:
                result = Result(
                    result_id=row.get('resultId'),
                    race_id=row['raceId'],
                    driver_id=row['driverId'],
                    constructor_id=row['constructorId'],
                    number=row.get('number') if pd.notna(row.get('number')) else None,
                    grid=row['grid'],
                    position=row.get('position') if pd.notna(row.get('position')) else None,
                    position_text=row['positionText'],
                    position_order=row['positionOrder'],
                    points=row.get('points', 0),
                    laps=row['laps'],
                    time_text=row.get('time') if pd.notna(row.get('time')) else None,
                    milliseconds=row.get('milliseconds') if pd.notna(row.get('milliseconds')) else None,
                    fastest_lap=row.get('fastestLap') if pd.notna(row.get('fastestLap')) else None,
                    rank=row.get('rank') if pd.notna(row.get('rank')) else None,
                    fastest_lap_time=row.get('fastestLapTime') if pd.notna(row.get('fastestLapTime')) else None,
                    fastest_lap_speed=row.get('fastestLapSpeed') if pd.notna(row.get('fastestLapSpeed')) else None,
                    status_id=row['statusId']
                )
                self.db.merge(result)
                success_count += 1

                # Коммит каждые 500 записей для производительности
                if success_count % 500 == 0:
                    self.db.commit()
                    logger.info(f"Загружено {success_count}/{len(df)} результатов...")

            except Exception as e:
                error_count += 1
                if error_count <= 10:  # Логируем только первые 10 ошибок
                    error_msg = f"Строка {index}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                continue

        self.db.commit()
        logger.info(f"Загрузка результатов завершена. Успешно: {success_count}, Ошибок: {error_count}")

        return {
            "success": success_count,
            "failed": error_count,
            "errors": errors
        }

    def load_results_async(self, df: pd.DataFrame):
        """Асинхронная загрузка результатов (для больших файлов)"""
        logger.info("Запуск асинхронной загрузки результатов...")
        result = self.load_results(df)
        logger.info(f"Асинхронная загрузка завершена: {result}")

    def load_all_kaggle_data(self):
        """
        Загрузить все данные из Kaggle dataset.
        Файлы должны находиться в /data/kaggle_dataset/
        """
        import os
        DATA_PATH = "/data/kaggle_dataset"

        logger.info("=== Начало загрузки полного Kaggle dataset ===" )

        # Загружаем в правильном порядке (из-за внешних ключей)
        files_order = [
            ("status.csv", self._load_status),
            ("drivers.csv", self._load_drivers_from_file),
            ("constructors.csv", self._load_constructors_from_file),
            ("circuits.csv", self._load_circuits_from_file),
            ("races.csv", self._load_races_from_file),
            ("results.csv", self._load_results_from_file)
        ]

        for filename, load_func in files_order:
            filepath = os.path.join(DATA_PATH, filename)
            if os.path.exists(filepath):
                logger.info(f"Загрузка {filename}...")
                try:
                    load_func(filepath)
                except Exception as e:
                    logger.error(f"Ошибка при загрузке {filename}: {e}")
            else:
                logger.warning(f"Файл {filename} не найден")

        logger.info("=== Загрузка Kaggle dataset завершена ===")

    def _load_status(self, filepath: str):
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            status = Status(
                status_id=row['statusId'],
                status=row['status']
            )
            self.db.merge(status)
        self.db.commit()
        logger.info(f"Загружено {len(df)} статусов")

    def _load_drivers_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_drivers(df)
        logger.info(f"Результат загрузки пилотов: {result}")

    def _load_constructors_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_constructors(df)
        logger.info(f"Результат загрузки команд: {result}")

    def _load_circuits_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_circuits(df)
        logger.info(f"Результат загрузки трасс: {result}")

    def _load_races_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        success = 0
        for _, row in df.iterrows():
            try:
                race = Race(
                    race_id=row['raceId'],
                    year=row['year'],
                    round=row['round'],
                    circuit_id=row['circuitId'],
                    name=row['name'],
                    date=pd.to_datetime(row['date']).date(),
                    time=pd.to_datetime(row['time']).time() if pd.notna(row.get('time')) else None,
                    url=row.get('url')
                )
                self.db.merge(race)
                success += 1
            except Exception as e:
                logger.error(f"Ошибка загрузки гонки: {e}")
        self.db.commit()
        logger.info(f"Загружено {success} гонок")

    def _load_results_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_results(df)
        logger.info(f"Результат загрузки результатов: {result}")

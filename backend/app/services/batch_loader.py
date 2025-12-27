import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Driver, Constructor, Circuit, Race, Result, Status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def safe_int(value):
    if pd.isna(value) or str(value).strip() in ['\\N', '', 'nan', 'None']:
        return None
    try:
        return int(float(str(value)))
    except:
        return None

def safe_float(value):
    if pd.isna(value) or str(value).strip() in ['\\N', '', 'nan', 'None']:
        return None
    try:
        return float(str(value))
    except:
        return None

def safe_str(value):
    if pd.isna(value) or str(value).strip() in ['\\N', '', 'nan', 'None']:
        return None
    return str(value).strip()

def safe_date(value):
    if pd.isna(value) or str(value).strip() in ['\\N', '', 'nan', 'None']:
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

def safe_time(value):
    if pd.isna(value) or str(value).strip() in ['\\N', '', 'nan', 'None']:
        return None
    try:
        return pd.to_datetime(value, format='%H:%M:%S').time()
    except:
        return None

class BatchLoader:
    def __init__(self, db: Session):
        self.db = db
        self.errors = []

    def load_drivers(self, df: pd.DataFrame) -> dict:
        """????????? ??????? ?? DataFrame ? ????????? ??????????"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"?????? ???????? {len(df)} ???????...")

        for index, row in df.iterrows():
            try:
                driver_id = safe_int(row.get('driverId'))
                
                # ????????? ?????????????
                existing = self.db.query(Driver).filter(Driver.driver_id == driver_id).first()
                if existing:
                    logger.debug(f"????? {driver_id} ??? ??????????, ??????????")
                    continue

                driver = Driver(
                    driver_id=driver_id,
                    driver_ref=safe_str(row.get('driverRef')) or 'unknown',
                    number=safe_int(row.get('number')),
                    code=safe_str(row.get('code')),
                    forename=safe_str(row.get('forename')) or 'Unknown',
                    surname=safe_str(row.get('surname')) or 'Unknown',
                    dob=safe_date(row.get('dob')),
                    nationality=safe_str(row.get('nationality')),
                    url=safe_str(row.get('url'))
                )
                self.db.add(driver)
                success_count += 1

                if success_count % 100 == 0:
                    self.db.commit()
                    logger.info(f"????????? {success_count} ???????...")

            except Exception as e:
                error_count += 1
                error_msg = f"?????? {index}, driver_id={row.get('driverId')}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                self.db.rollback()
                continue

        self.db.commit()
        logger.info(f"???????? ??????? ?????????. ???????: {success_count}, ??????: {error_count}")

        return {"success": success_count, "failed": error_count, "errors": errors}

    def load_constructors(self, df: pd.DataFrame) -> dict:
        """????????? ??????? ?? DataFrame ? ????????? ??????????"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"?????? ???????? {len(df)} ??????...")

        for index, row in df.iterrows():
            try:
                constructor_id = safe_int(row.get('constructorId'))
                
                existing = self.db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
                if existing:
                    continue

                constructor = Constructor(
                    constructor_id=constructor_id,
                    constructor_ref=safe_str(row.get('constructorRef')) or 'unknown',
                    name=safe_str(row.get('name')) or 'Unknown',
                    nationality=safe_str(row.get('nationality')),
                    url=safe_str(row.get('url'))
                )
                self.db.add(constructor)
                success_count += 1

                if success_count % 50 == 0:
                    self.db.commit()

            except Exception as e:
                error_count += 1
                errors.append(f"?????? {index}: {str(e)}")
                logger.error(f"?????? ???????? ??????? ? ?????? {index}: {e}")
                self.db.rollback()
                continue

        self.db.commit()
        logger.info(f"???????? ?????? ?????????. ???????: {success_count}, ??????: {error_count}")

        return {"success": success_count, "failed": error_count, "errors": errors}

    def load_circuits(self, df: pd.DataFrame) -> dict:
        """????????? ?????? ?? DataFrame ? ????????? ??????????"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"?????? ???????? {len(df)} ?????...")

        for index, row in df.iterrows():
            try:
                circuit_id = safe_int(row.get('circuitId'))
                
                existing = self.db.query(Circuit).filter(Circuit.circuit_id == circuit_id).first()
                if existing:
                    continue

                circuit = Circuit(
                    circuit_id=circuit_id,
                    circuit_ref=safe_str(row.get('circuitRef')) or 'unknown',
                    name=safe_str(row.get('name')) or 'Unknown',
                    location=safe_str(row.get('location')),
                    country=safe_str(row.get('country')),
                    lat=safe_float(row.get('lat')),
                    lng=safe_float(row.get('lng')),
                    alt=safe_int(row.get('alt')),
                    url=safe_str(row.get('url'))
                )
                self.db.add(circuit)
                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"?????? {index}: {str(e)}")
                self.db.rollback()
                continue

        self.db.commit()
        logger.info(f"???????? ????? ?????????. ???????: {success_count}")

        return {"success": success_count, "failed": error_count, "errors": errors}

    def load_results(self, df: pd.DataFrame) -> dict:
        """????????? ?????????? ????? ?? DataFrame ? ????????? ??????????"""
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"?????? ???????? {len(df)} ???????????...")

        for index, row in df.iterrows():
            try:
                result_id = safe_int(row.get('resultId'))
                
                # ????????? ?????????????
                existing = self.db.query(Result).filter(Result.result_id == result_id).first()
                if existing:
                    continue

                result = Result(
                    result_id=result_id,
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    constructor_id=int(row['constructorId']),
                    number=safe_int(row.get('number')),
                    grid=int(row['grid']),
                    position=safe_int(row.get('position')),
                    position_text=safe_str(row.get('positionText')) or 'N/A',
                    position_order=int(row['positionOrder']),
                    points=safe_float(row.get('points')) or 0.0,
                    laps=int(row['laps']),
                    time_text=safe_str(row.get('time')),
                    milliseconds=safe_int(row.get('milliseconds')),
                    fastest_lap=safe_int(row.get('fastestLap')),
                    rank=safe_int(row.get('rank')),
                    fastest_lap_time=safe_str(row.get('fastestLapTime')),
                    fastest_lap_speed=safe_float(row.get('fastestLapSpeed')),
                    status_id=int(row['statusId'])
                )
                self.db.add(result)
                success_count += 1

                if success_count % 500 == 0:
                    self.db.commit()
                    logger.info(f"????????? {success_count}/{len(df)} ???????????...")

            except Exception as e:
                error_count += 1
                if error_count <= 20:
                    error_msg = f"?????? {index}, result_id={row.get('resultId')}, driver_id={row.get('driverId')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                self.db.rollback()
                continue

        self.db.commit()
        logger.info(f"???????? ??????????? ?????????. ???????: {success_count}, ??????: {error_count}")

        return {"success": success_count, "failed": error_count, "errors": errors}

    def load_results_async(self, df: pd.DataFrame):
        """??????????? ???????? ???????????"""
        logger.info("?????? ??????????? ???????? ???????????...")
        result = self.load_results(df)
        logger.info(f"??????????? ???????? ?????????: {result}")

    def load_all_kaggle_data(self):
        """????????? ??? ?????? ?? Kaggle dataset"""
        import os
        DATA_PATH = "/data/kaggle_dataset"

        logger.info("=== ?????? ???????? ??????? Kaggle dataset ===")

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
                logger.info(f"???????? {filename}...")
                try:
                    load_func(filepath)
                except Exception as e:
                    logger.error(f"?????? ??? ???????? {filename}: {e}")
            else:
                logger.warning(f"???? {filename} ?? ??????")

        logger.info("=== ???????? Kaggle dataset ????????? ===")
        self.fix_all_sequences()

    def _load_status(self, filepath: str):
        """????????? ??????? ? ????????? ??????????"""
        df = pd.read_csv(filepath)
        df = df.drop_duplicates(subset=['statusId'], keep='first')
        success = 0
        
        for _, row in df.iterrows():
            try:
                status_id = int(row['statusId'])
                
                # ????????? ?????????????
                existing = self.db.query(Status).filter(Status.status_id == status_id).first()
                if existing:
                    logger.debug(f"?????? {status_id} ??? ??????????, ??????????")
                    continue
                
                status = Status(
                    status_id=status_id,
                    status=safe_str(row['status']) or 'Unknown'
                )
                self.db.add(status)
                success += 1
                
                if success % 50 == 0:
                    self.db.commit()
                    
            except Exception as e:
                logger.error(f"?????? ???????? status_id={row.get('statusId')}: {e}")
                self.db.rollback()
                continue
                
        self.db.commit()
        logger.info(f"????????? {success} ????????")

    def _load_drivers_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_drivers(df)
        logger.info(f"????????? ???????? ???????: {result}")

    def _load_constructors_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_constructors(df)
        logger.info(f"????????? ???????? ??????: {result}")

    def _load_circuits_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_circuits(df)
        logger.info(f"????????? ???????? ?????: {result}")

    def _load_races_from_file(self, filepath: str):
        """????????? ????? ? ????????? ??????????"""
        df = pd.read_csv(filepath)
        success = 0
        
        for _, row in df.iterrows():
            try:
                race_id = int(row['raceId'])
                
                # ????????? ?????????????
                existing = self.db.query(Race).filter(Race.race_id == race_id).first()
                if existing:
                    continue
                
                race = Race(
                    race_id=race_id,
                    year=int(row['year']),
                    round=int(row['round']),
                    circuit_id=int(row['circuitId']),
                    name=safe_str(row['name']) or 'Unknown',
                    date=safe_date(row.get('date')),
                    time=safe_time(row.get('time')),
                    url=safe_str(row.get('url'))
                )
                self.db.add(race)
                success += 1
                
                if success % 100 == 0:
                    self.db.commit()
                    
            except Exception as e:
                logger.error(f"?????? ???????? ????? race_id={row.get('raceId')}: {e}")
                self.db.rollback()
                continue
                
        self.db.commit()
        logger.info(f"????????? {success} ?????")

    def _load_results_from_file(self, filepath: str):
        df = pd.read_csv(filepath)
        result = self.load_results(df)
        logger.info(f"????????? ???????? ???????????: {result}")

    def fix_all_sequences(self):
        """????????? ??? sequences ????? ???????? ????????"""
        from sqlalchemy import text
        
        logger.info("??????????? sequences...")
        
        sequences = [
            ('drivers_driver_id_seq', 'drivers', 'driver_id'),
            ('constructors_constructor_id_seq', 'constructors', 'constructor_id'),
            ('circuits_circuit_id_seq', 'circuits', 'circuit_id'),
            ('races_race_id_seq', 'races', 'race_id'),
            ('results_result_id_seq', 'results', 'result_id'),
            ('status_status_id_seq', 'status', 'status_id'),
        ]
        
        for seq_name, table_name, id_column in sequences:
            try:
                query = text(
                    f"SELECT setval('{seq_name}', "
                    f"(SELECT COALESCE(MAX({id_column}), 0) + 1 FROM {table_name}), false)"
                )
                self.db.execute(query)
                self.db.commit()
                logger.info(f"? {seq_name} ?????????")
            except Exception as e:
                logger.error(f"? ?????? {seq_name}: {e}")

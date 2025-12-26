import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db, engine
from app.models import Driver, Constructor, Circuit, Race, Result, Status
from sqlalchemy.orm import Session
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_PATH = Path("/data/kaggle_dataset")
DRIVERS_CSV = DATA_PATH / "drivers.csv"
CONSTRUCTORS_CSV = DATA_PATH / "constructors.csv"
CIRCUITS_CSV = DATA_PATH / "circuits.csv"
RACES_CSV = DATA_PATH / "races.csv"
RESULTS_CSV = DATA_PATH / "results.csv"
STATUS_CSV = DATA_PATH / "status.csv"

def check_files_exist():
    files = [DRIVERS_CSV, CONSTRUCTORS_CSV, CIRCUITS_CSV, RACES_CSV, RESULTS_CSV, STATUS_CSV]
    missing_files = []
    for file in files:
        if not file.exists():
            missing_files.append(str(file))
            logger.warning(f"? ???? ?? ??????: {file}")
        else:
            logger.info(f"? ???? ??????: {file}")
    
    if missing_files:
        logger.error(f"??????????? ?????: {missing_files}")
        return False
    return True

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

def load_status(db: Session):
    try:
        existing = db.query(Status).count()
        if existing > 0:
            logger.info(f"? ??????? ??? ????????? ({existing} ???????). ??????????.")
            return existing
        
        logger.info("???????? ????????...")
        df = pd.read_csv(STATUS_CSV)
        df = df.drop_duplicates(subset=['statusId'], keep='first')
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                status = Status(
                    status_id=int(row['statusId']),
                    status=safe_str(row['status']) or 'Unknown'
                )
                db.add(status)
                success_count += 1
                
                if success_count % 50 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"?????? ???????: {e}")
                db.rollback()
                continue
        
        db.commit()
        logger.info(f"? ????????? {success_count} ????????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ????????: {e}")
        db.rollback()
        return 0

def load_drivers(db: Session):
    try:
        existing = db.query(Driver).count()
        if existing > 0:
            logger.info(f"? ?????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ???????...")
        df = pd.read_csv(DRIVERS_CSV)
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                driver = Driver(
                    driver_id=int(row['driverId']),
                    driver_ref=safe_str(row['driverRef']) or 'unknown',
                    number=safe_int(row.get('number')),
                    code=safe_str(row.get('code')),
                    forename=safe_str(row['forename']) or 'Unknown',
                    surname=safe_str(row['surname']) or 'Unknown',
                    dob=safe_date(row.get('dob')),
                    nationality=safe_str(row.get('nationality')),
                    url=safe_str(row.get('url'))
                )
                db.add(driver)
                success_count += 1

                if success_count % 100 == 0:
                    db.commit()
                    logger.info(f"  ????????? {success_count} ???????...")
            except Exception as e:
                logger.error(f"?????? ??????: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ???????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ???????: {e}")
        db.rollback()
        return 0

def load_constructors(db: Session):
    try:
        existing = db.query(Constructor).count()
        if existing > 0:
            logger.info(f"? ??????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ??????...")
        df = pd.read_csv(CONSTRUCTORS_CSV)

        success_count = 0
        for _, row in df.iterrows():
            try:
                constructor = Constructor(
                    constructor_id=int(row['constructorId']),
                    constructor_ref=safe_str(row['constructorRef']) or 'unknown',
                    name=safe_str(row['name']) or 'Unknown',
                    nationality=safe_str(row.get('nationality')),
                    url=safe_str(row.get('url'))
                )
                db.add(constructor)
                success_count += 1

                if success_count % 50 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"?????? ???????: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ??????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ??????: {e}")
        db.rollback()
        return 0

def load_circuits(db: Session):
    try:
        existing = db.query(Circuit).count()
        if existing > 0:
            logger.info(f"? ?????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ?????...")
        df = pd.read_csv(CIRCUITS_CSV)

        success_count = 0
        for _, row in df.iterrows():
            try:
                circuit = Circuit(
                    circuit_id=int(row['circuitId']),
                    circuit_ref=safe_str(row['circuitRef']) or 'unknown',
                    name=safe_str(row['name']) or 'Unknown',
                    location=safe_str(row.get('location')),
                    country=safe_str(row.get('country')),
                    lat=safe_float(row.get('lat')),
                    lng=safe_float(row.get('lng')),
                    alt=safe_int(row.get('alt')),
                    url=safe_str(row.get('url'))
                )
                db.add(circuit)
                success_count += 1
            except Exception as e:
                logger.error(f"?????? ??????: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ?????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ?????: {e}")
        db.rollback()
        return 0

def load_races(db: Session):
    try:
        existing = db.query(Race).count()
        if existing > 0:
            logger.info(f"? ????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ?????...")
        df = pd.read_csv(RACES_CSV)

        success_count = 0
        for _, row in df.iterrows():
            try:
                race = Race(
                    race_id=int(row['raceId']),
                    year=int(row['year']),
                    round=int(row['round']),
                    circuit_id=int(row['circuitId']),
                    name=safe_str(row['name']) or 'Unknown',
                    date=safe_date(row.get('date')),
                    time=safe_time(row.get('time')),
                    url=safe_str(row.get('url'))
                )
                db.add(race)
                success_count += 1

                if success_count % 100 == 0:
                    db.commit()
                    logger.info(f"  ????????? {success_count} ?????...")
            except Exception as e:
                logger.error(f"?????? ???????? ?????: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ?????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ?????: {e}")
        db.rollback()
        return 0

def load_results(db: Session):
    try:
        existing = db.query(Result).count()
        if existing > 0:
            logger.info(f"? ?????????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ???????????...")
        df = pd.read_csv(RESULTS_CSV)
        total = len(df)

        success_count = 0
        for _, row in df.iterrows():
            try:
                result = Result(
                    result_id=int(row['resultId']),
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    constructor_id=int(row['constructorId']),
                    number=safe_int(row.get('number')),
                    grid=int(row['grid']),
                    position=safe_int(row.get('position')),
                    position_text=safe_str(row['positionText']) or 'N/A',
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
                db.add(result)
                success_count += 1

                if success_count % 500 == 0:
                    db.commit()
                    progress = (success_count / total) * 100
                    logger.info(f"  ????????? {success_count}/{total} ??????????? ({progress:.1f}%)...")
            except Exception as e:
                logger.error(f"?????? ??????????: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ???????????")
        return success_count
    except Exception as e:
        logger.error(f"? ?????? ???????? ???????????: {e}")
        db.rollback()
        return 0

def main():
    logger.info("=== ?????? ???????? ?????? Kaggle F1 Dataset ===")

    if not check_files_exist():
        logger.error("?? ??? ????? ???????. ???????? ????????.")
        return

    db = next(get_db())

    try:
        start_time = datetime.now()

        stats = {
            'status': load_status(db),
            'drivers': load_drivers(db),
            'constructors': load_constructors(db),
            'circuits': load_circuits(db),
            'races': load_races(db),
            'results': load_results(db)
        }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "="*60)
        logger.info("=== ???????? ?????????? ===")
        logger.info(f"???????:      {stats['status']:>6} ???????")
        logger.info(f"??????:       {stats['drivers']:>6} ???????")
        logger.info(f"???????:      {stats['constructors']:>6} ???????")
        logger.info(f"??????:       {stats['circuits']:>6} ???????")
        logger.info(f"?????:        {stats['races']:>6} ???????")
        logger.info(f"??????????:   {stats['results']:>6} ???????")
        logger.info(f"\n????? ????????: {duration:.2f} ??????")
        logger.info("="*60)
        logger.info("\n? ???????? ?????? ????????? ???????!")

    except Exception as e:
        logger.error(f"? ??????????? ??????: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db, engine
from app.models import (
    Driver, Constructor, Circuit, Race, Result, Status,
    LapTime, PitStop, Qualifying
)
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
LAP_TIMES_CSV = DATA_PATH / "lap_times.csv"
PIT_STOPS_CSV = DATA_PATH / "pit_stops.csv"
QUALIFYING_CSV = DATA_PATH / "qualifying.csv"

def check_files_exist():
    files = [
        DRIVERS_CSV, CONSTRUCTORS_CSV, CIRCUITS_CSV, RACES_CSV, 
        RESULTS_CSV, STATUS_CSV, LAP_TIMES_CSV, PIT_STOPS_CSV, QUALIFYING_CSV
    ]
    missing_files = []
    for file in files:
        if not file.exists():
            missing_files.append(str(file))
            logger.warning(f"???? ?? ??????: {file}")
        else:
            logger.info(f"???? ??????: {file}")
    
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
            logger.info(f"? ??????? ??? ????????? ({existing}).")
            return existing
        logger.info("???????? ????????...")
        df = pd.read_csv(STATUS_CSV)
        df = df.drop_duplicates(subset=['statusId'], keep='first')
        for _, row in df.iterrows():
            db.add(Status(status_id=int(row['statusId']), status=safe_str(row['status']) or 'Unknown'))
        db.commit()
        return len(df)
    except Exception as e:
        logger.error(f"Err status: {e}")
        db.rollback()
        return 0

def load_drivers(db: Session):
    try:
        existing = db.query(Driver).count()
        if existing > 0: return existing
        logger.info("???????? ???????...")
        df = pd.read_csv(DRIVERS_CSV)
        for _, row in df.iterrows():
            db.add(Driver(
                driver_id=int(row['driverId']),
                driver_ref=safe_str(row['driverRef']),
                number=safe_int(row.get('number')),
                code=safe_str(row.get('code')),
                forename=safe_str(row['forename']),
                surname=safe_str(row['surname']),
                dob=safe_date(row.get('dob')),
                nationality=safe_str(row.get('nationality')),
                url=safe_str(row.get('url'))
            ))
        db.commit()
        return len(df)
    except Exception as e:
        db.rollback()
        return 0

def load_constructors(db: Session):
    try:
        existing = db.query(Constructor).count()
        if existing > 0: return existing
        logger.info("???????? ??????...")
        df = pd.read_csv(CONSTRUCTORS_CSV)
        for _, row in df.iterrows():
            db.add(Constructor(
                constructor_id=int(row['constructorId']),
                constructor_ref=safe_str(row['constructorRef']),
                name=safe_str(row['name']),
                nationality=safe_str(row.get('nationality')),
                url=safe_str(row.get('url'))
            ))
        db.commit()
        return len(df)
    except Exception as e:
        db.rollback()
        return 0

def load_circuits(db: Session):
    try:
        existing = db.query(Circuit).count()
        if existing > 0: return existing
        logger.info("???????? ?????...")
        df = pd.read_csv(CIRCUITS_CSV)
        for _, row in df.iterrows():
            db.add(Circuit(
                circuit_id=int(row['circuitId']),
                circuit_ref=safe_str(row['circuitRef']),
                name=safe_str(row['name']),
                location=safe_str(row.get('location')),
                country=safe_str(row.get('country')),
                lat=safe_float(row.get('lat')),
                lng=safe_float(row.get('lng')),
                alt=safe_int(row.get('alt')),
                url=safe_str(row.get('url'))
            ))
        db.commit()
        return len(df)
    except Exception as e:
        db.rollback()
        return 0

def load_races(db: Session):
    try:
        existing = db.query(Race).count()
        if existing > 0: return existing
        logger.info("???????? ?????...")
        df = pd.read_csv(RACES_CSV)
        for _, row in df.iterrows():
            db.add(Race(
                race_id=int(row['raceId']),
                year=int(row['year']),
                round=int(row['round']),
                circuit_id=int(row['circuitId']),
                name=safe_str(row['name']),
                date=safe_date(row.get('date')),
                time=safe_time(row.get('time')),
                url=safe_str(row.get('url'))
            ))
        db.commit()
        return len(df)
    except Exception as e:
        db.rollback()
        return 0

def load_results(db: Session):
    try:
        existing = db.query(Result).count()
        if existing > 0:
            logger.info(f"?????????? ??? ????????? ({existing}).")
            return existing
        logger.info("???????? ???????????...")
        df = pd.read_csv(RESULTS_CSV)
        count = 0
        for _, row in df.iterrows():
            db.add(Result(
                result_id=int(row['resultId']),
                race_id=int(row['raceId']),
                driver_id=int(row['driverId']),
                constructor_id=int(row['constructorId']),
                number=safe_int(row.get('number')),
                grid=int(row['grid']),
                position=safe_int(row.get('position')),
                position_text=safe_str(row['positionText']),
                position_order=int(row['positionOrder']),
                points=safe_float(row.get('points')),
                laps=int(row['laps']),
                time_text=safe_str(row.get('time')),
                milliseconds=safe_int(row.get('milliseconds')),
                fastest_lap=safe_int(row.get('fastestLap')),
                rank=safe_int(row.get('rank')),
                fastest_lap_time=safe_str(row.get('fastestLapTime')),
                fastest_lap_speed=safe_float(row.get('fastestLapSpeed')),
                status_id=int(row['statusId'])
            ))
            count += 1
            if count % 1000 == 0: db.commit()
        db.commit()
        return count
    except Exception as e:
        logger.error(f"Err results: {e}")
        db.rollback()
        return 0


def load_qualifying(db: Session):
    try:
        existing = db.query(Qualifying).count()
        if existing > 0:
            logger.info(f"???????????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ????????????...")
        df = pd.read_csv(QUALIFYING_CSV)
        total = len(df)
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                qual = Qualifying(
                    qualify_id=int(row['qualifyId']),
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    constructor_id=int(row['constructorId']),
                    number=safe_int(row.get('number')),
                    position=safe_int(row.get('position')),
                    q1=safe_str(row.get('q1')),
                    q2=safe_str(row.get('q2')),
                    q3=safe_str(row.get('q3'))
                )
                db.add(qual)
                success_count += 1
                if success_count % 1000 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"?????? ???????????? id {row.get('qualifyId')}: {e}")
                continue

        db.commit()
        logger.info(f"????????? {success_count} ????????????")
        return success_count
    except Exception as e:
        logger.error(f"?????? ???????? ????????????: {e}")
        db.rollback()
        return 0

def load_lap_times(db: Session):
    try:
        existing = db.query(LapTime).count()
        if existing > 0:
            logger.info(f"??????? ?????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ?????? ?????? (??? ????? ?????? ?????)...")
        df = pd.read_csv(LAP_TIMES_CSV)
        total = len(df)
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                lap = LapTime(
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    lap=int(row['lap']),
                    position=safe_int(row.get('position')),
                    time_text=safe_str(row.get('time')), 
                    milliseconds=safe_int(row.get('milliseconds'))
                )
                db.add(lap)
                success_count += 1
                if success_count % 5000 == 0:
                    db.commit()
                    progress = (success_count / total) * 100
                    logger.info(f"  ????????? {success_count}/{total} ?????? ({progress:.1f}%)...")
            except Exception as e:
                continue

        db.commit()
        logger.info(f"????????? {success_count} ?????? ??????")
        return success_count
    except Exception as e:
        logger.error(f"?????? ???????? ?????? ??????: {e}")
        db.rollback()
        return 0

def load_pit_stops(db: Session):
    try:
        existing = db.query(PitStop).count()
        if existing > 0:
            logger.info(f"? ???-????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ???-??????...")
        df = pd.read_csv(PIT_STOPS_CSV)
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                time_val = safe_time(row.get('time'))
                
                if time_val is None:
                    continue

                pit = PitStop(
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    stop=int(row['stop']),
                    lap=int(row['lap']),
                    time_of_day=time_val, 
                    duration=safe_str(row.get('duration')),
                    milliseconds=safe_int(row.get('milliseconds'))
                )
                db.add(pit)
                success_count += 1
                if success_count % 1000 == 0:
                    db.commit()
            except Exception as e:
                logger.error(f"?????? ???-?????: {e}")
                continue

        db.commit()
        logger.info(f"????????? {success_count} ???-??????")
        return success_count
    except Exception as e:
        logger.error(f"?????? ???????? ???-??????: {e}")
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
            'results': load_results(db),
            'qualifying': load_qualifying(db),
            'pit_stops': load_pit_stops(db),
            'lap_times': load_lap_times(db)
        }
        
        logger.info("=" * 60)
        fix_sequences(db) 
        logger.info("=" * 60)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "="*60)
        logger.info("=== ???????? ?????????? ===")
        for key, value in stats.items():
            logger.info(f"{key.capitalize():<15}: {value:>6} ???????")
            
        logger.info(f"\n????? ????????: {duration:.2f} ??????")
        logger.info("="*60)
        logger.info("\n? ???????? ?????? ????????? ???????!")

    except Exception as e:
        logger.error(f"??????????? ??????: {e}")
    finally:
        db.close()

def fix_sequences(db: Session):
    """????????? ??? sequences ????? ???????? ??????"""
    from sqlalchemy import text
    
    logger.info("??????????? sequences ??? ??????????????...")
    
    sequences = [
        ('drivers_driver_id_seq', 'drivers', 'driver_id'),
        ('constructors_constructor_id_seq', 'constructors', 'constructor_id'),
        ('circuits_circuit_id_seq', 'circuits', 'circuit_id'),
        ('races_race_id_seq', 'races', 'race_id'),
        ('results_result_id_seq', 'results', 'result_id'),
        ('status_status_id_seq', 'status', 'status_id'),
        ('qualifying_qualify_id_seq', 'qualifying', 'qualify_id'),
    ]
    
    for seq_name, table_name, id_column in sequences:
        try:
            query = text(f"SELECT setval('{seq_name}', (SELECT COALESCE(MAX({id_column}), 0) + 1 FROM {table_name}), false)")
            db.execute(query)
            db.commit()
            logger.info(f"????????? sequence {seq_name}")
        except Exception as e:
            logger.warning(f"?? ??????? ????????? sequence {seq_name} (???????? ??? ??? ??? ??? ??????): {e}")
            db.rollback()
    
    logger.info("Sequences ??????????.")

if __name__ == "__main__":
    main()

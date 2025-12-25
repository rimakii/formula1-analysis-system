import sys
import os
from pathlib import Path

# ????????? ???? ? app ??? ???????
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db, engine
from app.models import Driver, Constructor, Circuit, Race, Result, Status
from sqlalchemy.orm import Session
import pandas as pd
import logging
from datetime import datetime

# ????????? ???????????
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ???? ? CSV ??????
DATA_PATH = Path("/data/kaggle_dataset")
DRIVERS_CSV = DATA_PATH / "drivers.csv"
CONSTRUCTORS_CSV = DATA_PATH / "constructors.csv"
CIRCUITS_CSV = DATA_PATH / "circuits.csv"
RACES_CSV = DATA_PATH / "races.csv"
RESULTS_CSV = DATA_PATH / "results.csv"
STATUS_CSV = DATA_PATH / "status.csv"

def check_files_exist():
    """???????? ??????? ???? ??????????? CSV ??????"""
    files = [
        DRIVERS_CSV,
        CONSTRUCTORS_CSV,
        CIRCUITS_CSV,
        RACES_CSV,
        RESULTS_CSV,
        STATUS_CSV
    ]

    missing_files = []
    for file in files:
        if not file.exists():
            missing_files.append(str(file))
            logger.warning(f"? ???? ?? ??????: {file}")
        else:
            logger.info(f"? ???? ??????: {file}")

    if missing_files:
        logger.error(f"??????????? ?????: {missing_files}")
        logger.error("???????? ??????? ? https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020")
        return False

    return True
def load_status(db: Session):
    """????????? ???????"""
    try:
        existing = db.query(Status).count()
        if existing > 0:
            logger.info(f"? ??????? ??? ????????? ({existing} ???????). ??????????.")
            return existing
        
        logger.info("???????? ????????...")
        df = pd.read_csv(STATUS_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])
        
        logger.info(f"??????? {len(df)} ???????? ? CSV")
        
        success_count = 0
        for _, row in df.iterrows():
            try:
                status_id = int(row['statusId'])
                status_text = str(row['status'])
                
                status = Status(
                    status_id=status_id,
                    status=status_text
                )
                db.merge(status)
                success_count += 1
                
                if success_count % 50 == 0:
                    db.commit()
                    logger.info(f"  ????????? {success_count} ????????...")
                    
            except Exception as e:
                logger.error(f"  ?????? ??? ???????? ???????: {e}")
                continue
        
        db.commit()
        logger.info(f"? ????????? {success_count} ????????")
        return success_count
        
    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ????????: {e}")
        db.rollback()
        return 0


def load_drivers(db: Session):
    """????????? ???????"""
    try:
        existing = db.query(Driver).count()
        if existing > 0:
            logger.info(f"? ?????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ???????...")
        # ????????? ??? \N ??? NULL ????????
        df = pd.read_csv(DRIVERS_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])

        success_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                # ?????????? ????????? ????
                dob = None
                if pd.notna(row.get('dob')):
                    try:
                        dob = pd.to_datetime(row['dob']).date()
                    except:
                        pass

                # ?????????? ????????? ???????? ?????
                driver_id = None
                if pd.notna(row.get('driverId')):
                    driver_id = int(row['driverId'])

                number = None
                if pd.notna(row.get('number')):
                    try:
                        number = int(float(row['number']))
                    except:
                        pass

                driver = Driver(
                    driver_id=driver_id,
                    driver_ref=str(row['driverRef']),
                    number=number,
                    code=str(row['code']) if pd.notna(row.get('code')) else None,
                    forename=str(row['forename']),
                    surname=str(row['surname']),
                    dob=dob,
                    nationality=str(row['nationality']) if pd.notna(row.get('nationality')) else None,
                    url=str(row['url']) if pd.notna(row.get('url')) else None
                )
                db.merge(driver)
                success_count += 1

                # Commit ?????? 100 ???????
                if success_count % 100 == 0:
                    db.commit()
                    logger.info(f"  ????????? {success_count} ???????...")

            except Exception as e:
                error_count += 1
                if error_count <= 10:
                    logger.error(f"  ?????? ? ?????? {index}: {e}")
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ??????? (??????: {error_count})")
        return success_count

    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ???????: {e}")
        db.rollback()
        return 0

def load_constructors(db: Session):
    """????????? ???????"""
    try:
        existing = db.query(Constructor).count()
        if existing > 0:
            logger.info(f"? ??????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ??????...")
        df = pd.read_csv(CONSTRUCTORS_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])

        success_count = 0

        for index, row in df.iterrows():
            try:
                constructor_id = None
                if pd.notna(row.get('constructorId')):
                    constructor_id = int(row['constructorId'])

                constructor = Constructor(
                    constructor_id=constructor_id,
                    constructor_ref=str(row['constructorRef']),
                    name=str(row['name']),
                    nationality=str(row['nationality']) if pd.notna(row.get('nationality')) else None,
                    url=str(row['url']) if pd.notna(row.get('url')) else None
                )
                db.merge(constructor)
                success_count += 1

                if success_count % 50 == 0:
                    db.commit()

            except Exception as e:
                logger.error(f"  ?????? ? ?????? {index}: {e}")
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ??????")
        return success_count

    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ??????: {e}")
        db.rollback()
        return 0

def load_circuits(db: Session):
    """????????? ??????"""
    try:
        existing = db.query(Circuit).count()
        if existing > 0:
            logger.info(f"? ?????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ?????...")
        df = pd.read_csv(CIRCUITS_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])

        success_count = 0

        for _, row in df.iterrows():
            try:
                circuit_id = None
                if pd.notna(row.get('circuitId')):
                    circuit_id = int(row['circuitId'])

                lat = None
                if pd.notna(row.get('lat')):
                    lat = float(row['lat'])

                lng = None
                if pd.notna(row.get('lng')):
                    lng = float(row['lng'])

                alt = None
                if pd.notna(row.get('alt')):
                    try:
                        alt = int(float(row['alt']))
                    except:
                        pass

                circuit = Circuit(
                    circuit_id=circuit_id,
                    circuit_ref=str(row['circuitRef']),
                    name=str(row['name']),
                    location=str(row['location']) if pd.notna(row.get('location')) else None,
                    country=str(row['country']) if pd.notna(row.get('country')) else None,
                    lat=lat,
                    lng=lng,
                    alt=alt,
                    url=str(row['url']) if pd.notna(row.get('url')) else None
                )
                db.merge(circuit)
                success_count += 1
            except Exception as e:
                logger.error(f"  ??????: {e}")
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ?????")
        return success_count

    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ?????: {e}")
        db.rollback()
        return 0

def load_races(db: Session):
    """????????? ?????"""
    try:
        existing = db.query(Race).count()
        if existing > 0:
            logger.info(f"? ????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ?????...")
        df = pd.read_csv(RACES_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])

        success_count = 0

        for _, row in df.iterrows():
            try:
                race_id = None
                if pd.notna(row.get('raceId')):
                    race_id = int(row['raceId'])

                # ????????? ????
                race_date = None
                if pd.notna(row.get('date')):
                    try:
                        race_date = pd.to_datetime(row['date']).date()
                    except:
                        pass

                # ????????? ???????
                race_time = None
                if pd.notna(row.get('time')):
                    try:
                        race_time = pd.to_datetime(row['time'], format='%H:%M:%S').time()
                    except:
                        pass

                race = Race(
                    race_id=race_id,
                    year=int(row['year']),
                    round=int(row['round']),
                    circuit_id=int(row['circuitId']),
                    name=str(row['name']),
                    date=race_date,
                    time=race_time,
                    url=str(row['url']) if pd.notna(row.get('url')) else None
                )
                db.merge(race)
                success_count += 1

                if success_count % 100 == 0:
                    db.commit()
                    logger.info(f"  ????????? {success_count} ?????...")

            except Exception as e:
                logger.error(f"  ??????: {e}")
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ?????")
        return success_count

    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ?????: {e}")
        db.rollback()
        return 0

def load_results(db: Session):
    """????????? ?????????? ?????"""
    try:
        existing = db.query(Result).count()
        if existing > 0:
            logger.info(f"? ?????????? ??? ????????? ({existing} ???????). ??????????.")
            return existing

        logger.info("???????? ???????????...")
        df = pd.read_csv(RESULTS_CSV, na_values=['\\N', 'NULL', '', 'nan', 'N/A'])
        total = len(df)

        logger.info(f"????? ??????????? ??? ????????: {total}")

        success_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                # ?????????? ?????????? ???? ?????
                result_id = None
                if pd.notna(row.get('resultId')):
                    result_id = int(row['resultId'])

                number = None
                if pd.notna(row.get('number')):
                    try:
                        number = int(float(row['number']))
                    except:
                        pass

                position = None
                if pd.notna(row.get('position')):
                    try:
                        position = int(float(row['position']))
                    except:
                        pass

                milliseconds = None
                if pd.notna(row.get('milliseconds')):
                    try:
                        milliseconds = int(float(row['milliseconds']))
                    except:
                        pass

                fastest_lap = None
                if pd.notna(row.get('fastestLap')):
                    try:
                        fastest_lap = int(float(row['fastestLap']))
                    except:
                        pass

                rank = None
                if pd.notna(row.get('rank')):
                    try:
                        rank = int(float(row['rank']))
                    except:
                        pass

                fastest_lap_speed = None
                if pd.notna(row.get('fastestLapSpeed')):
                    try:
                        fastest_lap_speed = float(row['fastestLapSpeed'])
                    except:
                        pass

                result = Result(
                    result_id=result_id,
                    race_id=int(row['raceId']),
                    driver_id=int(row['driverId']),
                    constructor_id=int(row['constructorId']),
                    number=number,
                    grid=int(row['grid']),
                    position=position,
                    position_text=str(row['positionText']),
                    position_order=int(row['positionOrder']),
                    points=float(row['points']) if pd.notna(row.get('points')) else 0.0,
                    laps=int(row['laps']),
                    time_text=str(row['time']) if pd.notna(row.get('time')) else None,
                    milliseconds=milliseconds,
                    fastest_lap=fastest_lap,
                    rank=rank,
                    fastest_lap_time=str(row['fastestLapTime']) if pd.notna(row.get('fastestLapTime')) else None,
                    fastest_lap_speed=fastest_lap_speed,
                    status_id=int(row['statusId'])
                )
                db.merge(result)
                success_count += 1

                # Commit ?????? 500 ???????
                if success_count % 500 == 0:
                    db.commit()
                    progress = (success_count / total) * 100
                    logger.info(f"  ????????? {success_count}/{total} ??????????? ({progress:.1f}%)...")

            except Exception as e:
                error_count += 1
                if error_count <= 10:
                    logger.error(f"  ?????? ? ?????? {index}: {e}")
                continue

        db.commit()
        logger.info(f"? ????????? {success_count} ??????????? (??????: {error_count})")
        return success_count

    except Exception as e:
        logger.error(f"? ?????? ??? ???????? ???????????: {e}")
        db.rollback()
        return 0

def main():
    """???????? ??????? ???????? ??????"""
    logger.info("=== ?????? ???????? ?????? Kaggle F1 Dataset ===")

    # ???????? ??????? ??????
    if not check_files_exist():
        logger.error("?? ??? ????? ???????. ???????? ????????.")
        return

    # ???????? ?????? ??
    db = next(get_db())

    try:
        start_time = datetime.now()

        # ????????? ?????? ? ?????????? ??????? (??-?? ??????? ??????)
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

        # ???????? ??????????
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
        logger.error(f"? ??????????? ?????? ??? ???????? ??????: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
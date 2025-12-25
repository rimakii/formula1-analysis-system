from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/driver-stats/{driver_id}")
def get_driver_stats(driver_id: int, db: Session = Depends(get_db)):
    query = text("SELECT * FROM get_driver_career_stats(:driver_id)")
    result = db.execute(query, {"driver_id": driver_id}).fetchone()
    if not result:
        return {"message": "No stats found"}
    return dict(result._mapping)

@router.get("/season-standings/{year}")
def get_season_standings(year: int, db: Session = Depends(get_db)):
    query = text("SELECT * FROM get_season_driver_standings(:year)")
    results = db.execute(query, {"year": year}).fetchall()
    return [dict(row._mapping) for row in results]

@router.get("/constructor-standings/{year}")
def get_constructor_standings(year: int, db: Session = Depends(get_db)):
    query = text("SELECT * FROM get_season_constructor_standings(:year)")
    results = db.execute(query, {"year": year}).fetchall()
    return [dict(row._mapping) for row in results]

@router.get("/circuit-history/{circuit_id}")
def get_circuit_history(circuit_id: int, limit: int = 10, db: Session = Depends(get_db)):
    query = text("SELECT * FROM get_circuit_history(:circuit_id, :limit)")
    results = db.execute(query, {"circuit_id": circuit_id, "limit": limit}).fetchall()
    return [dict(row._mapping) for row in results]

@router.get("/driver-statistics")
def get_all_driver_statistics(db: Session = Depends(get_db)):
    query = text("SELECT * FROM v_driver_statistics ORDER BY total_points DESC LIMIT 50")
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

@router.get("/constructor-statistics")
def get_all_constructor_statistics(db: Session = Depends(get_db)):
    query = text("SELECT * FROM v_constructor_statistics ORDER BY total_points DESC LIMIT 50")
    results = db.execute(query).fetchall()
    return [dict(row._mapping) for row in results]

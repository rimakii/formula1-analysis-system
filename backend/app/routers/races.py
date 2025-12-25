from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Race
from app.schemas import RaceCreate, RaceResponse
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/races", tags=["Races"])

@router.get("", response_model=List[RaceResponse])
def get_races(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    races = db.query(Race).offset(skip).limit(limit).all()
    return races

@router.get("/{race_id}", response_model=RaceResponse)
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.query(Race).filter(Race.race_id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race

@router.post("", response_model=RaceResponse)
def create_race(
    race: RaceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_race = Race(**race.model_dump())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race

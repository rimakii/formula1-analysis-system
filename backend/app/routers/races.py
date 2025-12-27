"""
API ????????? ??? ?????? ? ???????
?????? CRUD ????? ORM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models import Race
from app.schemas import RaceCreate, RaceResponse, RaceUpdate
from app.auth.dependencies import require_admin, get_current_active_user


router = APIRouter(prefix="/races", tags=["Races"])


@router.get("", response_model=List[RaceResponse])
def get_races(
    skip: int = 0, 
    limit: int = 100,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    ???????? ?????? ????? ? ???????????.
    - skip: ?????????? N ??????? (pagination)
    - limit: ???????? ???????
    - year: ?????? ?? ???? (???????????)
    """
    query = db.query(Race)
    
    if year:
        query = query.filter(Race.year == year)
    
    races = query.order_by(Race.year.desc(), Race.round).offset(skip).limit(limit).all()
    return races


@router.get("/{race_id}", response_model=RaceResponse)
def get_race(race_id: int, db: Session = Depends(get_db)):
    """???????? ?????????? ? ?????????? ????? ?? ID"""
    race = db.query(Race).filter(Race.race_id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail=f"Race with ID {race_id} not found")
    return race


@router.post("", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
def create_race(
    race: RaceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????? ????? (????????? ???? ??????????????).
    race_id ???????????? ????????????? PostgreSQL.
    """
    try:
        db_race = Race(**race.model_dump())
        db.add(db_race)
        db.commit()
        db.refresh(db_race)
        return db_race
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'unique' in error_msg and 'year' in error_msg and 'round' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Race for year {race.year} round {race.round} already exists"
            )
        elif 'circuit_id' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Circuit with ID {race.circuit_id} does not exist"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create race: {str(e.orig)}")


@router.put("/{race_id}", response_model=RaceResponse)
def update_race(
    race_id: int,
    race_update: RaceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ???????? ?????????? ? ????? (????????? ???? ??????????????).
    ????? ???????? ???????? - ?????? ????????? ????.
    """
    db_race = db.query(Race).filter(Race.race_id == race_id).first()
    if not db_race:
        raise HTTPException(status_code=404, detail=f"Race with ID {race_id} not found")
    
    update_data = race_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_race, field, value)
    
    try:
        db.commit()
        db.refresh(db_race)
        return db_race
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e.orig)}")


@router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_race(
    race_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????? (????????? ???? ??????????????).
    ????????: ???????? ?????? ??? ????????? results, qualifying ? ?.?.
    """
    race = db.query(Race).filter(Race.race_id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail=f"Race with ID {race_id} not found")
    
    try:
        db.delete(race)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete race: {str(e.orig)}"
        )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Result
from app.schemas import ResultCreate, ResultResponse
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/results", tags=["Results"])

@router.get("", response_model=List[ResultResponse])
def get_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    results = db.query(Result).offset(skip).limit(limit).all()
    return results

@router.get("/race/{race_id}", response_model=List[ResultResponse])
def get_race_results(race_id: int, db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.race_id == race_id).all()
    return results

@router.post("", response_model=ResultResponse)
def create_result(
    result: ResultCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_result = Result(**result.model_dump())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

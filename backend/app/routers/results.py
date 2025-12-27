"""
API ????????? ??? ?????? ? ???????????? ?????
?????? CRUD ????? ORM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models import Result
from app.schemas import ResultCreate, ResultResponse, ResultUpdate
from app.auth.dependencies import require_admin, get_current_active_user


router = APIRouter(prefix="/results", tags=["Results"])


@router.get("", response_model=List[ResultResponse])
def get_results(
    skip: int = 0,
    limit: int = 100,
    race_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    ???????? ?????? ??????????? ? ???????????.
    - skip: ?????????? N ???????
    - limit: ???????? ???????
    - race_id: ?????? ?? ?????
    - driver_id: ?????? ?? ??????
    """
    query = db.query(Result)
    
    if race_id:
        query = query.filter(Result.race_id == race_id)
    
    if driver_id:
        query = query.filter(Result.driver_id == driver_id)
    
    results = query.order_by(Result.race_id.desc(), Result.position_order).offset(skip).limit(limit).all()
    return results



@router.get("/{result_id}", response_model=ResultResponse)
def get_result(result_id: int, db: Session = Depends(get_db)):
    """???????? ?????????? ????????? ?? ID"""
    result = db.query(Result).filter(Result.result_id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Result with ID {result_id} not found")
    return result


@router.post("", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
def create_result(
    result: ResultCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????? ????????? ????? (????????? ???? ??????????????).
    result_id ???????????? ????????????? PostgreSQL.
    """
    try:
        db_result = Result(**result.model_dump())
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'race_id' in error_msg:
            raise HTTPException(status_code=400, detail=f"Race ID {result.race_id} does not exist")
        elif 'driver_id' in error_msg:
            raise HTTPException(status_code=400, detail=f"Driver ID {result.driver_id} does not exist")
        elif 'constructor_id' in error_msg:
            raise HTTPException(status_code=400, detail=f"Constructor ID {result.constructor_id} does not exist")
        elif 'status_id' in error_msg:
            raise HTTPException(status_code=400, detail=f"Status ID {result.status_id} does not exist")
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create result: {str(e.orig)}")


@router.put("/{result_id}", response_model=ResultResponse)
def update_result(
    result_id: int,
    result_update: ResultUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ???????? ????????? ????? (????????? ???? ??????????????).
    ????? ???????? ???????? - ?????? ????????? ????.
    """
    db_result = db.query(Result).filter(Result.result_id == result_id).first()
    if not db_result:
        raise HTTPException(status_code=404, detail=f"Result with ID {result_id} not found")
    
    update_data = result_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_result, field, value)
    
    try:
        db.commit()
        db.refresh(db_result)
        return db_result
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e.orig)}")


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????????? ????? (????????? ???? ??????????????).
    """
    result = db.query(Result).filter(Result.result_id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Result with ID {result_id} not found")
    
    try:
        db.delete(result)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Cannot delete result: {str(e.orig)}")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models import Driver
from app.schemas import DriverCreate, DriverResponse, DriverUpdate
from app.auth.dependencies import require_admin, get_current_active_user


router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("", response_model=List[DriverResponse])
def get_drivers(
    skip: int = 0, 
    limit: int = 100,
    nationality: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Driver)
    
    if nationality:
        query = query.filter(Driver.nationality == nationality)
    
    drivers = query.offset(skip).limit(limit).all()
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver with ID {driver_id} not found")
    return driver

@router.get("/by-ref/{driver_ref}", response_model=DriverResponse)
def get_driver_by_ref(driver_ref: str, db: Session = Depends(get_db)):
    """???????? ?????? ?? driver_ref"""
    driver = db.query(Driver).filter(Driver.driver_ref == driver_ref).first()
    if not driver:
        raise HTTPException(
            status_code=404, 
            detail=f"Driver with ref '{driver_ref}' not found"
        )
    return driver


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """??????? ?????? ?????? (????????? ???? ??????????????)"""
    try:
        db_driver = Driver(**driver.model_dump())
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        return db_driver
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if 'driver_ref' in error_msg or 'unique' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Driver with reference '{driver.driver_ref}' already exists"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create driver: {str(e.orig)}")


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver_update: DriverUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail=f"Driver with ID {driver_id} not found")
    
    update_data = driver_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_driver, field, value)
    
    try:
        db.commit()
        db.refresh(db_driver)
        return db_driver
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver with ID {driver_id} not found")
    
    try:
        db.delete(driver)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete driver: foreign key constraint. {str(e)}"
        )

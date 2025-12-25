from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Constructor
from app.schemas import ConstructorCreate, ConstructorResponse
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/constructors", tags=["Constructors"])

@router.get("", response_model=List[ConstructorResponse])
def get_constructors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    constructors = db.query(Constructor).offset(skip).limit(limit).all()
    return constructors

@router.get("/{constructor_id}", response_model=ConstructorResponse)
def get_constructor(constructor_id: int, db: Session = Depends(get_db)):
    constructor = db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail="Constructor not found")
    return constructor

@router.post("", response_model=ConstructorResponse, status_code=status.HTTP_201_CREATED)
def create_constructor(
    constructor: ConstructorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_constructor = Constructor(**constructor.model_dump())
    db.add(db_constructor)
    db.commit()
    db.refresh(db_constructor)
    return db_constructor

@router.delete("/{constructor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_constructor(
    constructor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    constructor = db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail="Constructor not found")
    db.delete(constructor)
    db.commit()
    return None

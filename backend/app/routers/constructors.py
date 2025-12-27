"""
API ????????? ??? ?????? ? ?????????/??????????????
?????? CRUD ????? ORM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models import Constructor
from app.schemas import ConstructorCreate, ConstructorResponse, ConstructorUpdate
from app.auth.dependencies import require_admin, get_current_active_user


router = APIRouter(prefix="/constructors", tags=["Constructors"])


@router.get("", response_model=List[ConstructorResponse])
def get_constructors(
    skip: int = 0,
    limit: int = 100,
    nationality: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ???????? ?????? ?????? ? ???????????.
    - skip: ?????????? N ??????? (pagination)
    - limit: ???????? ???????
    - nationality: ?????? ?? ?????????????? (???????????)
    """
    query = db.query(Constructor)
    
    if nationality:
        query = query.filter(Constructor.nationality == nationality)
    
    constructors = query.order_by(Constructor.name).offset(skip).limit(limit).all()
    return constructors


@router.get("/{constructor_id}", response_model=ConstructorResponse)
def get_constructor(constructor_id: int, db: Session = Depends(get_db)):
    """???????? ?????????? ? ?????????? ??????? ?? ID"""
    constructor = db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail=f"Constructor with ID {constructor_id} not found")
    return constructor


@router.post("", response_model=ConstructorResponse, status_code=status.HTTP_201_CREATED)
def create_constructor(
    constructor: ConstructorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????? ??????? (????????? ???? ??????????????).
    constructor_id ???????????? ????????????? PostgreSQL.
    """
    try:
        db_constructor = Constructor(**constructor.model_dump())
        db.add(db_constructor)
        db.commit()
        db.refresh(db_constructor)
        return db_constructor
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'constructor_ref' in error_msg or 'unique' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Constructor with reference '{constructor.constructor_ref}' already exists"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create constructor: {str(e.orig)}")


@router.put("/{constructor_id}", response_model=ConstructorResponse)
def update_constructor(
    constructor_id: int,
    constructor_update: ConstructorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ???????? ?????????? ? ??????? (????????? ???? ??????????????).
    ????? ???????? ???????? - ?????? ????????? ????.
    """
    db_constructor = db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
    if not db_constructor:
        raise HTTPException(status_code=404, detail=f"Constructor with ID {constructor_id} not found")
    
    update_data = constructor_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_constructor, field, value)
    
    try:
        db.commit()
        db.refresh(db_constructor)
        return db_constructor
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e.orig)}")



@router.delete("/{constructor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_constructor(
    constructor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ??????? (????????? ???? ??????????????).
    ????????: ????? ?? ????????? ???? ???? ????????? results (RESTRICT constraint).
    """
    constructor = db.query(Constructor).filter(Constructor.constructor_id == constructor_id).first()
    if not constructor:
        raise HTTPException(status_code=404, detail=f"Constructor with ID {constructor_id} not found")
    
    try:
        db.delete(constructor)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete constructor: has related results. {str(e.orig)}"
        )

"""
API ????????? ??? ?????? ? ????????
?????? CRUD ????? ORM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.database import get_db
from app.models import Circuit
from app.schemas import CircuitCreate, CircuitResponse, CircuitUpdate
from app.auth.dependencies import require_admin, get_current_active_user


router = APIRouter(prefix="/circuits", tags=["Circuits"])


@router.get("", response_model=List[CircuitResponse])
def get_circuits(
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    ???????? ?????? ????? ? ???????????.
    - skip: ?????????? N ??????? (pagination)
    - limit: ???????? ???????
    - country: ?????? ?? ?????? (???????????)
    """
    query = db.query(Circuit)
    
    if country:
        query = query.filter(Circuit.country == country)
    
    circuits = query.order_by(Circuit.name).offset(skip).limit(limit).all()
    return circuits


@router.get("/{circuit_id}", response_model=CircuitResponse)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    """???????? ?????????? ? ?????????? ?????? ?? ID"""
    circuit = db.query(Circuit).filter(Circuit.circuit_id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail=f"Circuit with ID {circuit_id} not found")
    return circuit


@router.post("", response_model=CircuitResponse, status_code=status.HTTP_201_CREATED)
def create_circuit(
    circuit: CircuitCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ????? ?????? (????????? ???? ??????????????).
    circuit_id ???????????? ????????????? PostgreSQL.
    """
    try:
        db_circuit = Circuit(**circuit.model_dump())
        db.add(db_circuit)
        db.commit()
        db.refresh(db_circuit)
        return db_circuit
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'circuit_ref' in error_msg or 'unique' in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Circuit with reference '{circuit.circuit_ref}' already exists"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create circuit: {str(e.orig)}")


@router.put("/{circuit_id}", response_model=CircuitResponse)
def update_circuit(
    circuit_id: int,
    circuit_update: CircuitUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ???????? ?????????? ? ?????? (????????? ???? ??????????????).
    ????? ???????? ???????? - ?????? ????????? ????.
    """
    db_circuit = db.query(Circuit).filter(Circuit.circuit_id == circuit_id).first()
    if not db_circuit:
        raise HTTPException(status_code=404, detail=f"Circuit with ID {circuit_id} not found")
    
    update_data = circuit_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_circuit, field, value)
    
    try:
        db.commit()
        db.refresh(db_circuit)
        return db_circuit
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e.orig)}")


@router.delete("/{circuit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_circuit(
    circuit_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    ??????? ?????? (????????? ???? ??????????????).
    ????????: ????? ?? ????????? ???? ???? ????????? ????? (RESTRICT constraint).
    """
    circuit = db.query(Circuit).filter(Circuit.circuit_id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail=f"Circuit with ID {circuit_id} not found")
    
    try:
        db.delete(circuit)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete circuit: has related races. {str(e.orig)}"
        )

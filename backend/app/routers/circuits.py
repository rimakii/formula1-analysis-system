from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Circuit
from app.schemas import CircuitCreate, CircuitResponse
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/circuits", tags=["Circuits"])

@router.get("", response_model=List[CircuitResponse])
def get_circuits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    circuits = db.query(Circuit).offset(skip).limit(limit).all()
    return circuits

@router.get("/{circuit_id}", response_model=CircuitResponse)
def get_circuit(circuit_id: int, db: Session = Depends(get_db)):
    circuit = db.query(Circuit).filter(Circuit.circuit_id == circuit_id).first()
    if not circuit:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return circuit

@router.post("", response_model=CircuitResponse)
def create_circuit(
    circuit: CircuitCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_circuit = Circuit(**circuit.model_dump())
    db.add(db_circuit)
    db.commit()
    db.refresh(db_circuit)
    return db_circuit

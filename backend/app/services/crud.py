from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    """
    ??????? ????? ??? CRUD ????????.
    ????????? ??????????? ???????? Create, Read, Update, Delete.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """???????? ?????? ?? ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """???????? ?????? ???????? ? ??????????"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        """??????? ????? ??????"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: dict
    ) -> ModelType:
        """???????? ???????????? ??????"""
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """??????? ?????? ?? ID"""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session) -> int:
        """?????????? ?????????? ???????"""
        return db.query(self.model).count()

    def exists(self, db: Session, id: int) -> bool:
        """????????? ????????????? ???????"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

from app.models import Driver, Constructor, Circuit, Race, Result

class CRUDDriver(CRUDBase[Driver]):
    """CRUD ???????? ??? ???????"""

    def get_by_ref(self, db: Session, driver_ref: str) -> Optional[Driver]:
        return db.query(Driver).filter(Driver.driver_ref == driver_ref).first()

    def get_by_nationality(self, db: Session, nationality: str) -> List[Driver]:
        return db.query(Driver).filter(Driver.nationality == nationality).all()

class CRUDConstructor(CRUDBase[Constructor]):
    """CRUD ???????? ??? ??????"""

    def get_by_ref(self, db: Session, constructor_ref: str) -> Optional[Constructor]:
        return db.query(Constructor).filter(Constructor.constructor_ref == constructor_ref).first()

class CRUDCircuit(CRUDBase[Circuit]):
    """CRUD ???????? ??? ?????"""

    def get_by_country(self, db: Session, country: str) -> List[Circuit]:
        return db.query(Circuit).filter(Circuit.country == country).all()

class CRUDRace(CRUDBase[Race]):
    """CRUD ???????? ??? ?????"""

    def get_by_year(self, db: Session, year: int) -> List[Race]:
        return db.query(Race).filter(Race.year == year).order_by(Race.round).all()

    def get_by_circuit(self, db: Session, circuit_id: int) -> List[Race]:
        return db.query(Race).filter(Race.circuit_id == circuit_id).all()

class CRUDResult(CRUDBase[Result]):
    """CRUD ???????? ??? ???????????"""

    def get_by_race(self, db: Session, race_id: int) -> List[Result]:
        return db.query(Result).filter(Result.race_id == race_id).order_by(Result.position_order).all()

    def get_by_driver(self, db: Session, driver_id: int) -> List[Result]:
        return db.query(Result).filter(Result.driver_id == driver_id).all()

    def get_wins(self, db: Session, driver_id: int) -> List[Result]:
        return db.query(Result).filter(
            Result.driver_id == driver_id,
            Result.position == 1
        ).all()

crud_driver = CRUDDriver(Driver)
crud_constructor = CRUDConstructor(Constructor)
crud_circuit = CRUDCircuit(Circuit)
crud_race = CRUDRace(Race)
crud_result = CRUDResult(Result)

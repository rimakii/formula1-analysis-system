from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DriverBase(BaseModel):
    driver_ref: str
    forename: str
    surname: str
    number: Optional[int] = None
    code: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    url: Optional[str] = None

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    driver_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConstructorBase(BaseModel):
    constructor_ref: str
    name: str
    nationality: Optional[str] = None
    url: Optional[str] = None

class ConstructorCreate(ConstructorBase):
    pass

class ConstructorResponse(ConstructorBase):
    constructor_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CircuitBase(BaseModel):
    circuit_ref: str
    name: str
    location: Optional[str] = None
    country: Optional[str] = None

class CircuitCreate(CircuitBase):
    pass

class CircuitResponse(CircuitBase):
    circuit_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RaceBase(BaseModel):
    year: int
    round: int
    circuit_id: int
    name: str
    date: date

class RaceCreate(RaceBase):
    pass

class RaceResponse(RaceBase):
    race_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResultBase(BaseModel):
    race_id: int
    driver_id: int
    constructor_id: int
    grid: int
    position: Optional[int] = None
    position_text: str
    position_order: int
    points: Decimal = Decimal(0)
    laps: int
    status_id: int

class ResultCreate(ResultBase):
    pass

class ResultResponse(ResultBase):
    result_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

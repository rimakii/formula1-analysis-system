"""
Pydantic ????? ??? ????????? ?????? API
F1 Analytics System
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, time as Time, datetime
from typing import Optional
from decimal import Decimal


# ====================
# USER SCHEMAS
# ====================

class UserBase(BaseModel):
    """??????? ????? ????????????"""
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """????? ??? ???????? ????????????"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """????? ?????? ? ??????? ????????????"""
    user_id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """????? ??? ?????????? ????????????"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# AUTH SCHEMAS
# ====================

class Token(BaseModel):
    """JWT ?????"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """?????? ?? JWT ??????"""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """????? ??? ??????"""
    username: EmailStr  # email ???????????? ??? username
    password: str


# ====================
# DRIVER SCHEMAS
# ====================

class DriverBase(BaseModel):
    """??????? ????? ??????"""
    driver_ref: str = Field(..., min_length=1, max_length=255)
    forename: str = Field(..., min_length=1, max_length=255)
    surname: str = Field(..., min_length=1, max_length=255)
    number: Optional[int] = Field(None, ge=0, le=999)
    code: Optional[str] = Field(None, max_length=3)
    dob: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=255)


class DriverCreate(DriverBase):
    """????? ??? ???????? ?????? (driver_id ???????????????? ??)"""
    pass


class DriverResponse(DriverBase):
    """????? ?????? ? ??????? ??????"""
    driver_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DriverUpdate(BaseModel):
    """????? ??? ?????????? ?????? (??? ???? ???????????)"""
    driver_ref: Optional[str] = Field(None, min_length=1, max_length=255)
    number: Optional[int] = Field(None, ge=0, le=999)
    code: Optional[str] = Field(None, max_length=3)
    forename: Optional[str] = Field(None, min_length=1, max_length=255)
    surname: Optional[str] = Field(None, min_length=1, max_length=255)
    dob: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=255)
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# CONSTRUCTOR SCHEMAS
# ====================

class ConstructorBase(BaseModel):
    """??????? ????? ???????"""
    constructor_ref: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    nationality: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=255)


class ConstructorCreate(ConstructorBase):
    """????? ??? ???????? ???????"""
    pass


class ConstructorResponse(ConstructorBase):
    """????? ?????? ? ??????? ???????"""
    constructor_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConstructorUpdate(BaseModel):
    """????? ??? ?????????? ???????"""
    constructor_ref: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    nationality: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=255)
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# CIRCUIT SCHEMAS
# ====================

class CircuitBase(BaseModel):
    """??????? ????? ??????"""
    circuit_ref: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=255)
    lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    alt: Optional[int] = None
    url: Optional[str] = Field(None, max_length=255)


class CircuitCreate(CircuitBase):
    """????? ??? ???????? ??????"""
    pass


class CircuitResponse(CircuitBase):
    """????? ?????? ? ??????? ??????"""
    circuit_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CircuitUpdate(BaseModel):
    """????? ??? ?????????? ??????"""
    circuit_ref: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=255)
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None
    alt: Optional[int] = None
    url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# RACE SCHEMAS
# ====================

class RaceBase(BaseModel):
    """??????? ????? ?????"""
    year: int = Field(..., ge=1950, le=2100)
    round: int = Field(..., ge=1, le=30)
    circuit_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    date: date
    time: Optional[Time] = None 
    url: Optional[str] = Field(None, max_length=255)



class RaceCreate(RaceBase):
    """????? ??? ???????? ?????"""
    pass


class RaceResponse(BaseModel):
    """????? ?????? ? ??????? ?????"""
    race_id: int
    year: int
    round: int
    circuit_id: int
    name: str
    date: date
    time: Optional[Time] = None
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



class RaceUpdate(BaseModel):
    """????? ??? ?????????? ?????"""
    year: Optional[int] = Field(None, ge=1950, le=2100)
    round: Optional[int] = Field(None, ge=1, le=30)
    circuit_id: Optional[int] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[date] = None
    time: Optional[Time] = None
    url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# RESULT SCHEMAS
# ====================

class ResultBase(BaseModel):
    """??????? ????? ?????????? ?????"""
    race_id: int = Field(..., gt=0)
    driver_id: int = Field(..., gt=0)
    constructor_id: int = Field(..., gt=0)
    number: Optional[int] = Field(None, ge=0, le=999)
    grid: int = Field(..., ge=0)
    position: Optional[int] = Field(None, ge=1, le=30)
    position_text: str = Field(..., max_length=10)
    position_order: int = Field(..., ge=1)
    points: Decimal = Field(default=Decimal("0.0"), ge=0)
    laps: int = Field(..., ge=0)
    time_text: Optional[str] = Field(None, max_length=255)
    milliseconds: Optional[int] = Field(None, ge=0)
    fastest_lap: Optional[int] = Field(None, ge=1)
    rank: Optional[int] = Field(None, ge=0)
    fastest_lap_time: Optional[str] = Field(None, max_length=255)
    fastest_lap_speed: Optional[Decimal] = Field(None, ge=0)
    status_id: int = Field(..., gt=0)


class ResultCreate(ResultBase):
    """????? ??? ???????? ??????????"""
    pass


class ResultResponse(ResultBase):
    """????? ?????? ? ??????? ??????????"""
    result_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ResultUpdate(BaseModel):
    """????? ??? ?????????? ??????????"""
    race_id: Optional[int] = None
    driver_id: Optional[int] = None
    constructor_id: Optional[int] = None
    number: Optional[int] = None
    grid: Optional[int] = None
    position: Optional[int] = None
    position_text: Optional[str] = None
    position_order: Optional[int] = None
    points: Optional[Decimal] = None
    laps: Optional[int] = None
    time_text: Optional[str] = None
    milliseconds: Optional[int] = None
    fastest_lap: Optional[int] = None
    rank: Optional[int] = None
    fastest_lap_time: Optional[str] = None
    fastest_lap_speed: Optional[Decimal] = None
    status_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# STATUS SCHEMAS
# ====================

class StatusBase(BaseModel):
    """??????? ????? ??????? ??????"""
    status: str = Field(..., min_length=1, max_length=255)


class StatusCreate(StatusBase):
    """????? ??? ???????? ???????"""
    pass


class StatusResponse(StatusBase):
    """????? ?????? ? ??????? ???????"""
    status_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ====================
# ANALYTICS SCHEMAS (??? VIEW ? ???????)
# ====================

class DriverStatistics(BaseModel):
    """?????????? ?????? ?? VIEW"""
    driver_id: int
    driver_ref: str
    full_name: str
    nationality: Optional[str]
    dob: Optional[date]
    total_races: int
    total_points: Decimal
    wins: int
    podiums: int
    top_10_finishes: int
    fastest_laps: int
    career_start_year: Optional[int]
    career_end_year: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)


class ConstructorStatistics(BaseModel):
    """?????????? ??????? ?? VIEW"""
    constructor_id: int
    constructor_ref: str
    name: str
    nationality: Optional[str]
    total_races: int
    total_points: Decimal
    wins: int
    podiums: int
    first_year: Optional[int]
    last_year: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)


class SeasonStanding(BaseModel):
    """????????? ??????? ?? ???????"""
    position: int
    driver_id: Optional[int] = None
    constructor_id: Optional[int] = None
    name: str
    nationality: str
    total_points: Decimal
    wins: int
    podiums: int
    races: int
    
    model_config = ConfigDict(from_attributes=True)

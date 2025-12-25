from sqlalchemy import Column, Integer, String, Date, Time, Numeric, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Driver(Base):
    __tablename__ = "drivers"

    driver_id = Column(Integer, primary_key=True, index=True)
    driver_ref = Column(String(100), unique=True, nullable=False)
    number = Column(Integer)
    code = Column(String(3))
    forename = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    dob = Column(Date)
    nationality = Column(String(100))
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    results = relationship("Result", back_populates="driver")
    qualifying = relationship("Qualifying", back_populates="driver")

class Constructor(Base):
    __tablename__ = "constructors"

    constructor_id = Column(Integer, primary_key=True, index=True)
    constructor_ref = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    nationality = Column(String(100))
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    results = relationship("Result", back_populates="constructor")
    qualifying = relationship("Qualifying", back_populates="constructor")

class Circuit(Base):
    __tablename__ = "circuits"

    circuit_id = Column(Integer, primary_key=True, index=True)
    circuit_ref = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    location = Column(String(200))
    country = Column(String(100))
    lat = Column(Numeric(10, 6))
    lng = Column(Numeric(10, 6))
    alt = Column(Integer)
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    races = relationship("Race", back_populates="circuit")

class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(100), unique=True, nullable=False)

    results = relationship("Result", back_populates="status_ref")

class Race(Base):
    __tablename__ = "races"

    race_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    circuit_id = Column(Integer, ForeignKey("circuits.circuit_id"), nullable=False)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time)
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    circuit = relationship("Circuit", back_populates="races")
    results = relationship("Result", back_populates="race", cascade="all, delete-orphan")
    qualifying = relationship("Qualifying", back_populates="race", cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id"), nullable=False)
    number = Column(Integer)
    grid = Column(Integer, nullable=False)
    position = Column(Integer)
    position_text = Column(String(10), nullable=False)
    position_order = Column(Integer, nullable=False)
    points = Column(Numeric(5, 2), nullable=False, default=0)
    laps = Column(Integer, nullable=False)
    time_text = Column(String(50))
    milliseconds = Column(Integer)
    fastest_lap = Column(Integer)
    rank = Column(Integer)
    fastest_lap_time = Column(String(20))
    fastest_lap_speed = Column(String(20))
    status_id = Column(Integer, ForeignKey("status.status_id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    race = relationship("Race", back_populates="results")
    driver = relationship("Driver", back_populates="results")
    constructor = relationship("Constructor", back_populates="results")
    status_ref = relationship("Status", back_populates="results")

class Qualifying(Base):
    __tablename__ = "qualifying"

    qualify_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id"), nullable=False)
    number = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    q1 = Column(String(20))
    q2 = Column(String(20))
    q3 = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

    race = relationship("Race", back_populates="qualifying")
    driver = relationship("Driver", back_populates="qualifying")
    constructor = relationship("Constructor", back_populates="qualifying")

class LapTime(Base):
    __tablename__ = "lap_times"

    lap_time_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    lap = Column(Integer, nullable=False)
    position = Column(Integer)
    time_text = Column(String(20))
    milliseconds = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class PitStop(Base):
    __tablename__ = "pit_stops"

    pit_stop_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    stop = Column(Integer, nullable=False)
    lap = Column(Integer, nullable=False)
    time_of_day = Column(Time, nullable=False)
    duration = Column(String(20))
    milliseconds = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class DriverStanding(Base):
    __tablename__ = "driver_standings"

    driver_standing_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    points = Column(Numeric(8, 2), nullable=False, default=0)
    position = Column(Integer, nullable=False)
    position_text = Column(String(10))
    wins = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class ConstructorStanding(Base):
    __tablename__ = "constructor_standings"

    constructor_standing_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id"), nullable=False)
    points = Column(Numeric(8, 2), nullable=False, default=0)
    position = Column(Integer, nullable=False)
    position_text = Column(String(10))
    wins = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"

    audit_id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    operation = Column(String(10), nullable=False)
    record_id = Column(Integer, nullable=False)
    old_data = Column(Text)
    new_data = Column(Text)
    changed_by = Column(String(255))
    changed_at = Column(TIMESTAMP, server_default=func.now())

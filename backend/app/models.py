"""
SQLAlchemy ?????? ??? F1 Analytics System
???????????????? ? 01_create_tables.sql
"""

from sqlalchemy import (
    Column, Integer, String, Date, Time, Numeric, Boolean, 
    ForeignKey, CheckConstraint, UniqueConstraint, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from app.database import Base


class Driver(Base):
    """?????? ???????-1"""
    __tablename__ = "drivers"

    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_ref = Column(String(100), unique=True, nullable=False)
    number = Column(Integer)
    code = Column(String(3))
    forename = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    dob = Column(Date)
    nationality = Column(String(100))
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    results = relationship("Result", back_populates="driver")
    qualifying = relationship("Qualifying", back_populates="driver")
    lap_times = relationship("LapTime", back_populates="driver")
    pit_stops = relationship("PitStop", back_populates="driver")
    driver_standings = relationship("DriverStanding", back_populates="driver")

    def __repr__(self):
        return f"<Driver(id={self.driver_id}, name='{self.forename} {self.surname}')>"


class Constructor(Base):
    """???????/???????????? ???????-1"""
    __tablename__ = "constructors"

    constructor_id = Column(Integer, primary_key=True, autoincrement=True)
    constructor_ref = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    nationality = Column(String(100))
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    results = relationship("Result", back_populates="constructor")
    qualifying = relationship("Qualifying", back_populates="constructor")
    constructor_standings = relationship("ConstructorStanding", back_populates="constructor")

    def __repr__(self):
        return f"<Constructor(id={self.constructor_id}, name='{self.name}')>"


class Circuit(Base):
    """???????? ??????"""
    __tablename__ = "circuits"

    circuit_id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_ref = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    location = Column(String(200))
    country = Column(String(100))
    lat = Column(Numeric(10, 6))
    lng = Column(Numeric(10, 6))
    alt = Column(Integer)
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    races = relationship("Race", back_populates="circuit")

    def __repr__(self):
        return f"<Circuit(id={self.circuit_id}, name='{self.name}')>"


class Status(Base):
    """??????? ?????? ?????"""
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(100), nullable=False)

    results = relationship("Result", back_populates="status_ref")

    def __repr__(self):
        return f"<Status(id={self.status_id}, status='{self.status}')>"


class Race(Base):
    """?????"""
    __tablename__ = "races"

    race_id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    circuit_id = Column(Integer, ForeignKey("circuits.circuit_id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time)
    url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('year >= 1950 AND year <= 2100', name='races_year_check'),
        CheckConstraint('round > 0', name='races_round_check'),
        UniqueConstraint('year', 'round', name='races_year_round_key'),
    )

    circuit = relationship("Circuit", back_populates="races")
    results = relationship("Result", back_populates="race", cascade="all, delete-orphan")
    qualifying = relationship("Qualifying", back_populates="race", cascade="all, delete-orphan")
    lap_times = relationship("LapTime", back_populates="race", cascade="all, delete-orphan")
    pit_stops = relationship("PitStop", back_populates="race", cascade="all, delete-orphan")
    driver_standings = relationship("DriverStanding", back_populates="race", cascade="all, delete-orphan")
    constructor_standings = relationship("ConstructorStanding", back_populates="race", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Race(id={self.race_id}, name='{self.name}', year={self.year})>"


class Result(Base):
    """?????????? ?????"""
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="RESTRICT"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id", ondelete="RESTRICT"), nullable=False)
    number = Column(Integer)
    grid = Column(Integer, nullable=False)
    position = Column(Integer)
    position_text = Column(String(10), nullable=False)
    position_order = Column(Integer, nullable=False)
    points = Column(Numeric(5, 2), nullable=False, default=0)
    laps = Column(Integer, nullable=False)
    time_text = Column(String(50))
    milliseconds = Column(BigInteger)
    fastest_lap = Column(Integer)
    rank = Column(Integer)
    fastest_lap_time = Column(String(20))
    fastest_lap_speed = Column(String(20))
    status_id = Column(Integer, ForeignKey("status.status_id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('grid >= 0', name='results_grid_check'),
        CheckConstraint('position > 0', name='results_position_check'),
        CheckConstraint('position_order > 0', name='results_position_order_check'),
        CheckConstraint('points >= 0', name='results_points_check'),
        CheckConstraint('laps >= 0', name='results_laps_check'),
        CheckConstraint('fastest_lap > 0', name='results_fastest_lap_check'),
    )

    race = relationship("Race", back_populates="results")
    driver = relationship("Driver", back_populates="results")
    constructor = relationship("Constructor", back_populates="results")
    status_ref = relationship("Status", back_populates="results")

    def __repr__(self):
        return f"<Result(id={self.result_id}, race_id={self.race_id}, position={self.position})>"


class Qualifying(Base):
    """?????????? ????????????"""
    __tablename__ = "qualifying"

    qualify_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="RESTRICT"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id", ondelete="RESTRICT"), nullable=False)
    number = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    q1 = Column(String(20))
    q2 = Column(String(20))
    q3 = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('position > 0', name='qualifying_position_check'),
        UniqueConstraint('race_id', 'driver_id', name='qualifying_race_id_driver_id_key'),
    )

    race = relationship("Race", back_populates="qualifying")
    driver = relationship("Driver", back_populates="qualifying")
    constructor = relationship("Constructor", back_populates="qualifying")

    def __repr__(self):
        return f"<Qualifying(id={self.qualify_id}, race_id={self.race_id}, position={self.position})>"


class LapTime(Base):
    """????? ??????????? ??????"""
    __tablename__ = "lap_times"

    lap_time_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="RESTRICT"), nullable=False)
    lap = Column(Integer, nullable=False)
    position = Column(Integer)
    time_text = Column(String(20))
    milliseconds = Column(BigInteger)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('lap > 0', name='lap_times_lap_check'),
        CheckConstraint('position > 0', name='lap_times_position_check'),
        UniqueConstraint('race_id', 'driver_id', 'lap', name='lap_times_race_id_driver_id_lap_key'),
    )

    race = relationship("Race", back_populates="lap_times")
    driver = relationship("Driver", back_populates="lap_times")

    def __repr__(self):
        return f"<LapTime(race_id={self.race_id}, driver_id={self.driver_id}, lap={self.lap})>"


class PitStop(Base):
    """???-?????"""
    __tablename__ = "pit_stops"

    pit_stop_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="RESTRICT"), nullable=False)
    stop = Column(Integer, nullable=False)
    lap = Column(Integer, nullable=False)
    time_of_day = Column(Time, nullable=False)
    duration = Column(String(20))
    milliseconds = Column(BigInteger)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('stop > 0', name='pit_stops_stop_check'),
        CheckConstraint('lap > 0', name='pit_stops_lap_check'),
        UniqueConstraint('race_id', 'driver_id', 'stop', name='pit_stops_race_id_driver_id_stop_key'),
    )

    race = relationship("Race", back_populates="pit_stops")
    driver = relationship("Driver", back_populates="pit_stops")

    def __repr__(self):
        return f"<PitStop(race_id={self.race_id}, driver_id={self.driver_id}, stop={self.stop})>"


class DriverStanding(Base):
    """????????? ??????? ???????"""
    __tablename__ = "driver_standings"

    driver_standing_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id", ondelete="RESTRICT"), nullable=False)
    points = Column(Numeric(8, 2), nullable=False, default=0)
    position = Column(Integer, nullable=False)
    position_text = Column(String(10))
    wins = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('points >= 0', name='driver_standings_points_check'),
        CheckConstraint('position > 0', name='driver_standings_position_check'),
        CheckConstraint('wins >= 0', name='driver_standings_wins_check'),
        UniqueConstraint('race_id', 'driver_id', name='driver_standings_race_id_driver_id_key'),
    )

    race = relationship("Race", back_populates="driver_standings")
    driver = relationship("Driver", back_populates="driver_standings")

    def __repr__(self):
        return f"<DriverStanding(race_id={self.race_id}, position={self.position})>"


class ConstructorStanding(Base):
    """????????? ??????? ??????"""
    __tablename__ = "constructor_standings"

    constructor_standing_id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id", ondelete="CASCADE"), nullable=False)
    constructor_id = Column(Integer, ForeignKey("constructors.constructor_id", ondelete="RESTRICT"), nullable=False)
    points = Column(Numeric(8, 2), nullable=False, default=0)
    position = Column(Integer, nullable=False)
    position_text = Column(String(10))
    wins = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint('points >= 0', name='constructor_standings_points_check'),
        CheckConstraint('position > 0', name='constructor_standings_position_check'),
        CheckConstraint('wins >= 0', name='constructor_standings_wins_check'),
        UniqueConstraint('race_id', 'constructor_id', name='constructor_standings_race_id_constructor_id_key'),
    )

    race = relationship("Race", back_populates="constructor_standings")
    constructor = relationship("Constructor", back_populates="constructor_standings")

    def __repr__(self):
        return f"<ConstructorStanding(race_id={self.race_id}, position={self.position})>"

class User(Base):
    """???????????? ???????"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    def __repr__(self):
        return f"<User(id={self.user_id}, email='{self.email}')>"


class AuditLog(Base):
    """?????? ?????? ?????????"""
    __tablename__ = "audit_log"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    operation = Column(String(10), nullable=False)
    record_id = Column(Integer, nullable=False)
    old_data = Column(JSONB)
    new_data = Column(JSONB)
    changed_by = Column(String(255))
    changed_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("operation IN ('INSERT', 'UPDATE', 'DELETE')", name='audit_log_operation_check'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.audit_id}, table='{self.table_name}', op='{self.operation}')>"

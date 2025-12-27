CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ??????? ???????
CREATE TABLE drivers (
    driver_id SERIAL PRIMARY KEY,
    driver_ref VARCHAR(100) NOT NULL UNIQUE,
    number INTEGER,
    code VARCHAR(3),
    forename VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    dob DATE,
    nationality VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ??????? ??????
CREATE TABLE constructors (
    constructor_id SERIAL PRIMARY KEY,
    constructor_ref VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    nationality VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ??????? ?????
CREATE TABLE circuits (
    circuit_id SERIAL PRIMARY KEY,
    circuit_ref VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    country VARCHAR(100),
    lat DECIMAL(10, 6),
    lng DECIMAL(10, 6),
    alt INTEGER,
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ??????? ????????
CREATE TABLE status (
    status_id SERIAL PRIMARY KEY,
    status VARCHAR(100) NOT NULL
);

-- ??????? ?????
CREATE TABLE races (
    race_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL CHECK (year >= 1950 AND year <= 2100),
    round INTEGER NOT NULL CHECK (round > 0),
    circuit_id INTEGER NOT NULL REFERENCES circuits(circuit_id) ON DELETE RESTRICT,
    name VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    time TIME,
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (year, round)
);

-- ??????? ??????????? ?????
CREATE TABLE results (
    result_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    constructor_id INTEGER NOT NULL REFERENCES constructors(constructor_id) ON DELETE RESTRICT,
    number INTEGER,
    grid INTEGER NOT NULL CHECK (grid >= 0),
    position INTEGER CHECK (position > 0),
    position_text VARCHAR(10) NOT NULL,
    position_order INTEGER NOT NULL CHECK (position_order > 0),
    points DECIMAL(5, 2) NOT NULL DEFAULT 0 CHECK (points >= 0),
    laps INTEGER NOT NULL CHECK (laps >= 0),
    time_text VARCHAR(50),
    milliseconds BIGINT,
    fastest_lap INTEGER CHECK (fastest_lap > 0),
    rank INTEGER, 
    fastest_lap_time VARCHAR(20),
    fastest_lap_speed VARCHAR(20),
    status_id INTEGER NOT NULL REFERENCES status(status_id) ON DELETE RESTRICT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ??????? ???????????????? ???????????
CREATE TABLE qualifying (
    qualify_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    constructor_id INTEGER NOT NULL REFERENCES constructors(constructor_id) ON DELETE RESTRICT,
    number INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    q1 VARCHAR(20),
    q2 VARCHAR(20),
    q3 VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (race_id, driver_id)
);

-- ??????? ??????? ??????????? ?????? 
CREATE TABLE lap_times (
    lap_time_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    lap INTEGER NOT NULL CHECK (lap > 0),
    position INTEGER CHECK (position > 0),
    time_text VARCHAR(20),
    milliseconds BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (race_id, driver_id, lap)
);

-- ??????? ???-??????
CREATE TABLE pit_stops (
    pit_stop_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    stop INTEGER NOT NULL CHECK (stop > 0),
    lap INTEGER NOT NULL CHECK (lap > 0),
    time_of_day TIME NOT NULL,
    duration VARCHAR(20),
    milliseconds BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (race_id, driver_id, stop)
);

-- ??????? ????????? ??????? ???????
CREATE TABLE driver_standings (
    driver_standing_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id) ON DELETE RESTRICT,
    points DECIMAL(8, 2) NOT NULL DEFAULT 0 CHECK (points >= 0),
    position INTEGER NOT NULL CHECK (position > 0),
    position_text VARCHAR(10),
    wins INTEGER NOT NULL DEFAULT 0 CHECK (wins >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (race_id, driver_id)
);

-- ??????? ????????? ??????? ??????
CREATE TABLE constructor_standings (
    constructor_standing_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    constructor_id INTEGER NOT NULL REFERENCES constructors(constructor_id) ON DELETE RESTRICT,
    points DECIMAL(8, 2) NOT NULL DEFAULT 0 CHECK (points >= 0),
    position INTEGER NOT NULL CHECK (position > 0),
    position_text VARCHAR(10),
    wins INTEGER NOT NULL DEFAULT 0 CHECK (wins >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (race_id, constructor_id)
);


-- ??????? ????????????? ???????
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ??????? ??????? ??????
CREATE TABLE audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id INTEGER NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

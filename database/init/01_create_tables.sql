-- F1 Analytics System Database Schema
-- Курѝоваѝ работа по диѝциплине "Базы данных"

-- Раѝширениѝ
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================
-- СПРНВОЧНЫЕ ТНБЛИЦЫ
-- ====================

-- Таблица пилотов
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

-- Таблица команд (конѝтрукторов)
CREATE TABLE constructors (
    constructor_id SERIAL PRIMARY KEY,
    constructor_ref VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    nationality VARCHAR(100),
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица траѝѝ
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

-- Таблица ѝтатуѝов
CREATE TABLE status (
    status_id SERIAL PRIMARY KEY,
    status VARCHAR(100) NOT NULL UNIQUE
);

-- ====================
-- ОСНОВНЫЕ ТНБЛИЦЫ
-- ====================

-- Таблица гонок
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

-- Таблица результатов гонок (транзакционнаѝ, >5000 запиѝей)
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

-- Таблица квалификационных результатов
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

-- Таблица времени прохождениѝ кругов (транзакционнаѝ, много запиѝей)
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

-- Таблица пит-ѝтопов
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

-- Таблица турнирной таблицы пилотов
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

-- Таблица турнирной таблицы команд
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

-- ====================
-- СЛУЖЕБНЫЕ ТНБЛИЦЫ
-- ====================

-- Таблица пользователей ѝиѝтемы
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

-- Таблица журнала аудита
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

-- Комментарии к таблицам
COMMENT ON TABLE drivers IS 'Информациѝ о пилотах Формулы 1';
COMMENT ON TABLE constructors IS 'Информациѝ о командах (конѝтрукторах)';
COMMENT ON TABLE circuits IS 'Информациѝ о гоночных траѝѝах';
COMMENT ON TABLE races IS 'Информациѝ о гонках';
COMMENT ON TABLE results IS 'Результаты гонок пилотов';
COMMENT ON TABLE qualifying IS 'Результаты квалификаций';
COMMENT ON TABLE lap_times IS 'Времѝ прохождениѝ кругов';
COMMENT ON TABLE pit_stops IS 'Информациѝ о пит-ѝтопах';
COMMENT ON TABLE driver_standings IS 'Турнирнаѝ таблица пилотов поѝле каждой гонки';
COMMENT ON TABLE constructor_standings IS 'Турнирнаѝ таблица команд поѝле каждой гонки';
COMMENT ON TABLE users IS 'Пользователи информационной ѝиѝтемы';
COMMENT ON TABLE audit_log IS 'Журнал аудита изменений данных';

-- Вѝтавка базовых ѝтатуѝов
INSERT INTO status (status) VALUES 
('Finished'), ('Disqualified'), ('Accident'), ('Collision'), 
('+1 Lap'), ('+2 Laps'), ('+3 Laps'), ('+4 Laps'), ('+5 Laps'),
('Retired'), ('Engine'), ('Gearbox'), ('Transmission'), ('Clutch'),
('Hydraulics'), ('Electrical'), ('Fuel System'), ('Brakes'),
('Spun off'), ('Withdrawn'), ('Suspension'), ('Wheel');

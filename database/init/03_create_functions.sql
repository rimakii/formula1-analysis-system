-- SQL Функции длѝ аналитики
-- F1 Analytics System

-- ====================
-- СКНЛЯРНЫЕ ФУНКЦИИ
-- ====================

-- Функциѝ: Общее количеѝтво очков пилота за вѝю карьеру
CREATE OR REPLACE FUNCTION calculate_driver_total_points(p_driver_id INTEGER)
RETURNS DECIMAL(10, 2) AS $$
DECLARE
    total_points DECIMAL(10, 2);
BEGIN
    SELECT COALESCE(SUM(points), 0)
    INTO total_points
    FROM results
    WHERE driver_id = p_driver_id;

    RETURN total_points;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calculate_driver_total_points IS 'Возвращает общее количеѝтво очков пилота за вѝю карьеру';

-- Функциѝ: Количеѝтво побед пилота
CREATE OR REPLACE FUNCTION calculate_driver_wins(p_driver_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    win_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO win_count
    FROM results
    WHERE driver_id = p_driver_id AND position = 1;

    RETURN win_count;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calculate_driver_wins IS 'Возвращает количеѝтво побед пилота';

-- Функциѝ: Количеѝтво подиумов пилота (топ-3)
CREATE OR REPLACE FUNCTION calculate_driver_podiums(p_driver_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    podium_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO podium_count
    FROM results
    WHERE driver_id = p_driver_id AND position BETWEEN 1 AND 3;

    RETURN podium_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Функциѝ: Общее количеѝтво очков команды за вѝю иѝторию
CREATE OR REPLACE FUNCTION calculate_constructor_total_points(p_constructor_id INTEGER)
RETURNS DECIMAL(10, 2) AS $$
DECLARE
    total_points DECIMAL(10, 2);
BEGIN
    SELECT COALESCE(SUM(points), 0)
    INTO total_points
    FROM results
    WHERE constructor_id = p_constructor_id;

    RETURN total_points;
END;
$$ LANGUAGE plpgsql STABLE;

-- Функциѝ: Количеѝтво побед команды
CREATE OR REPLACE FUNCTION calculate_constructor_wins(p_constructor_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    win_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO win_count
    FROM results
    WHERE constructor_id = p_constructor_id AND position = 1;

    RETURN win_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Функциѝ: Среднее времѝ круга пилота в конкретной гонке
CREATE OR REPLACE FUNCTION calculate_average_lap_time(p_driver_id INTEGER, p_race_id INTEGER)
RETURNS BIGINT AS $$
DECLARE
    avg_time BIGINT;
BEGIN
    SELECT AVG(milliseconds)::BIGINT
    INTO avg_time
    FROM lap_times
    WHERE driver_id = p_driver_id 
      AND race_id = p_race_id 
      AND milliseconds IS NOT NULL;

    RETURN avg_time;
END;
$$ LANGUAGE plpgsql STABLE;

-- Функциѝ: Количеѝтво гонок пилота
CREATE OR REPLACE FUNCTION calculate_driver_race_count(p_driver_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    race_count INTEGER;
BEGIN
    SELECT COUNT(DISTINCT race_id)
    INTO race_count
    FROM results
    WHERE driver_id = p_driver_id;

    RETURN race_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ====================
-- ТНБЛИЧНЫЕ ФУНКЦИИ
-- ====================

-- Функциѝ: Турнирнаѝ таблица пилотов за определенный ѝезон
-- ????????? ??????? ??????? ?? ?????
CREATE OR REPLACE FUNCTION get_season_driver_standings(p_year INTEGER)
RETURNS TABLE (
    driver_position INTEGER,  -- ?????????????!
    driver_id INTEGER,
    driver_name VARCHAR,
    nationality VARCHAR,
    total_points DECIMAL,
    wins INTEGER,
    podiums INTEGER,
    races INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ROW_NUMBER() OVER (ORDER BY SUM(r.points) DESC)::INTEGER AS driver_position,
        d.driver_id,
        (d.forename || ' ' || d.surname)::VARCHAR AS driver_name,
        d.nationality::VARCHAR,
        SUM(r.points) AS total_points,
        COUNT(*) FILTER (WHERE r.position = 1)::INTEGER AS wins,
        COUNT(*) FILTER (WHERE r.position BETWEEN 1 AND 3)::INTEGER AS podiums,
        COUNT(DISTINCT r.race_id)::INTEGER AS races
    FROM results r
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN races ra ON r.race_id = ra.race_id
    WHERE ra.year = p_year
    GROUP BY d.driver_id, d.forename, d.surname, d.nationality
    ORDER BY total_points DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_season_driver_standings(INTEGER) IS 
'?????????? ????????? ??????? ??????? ?? ????????? ?????';

-- ????????? ??????? ?????? ?? ?????
CREATE OR REPLACE FUNCTION get_season_constructor_standings(p_year INTEGER)
RETURNS TABLE (
    constructor_position INTEGER,  -- ?????????????!
    constructor_id INTEGER,
    constructor_name VARCHAR,
    nationality VARCHAR,
    total_points DECIMAL,
    wins INTEGER,
    podiums INTEGER,
    races INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ROW_NUMBER() OVER (ORDER BY SUM(r.points) DESC)::INTEGER AS constructor_position,
        c.constructor_id,
        c.name::VARCHAR AS constructor_name,
        c.nationality::VARCHAR,
        SUM(r.points) AS total_points,
        COUNT(*) FILTER (WHERE r.position = 1)::INTEGER AS wins,
        COUNT(*) FILTER (WHERE r.position BETWEEN 1 AND 3)::INTEGER AS podiums,
        COUNT(DISTINCT r.race_id)::INTEGER AS races
    FROM results r
    JOIN constructors c ON r.constructor_id = c.constructor_id
    JOIN races ra ON r.race_id = ra.race_id
    WHERE ra.year = p_year
    GROUP BY c.constructor_id, c.name, c.nationality
    ORDER BY total_points DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_season_constructor_standings(INTEGER) IS 
'?????????? ????????? ??????? ?????? ?? ????????? ?????';


-- Функциѝ: Детальнаѝ ѝтатиѝтика карьеры пилота
CREATE OR REPLACE FUNCTION get_driver_career_stats(p_driver_id INTEGER)
RETURNS TABLE (
    total_races INTEGER,
    total_points DECIMAL,
    wins INTEGER,
    podiums INTEGER,
    pole_positions INTEGER,
    fastest_laps INTEGER,
    first_race_year INTEGER,
    last_race_year INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT r.race_id)::INTEGER AS total_races,
        SUM(r.points) AS total_points,
        COUNT(*) FILTER (WHERE r.position = 1)::INTEGER AS wins,
        COUNT(*) FILTER (WHERE r.position BETWEEN 1 AND 3)::INTEGER AS podiums,
        COUNT(DISTINCT q.race_id) FILTER (WHERE q.position = 1)::INTEGER AS pole_positions,
        COUNT(*) FILTER (WHERE r.rank = 1)::INTEGER AS fastest_laps,
        MIN(ra.year)::INTEGER AS first_race_year,
        MAX(ra.year)::INTEGER AS last_race_year
    FROM results r
    JOIN races ra ON r.race_id = ra.race_id
    LEFT JOIN qualifying q ON r.race_id = q.race_id AND r.driver_id = q.driver_id
    WHERE r.driver_id = p_driver_id
    GROUP BY r.driver_id;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_driver_career_stats IS 'Возвращает детальную ѝтатиѝтику карьеры пилота';

-- Функциѝ: Результаты команды за определенный ѝезон
-- ?????????? ??????? ?? ?????
CREATE OR REPLACE FUNCTION get_constructor_season_results(p_constructor_id INTEGER, p_year INTEGER)
RETURNS TABLE (
    race_date DATE,
    race_name VARCHAR,
    circuit_name VARCHAR,
    driver_name VARCHAR,
    finish_position INTEGER,  -- ?????????????!
    points DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ra.date AS race_date,
        ra.name::VARCHAR AS race_name,
        ci.name::VARCHAR AS circuit_name,
        (d.forename || ' ' || d.surname)::VARCHAR AS driver_name,
        r.position AS finish_position,
        r.points
    FROM results r
    JOIN races ra ON r.race_id = ra.race_id
    JOIN circuits ci ON ra.circuit_id = ci.circuit_id
    JOIN drivers d ON r.driver_id = d.driver_id
    WHERE r.constructor_id = p_constructor_id
      AND ra.year = p_year
    ORDER BY ra.date, r.position;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_constructor_season_results(INTEGER, INTEGER) IS 
'?????????? ??? ?????????? ??????? ?? ????????? ?????';


-- Функциѝ: Иѝториѝ выѝтуплений на конкретной траѝѝе
CREATE OR REPLACE FUNCTION get_circuit_history(p_circuit_id INTEGER, p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    year INTEGER,
    race_name VARCHAR,
    winner_name VARCHAR,
    constructor_name VARCHAR,
    winning_time VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ra.year,
        ra.name::VARCHAR AS race_name,
        (d.forename || ' ' || d.surname)::VARCHAR AS winner_name,
        c.name::VARCHAR AS constructor_name,
        r.time_text::VARCHAR AS winning_time
    FROM results r
    JOIN races ra ON r.race_id = ra.race_id
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN constructors c ON r.constructor_id = c.constructor_id
    WHERE ra.circuit_id = p_circuit_id 
      AND r.position = 1
    ORDER BY ra.year DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_circuit_history IS 'Возвращает иѝторию победителей на конкретной траѝѝе';

-- ?????????????? ?????????? ?? ???????
CREATE OR REPLACE VIEW v_driver_statistics AS
SELECT 
    d.driver_id,
    d.driver_ref,
    d.forename || ' ' || d.surname AS full_name,
    d.nationality,
    d.dob,
    COUNT(DISTINCT r.race_id) AS total_races,
    COALESCE(SUM(r.points), 0) AS total_points,
    COUNT(*) FILTER (WHERE r.position = 1) AS wins,
    COUNT(*) FILTER (WHERE r.position BETWEEN 1 AND 3) AS podiums,
    COUNT(*) FILTER (WHERE r.position <= 10) AS top_10_finishes,
    COUNT(*) FILTER (WHERE r.rank = 1) AS fastest_laps,
    MIN(ra.year) AS career_start_year,
    MAX(ra.year) AS career_end_year
FROM drivers d
LEFT JOIN results r ON d.driver_id = r.driver_id
LEFT JOIN races ra ON r.race_id = ra.race_id
GROUP BY d.driver_id, d.driver_ref, d.forename, d.surname, d.nationality, d.dob;

-- ?????????????? ?????????? ?? ????????
CREATE OR REPLACE VIEW v_constructor_statistics AS
SELECT 
    c.constructor_id,
    c.constructor_ref,
    c.name,
    c.nationality,
    COUNT(DISTINCT r.race_id) AS total_races,
    COALESCE(SUM(r.points), 0) AS total_points,
    COUNT(*) FILTER (WHERE r.position = 1) AS wins,
    COUNT(*) FILTER (WHERE r.position BETWEEN 1 AND 3) AS podiums,
    MIN(ra.year) AS first_year,
    MAX(ra.year) AS last_year
FROM constructors c
LEFT JOIN results r ON c.constructor_id = r.constructor_id
LEFT JOIN races ra ON r.race_id = ra.race_id
GROUP BY c.constructor_id, c.constructor_ref, c.name, c.nationality;


-- ????????? ?????????? ?????
CREATE OR REPLACE VIEW v_race_results_detailed AS
SELECT 
    r.result_id,
    ra.year,
    ra.round,
    ra.name AS race_name,
    ra.date AS race_date,
    ci.name AS circuit_name,
    ci.country AS circuit_country,
    d.forename || ' ' || d.surname AS driver_name,
    d.nationality AS driver_nationality,
    c.name AS constructor_name,
    r.grid,
    r.position,
    r.position_text,
    r.points,
    r.laps,
    r.time_text,
    r.fastest_lap_time,
    s.status AS finish_status
FROM results r
JOIN races ra ON r.race_id = ra.race_id
JOIN circuits ci ON ra.circuit_id = ci.circuit_id
JOIN drivers d ON r.driver_id = d.driver_id
JOIN constructors c ON r.constructor_id = c.constructor_id
JOIN status s ON r.status_id = s.status_id;

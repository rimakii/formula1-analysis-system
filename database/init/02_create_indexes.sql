
-- ??????? ?? ??????? ??????

-- Races
CREATE INDEX idx_races_circuit_id ON races(circuit_id);
CREATE INDEX idx_races_year ON races(year);
CREATE INDEX idx_races_date ON races(date);
CREATE INDEX idx_races_year_round ON races(year, round);

-- Results
CREATE INDEX idx_results_race_id ON results(race_id);
CREATE INDEX idx_results_driver_id ON results(driver_id);
CREATE INDEX idx_results_constructor_id ON results(constructor_id);
CREATE INDEX idx_results_status_id ON results(status_id);

-- ????????? ??????? ??? ?????? ????????
CREATE INDEX idx_results_driver_race ON results(driver_id, race_id);
CREATE INDEX idx_results_constructor_race ON results(constructor_id, race_id);
CREATE INDEX idx_results_position ON results(position) WHERE position IS NOT NULL;
CREATE INDEX idx_results_points ON results(points) WHERE points > 0;

-- Qualifying
CREATE INDEX idx_qualifying_race_id ON qualifying(race_id);
CREATE INDEX idx_qualifying_driver_id ON qualifying(driver_id);
CREATE INDEX idx_qualifying_constructor_id ON qualifying(constructor_id);
CREATE INDEX idx_qualifying_position ON qualifying(position);

-- Lap Times
CREATE INDEX idx_lap_times_race_id ON lap_times(race_id);
CREATE INDEX idx_lap_times_driver_id ON lap_times(driver_id);
CREATE INDEX idx_lap_times_race_driver ON lap_times(race_id, driver_id);
CREATE INDEX idx_lap_times_milliseconds ON lap_times(milliseconds) WHERE milliseconds IS NOT NULL;

-- Pit Stops
CREATE INDEX idx_pit_stops_race_id ON pit_stops(race_id);
CREATE INDEX idx_pit_stops_driver_id ON pit_stops(driver_id);
CREATE INDEX idx_pit_stops_race_driver ON pit_stops(race_id, driver_id);

-- Driver Standings
CREATE INDEX idx_driver_standings_race_id ON driver_standings(race_id);
CREATE INDEX idx_driver_standings_driver_id ON driver_standings(driver_id);
CREATE INDEX idx_driver_standings_position ON driver_standings(position);
CREATE INDEX idx_driver_standings_points ON driver_standings(points DESC);

-- Constructor Standings
CREATE INDEX idx_constructor_standings_race_id ON constructor_standings(race_id);
CREATE INDEX idx_constructor_standings_constructor_id ON constructor_standings(constructor_id);
CREATE INDEX idx_constructor_standings_position ON constructor_standings(position);
CREATE INDEX idx_constructor_standings_points ON constructor_standings(points DESC);

-- ??????? ??? ??????

-- Drivers
CREATE INDEX idx_drivers_surname ON drivers(surname);
CREATE INDEX idx_drivers_nationality ON drivers(nationality);
CREATE INDEX idx_drivers_ref ON drivers(driver_ref);

-- Constructors
CREATE INDEX idx_constructors_name ON constructors(name);
CREATE INDEX idx_constructors_nationality ON constructors(nationality);

-- Circuits
CREATE INDEX idx_circuits_country ON circuits(country);
CREATE INDEX idx_circuits_name ON circuits(name);

-- ??????? ??? ??????

CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_operation ON audit_log(operation);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);

-- ??????? ??? USERS

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;

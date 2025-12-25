-- Триггеры длѝ аудита и автоматичеѝкого обновлениѝ
-- F1 Analytics System

-- ??????? ??? ???????? ??????
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    record_pk INTEGER;
    pk_column_name TEXT;
BEGIN
    -- ?????????? ??? ??????? ?????????? ????? ?? ???????
    pk_column_name := CASE TG_TABLE_NAME
        WHEN 'drivers' THEN 'driver_id'
        WHEN 'constructors' THEN 'constructor_id'
        WHEN 'circuits' THEN 'circuit_id'
        WHEN 'races' THEN 'race_id'
        WHEN 'results' THEN 'result_id'
        WHEN 'qualifying' THEN 'qualify_id'
        WHEN 'lap_times' THEN 'race_id'  -- ??????????? ????, ?????????? race_id
        WHEN 'pit_stops' THEN 'race_id'  -- ??????????? ????
        WHEN 'driver_standings' THEN 'driver_standings_id'
        WHEN 'constructor_standings' THEN 'constructor_standings_id'
        WHEN 'users' THEN 'user_id'
        ELSE NULL
    END;

    IF TG_OP = 'DELETE' THEN
        -- ????????? ID ?? OLD
        EXECUTE format('SELECT ($1).%I', pk_column_name) 
        USING OLD INTO record_pk;
        
        INSERT INTO audit_log (table_name, operation, record_id, old_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, record_pk, row_to_json(OLD)::JSONB, current_user);
        
        RETURN OLD;
        
    ELSIF TG_OP = 'UPDATE' THEN
        -- ????????? ID ?? NEW
        EXECUTE format('SELECT ($1).%I', pk_column_name) 
        USING NEW INTO record_pk;
        
        INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, record_pk, 
                row_to_json(OLD)::JSONB, 
                row_to_json(NEW)::JSONB, 
                current_user);
        
        RETURN NEW;
        
    ELSIF TG_OP = 'INSERT' THEN
        -- ????????? ID ?? NEW
        EXECUTE format('SELECT ($1).%I', pk_column_name) 
        USING NEW INTO record_pk;
        
        INSERT INTO audit_log (table_name, operation, record_id, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, record_pk, 
                row_to_json(NEW)::JSONB, 
                current_user);
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION audit_trigger_function() IS 
'??????? ???????? ??? ??????????? ???? ????????? ?????? ? ??????? audit_log';



-- Триггеры аудита длѝ оѝновных таблиц
CREATE TRIGGER audit_drivers_trigger
AFTER INSERT OR UPDATE OR DELETE ON drivers
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_constructors_trigger
AFTER INSERT OR UPDATE OR DELETE ON constructors
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_races_trigger
AFTER INSERT OR UPDATE OR DELETE ON races
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_results_trigger
AFTER INSERT OR UPDATE OR DELETE ON results
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Функциѝ длѝ автоматичеѝкого обновлениѝ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры длѝ автоматичеѝкого обновлениѝ updated_at
CREATE TRIGGER update_drivers_updated_at
BEFORE UPDATE ON drivers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_constructors_updated_at
BEFORE UPDATE ON constructors
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_races_updated_at
BEFORE UPDATE ON races
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_results_updated_at
BEFORE UPDATE ON results
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION audit_trigger_function IS 'Функциѝ длѝ запиѝи вѝех изменений в audit_log';
COMMENT ON FUNCTION update_updated_at_column IS 'Нвтоматичеѝки обновлѝет поле updated_at';

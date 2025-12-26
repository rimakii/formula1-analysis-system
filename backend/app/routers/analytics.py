"""
API ????????? ??? ????????? ? ???????
??????? SQL ??????? ? JOIN, ?????????? ? ????????????
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.auth.dependencies import get_current_active_user


router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ====================
# ?????? ??????? POSTGRESQL
# ====================

@router.get("/driver-career/{driver_id}")
def get_driver_career_stats(driver_id: int, db: Session = Depends(get_db)):
    """
    ????????? ?????????? ??????? ?????? ????? PostgreSQL ???????.
    ????????: ?????, ????, ??????, ???????, ????-???????, ??????? ?????.
    """
    query = text("SELECT * FROM get_driver_career_stats(:driver_id)")
    result = db.execute(query, {"driver_id": driver_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No career data found for driver ID {driver_id}")
    
    return dict(result._mapping)


@router.get("/season-standings/drivers/{year}")
def get_season_driver_standings(year: int, db: Session = Depends(get_db)):
    """
    ????????? ??????? ??????? ?? ????? ????? PostgreSQL ???????.
    ???????? ????????: SUM(points), COUNT(wins), COUNT(podiums).
    """
    query = text("SELECT * FROM get_season_driver_standings(:year)")
    results = db.execute(query, {"year": year}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No standings data found for year {year}")
    
    return [dict(row._mapping) for row in results]


@router.get("/season-standings/constructors/{year}")
def get_season_constructor_standings(year: int, db: Session = Depends(get_db)):
    """
    ????????? ??????? ?????? ?? ????? ????? PostgreSQL ???????.
    """
    query = text("SELECT * FROM get_season_constructor_standings(:year)")
    results = db.execute(query, {"year": year}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No constructor standings for year {year}")
    
    return [dict(row._mapping) for row in results]


@router.get("/circuit-history/{circuit_id}")
def get_circuit_history(circuit_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    ??????? ??????????? ?? ?????? ????? PostgreSQL ???????.
    """
    query = text("SELECT * FROM get_circuit_history(:circuit_id, :limit)")
    results = db.execute(query, {"circuit_id": circuit_id, "limit": limit}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No history found for circuit ID {circuit_id}")
    
    return [dict(row._mapping) for row in results]


# ====================
# ?????? VIEW
# ====================

@router.get("/driver-statistics")
def get_all_driver_statistics(limit: int = 50, db: Session = Depends(get_db)):
    """
    ?????????? ???? ??????? ?? VIEW v_driver_statistics.
    ???????? ????????: total_points, wins, podiums, fastest_laps.
    """
    query = text("SELECT * FROM v_driver_statistics ORDER BY total_points DESC LIMIT :limit")
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [dict(row._mapping) for row in results]


@router.get("/constructor-statistics")
def get_all_constructor_statistics(limit: int = 50, db: Session = Depends(get_db)):
    """
    ?????????? ???? ?????? ?? VIEW v_constructor_statistics.
    """
    query = text("SELECT * FROM v_constructor_statistics ORDER BY total_points DESC LIMIT :limit")
    results = db.execute(query, {"limit": limit}).fetchall()
    
    return [dict(row._mapping) for row in results]


# ====================
# ??????? SQL ??????? ? JOIN ? ????????????
# ====================

@router.get("/race-results-detailed/{race_id}")
def get_race_results_detailed(race_id: int, db: Session = Depends(get_db)):
    """
    ??????? SQL: ????????? ?????????? ????? ? JOIN (5 ??????) ? ???????????.
    
    JOIN: results + drivers + constructors + status + races
    ?????????: ??????? ????? ????? ?? lap_times
    """
    query = text("""
        SELECT 
            r.result_id,
            r.position,
            r.position_text,
            d.forename || ' ' || d.surname AS driver_name,
            d.nationality AS driver_nationality,
            c.name AS constructor_name,
            r.grid,
            r.points,
            r.laps,
            r.time_text,
            r.fastest_lap_time,
            r.fastest_lap_speed,
            s.status AS finish_status,
            ra.name AS race_name,
            ra.date AS race_date,
            -- ?????????: ??????? ????? ????? ?????? ? ???? ?????
            (SELECT AVG(milliseconds) 
             FROM lap_times lt 
             WHERE lt.race_id = r.race_id 
               AND lt.driver_id = r.driver_id
            )::BIGINT AS avg_lap_time_ms,
            -- ?????????: ?????????? ???-??????
            (SELECT COUNT(*) 
             FROM pit_stops ps 
             WHERE ps.race_id = r.race_id 
               AND ps.driver_id = r.driver_id
            ) AS pit_stops_count
        FROM results r
        JOIN drivers d ON r.driver_id = d.driver_id
        JOIN constructors c ON r.constructor_id = c.constructor_id
        JOIN status s ON r.status_id = s.status_id
        JOIN races ra ON r.race_id = ra.race_id
        WHERE r.race_id = :race_id
        ORDER BY r.position_order
    """)
    
    results = db.execute(query, {"race_id": race_id}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for race ID {race_id}")
    
    return [dict(row._mapping) for row in results]


@router.get("/top-drivers-by-year/{year}")
def get_top_drivers_by_year(year: int, min_races: int = 5, db: Session = Depends(get_db)):
    """
    ??????? SQL: ?????? ? ?????? ???? ???????? ?? ?????.
    
    CTE (WITH): ????????? ??????
    JOIN: drivers + results + races
    ?????????: ?????????? ?? ???????? ????????
    ????????: SUM, COUNT, AVG, ROUND
    """
    query = text("""
        WITH season_stats AS (
            SELECT 
                d.driver_id,
                d.forename || ' ' || d.surname AS driver_name,
                d.nationality,
                SUM(r.points) AS total_points,
                COUNT(DISTINCT r.race_id) AS races_count,
                COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins,
                COUNT(CASE WHEN r.position <= 3 THEN 1 END) AS podiums,
                COUNT(CASE WHEN r.position <= 10 THEN 1 END) AS top_10_finishes,
                ROUND(AVG(r.position), 2) AS avg_position
            FROM results r
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE ra.year = :year
              AND r.position IS NOT NULL
            GROUP BY d.driver_id, d.forename, d.surname, d.nationality
            HAVING COUNT(DISTINCT r.race_id) >= :min_races
        )
        SELECT 
            driver_id,
            driver_name,
            nationality,
            total_points,
            races_count,
            wins,
            podiums,
            top_10_finishes,
            avg_position,
            ROUND(total_points / races_count, 2) AS avg_points_per_race,
            -- ?????????: ????????? ?? ??????? ?? ??????
            ROUND((total_points - (SELECT AVG(total_points) FROM season_stats)) / 
                  (SELECT STDDEV(total_points) FROM season_stats), 2) AS points_z_score
        FROM season_stats
        WHERE total_points > (SELECT AVG(total_points) FROM season_stats)
        ORDER BY total_points DESC
    """)
    
    results = db.execute(query, {"year": year, "min_races": min_races}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for year {year}")
    
    return [dict(row._mapping) for row in results]


@router.get("/constructor-performance/{constructor_id}")
def get_constructor_performance(constructor_id: int, db: Session = Depends(get_db)):
    """
    ??????? SQL: ?????????????????? ??????? ?? ?????.
    
    JOIN: results + races + constructors + drivers
    ????????: SUM, COUNT, AVG, MIN, MAX, ROUND
    GROUP BY: ?? ?????
    """
    query = text("""
        SELECT 
            ra.year,
            c.name AS constructor_name,
            COUNT(DISTINCT r.race_id) AS races_participated,
            COUNT(DISTINCT r.driver_id) AS drivers_count,
            SUM(r.points) AS total_points,
            COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins,
            COUNT(CASE WHEN r.position <= 3 THEN 1 END) AS podiums,
            COUNT(CASE WHEN r.position <= 10 THEN 1 END) AS points_finishes,
            ROUND(AVG(r.position), 2) AS avg_finish_position,
            MIN(CASE WHEN r.position IS NOT NULL THEN r.position END) AS best_finish,
            MAX(CASE WHEN r.position IS NOT NULL THEN r.position END) AS worst_finish,
            -- ??????? ??????????? ?????
            ROUND(100.0 * COUNT(CASE WHEN r.position IS NOT NULL THEN 1 END) / 
                  COUNT(*), 2) AS finish_rate_percent,
            -- ??????? ???? ?? ?????
            ROUND(SUM(r.points) / COUNT(DISTINCT r.race_id), 2) AS avg_points_per_race,
            -- ?????? ????? ?????? (?????????)
            (SELECT d.forename || ' ' || d.surname
             FROM results r2
             JOIN drivers d ON r2.driver_id = d.driver_id
             WHERE r2.constructor_id = c.constructor_id
               AND r2.race_id IN (SELECT race_id FROM races WHERE year = ra.year)
             GROUP BY d.driver_id, d.forename, d.surname
             ORDER BY SUM(r2.points) DESC
             LIMIT 1
            ) AS best_driver_of_season
        FROM results r
        JOIN races ra ON r.race_id = ra.race_id
        JOIN constructors c ON r.constructor_id = c.constructor_id
        WHERE c.constructor_id = :constructor_id
        GROUP BY ra.year, c.name, c.constructor_id
        ORDER BY ra.year DESC
    """)
    
    results = db.execute(query, {"constructor_id": constructor_id}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for constructor ID {constructor_id}")
    
    return [dict(row._mapping) for row in results]


@router.get("/driver-vs-driver")
def compare_drivers(
    driver1_id: int,
    driver2_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    ??????? SQL: ????????? ???? ??????? (head-to-head).
    
    UNION: ??????????? ?????????? ???? ???????
    JOIN: drivers + results + races
    ????????: SUM, COUNT, AVG
    ???????? ??????????: ?? ???? (???????????)
    """
    year_filter = "AND ra.year = :year" if year else ""
    
    query = text(f"""
        WITH driver1_stats AS (
            SELECT 
                d.driver_id,
                d.forename || ' ' || d.surname AS driver_name,
                COUNT(DISTINCT r.race_id) AS races,
                SUM(r.points) AS total_points,
                COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins,
                COUNT(CASE WHEN r.position <= 3 THEN 1 END) AS podiums,
                ROUND(AVG(r.position), 2) AS avg_position,
                COUNT(CASE WHEN r.rank = 1 THEN 1 END) AS fastest_laps
            FROM results r
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE d.driver_id = :driver1_id
              {year_filter}
              AND r.position IS NOT NULL
            GROUP BY d.driver_id, d.forename, d.surname
        ),
        driver2_stats AS (
            SELECT 
                d.driver_id,
                d.forename || ' ' || d.surname AS driver_name,
                COUNT(DISTINCT r.race_id) AS races,
                SUM(r.points) AS total_points,
                COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins,
                COUNT(CASE WHEN r.position <= 3 THEN 1 END) AS podiums,
                ROUND(AVG(r.position), 2) AS avg_position,
                COUNT(CASE WHEN r.rank = 1 THEN 1 END) AS fastest_laps
            FROM results r
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE d.driver_id = :driver2_id
              {year_filter}
              AND r.position IS NOT NULL
            GROUP BY d.driver_id, d.forename, d.surname
        )
        SELECT * FROM driver1_stats
        UNION ALL
        SELECT * FROM driver2_stats
    """)
    
    params = {"driver1_id": driver1_id, "driver2_id": driver2_id}
    if year:
        params["year"] = year
    
    results = db.execute(query, params).fetchall()
    
    if len(results) != 2:
        raise HTTPException(status_code=404, detail="One or both drivers not found or have no data")
    
    return {
        "comparison": [dict(row._mapping) for row in results],
        "year_filter": year if year else "All time"
    }


@router.get("/fastest-pit-stops/{year}")
def get_fastest_pit_stops(year: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    ??????? SQL: ????? ??????? ???-????? ??????.
    
    JOIN: pit_stops + drivers + constructors + races
    ??????????: ?? ???? ? ??????? ??????
    ??????????: ?? ???????
    """
    query = text("""
        SELECT 
            ps.milliseconds,
            ps.duration,
            ps.stop AS stop_number,
            ps.lap,
            d.forename || ' ' || d.surname AS driver_name,
            c.name AS constructor_name,
            ra.name AS race_name,
            ra.date AS race_date,
            -- ???? ???-????? ? ?????
            RANK() OVER (PARTITION BY ps.race_id ORDER BY ps.milliseconds) AS pit_stop_rank_in_race
        FROM pit_stops ps
        JOIN drivers d ON ps.driver_id = d.driver_id
        JOIN results r ON ps.race_id = r.race_id AND ps.driver_id = r.driver_id
        JOIN constructors c ON r.constructor_id = c.constructor_id
        JOIN races ra ON ps.race_id = ra.race_id
        WHERE ra.year = :year
          AND ps.milliseconds IS NOT NULL
        ORDER BY ps.milliseconds ASC
        LIMIT :limit
    """)
    
    results = db.execute(query, {"year": year, "limit": limit}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No pit stop data for year {year}")
    
    return [dict(row._mapping) for row in results]

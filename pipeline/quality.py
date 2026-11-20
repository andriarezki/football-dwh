"""Data-quality checks. Each check returns (name, failed_rows). Results are stored in dq_results."""
import duckdb

CHECKS = {
  "stg_not_empty": "SELECT CASE WHEN count(*)=0 THEN 1 ELSE 0 END FROM stg_match",
  "match_key_unique": "SELECT count(*) - count(DISTINCT (match_date, home_team, away_team)) FROM stg_match",
  "no_null_goals": "SELECT count(*) FROM stg_match WHERE home_goals IS NULL OR away_goals IS NULL",
  "goals_non_negative": "SELECT count(*) FROM stg_match WHERE home_goals < 0 OR away_goals < 0",
  "result_matches_goals": """SELECT count(*) FROM stg_match WHERE result <>
      CASE WHEN home_goals>away_goals THEN 'H' WHEN home_goals<away_goals THEN 'A' ELSE 'D' END""",
  "team_plays_itself": "SELECT count(*) FROM stg_match WHERE home_team = away_team",
  "odds_above_one": "SELECT count(*) FROM stg_match WHERE odds_home <= 1 OR odds_draw <= 1 OR odds_away <= 1",
  "fact_rows_equal_staging": "SELECT abs((SELECT count(*) FROM fact_match) - (SELECT count(*) FROM stg_match))",
  "fact_fk_teams": """SELECT count(*) FROM fact_match f LEFT JOIN dim_team t ON t.team_key=f.home_team_key
      LEFT JOIN dim_team a ON a.team_key=f.away_team_key WHERE t.team_key IS NULL OR a.team_key IS NULL""",
  "full_season_380": """SELECT count(*) FROM (SELECT season_code FROM stg_match GROUP BY 1 HAVING count(*) <> 380
      AND season_code NOT IN (SELECT max(season_code) FROM stg_match))""",
}

def run(con: duckdb.DuckDBPyConnection) -> list[tuple[str, int]]:
    con.execute("CREATE OR REPLACE TABLE dq_results(check_name VARCHAR, failed_rows BIGINT, run_at TIMESTAMP)")
    out = []
    for name, sql in CHECKS.items():
        failed = con.execute(sql).fetchone()[0]
        con.execute("INSERT INTO dq_results VALUES (?, ?, now())", [name, failed])
        out.append((name, failed))
    return out

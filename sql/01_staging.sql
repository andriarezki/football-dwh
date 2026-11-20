-- Staging: typed, cleaned view of every raw season file (one row per match)
CREATE OR REPLACE TABLE stg_match AS
SELECT
  regexp_extract(filename, 'E0_(\d{4})\.csv', 1)                   AS season_code,
  coalesce(try_strptime(Date,'%d/%m/%Y'), try_strptime(Date,'%d/%m/%y'))::DATE                                AS match_date,
  HomeTeam                                                         AS home_team,
  AwayTeam                                                         AS away_team,
  TRY_CAST(FTHG AS INT) AS home_goals, TRY_CAST(FTAG AS INT) AS away_goals, FTR AS result,
  HS::INT AS home_shots, "AS"::INT AS away_shots,
  HST::INT AS home_sot, AST::INT AS away_sot,
  HC::INT AS home_corners, AC::INT AS away_corners,
  HY::INT AS home_yellow, AY::INT AS away_yellow,
  HR::INT AS home_red, AR::INT AS away_red,
  AvgH::DOUBLE AS odds_home, AvgD::DOUBLE AS odds_draw, AvgA::DOUBLE AS odds_away
FROM read_csv('lake/raw/season=*/E0_*.csv', filename=true, header=true, union_by_name=true, all_varchar=true)
WHERE HomeTeam IS NOT NULL AND Date IS NOT NULL;

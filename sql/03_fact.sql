-- Fact grain: one row per match. Surrogate keys from dimensions.
CREATE OR REPLACE TABLE fact_match AS
SELECT
  row_number() OVER (ORDER BY m.match_date, m.home_team) AS match_key,
  s.season_key, m.match_date AS date_key, h.team_key AS home_team_key, a.team_key AS away_team_key,
  m.home_goals, m.away_goals, m.result,
  m.home_goals + m.away_goals AS total_goals,
  m.home_shots, m.away_shots, m.home_sot, m.away_sot,
  m.home_corners, m.away_corners, m.home_yellow, m.away_yellow, m.home_red, m.away_red,
  m.odds_home, m.odds_draw, m.odds_away
FROM stg_match m
JOIN dim_season s ON s.season_code = m.season_code
JOIN dim_team h ON h.team_name = m.home_team
JOIN dim_team a ON a.team_name = m.away_team;

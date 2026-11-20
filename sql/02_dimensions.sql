CREATE OR REPLACE TABLE dim_team AS
SELECT row_number() OVER (ORDER BY team) AS team_key, team AS team_name
FROM (SELECT home_team AS team FROM stg_match UNION SELECT away_team FROM stg_match);

CREATE OR REPLACE TABLE dim_season AS
SELECT row_number() OVER (ORDER BY season_code) AS season_key, season_code,
       '20' || substr(season_code,1,2) || '/' || substr(season_code,3,2) AS season_label
FROM (SELECT DISTINCT season_code FROM stg_match);

CREATE OR REPLACE TABLE dim_date AS
SELECT d AS date_key, year(d) AS year, month(d) AS month, dayname(d) AS weekday,
       CASE WHEN dayofweek(d) IN (0,6) THEN true ELSE false END AS is_weekend
FROM (SELECT DISTINCT match_date AS d FROM stg_match);

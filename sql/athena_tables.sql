-- Run in Amazon Athena after s3_publish. Replace <bucket>. Curated Parquet becomes queryable SQL, pay per scan.
CREATE DATABASE IF NOT EXISTS football_dwh;
CREATE EXTERNAL TABLE IF NOT EXISTS football_dwh.mart_season_summary (
  season_label string, matches bigint, avg_goals double,
  home_win_pct double, draw_pct double, away_win_pct double)
STORED AS PARQUET LOCATION 's3://<bucket>/football-dwh/curated/mart_season_summary/';

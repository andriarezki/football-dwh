-- Mart 1: team-season table (3 pts win, 1 draw) with ranking via window function
CREATE OR REPLACE TABLE mart_team_season AS
WITH t AS (
  SELECT season_key, home_team_key AS team_key, home_goals gf, away_goals ga,
         CASE result WHEN 'H' THEN 3 WHEN 'D' THEN 1 ELSE 0 END pts FROM fact_match
  UNION ALL
  SELECT season_key, away_team_key, away_goals, home_goals,
         CASE result WHEN 'A' THEN 3 WHEN 'D' THEN 1 ELSE 0 END FROM fact_match
), agg AS (
  SELECT season_key, team_key, count(*) played, sum(pts) points,
         sum(gf) goals_for, sum(ga) goals_against, sum(gf)-sum(ga) goal_diff
  FROM t GROUP BY 1,2
)
SELECT s.season_label, tm.team_name, a.played, a.points, a.goals_for, a.goals_against, a.goal_diff,
       rank() OVER (PARTITION BY a.season_key ORDER BY a.points DESC, a.goal_diff DESC, a.goals_for DESC) AS position
FROM agg a JOIN dim_season s USING (season_key) JOIN dim_team tm USING (team_key);

-- Mart 2: home advantage and goals per season
CREATE OR REPLACE TABLE mart_season_summary AS
SELECT s.season_label, count(*) matches, round(avg(total_goals),2) avg_goals,
       round(100.0*avg((result='H')::INT),1) home_win_pct,
       round(100.0*avg((result='D')::INT),1) draw_pct,
       round(100.0*avg((result='A')::INT),1) away_win_pct
FROM fact_match f JOIN dim_season s USING (season_key) GROUP BY 1 ORDER BY 1;

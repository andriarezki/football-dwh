"""Build a self-contained static dashboard (web/index.html) from the warehouse. No external requests."""
import json, sys
from pathlib import Path
import duckdb

db = sys.argv[1] if len(sys.argv) > 1 else "warehouse.duckdb"
c = duckdb.connect(db, read_only=True)
q = lambda sql: c.execute(sql).fetchall()
data = {
    "summary": q("SELECT season_label, matches, avg_goals, home_win_pct, draw_pct, away_win_pct FROM mart_season_summary ORDER BY 1"),
    "table": q("SELECT season_label, position, team_name, played, points, goals_for, goals_against, goal_diff FROM mart_team_season ORDER BY 1, 2"),
    "dq": q("SELECT check_name, failed_rows, strftime(run_at, '%Y-%m-%d %H:%M') FROM dq_results ORDER BY 1"),
    "counts": q("SELECT (SELECT count(*) FROM fact_match), (SELECT count(*) FROM dim_team), (SELECT count(*) FROM dim_season)")[0],
}
tpl = Path("web/template.html").read_text()
Path("web/index.html").write_text(tpl.replace("/*DATA*/null", json.dumps(data)))
print("built web/index.html", len(data["table"]), "table rows")

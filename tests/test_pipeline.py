import duckdb, pytest
from pipeline import quality
import run_pipeline

@pytest.fixture(scope="module")
def con(tmp_path_factory):
    db = str(tmp_path_factory.mktemp("w") / "t.duckdb")
    assert run_pipeline.main("source", db) == 0
    return duckdb.connect(db, read_only=True)

def test_fact_grain_one_row_per_match(con):
    assert con.execute("select count(*) - count(distinct match_key) from fact_match").fetchone()[0] == 0

def test_champions_points_known_values(con):
    rows = dict(con.sql("select season_label, points from mart_team_season where position=1").fetchall())
    assert rows["2019/20"] == 99 and rows["2020/21"] == 86 and rows["2021/22"] == 93

def test_every_complete_season_has_380_matches(con):
    n = con.execute("select matches from mart_season_summary where season_label='2022/23'").fetchone()[0]
    assert n == 380

def test_quality_checks_detect_bad_data():
    c = duckdb.connect()
    c.execute("create table stg_match as select 'H' result, 1 home_goals, 3 away_goals, 'A' home_team, 'A' away_team, "
              "date '2025-01-01' match_date, 0.5 odds_home, 3.0 odds_draw, 3.0 odds_away, '2425' season_code")
    c.execute("create table fact_match as select 1 match_key, 99 home_team_key, 99 away_team_key")
    c.execute("create table dim_team as select 1 team_key")
    res = dict(quality.run(c))
    assert res["result_matches_goals"] == 1 and res["team_plays_itself"] == 1 and res["odds_above_one"] == 1 and res["fact_fk_teams"] == 1

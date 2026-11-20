# Football DWH: a small ETL/ELT data warehouse with a data-quality gate

A portfolio project showing the core data-engineering loop end to end on real data
(English Premier League results, 2019/20 to 2026/27, from football-data.co.uk, 2,760 matches).

```
source CSVs --extract--> lake/raw/season=XXXX/ (partitioned, hash manifest, idempotent)
            --SQL-->     stg_match (typed, cleaned)
            --SQL-->     dim_team, dim_season, dim_date  +  fact_match (grain: one row per match)
            --SQL-->     mart_team_season (rank via window function), mart_season_summary
            --quality--> 10 automated checks (gate: pipeline fails, exports skipped)
            --export-->  Parquet files in export/
```

## Run
```bash
pip install -r requirements.txt
python run_pipeline.py        # full pipeline, ~1 second
pytest -q                     # tests incl. known champions' points (Liverpool 99 in 2019/20)
```

## What it demonstrates
- ETL/ELT with SQL-first transformations (DuckDB), star schema (dimensions + fact), window functions
- Idempotent extract using SHA-256 manifest; partitioned lake layout
- Data quality as code: uniqueness, null, range, result-vs-goals consistency, foreign keys, row-count reconciliation, season completeness
- Tests that verify both the business numbers and that the quality checks really catch bad data
- CI with GitHub Actions; Parquet export

## Honest scope
Runs locally on DuckDB. It is not deployed on AWS or Microsoft Fabric. The lake layout uses S3-style keys so the
extract and load steps can be pointed at S3 later (planned: S3 + Athena/Glue version). No Airflow yet (planned).

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
- Orchestration with Airflow, CI with GitHub Actions, Parquet export

## Orchestration (Airflow)
`airflow/` has a single-container Airflow (Docker, UI on localhost only) and the DAG `football_dwh_daily`
(03:00 daily, 2 retries): `extract >> transform_and_quality_gate`. Verified on a small VPS: scheduled and manual runs succeeded.
```bash
cd airflow && docker compose up -d   # DAG appears after ~1 minute; unpause it in the UI or CLI
```

## S3 / Athena
`python -m pipeline.s3_publish <bucket>` uploads the raw zone and curated Parquet (one folder per table);
`sql/athena_tables.sql` exposes them to Amazon Athena.

### Zero-cost S3 on a VPS
`s3store/` runs SeaweedFS (S3-compatible, localhost only) in Docker, so the S3 code path is exercised for real without a cloud bill:
```bash
cd s3store && cp s3.json.template s3.json   # edit keys; put the same keys in .env (AWS_* variables, AWS_ENDPOINT_URL=http://127.0.0.1:8333)
docker compose up -d && cd .. && set -a && . s3store/.env && set +a
python -m pipeline.s3_publish football-lake      # create the bucket first (boto3 create_bucket)
python scripts/query_s3.py                       # Athena-style SQL over the Parquet in S3
```

## Honest scope
- Core pipeline and Airflow DAG are tested and run on DuckDB locally.
- The S3 publisher is unit-tested with a mocked S3 (moto) and was run end to end against a real S3-compatible server (SeaweedFS).
  It has NOT been run on AWS itself, nothing here runs on Microsoft Fabric, and the Athena DDL is untested on real Athena.
- Data: football-data.co.uk (free for personal and research use; check their terms before commercial use).

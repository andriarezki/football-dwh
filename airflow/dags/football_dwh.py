"""Daily orchestration of the football DWH: extract -> transform -> quality gate -> export.
Each stage is a separate task so failures are visible per step; the quality task fails the DAG run."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

REPO = "/opt/football-dwh"  # mounted read-only
WORK = "/tmp/fdwh"  # writable scratch copy (container user is not root)
default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="football_dwh_daily",
    start_date=datetime(2026, 11, 1),
    schedule="0 3 * * *",
    catchup=False,
    default_args=default_args,
    tags=["dwh", "duckdb"],
) as dag:
    extract = BashOperator(
        task_id="extract",
        bash_command=(f"rm -rf {WORK} && mkdir -p {WORK} && cp -r {REPO}/pipeline {REPO}/sql {REPO}/source {REPO}/run_pipeline.py {WORK}/ "
                      f"&& cd {WORK} && python -c \"from pipeline import extract; print(extract.land('source'))\""),
    )
    transform_and_quality = BashOperator(
        task_id="transform_and_quality_gate",
        bash_command=f"cd {WORK} && python run_pipeline.py source {WORK}/warehouse.duckdb",
    )
    extract >> transform_and_quality

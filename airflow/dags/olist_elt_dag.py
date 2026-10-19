from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"  # chemin du projet vu depuis Airflow

with DAG(
    dag_id="olist_elt",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["olist", "elt"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_raw",
        bash_command=f"cd {PROJECT} && python ingestion/load_raw_duckdb.py",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {PROJECT}/dbt_project && dbt build --profiles-dir .",
    )

    ingest >> dbt_build
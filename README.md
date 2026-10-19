\# E-commerce ELT Platform (Olist)

Pipeline ELT sur le jeu de données Olist : ingestion, transformation, dashboard.

\## Architecture

CSV Olist -> ingestion (Python) -> DuckDB (raw) -> dbt (staging, intermediate, marts) -> Streamlit

Orchestration : Airflow. CI : GitHub Actions.

\## Lancer le projet

1\. python -m venv .venv puis .venv\Scripts\activate

2\. pip install -r ingestion/requirements.txt dbt-duckdb streamlit

3\. Placer les CSV Olist dans data/

4\. python ingestion/load_raw_duckdb.py

5\. cd dbt_project, dbt deps, dbt build

6\. streamlit run dashboard/app.py

\## Structure

\- ingestion/ : chargement des CSV bruts

\- dbt_project/ : modèles et tests dbt

\- dashboard/ : application Streamlit

\- airflow/dags/ : DAG d'orchestration

\- docs/ : captures et documentation
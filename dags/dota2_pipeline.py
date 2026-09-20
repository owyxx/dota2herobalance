#DAG для запуска ETL-пайплайна Dota 2.

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'sergey',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dota2_balance_pipeline',
    default_args=default_args,
    description='ETL pipeline for Dota 2 balance analysis',
    schedule_interval='0 6 * * *',  # Каждый день в 6:00
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=['dota2', 'etl'],
) as dag:
    run_pipeline = BashOperator(
        task_id='run_etl_pipeline',
        bash_command='cd /opt/airflow && python /opt/airflow/src/main_airflow.py',
    )
    
    run_pipeline
"""
Weather ETL DAG
This DAG extracts weather data from Open-Meteo API,
transforms it, and loads it to PostgreSQL database.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
from pathlib import Path

# Add scripts directory to Python path
scripts_dir = Path('/opt/airflow/scripts')
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Import ETL functions
from extract import extract_weather_data
from transform import transform_hourly_data, transform_daily_data
from load import load_hourly_data, load_daily_data

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='weather_etl_dag',
    default_args=default_args,
    description='Extract, Transform, and Load weather data from Open-Meteo API',
    schedule_interval='@daily',  # Run once a day
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Don't run for past dates
    tags=['weather', 'etl', 'open-meteo'],
) as dag:
    
    # Task 1: Extract weather data
    extract_task = PythonOperator(
        task_id='extract_weather_data',
        python_callable=extract_weather_data,
        op_kwargs={
            'start_date': '{{ ds }}',  # Execution date
            'end_date': '{{ ds }}',
        },
    )
    
    # Task 2: Transform hourly data
    transform_hourly_task = PythonOperator(
        task_id='transform_hourly_data',
        python_callable=transform_hourly_data,
        op_kwargs={
            'responses': '{{ ti.xcom_pull(task_ids="extract_weather_data") }}',
        },
    )
    
    # Task 3: Transform daily data
    transform_daily_task = PythonOperator(
        task_id='transform_daily_data',
        python_callable=transform_daily_data,
        op_kwargs={
            'responses': '{{ ti.xcom_pull(task_ids="extract_weather_data") }}',
        },
    )
    
    # Task 4: Load hourly data to PostgreSQL
    load_hourly_task = PythonOperator(
        task_id='load_hourly_data',
        python_callable=load_hourly_data,
        op_kwargs={
            'hourly_df': '{{ ti.xcom_pull(task_ids="transform_hourly_data") }}',
        },
    )
    
    # Task 5: Load daily data to PostgreSQL
    load_daily_task = PythonOperator(
        task_id='load_daily_data',
        python_callable=load_daily_data,
        op_kwargs={
            'daily_df': '{{ ti.xcom_pull(task_ids="transform_daily_data") }}',
        },
    )
    
    # Define task dependencies
    # Extract first, then transform in parallel, then load in parallel
    extract_task >> [transform_hourly_task, transform_daily_task]
    transform_hourly_task >> load_hourly_task
    transform_daily_task >> load_daily_task
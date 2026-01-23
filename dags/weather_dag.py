from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

AIRFLOW_HOME = Path(__file__).parent.parent
sys.path.insert(0, str(AIRFLOW_HOME / "scripts"))

from extract import extract_weather_data
from load import load_daily_data, load_hourly_data
from transform import transform_daily_data, transform_hourly_data

default_args = {
    'owner': 'nhatnam',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'weather_dag',
    default_args=default_args,
    description='DAG for Weather Pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['weather', 'pipeline']
)

# WRAPPER FUNCTIONS

def extract_weather_wrapper(**context):
    print("Starting extract task...")
    responses = extract_weather_data(**context)
    print(f"Extracted data for {len(responses)} cities")
    
    return {
        "status": "success",
        "num_cities": len(responses),
        "execution_date": context.get('ds')
    }

def transform_hourly_wrapper(**context):

    print("Starting transform hourly task...")
    
    responses = extract_weather_data(**context)
    
    hourly_df = transform_hourly_data(responses, **context)
    
    print(f"Transformed {len(hourly_df)} hourly records")
    
    return {
        "status": "success",
        "records": len(hourly_df),
        "table": "weather_hourly"
    }

def transform_daily_wrapper(**context):
    
    print("Starting transform daily task...")
    
    responses = extract_weather_data(**context)
    
    daily_df = transform_daily_data(responses, **context)
    
    print(f"Transformed {len(daily_df)} daily records")
    
    return {
        "status": "success",
        "records": len(daily_df),
        "table": "weather_daily"
    }

def load_hourly_wrapper(**context):

    print("Starting load hourly task...")
    
    responses = extract_weather_data(**context)
    hourly_df = transform_hourly_data(responses, **context)
    
    num_records = load_hourly_data(hourly_df, **context)
    
    print(f"Loaded {num_records} hourly records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_hourly"
    }

def load_daily_wrapper(**context):

    print("Starting load daily task...")
    
    responses = extract_weather_data(**context)
    daily_df = transform_daily_data(responses, **context)
    
    num_records = load_daily_data(daily_df, **context)
    
    print(f"Loaded {num_records} daily records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_daily"
    }

extract_task = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_wrapper,
    provide_context=True,
    dag=dag,
)

transform_hourly_task = PythonOperator(
    task_id='transform_hourly_data',
    python_callable=transform_hourly_wrapper,
    provide_context=True,
    dag=dag,
)

transform_daily_task = PythonOperator(
    task_id='transform_daily_data',
    python_callable=transform_daily_wrapper,
    provide_context=True,
    dag=dag,
)

load_hourly_task = PythonOperator(
    task_id='load_hourly_data',
    python_callable=load_hourly_wrapper,
    provide_context=True,
    dag=dag,
)

load_daily_task = PythonOperator(
    task_id='load_daily_data',
    python_callable=load_daily_wrapper,
    provide_context=True,
    dag=dag,
)


# TASK DEPENDENCIES
extract_task >> [transform_hourly_task, transform_daily_task]
transform_hourly_task >> load_hourly_task
transform_daily_task >> load_daily_task

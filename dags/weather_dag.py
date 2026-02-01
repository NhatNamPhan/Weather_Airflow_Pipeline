from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path
import pickle
import os

AIRFLOW_HOME = Path(__file__).parent.parent
sys.path.insert(0, str(AIRFLOW_HOME / "scripts"))

from extract import extract_weather_data
from load import load_daily_data, load_hourly_data
from transform import transform_daily_data, transform_hourly_data

default_args = {
    'owner': 'nhatnam',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 12),
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
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
    """Extract weather data once and save to file"""
    print("Starting extract task...")
    responses = extract_weather_data(**context)
    print(f"Extracted data for {len(responses)} cities")
    
    # Save responses to a temporary file for reuse
    execution_date = context.get('ds_nodash')
    data_dir = AIRFLOW_HOME / "data" / "temp"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    responses_file = data_dir / f"weather_responses_{execution_date}.pkl"
    with open(responses_file, 'wb') as f:
        pickle.dump(responses, f)
    
    print(f"Saved responses to {responses_file}")
    
    return {
        "status": "success",
        "num_cities": len(responses),
        "execution_date": context.get('ds'),
        "responses_file": str(responses_file)
    }

def transform_hourly_wrapper(**context):
    """Transform hourly data using cached responses"""
    print("Starting transform hourly task...")
    
    # Load responses from file instead of calling API again
    execution_date = context.get('ds_nodash')
    data_dir = AIRFLOW_HOME / "data" / "temp"
    responses_file = data_dir / f"weather_responses_{execution_date}.pkl"
    
    print(f"Loading responses from {responses_file}")
    with open(responses_file, 'rb') as f:
        responses = pickle.load(f)
    
    hourly_df = transform_hourly_data(responses, **context)
    
    print(f"Transformed {len(hourly_df)} hourly records")
    
    return {
        "status": "success",
        "records": len(hourly_df),
        "table": "weather_hourly"
    }

def transform_daily_wrapper(**context):
    """Transform daily data using cached responses"""
    print("Starting transform daily task...")
    
    # Load responses from file instead of calling API again
    execution_date = context.get('ds_nodash')
    data_dir = AIRFLOW_HOME / "data" / "temp"
    responses_file = data_dir / f"weather_responses_{execution_date}.pkl"
    
    print(f"Loading responses from {responses_file}")
    with open(responses_file, 'rb') as f:
        responses = pickle.load(f)
    
    daily_df = transform_daily_data(responses, **context)
    
    print(f"Transformed {len(daily_df)} daily records")
    
    return {
        "status": "success",
        "records": len(daily_df),
        "table": "weather_daily"
    }

def load_hourly_wrapper(**context):
    """Load hourly data using cached responses"""
    print("Starting load hourly task...")
    
    # Load responses from file instead of calling API again
    execution_date = context.get('ds_nodash')
    data_dir = AIRFLOW_HOME / "data" / "temp"
    responses_file = data_dir / f"weather_responses_{execution_date}.pkl"
    
    print(f"Loading responses from {responses_file}")
    with open(responses_file, 'rb') as f:
        responses = pickle.load(f)
    
    hourly_df = transform_hourly_data(responses, **context)
    
    num_records = load_hourly_data(hourly_df, **context)
    
    print(f"Loaded {num_records} hourly records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_hourly"
    }

def load_daily_wrapper(**context):
    """Load daily data using cached responses"""
    print("Starting load daily task...")
    
    # Load responses from file instead of calling API again
    execution_date = context.get('ds_nodash')
    data_dir = AIRFLOW_HOME / "data" / "temp"
    responses_file = data_dir / f"weather_responses_{execution_date}.pkl"
    
    print(f"Loading responses from {responses_file}")
    with open(responses_file, 'rb') as f:
        responses = pickle.load(f)
    
    daily_df = transform_daily_data(responses, **context)
    
    num_records = load_daily_data(daily_df, **context)
    
    print(f"Loaded {num_records} daily records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_daily"
    }

def cleanup_temp_files_wrapper(**context):
    """Clean up temporary pickle files older than 7 days"""
    print("Starting cleanup task...")
    
    data_dir = AIRFLOW_HOME / "data" / "temp"
    if not data_dir.exists():
        print("No temp directory found, nothing to clean")
        return {"status": "success", "files_deleted": 0}
    
    files_deleted = 0
    current_time = datetime.now()
    
    for file_path in data_dir.glob("weather_responses_*.pkl"):
        # Get file modification time
        file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_days = (current_time - file_modified).days
        
        # Delete files older than 7 days
        if age_days > 7:
            file_path.unlink()
            files_deleted += 1
            print(f"Deleted old file: {file_path.name} (age: {age_days} days)")
    
    print(f"Cleanup complete. Deleted {files_deleted} old files")
    
    return {
        "status": "success",
        "files_deleted": files_deleted
    }

# TASK DEFINITIONS

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

cleanup_task = PythonOperator(
    task_id='cleanup_temp_files',
    python_callable=cleanup_temp_files_wrapper,
    provide_context=True,
    dag=dag,
)


# TASK DEPENDENCIES
extract_task >> [transform_hourly_task, transform_daily_task]
transform_hourly_task >> load_hourly_task
transform_daily_task >> load_daily_task
[load_hourly_task, load_daily_task] >> cleanup_task


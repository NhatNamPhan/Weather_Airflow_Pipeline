from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add scripts folder to Python path
AIRFLOW_HOME = Path(__file__).parent.parent
sys.path.insert(0, str(AIRFLOW_HOME / "scripts"))

# Now import from scripts
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

# ============================================
# WRAPPER FUNCTIONS
# ============================================
# Chú ý: WeatherApiResponse không thể serialize qua XCom
# Nên mỗi task phải tự gọi extract_weather_data

def extract_weather_wrapper(**context):
    """
    Extract weather data - chỉ return metadata để check success
    """
    print("📥 Starting extract task...")
    responses = extract_weather_data(**context)
    print(f"✅ Extracted data for {len(responses)} cities")
    
    # Return metadata thay vì responses object
    return {
        "status": "success",
        "num_cities": len(responses),
        "execution_date": context.get('ds')
    }

def transform_hourly_wrapper(**context):
    """
    Transform hourly data - re-extract vì không thể lấy từ XCom
    """
    print("🔄 Starting transform hourly task...")
    
    # Re-extract data (vì responses không serialize được)
    responses = extract_weather_data(**context)
    
    # Transform
    hourly_df = transform_hourly_data(responses, **context)
    
    print(f"📊 Transformed {len(hourly_df)} hourly records")
    
    # Return metadata
    return {
        "status": "success",
        "records": len(hourly_df),
        "table": "weather_hourly"
    }

def transform_daily_wrapper(**context):
    """
    Transform daily data - re-extract vì không thể lấy từ XCom
    """
    print("🔄 Starting transform daily task...")
    
    # Re-extract data (vì responses không serialize được)
    responses = extract_weather_data(**context)
    
    # Transform
    daily_df = transform_daily_data(responses, **context)
    
    print(f"📊 Transformed {len(daily_df)} daily records")
    
    # Return metadata
    return {
        "status": "success",
        "records": len(daily_df),
        "table": "weather_daily"
    }

def load_hourly_wrapper(**context):
    """
    Load hourly data to PostgreSQL
    """
    print("💾 Starting load hourly task...")
    
    # Re-extract và transform (vì DataFrame cũng khó serialize)
    responses = extract_weather_data(**context)
    hourly_df = transform_hourly_data(responses, **context)
    
    # Load
    num_records = load_hourly_data(hourly_df, **context)
    
    print(f"✅ Loaded {num_records} hourly records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_hourly"
    }

def load_daily_wrapper(**context):
    """
    Load daily data to PostgreSQL
    """
    print("💾 Starting load daily task...")
    
    # Re-extract và transform (vì DataFrame cũng khó serialize)
    responses = extract_weather_data(**context)
    daily_df = transform_daily_data(responses, **context)
    
    # Load
    num_records = load_daily_data(daily_df, **context)
    
    print(f"✅ Loaded {num_records} daily records to PostgreSQL")
    
    return {
        "status": "success",
        "records": num_records,
        "table": "weather_daily"
    }

# Định nghĩa các tasks
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


# ============================================
# TASK DEPENDENCIES
# ============================================
# Workflow:
# 1. extract_task: Validate data có thể lấy được từ API
# 2. transform tasks: Chạy song song, mỗi task tự extract lại
# 3. load tasks: Chạy sau transform, cũng tự extract + transform lại
#
# Lưu ý: Vì WeatherApiResponse và DataFrame không serialize được qua XCom,
# nên mỗi task phải tự gọi lại extract_weather_data().
# Trade-off: Gọi API nhiều lần hơn, nhưng tránh được XCom serialization issues.

extract_task >> [transform_hourly_task, transform_daily_task]
transform_hourly_task >> load_hourly_task
transform_daily_task >> load_daily_task

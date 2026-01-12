"""
DAG mẫu để test Airflow setup
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments
default_args = {
    'owner': 'nhatnam',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 6),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Tạo DAG instance
dag = DAG(
    'weather_test_dag',
    default_args=default_args,
    description='Simple test DAG for Weather Pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['test', 'weather']
)

def print_hello():
    """Print hello message"""
    print("Hello from Airflow!")
    print("Airflow is running successfully!")
    return "Success"

def print_date():
    """Print current date"""
    from datetime import datetime
    current_time = datetime.now()
    print(f"Current date and time: {current_time}")
    return current_time.strftime('%Y-%m-%d %H:%M:%S')

def check_environment():
    """Check Python environment"""
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    return "Environment check completed"

# Task 1: Print hello
hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# Task 2: Print date
date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag,
)

# Task 3: Check environment
env_task = PythonOperator(
    task_id='check_environment',
    python_callable=check_environment,
    dag=dag,
)

# Task 4: Bash command
bash_task = BashOperator(
    task_id='print_pwd',
    bash_command='pwd && ls -la',
    dag=dag,
)

# Định nghĩa thứ tự thực hiện
# hello_task chạy trước, sau đó date_task và env_task chạy song song
# cuối cùng bash_task chạy sau khi cả hai task trên hoàn thành
hello_task >> [date_task, env_task] >> bash_task

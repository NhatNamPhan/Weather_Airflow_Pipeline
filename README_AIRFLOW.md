# Hướng dẫn cài đặt và sử dụng Airflow trên Docker

## 📋 Yêu cầu
- Docker Desktop đã được cài đặt và đang chạy
- PowerShell hoặc Command Prompt

## 🚀 Cài đặt

### Bước 1: Khởi động Airflow
```powershell
# Sử dụng file .env.airflow
docker-compose -f docker-compose-airflow.yml --env-file .env.airflow up -d
```

### Bước 2: Kiểm tra trạng thái
```powershell
docker-compose -f docker-compose-airflow.yml ps
```

### Bước 3: Truy cập Airflow Web UI
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

## 📁 Cấu trúc thư mục

```
Weather_Airflow_Pipeline/
├── dags/              # Đặt các DAG files ở đây
├── logs/              # Airflow logs
├── plugins/           # Airflow plugins (nếu có)
├── config/            # Airflow configuration files
├── scripts/           # Scripts của bạn (extract.py, transform.py, load.py)
└── docker-compose-airflow.yml
```

## 📝 Tạo DAG mẫu

Tạo file `dags/weather_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'nhatnam',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 6),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_test_dag',
    default_args=default_args,
    description='Test DAG',
    schedule_interval='@daily',
    catchup=False,
    tags=['test']
)

def hello_world():
    print("Hello from Airflow!")
    return "Success"

task = PythonOperator(
    task_id='hello_task',
    python_callable=hello_world,
    dag=dag,
)
```

## 🛠️ Các lệnh hữu ích

### Xem logs
```powershell
# Logs của webserver
docker-compose -f docker-compose-airflow.yml logs airflow-webserver

# Logs của scheduler
docker-compose -f docker-compose-airflow.yml logs airflow-scheduler
```

### Dừng Airflow
```powershell
docker-compose -f docker-compose-airflow.yml down
```

### Khởi động lại
```powershell
docker-compose -f docker-compose-airflow.yml restart
```

### Xóa hoàn toàn (bao gồm volumes)
```powershell
docker-compose -f docker-compose-airflow.yml down -v
```

### Chạy Airflow CLI commands
```powershell
# List tất cả DAGs
docker-compose -f docker-compose-airflow.yml exec airflow-webserver airflow dags list

# Test một task
docker-compose -f docker-compose-airflow.yml exec airflow-webserver airflow tasks test <dag_id> <task_id> 2026-01-06

# Trigger DAG
docker-compose -f docker-compose-airflow.yml exec airflow-webserver airflow dags trigger <dag_id>
```

## 📦 Cài đặt thêm Python packages

Nếu cần cài thêm packages (ví dụ: requests, pandas), sửa file `.env.airflow`:

```env
_PIP_ADDITIONAL_REQUIREMENTS=requests pandas sqlalchemy psycopg2-binary
```

Sau đó restart:
```powershell
docker-compose -f docker-compose-airflow.yml down
docker-compose -f docker-compose-airflow.yml up -d
```

## ⚙️ Cấu hình

- **Database**: SQLite (lưu tại `/opt/airflow/airflow.db` trong container)
- **Executor**: LocalExecutor (không cần Celery/Redis)
- **Port**: 8080
- **Load examples**: False (không load DAG examples mặc định)

## 🔧 Troubleshooting

### Container không start được
```powershell
# Kiểm tra logs
docker-compose -f docker-compose-airflow.yml logs

# Rebuild nếu cần
docker-compose -f docker-compose-airflow.yml up -d --force-recreate
```

### DAG không xuất hiện trong UI
1. Kiểm tra file DAG có lỗi syntax không
2. Đợi 30-60s để Airflow scan DAG folder
3. Kiểm tra logs của scheduler

### Permission issues
Nếu gặp lỗi permission trên Windows, chạy:
```powershell
docker-compose -f docker-compose-airflow.yml down -v
docker-compose -f docker-compose-airflow.yml up -d
```

## 📚 Tài liệu tham khảo
- [Apache Airflow Official Docs](https://airflow.apache.org/docs/)
- [Airflow Docker Setup](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

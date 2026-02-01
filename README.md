# 🌤️ Weather Airflow Pipeline

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.8.1-orange.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)

An automated end-to-end data pipeline that extracts, transforms, and loads weather data from the Open-Meteo API, orchestrated by Apache Airflow, stored in PostgreSQL, and visualized through an interactive Streamlit dashboard.

## 📊 Project Overview

This project demonstrates a production-ready ETL pipeline that:
- **Extracts** weather data from Open-Meteo API for 4 global cities
- **Transforms** raw data into structured daily and hourly datasets
- **Loads** processed data into PostgreSQL database
- **Orchestrates** workflows using Apache Airflow with parallel processing
- **Visualizes** insights through an interactive Streamlit dashboard

### 🌍 Cities Tracked
- Washington DC 🇺🇸
- London 🇬🇧
- Tokyo 🇯🇵
- Hanoi 🇻🇳

## ✨ Key Features

### 🔄 ETL Pipeline
- **Automated Daily Runs**: Scheduled via Airflow (`@daily`)
- **Parallel Processing**: Simultaneous hourly and daily data transformation
- **Efficient Caching**: Single API call per execution with pickle serialization
- **Error Handling**: Retry logic with exponential backoff (3 retries, 2-min delay)
- **Resource Management**: Auto-cleanup of temp files older than 7 days

### 📈 Dashboard
- **4 Analysis Tabs**: Temperature, Precipitation, Statistical Breakdown, Hourly Analysis
- **10+ Interactive Charts**: Plotly visualizations with hover effects
- **Smart Caching**: 1-hour TTL for optimal performance
- **Responsive Design**: Professional UI with glassmorphism effects
- **Real-time Data**: Displays latest weather trends and statistics

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Orchestration** | Apache Airflow 2.8.1 |
| **Database** | PostgreSQL 14+ |
| **Data Processing** | Python, Pandas, NumPy |
| **Visualization** | Streamlit, Plotly |
| **Containerization** | Docker, Docker Compose |
| **API Client** | openmeteo-requests |
| **Others** | SQLAlchemy, python-dotenv |

## 📁 Project Structure

```
Weather_Airflow_Pipeline/
├── dags/
│   └── weather_dag.py          # Airflow DAG definition
├── scripts/
│   ├── config.py               # Configuration settings
│   ├── extract.py              # Data extraction from API
│   ├── transform.py            # Data transformation logic
│   └── load.py                 # Data loading to PostgreSQL
├── config/
│   └── cities.json             # City coordinates configuration
├── notebooks/
│   └── Demo_ETL.ipynb          # Jupyter notebook for testing
├── dashboard.py                # Streamlit dashboard application
├── docker-compose-airflow.yml  # Airflow services configuration
├── requirements.txt            # Python dependencies
├── .env                        # Database credentials
├── .env.airflow                # Airflow configuration
└── README.md                   # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- PostgreSQL 14+ (or use Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NhatNamPhan/Weather_Airflow_Pipeline.git
   cd Weather_Airflow_Pipeline
   ```

2. **Set up environment variables**
   
   Create `.env` file for database connection:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=weather_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

   Create `.env.airflow` file:
   ```env
   AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
   AIRFLOW__CORE__EXECUTOR=LocalExecutor
   _AIRFLOW_WWW_USER_USERNAME=admin
   _AIRFLOW_WWW_USER_PASSWORD=admin
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline

#### Option 1: Using Docker (Recommended)

1. **Start Airflow services**
   ```bash
   docker-compose -f docker-compose-airflow.yml up -d
   ```

2. **Access Airflow UI**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

3. **Enable the DAG**
   - Navigate to DAGs page
   - Toggle on `weather_dag`

#### Option 2: Manual Execution

1. **Run ETL manually**
   ```bash
   python scripts/load.py
   ```

2. **Launch Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

## 📊 Dashboard Usage

1. **Start the dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Access the dashboard**
   - URL: http://localhost:8501

3. **Features**
   - Select city and year from top filters
   - Navigate through 4 analysis tabs
   - Hover over charts for detailed information
   - View raw data in expandable table

## 🏗️ Architecture

### Airflow DAG Flow

```
Extract Weather Data
        ↓
    ┌───┴───┐
    ↓       ↓
Transform   Transform
Hourly      Daily
    ↓       ↓
  Load      Load
 Hourly    Daily
    └───┬───┘
        ↓
   Cleanup Temp Files
```

### Data Pipeline Stages

1. **Extract**: Single API call fetches all city data
2. **Transform**: Parallel processing of hourly and daily data
3. **Load**: Idempotent loading to PostgreSQL tables
4. **Cleanup**: Removes temporary pickle files >7 days old

## 📈 Key Metrics

- **Data Volume**: 100,000+ records (2020-present)
- **Update Frequency**: Daily at midnight
- **API Efficiency**: 80% reduction in API calls via caching
- **Processing Time**: ~2-3 minutes per execution
- **Storage**: ~50MB database size

## 🎯 Use Cases

- **Weather Analysis**: Track long-term temperature and precipitation trends
- **Climate Comparison**: Compare weather patterns across global cities
- **Data Engineering Portfolio**: Showcase ETL, orchestration, and visualization skills
- **Learning Project**: Study Airflow DAG design and Docker deployment

## 🔧 Configuration

### Adding New Cities

Edit `config/cities.json`:
```json
{
  "cities": [
    {
      "name": "New City",
      "latitude": 00.0000,
      "longitude": 00.0000
    }
  ]
}
```

### Adjusting Schedule

Modify in `dags/weather_dag.py`:
```python
schedule_interval='@daily'  # Change to @hourly, @weekly, etc.
```

## 🧪 Testing

Run manual ETL test:
```bash
python scripts/load.py
```

Expected output:
```
Extracting weather data from 2020-01-01 to 2026-02-01
Calling API for 4 cities...
Successfully received 4 responses
Transformed 35040 hourly records
Transformed 2192 daily records
Successfully loaded to PostgreSQL
ETL pipeline completed successfully!
```

## 🐛 Troubleshooting

### Common Issues

**Airflow not starting**
- Check Docker logs: `docker-compose -f docker-compose-airflow.yml logs`
- Verify `.env.airflow` configuration

**Database connection errors**
- Ensure PostgreSQL is running
- Verify `.env` credentials
- Check firewall settings

**Dashboard not loading data**
- Confirm ETL has run successfully
- Check database contains data: `SELECT COUNT(*) FROM weather_daily;`

## 📝 Future Improvements

- [ ] Add unit tests with pytest
- [ ] Implement data quality checks with Great Expectations
- [ ] Add email/Slack alerting on pipeline failures
- [ ] Switch to incremental loading for scalability
- [ ] Add CI/CD pipeline with GitHub Actions
- [ ] Implement data versioning
- [ ] Add more cities and weather parameters

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Nhat Nam Phan**
- GitHub: [@NhatNamPhan](https://github.com/NhatNamPhan)
- Project Link: [Weather_Airflow_Pipeline](https://github.com/NhatNamPhan/Weather_Airflow_Pipeline)

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing free weather API
- [Apache Airflow](https://airflow.apache.org/) for workflow orchestration
- [Streamlit](https://streamlit.io/) for rapid dashboard development

---

⭐ **Star this repository if you found it helpful!**
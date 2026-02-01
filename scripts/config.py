"""
Configuration module for Weather ETL Pipeline.
Loads environment variables and defines constants.
Supports both local .env files and Streamlit Cloud secrets.
"""
import os
import json
from pathlib import Path

# Streamlit Cloud secrets support
try:
    import streamlit as st
    # Running on Streamlit Cloud - use secrets
    DB_USER = st.secrets.get("DB_USER", os.getenv("DB_USER", "postgres"))
    DB_PASSWORD = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
    DB_HOST = st.secrets.get("DB_HOST", os.getenv("DB_HOST", "localhost"))
    DB_PORT = st.secrets.get("DB_PORT", os.getenv("DB_PORT", "5432"))
    DB_NAME = st.secrets.get("DB_NAME", os.getenv("DB_NAME", "weather_db"))
except (ImportError, FileNotFoundError):
    # Running locally - use .env file
    from dotenv import load_dotenv
    load_dotenv()
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "weather_db")

# Project paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARCHIVE_DATA_DIR = DATA_DIR / "archive"

# Database connection string
DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Open-Meteo API configuration
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"
API_RETRY_COUNT = 5
API_BACKOFF_FACTOR = 0.2

# Load cities configuration
def load_cities_config():
    """Load cities configuration from JSON file."""
    cities_file = CONFIG_DIR / "cities.json"
    with open(cities_file, 'r') as f:
        config = json.load(f)
    return config['cities']

CITIES = load_cities_config()

# Weather parameters
DAILY_PARAMS = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weather_code"]
HOURLY_PARAMS = ["temperature_2m", "precipitation", "weather_code", "relative_humidity_2m", "wind_speed_10m"]

# Data retention (days) 
DATA_RETENTION_DAYS = 30

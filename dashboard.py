import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from scripts.config import DB_CONNECTION_STRING

engine = create_engine(DB_CONNECTION_STRING)
st.title("Weather Dashboard")
df = pd.read_sql("SELECT * FROM weather_daily", engine)

# Set the date column as index if it exists
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

# Select only numeric columns for the line chart
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    st.line_chart(df[numeric_cols])
else:
    st.warning("No numeric columns found in the data")

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine
from scripts.config import DB_CONNECTION_STRING

# Page config
st.set_page_config(layout="wide", page_title="Weather Dashboard")
st.title("🌤️ Weather Dashboard")

# Connect to database
engine = create_engine(DB_CONNECTION_STRING)
city = 'Tokyo'
sql = "SELECT * FROM weather_daily WHERE city = %s", city
# ===== LOAD DATA =====
@st.cache_data
def load_data():
    """Load weather data from database"""
    df_daily = pd.read_sql(sql=sql, con=engine)
    
    # Convert to datetime
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    
    # Extract year, month, day
    df_daily['year'] = df_daily['date'].dt.year
    df_daily['month'] = df_daily['date'].dt.month
    df_daily['day'] = df_daily['date'].dt.day
    df_daily['month_day'] = df_daily['date'].dt.strftime('%m-%d')

    
    return df_daily

df_daily, df_hourly = load_data()

# ===== TABS =====
tab1, tab2 = st.tabs(["📊 Compare Years", "⏰ Hourly Trends"])

# ===== TAB 1: COMPARE YEARS =====
with tab1:
    st.subheader("Compare different years")
    
    # Get available years
    available_years = sorted(df_daily['year'].unique())
    
    # Multiselect years to compare
    selected_years = st.pills(
        "Years to compare",
        available_years,
        default=available_years[-1:],  # Default: latest year
        selection_mode="multi"
    )
    
    if selected_years:
        # Filter data for selected years
        df_selected = df_daily[df_daily['year'].isin(selected_years)].copy()
        
        # Temperature chart
        st.write("### Temperature")
        temp_chart = alt.Chart(df_selected).mark_area(
            opacity=0.3,
            interpolate='monotone'
        ).encode(
            x=alt.X('month_day:N').title('Date'),
            y=alt.Y('temperature_2m_max:Q').title('Temperature (°C)').scale(zero=False),
            color=alt.Color('year:N').title('Year'),
            tooltip=['month_day:N', 'temperature_2m_max:Q', 'year:N']
        ).properties(
            width=900,
            height=400
        ).interactive()
        
        st.altair_chart(temp_chart, use_container_width=True)
        
        # Precipitation chart
        st.write("### Precipitation")
        precip_chart = alt.Chart(df_selected).mark_bar(
            opacity=0.7
        ).encode(
            x=alt.X('month_day:N').title('Date'),
            y=alt.Y('precipitation_sum:Q').title('Precipitation (mm)'),
            color=alt.Color('year:N').title('Year'),
            xOffset='year:N'
        ).properties(
            width=900,
            height=300
        ).interactive()
        
        st.altair_chart(precip_chart, use_container_width=True)
    else:
        st.warning("Please select at least one year")
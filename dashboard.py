import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from scripts.config import DB_CONNECTION_STRING
from datetime import datetime
import json
import os

# Page config
st.set_page_config(layout="wide", page_title="Weather Dashboard", page_icon="🌤️")

# Custom CSS for modern styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        font-weight: 500;
    }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .plot-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin: 10px 0;
    }
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-weight: 700 !important;
    }
    h3 {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Load cities from JSON
@st.cache_data
def load_cities():
    cities_file = os.path.join(os.path.dirname(__file__), 'config', 'cities.json')
    with open(cities_file, 'r') as f:
        data = json.load(f)
    return [city['name'] for city in data['cities']]

cities = load_cities()

# Header
st.title("🌤️ Weather Dashboard")
st.markdown("### Real-time Weather Analytics and Trends")

# Filters on main page
st.markdown("")
col_city, col_year = st.columns([1, 1])

with col_city:
    selected_city = st.selectbox(
        "🌍 Select City",
        cities,
        index=cities.index('Hanoi') if 'Hanoi' in cities else 0,
        help="Choose a city to view weather data"
    )

# Connect database
@st.cache_data(ttl=300)
def load_data(city):
    engine = create_engine(DB_CONNECTION_STRING)
    sql = 'SELECT * FROM weather_daily WHERE city = %s'
    df = pd.read_sql(sql=sql, con=engine, params=(city,))
    
    # Transform data
    df = df.rename(columns={
        'temperature_max': 'temp_max',
        'temperature_min': 'temp_min',
        'precipitation_sum': 'precipitation'
    })
    df['year'] = df['date'].dt.year
    
    # Weather description mapping
    weather_desc_map = {
        0: "sun",
        1: "sun",
        2: "sun",
        3: "cloud",
        51: "drizzle",
        53: "drizzle",
        55: "drizzle",
        61: "rain",
        63: "rain",
        65: "rain",
        71: "snow",
        73: "snow",
        75: "snow"
    }
    df['weather_desc'] = df['weather_code'].map(weather_desc_map)
    
    return df

# Load hourly data function
@st.cache_data(ttl=3600)
def load_hourly_data(city, selected_date):
    """Load hourly weather data for a specific city and date"""
    engine = create_engine(DB_CONNECTION_STRING)
    sql = '''
        SELECT * FROM weather_hourly 
        WHERE city = %s 
        AND DATE(date) = %s
        ORDER BY date
    '''
    df = pd.read_sql(sql=sql, con=engine, params=(city, selected_date))
    
    if df.empty:
        return df
    
    # Rename columns for consistency
    df = df.rename(columns={
        'temperature_2m': 'temperature',
        'relative_humidity_2m': 'humidity',
        'wind_speed_10m': 'wind_speed'
    })
    
    # Extract hour from datetime
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    
    # Weather description mapping
    weather_desc_map = {
        0: "sun",
        1: "sun",
        2: "sun",
        3: "cloud",
        51: "drizzle",
        53: "drizzle",
        55: "drizzle",
        61: "rain",
        63: "rain",
        65: "rain",
        71: "snow",
        73: "snow",
        75: "snow"
    }
    df['weather_desc'] = df['weather_code'].map(weather_desc_map)
    
    return df


# Load data for selected city
df_daily = load_data(selected_city)

# Year selector
with col_year:
    years = sorted(df_daily['year'].unique(), reverse=True)
    selected_year = st.selectbox(
        "📅 Select Year",
        years,
        index=0,
        help="Choose a year to view weather data"
    )

# Update page title with selected city
st.markdown(f"<h2 style='text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>📍 {selected_city}</h2>", unsafe_allow_html=True)

# Filter data
df_filtered = df_daily[df_daily['year'] == selected_year].copy()
df_filtered = df_filtered.sort_values('date')

# Calculate metrics
if not df_filtered.empty:
    latest_data = df_filtered.iloc[-1]
    avg_temp = df_filtered['temp_max'].mean()
    total_precipitation = df_filtered['precipitation'].sum()
    sunny_days = len(df_filtered[df_filtered['weather_desc'].isin(['sun'])])
    rainy_days = len(df_filtered[df_filtered['weather_desc'].str.contains('rain', na=False)])
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌡️ Current Temp (Max)",
            value=f"{latest_data['temp_max']:.1f}°C",
            delta=f"{latest_data['temp_max'] - avg_temp:.1f}°C from avg"
        )
    
    with col2:
        st.metric(
            label="💧 Total Precipitation",
            value=f"{total_precipitation:.1f} mm",
            delta=f"{len(df_filtered)} days tracked"
        )
    
    with col3:
        st.metric(
            label="☀️ Sunny Days",
            value=f"{sunny_days}",
            delta=f"{(sunny_days/len(df_filtered)*100):.1f}%"
        )
    
    with col4:
        st.metric(
            label="🌧️ Rainy Days",
            value=f"{rainy_days}",
            delta=f"{(rainy_days/len(df_filtered)*100):.1f}%"
        )
    
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Temperature Analysis", "💧 Precipitation & Weather", "📊 Statistical Breakdown", "⏰ Hourly Analysis"])
    
    # TAB 1: Temperature Analysis
    with tab1:
        st.markdown("")  # Spacing
        
        # Temperature trend chart - Full width
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=df_filtered['temp_max'],
            name='Max Temperature °C',
            line=dict(color='#FF6B6B', width=3, shape='spline'),
            fill=None,
            mode='lines+markers',
            marker=dict(size=7, symbol='circle', line=dict(color='white', width=2)),
            hovertemplate='<b>Max Temp</b>: %{y:.1f}°C<br><b>Date</b>: %{x|%b %d, %Y}<extra></extra>'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=df_filtered['temp_min'],
            name='Min Temperature °C',
            line=dict(color='#4ECDC4', width=3, shape='spline'),
            fill=None,
            mode='lines+markers',
            marker=dict(size=7, symbol='circle', line=dict(color='white', width=2)),
            hovertemplate='<b>Min Temp</b>: %{y:.1f}°C<br><b>Date</b>: %{x|%b %d, %Y}<extra></extra>'
        ))
        
        fig_temp.update_layout(
            title=dict(
                text=f'Daily Temperature Range - {selected_year}',
                font=dict(size=24, family='Arial, sans-serif', color='#2C3E50', weight=700),
                x=0.5,
                xanchor='center'
            ),
            hovermode='x unified',
            xaxis=dict(
                title=dict(text='Date', font=dict(size=16, color='#1a1a1a', weight=600)),
                tickformat='%b %d',
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.3)',
                gridwidth=1,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif')
            ),
            yaxis=dict(
                title=dict(text='Temperature (°C)', font=dict(size=16, color='#1a1a1a', weight=600)),
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.3)',
                gridwidth=1,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif')
            ),
            plot_bgcolor='rgba(255, 255, 255, 0.95)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            height=500,
            margin=dict(l=60, r=40, t=80, b=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=13, color='black'),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1
            ),
            font=dict(family='Arial, sans-serif')
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Temperature statistics in columns
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="🔥 Average Max Temp",
                value=f"{df_filtered['temp_max'].mean():.1f}°C"
            )
        with col2:
            st.metric(
                label="❄️ Average Min Temp",
                value=f"{df_filtered['temp_min'].mean():.1f}°C"
            )
        with col3:
            st.metric(
                label="📊 Temperature Range",
                value=f"{(df_filtered['temp_max'].mean() - df_filtered['temp_min'].mean()):.1f}°C"
            )
    
    # TAB 2: Precipitation & Weather
    with tab2:
        st.markdown("")  # Spacing
        
        # Precipitation chart
        df_filtered['month'] = df_filtered['date'].dt.month_name()
        df_filtered['month'] = df_filtered['month'].str[0:3]
        
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            x=df_filtered['month'],
            y=df_filtered['precipitation'],
            name='Precipitation',
            marker=dict(
                color=df_filtered['precipitation'],
                colorscale=[
                    [0, '#E3F2FD'],
                    [0.3, '#90CAF9'],
                    [0.6, '#42A5F5'],
                    [1, '#1976D2']
                ],
                line=dict(color='rgba(255, 255, 255, 0.8)', width=2),
                showscale=True,
                colorbar=dict(
                    title='mm',
                    thickness=15,
                    len=0.7
                )
            ),
            hovertemplate='<b>%{x}</b><br>Precipitation: %{y:.1f} mm<extra></extra>'
        ))
        
        fig_bar.update_layout(
            title=dict(
                text=f'Daily Precipitation - {selected_year}',
                font=dict(size=24, family='Arial, sans-serif', color='#2C3E50', weight=700),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(text='Month', font=dict(size=16, color='#1a1a1a', weight=600)),
                showgrid=False,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif')
            ),
            yaxis=dict(
                title=dict(text='Precipitation (mm)', font=dict(size=16, color='#1a1a1a', weight=600)),
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.3)',
                gridwidth=1,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif')
            ),
            plot_bgcolor='rgba(255, 255, 255, 0.95)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            height=450,
            margin=dict(l=60, r=40, t=80, b=60),
            font=dict(family='Arial, sans-serif', color='#1a1a1a')
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Weather distribution pie chart with better styling
        col_pie_left, col_pie_right = st.columns([1, 1])
        
        with col_pie_left:
            weather_counts = df_filtered['weather_desc'].value_counts().reset_index()
            weather_counts.columns = ['weather', 'count']
            
            weather_color_map = {
                'sun': '#FDB813',
                'cloud': '#95A5A6',
                'drizzle': '#74B9FF',
                'rain': '#0984E3',
                'snow': '#DFE6E9'
            }
            
            # Capitalize labels for better display
            weather_counts['weather_cap'] = weather_counts['weather'].str.capitalize()
            
            colors = [weather_color_map.get(w, '#BDC3C7') for w in weather_counts['weather']]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=weather_counts['weather_cap'],
                values=weather_counts['count'],
                hole=0.4,
                marker=dict(colors=colors, line=dict(color='white', width=3)),
                textposition='auto',
                textfont=dict(size=14, family='Arial, sans-serif', color='black', weight=600),
                hovertemplate='<b>%{label}</b><br>Days: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title=dict(
                    text=f'Weather Distribution - {selected_year}',
                    font=dict(size=22, family='Arial, sans-serif', color='#2C3E50', weight=700),
                    x=0.5,
                    xanchor='center'
                ),
                height=450,
                margin=dict(l=20, r=80, t=80, b=20),
                paper_bgcolor='rgba(255, 255, 255, 0)',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(size=13, color='black'),
                    bgcolor='rgba(255, 255, 255, 0.95)',
                    bordercolor='#2C3E50',
                    borderwidth=1
                ),
                font=dict(family='Arial, sans-serif')
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_pie_right:
            st.markdown("### 📋 Weather Summary")
            st.markdown("")
            
            # Display weather counts in a nice format
            for idx, row in weather_counts.iterrows():
                weather_emoji = {
                    'sun': '☀️',
                    'cloud': '☁️',
                    'drizzle': '🌦️',
                    'rain': '🌧️',
                    'snow': '❄️'
                }
                emoji = weather_emoji.get(row['weather'], '🌤️')
                percentage = (row['count'] / len(df_filtered)) * 100
                
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; 
                     margin-bottom: 10px; border-left: 5px solid {weather_color_map.get(row['weather'], '#BDC3C7')}'>
                    <h4 style='margin: 0; color: #2C3E50;'>{emoji} {row['weather'].capitalize()}</h4>
                    <p style='margin: 5px 0 0 0; font-size: 16px; color: #34495E;'>
                        <b>{row['count']}</b> days ({percentage:.1f}%)
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # TAB 3: Statistical Breakdown
    with tab3:
        st.markdown("")  # Spacing
        
        # Monthly weather breakdown
        df_percent = df_filtered.groupby(['month', 'weather_desc']).size().reset_index(name='count')
        df_percent['percent'] = (
            df_percent['count'] / df_percent.groupby('month')['count'].transform('sum')
        )
        
        month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        weather_colors = {
            'sun': '#FDB813',      
            'cloud': '#95A5A6',    
            'drizzle': '#74B9FF',  
            'rain': '#0984E3',     
            'snow': '#DFE6E9'      
        }
        
        # Sort the data by month for proper display
        df_percent['month_num'] = pd.to_datetime(df_percent['month'], format='%b').dt.month
        df_percent = df_percent.sort_values('month_num')
        
        fig_percent = go.Figure()
        
        # Get unique weather types and sort them for consistent stacking
        weather_types = sorted(df_percent['weather_desc'].unique())
        
        for weather in weather_types:
            df_weather = df_percent[df_percent['weather_desc'] == weather]
            fig_percent.add_trace(go.Bar(
                x=df_weather['month'],
                y=df_weather['percent'],
                name=weather.capitalize(),
                marker_color=weather_colors.get(weather, '#BDC3C7'),
                marker_line=dict(color='white', width=1.5),
                hovertemplate='<b>%{x}</b><br>' + weather.capitalize() + ': %{y:.1%}<extra></extra>',
                text=[f"{val:.0%}" if val > 0.05 else "" for val in df_weather['percent']],
                textposition='inside',
                textfont=dict(size=14, color='black', family='Arial, sans-serif')
            ))
        
        fig_percent.update_layout(
            barmode='stack',
            title=dict(
                text=f'Monthly Weather Distribution - {selected_year}',
                font=dict(size=24, family='Arial, sans-serif', color='#2C3E50', weight=700),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(text='Month', font=dict(size=16, color='#1a1a1a', weight=600)),
                showgrid=False,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif'),
                tickangle=0,
                showticklabels=True
            ),
            yaxis=dict(
                title=dict(text='Percentage of Days', font=dict(size=16, color='#1a1a1a', weight=600)),
                tickformat='.0%',
                showgrid=True,
                gridcolor='rgba(189, 195, 199, 0.3)',
                gridwidth=1,
                linecolor='#2C3E50',
                linewidth=2,
                tickfont=dict(size=14, color='#1a1a1a', family='Arial, sans-serif')
            ),
            plot_bgcolor='rgba(255, 255, 255, 0.95)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            height=550,
            margin=dict(l=70, r=50, t=90, b=80),
            legend=dict(
                title=dict(text='Weather Type', font=dict(size=14, color='#2C3E50', weight=600)),
                orientation="h",
                yanchor="bottom",
                y=-0.35,
                xanchor="center",
                x=0.5,
                font=dict(size=13, color='#2C3E50'),
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#BDC3C7',
                borderwidth=1
            ),
            font=dict(family='Arial, sans-serif'),
            uniformtext=dict(mode='hide', minsize=10)
        )
        
        st.plotly_chart(fig_percent, use_container_width=True)
        
        # Summary statistics
        st.markdown("")
        st.markdown("### 📈 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            driest_month = df_filtered.groupby('month')['precipitation'].sum().idxmin()
            st.metric(
                label="🌵 Driest Month",
                value=f"Month {driest_month}"
            )
        with col2:
            wettest_month = df_filtered.groupby('month')['precipitation'].sum().idxmax()
            st.metric(
                label="🌧️ Wettest Month",
                value=f"Month {wettest_month}"
            )
        with col3:
            st.metric(
                label="🔥 Warmest Day",
                value=f"{df_filtered['temp_max'].max():.1f}°C"
            )
        with col4:
            st.metric(
                label="❄️ Coldest Day",
                value=f"{df_filtered['temp_min'].min():.1f}°C"
            )
    
    # TAB 4: Hourly Analysis
    with tab4:
        st.markdown("")  # Spacing
        
        # Date picker for hourly data
        st.markdown("### 📅 Select Date for Hourly Analysis")
        
        # Get available dates from filtered data
        available_dates = df_filtered['date'].dt.date.unique()
        if len(available_dates) > 0:
            selected_date = st.date_input(
                "📅 Choose a date",
                value=available_dates[-1],
                min_value=available_dates[0],
                max_value=available_dates[-1],
                help="Select a date to view hourly weather data"
            )
            
            # Load hourly data
            df_hourly = load_hourly_data(selected_city, selected_date)
            
            if not df_hourly.empty:
                st.markdown("---")
                
                # 24-Hour Temperature Chart
                st.markdown("### 🌡️ 24-Hour Temperature Trend")
                
                fig_hourly_temp = go.Figure()
                
                fig_hourly_temp.add_trace(go.Scatter(
                    x=df_hourly['hour'],
                    y=df_hourly['temperature'],
                    mode='lines+markers',
                    name='Temperature',
                    line=dict(color='#FF6B6B', width=3, shape='spline'),
                    marker=dict(size=8, color='#FF6B6B', line=dict(color='white', width=2)),
                    hovertemplate='<b>Hour</b>: %{x}:00<br><b>Temp</b>: %{y:.1f}°C<extra></extra>'
                ))
                
                # Highlight max and min
                max_temp_idx = df_hourly['temperature'].idxmax()
                min_temp_idx = df_hourly['temperature'].idxmin()
                
                fig_hourly_temp.add_trace(go.Scatter(
                    x=[df_hourly.loc[max_temp_idx, 'hour']],
                    y=[df_hourly.loc[max_temp_idx, 'temperature']],
                    mode='markers',
                    name='Hottest',
                    marker=dict(size=15, color='#FF3838', symbol='star', line=dict(color='white', width=2)),
                    hovertemplate='<b>Hottest Hour</b><br>%{y:.1f}°C at %{x}:00<extra></extra>'
                ))
                
                fig_hourly_temp.add_trace(go.Scatter(
                    x=[df_hourly.loc[min_temp_idx, 'hour']],
                    y=[df_hourly.loc[min_temp_idx, 'temperature']],
                    mode='markers',
                    name='Coldest',
                    marker=dict(size=15, color='#4ECDC4', symbol='star', line=dict(color='white', width=2)),
                    hovertemplate='<b>Coldest Hour</b><br>%{y:.1f}°C at %{x}:00<extra></extra>'
                ))
                
                fig_hourly_temp.update_layout(
                    title=dict(
                        text=f'Temperature Throughout the Day - {selected_date}',
                        font=dict(size=24, family='Arial, sans-serif', color='#2C3E50', weight=700),
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        title=dict(text='Hour of Day', font=dict(size=16, color='#1a1a1a', weight=600)),
                        tickmode='linear',
                        tick0=0,
                        dtick=2,
                        showgrid=True,
                        gridcolor='rgba(189, 195, 199, 0.3)',
                        linecolor='#2C3E50',
                        linewidth=2,
                        tickfont=dict(size=14, color='#1a1a1a')
                    ),
                    yaxis=dict(
                        title=dict(text='Temperature (°C)', font=dict(size=16, color='#1a1a1a', weight=600)),
                        showgrid=True,
                        gridcolor='rgba(189, 195, 199, 0.3)',
                        linecolor='#2C3E50',
                        linewidth=2,
                        tickfont=dict(size=14, color='#1a1a1a')
                    ),
                    plot_bgcolor='rgba(255, 255, 255, 0.95)',
                    paper_bgcolor='rgba(255, 255, 255, 0)',
                    height=450,
                    margin=dict(l=70, r=50, t=90, b=100),
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.35,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=13, color='#1a1a1a'),
                        bgcolor='rgba(255, 255, 255, 0.9)',
                        bordercolor='#2C3E50',
                        borderwidth=1
                    )
                )
                
                st.plotly_chart(fig_hourly_temp, use_container_width=True)
                
                # Two columns for precipitation and weather distribution
                col_precip, col_weather = st.columns(2)
                
                with col_precip:
                    st.markdown("### 💧 Hourly Precipitation")
                    
                    fig_hourly_precip = go.Figure()
                    
                    fig_hourly_precip.add_trace(go.Bar(
                        x=df_hourly['hour'],
                        y=df_hourly['precipitation'],
                        marker=dict(
                            color=df_hourly['precipitation'],
                            colorscale=[
                                [0, '#E3F2FD'],
                                [0.5, '#42A5F5'],
                                [1, '#1976D2']
                            ],
                            line=dict(color='white', width=1.5)
                        ),
                        hovertemplate='<b>Hour</b>: %{x}:00<br><b>Precipitation</b>: %{y:.2f} mm<extra></extra>'
                    ))
                    
                    fig_hourly_precip.update_layout(
                        title=dict(
                            text='Precipitation by Hour',
                            font=dict(size=20, family='Arial, sans-serif', color='#2C3E50', weight=700),
                            x=0.5,
                            xanchor='center'
                        ),
                        xaxis=dict(
                            title=dict(text='Hour', font=dict(size=16, color='#1a1a1a', weight=600)),
                            tickmode='linear',
                            tick0=0,
                            dtick=3,
                            showgrid=False,
                            linecolor='#2C3E50',
                            tickfont=dict(size=14, color='#1a1a1a')
                        ),
                        yaxis=dict(
                            title=dict(text='mm', font=dict(size=16, color='#1a1a1a', weight=600)),
                            showgrid=True,
                            gridcolor='rgba(189, 195, 199, 0.3)',
                            linecolor='#2C3E50',
                            tickfont=dict(size=14, color='#1a1a1a')
                        ),
                        plot_bgcolor='rgba(255, 255, 255, 0.95)',
                        paper_bgcolor='rgba(255, 255, 255, 0)',
                        height=400,
                        margin=dict(l=60, r=30, t=70, b=60),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_hourly_precip, use_container_width=True)
                
                with col_weather:
                    st.markdown("### 🌤️ Weather Distribution")
                    
                    weather_hourly_counts = df_hourly['weather_desc'].value_counts().reset_index()
                    weather_hourly_counts.columns = ['weather', 'count']
                    
                    weather_color_map = {
                        'sun': '#FDB813',
                        'cloud': '#95A5A6',
                        'drizzle': '#74B9FF',
                        'rain': '#0984E3',
                        'snow': '#DFE6E9'
                    }
                    
                    fig_hourly_weather = go.Figure(data=[go.Bar(
                        x=weather_hourly_counts['weather'],
                        y=weather_hourly_counts['count'],
                        marker=dict(
                            color=[weather_color_map.get(w, '#BDC3C7') for w in weather_hourly_counts['weather']],
                            line=dict(color='white', width=2)
                        ),
                        text=weather_hourly_counts['count'],
                        textposition='auto',
                        textfont=dict(size=14, color='white', weight=600),
                        hovertemplate='<b>%{x}</b><br>Hours: %{y}<extra></extra>'
                    )])
                    
                    fig_hourly_weather.update_layout(
                        title=dict(
                            text='Hours by Weather Type',
                            font=dict(size=20, family='Arial, sans-serif', color='#2C3E50', weight=700),
                            x=0.5,
                            xanchor='center'
                        ),
                        xaxis=dict(
                            title=dict(text='Weather Type', font=dict(size=16, color='#1a1a1a', weight=600)),
                            showgrid=False,
                            linecolor='#2C3E50',
                            tickfont=dict(size=14, color='#1a1a1a')
                        ),
                        yaxis=dict(
                            title=dict(text='Hours', font=dict(size=16, color='#1a1a1a', weight=600)),
                            showgrid=True,
                            gridcolor='rgba(189, 195, 199, 0.3)',
                            linecolor='#2C3E50',
                            tickfont=dict(size=14, color='#1a1a1a')
                        ),
                        plot_bgcolor='rgba(255, 255, 255, 0.95)',
                        paper_bgcolor='rgba(255, 255, 255, 0)',
                        height=400,
                        margin=dict(l=60, r=30, t=70, b=60),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_hourly_weather, use_container_width=True)
                
                # Hourly Statistics Summary
                st.markdown("")
                st.markdown("### 📊 Hourly Statistics Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                warmest_hour = df_hourly.loc[df_hourly['temperature'].idxmax()]
                coldest_hour = df_hourly.loc[df_hourly['temperature'].idxmin()]
                
                with col1:
                    st.metric(
                        label="🔥 Warmest Hour",
                        value=f"{int(warmest_hour['hour'])}:00",
                        delta=f"{warmest_hour['temperature']:.1f}°C"
                    )
                with col2:
                    st.metric(
                        label="❄️ Coldest Hour",
                        value=f"{int(coldest_hour['hour'])}:00",
                        delta=f"{coldest_hour['temperature']:.1f}°C"
                    )
                with col3:
                    st.metric(
                        label="💧 Total Precipitation",
                        value=f"{df_hourly['precipitation'].sum():.2f} mm"
                    )
                with col4:
                    st.metric(
                        label="💨 Avg Wind Speed",
                        value=f"{df_hourly['wind_speed'].mean():.1f} km/h"
                    )
            else:
                st.warning(f"⚠️ No hourly data available for {selected_date}. Please select another date.")
        else:
            st.warning("⚠️ No dates available in the selected year.")
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(
            df_filtered[['date', 'temp_max', 'temp_min', 'precipitation', 'weather_desc']].sort_values('date', ascending=False),
            use_container_width=True,
            hide_index=True
        )
else:
    st.warning(f"No data available for {selected_year}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>"
    "<p>🌍 Weather Dashboard | Data updated from PostgreSQL Database</p>"
    "<p style='margin-top: 5px;'>"
    "<a href='https://github.com/NhatNamPhan/Weather_Airflow_Pipeline' target='_blank' "
    "style='color: #ffffff; text-decoration: none; font-size: 14px; "
    "background: rgba(255, 255, 255, 0.1); padding: 8px 15px; border-radius: 8px; "
    "display: inline-block; transition: all 0.3s; border: 1px solid rgba(255, 255, 255, 0.2);'>"
    "⭐ View on GitHub"
    "</a>"
    "</p>"
    "</div>",
    unsafe_allow_html=True
)
import pandas as pd
from sqlalchemy import create_engine
from config import DB_CONNECTION_STRING

def load_to_postgres(df, table_name, if_exists= 'replace', **context):
    print(f"Loading {len(df)} rows to table '{table_name}'...")
    
    engine = create_engine(DB_CONNECTION_STRING)
    
    df.to_sql(
        name= table_name,
        con= engine,
        if_exists= if_exists,
        index= False
    )
    
    print(f"Successfully loaded {len(df)} rows to '{table_name}'")
    
    return len(df)
    
def load_hourly_data(hourly_df, **context):
    return load_to_postgres(hourly_df, "weather_hourly", if_exists='replace')

def load_daily_data(daily_df, **context):
    return load_to_postgres(daily_df, "weather_daily", if_exists='replace')


if __name__ == "__main__":
    from extract import extract_weather_data
    from transform import transform_hourly_data, transform_daily_data
    
    print("Testing ETL pipeline...")
    
    # Extract
    responses = extract_weather_data()
    
    # Transform
    hourly_df = transform_hourly_data(responses)
    daily_df = transform_daily_data(responses)
    
    # Load
    load_hourly_data(hourly_df)
    load_daily_data(daily_df)
    
    print("ETL pipeline completed successfully!")

import pandas as pd
from config import CITIES

def transform_hourly_data(responses, **context):
    print("Transforming hourly weather data...")
    
    all_hourly_data = []
    
    for idx, response in enumerate(responses):
        hourly = response.Hourly()
        
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(3).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
        
        hourly_data = {
            "date": pd.date_range(
                start= pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end= pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq= pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        
        hourly_data["city"] = CITIES[idx]["name"]
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        
        df = pd.DataFrame(hourly_data)
        all_hourly_data.append(df)

    hourly_df = pd.concat(all_hourly_data, ignore_index=True)
    print(f"Transformed {len(hourly_df)} hourly records")
    print(f"Null Values: {hourly_df.isnull().sum().sum()}")
    
    return hourly_df

def transform_daily_data(responses, **context):
    print("Transforming daily weather data...")
    
    all_daily_data = []
    
    for idx, response in enumerate(responses):
        daily = response.Daily()
        
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
        
        daily_data = {
            "date": pd.date_range(
                start= pd.to_datetime(daily.Time(), unit="s", utc=True),
                end= pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq= pd.Timedelta(seconds= daily.Interval()),
                inclusive= "left"
            )
        }

        daily_data["city"] = CITIES[idx]["name"]
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["precipitation_sum"] = daily_precipitation_sum
        
        df = pd.DataFrame(daily_data)
        all_daily_data.append(df)
        
    daily_df = pd.concat(all_daily_data, ignore_index=True)
    print(f"Transformed {len(daily_df)} daily records")
    print(f"Null Value: {daily_df.isnull().sum().sum()}")
    
    return daily_df

if __name__ == "__main__":
    from extract import extract_weather_data
    
    responses = extract_weather_data()
    hourly_df = transform_hourly_data(responses)
    daily_df = transform_daily_data(responses)
    
    print("Hourly data simple:")
    print(hourly_df.head())
    print("Daily data simple:")
    print(daily_df.head())
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import pandas as pd
from config import (
    CITIES,
    WEATHER_API_URL,
    API_RETRY_COUNT,
    API_BACKOFF_FACTOR,
    DAILY_PARAMS,
    HOURLY_PARAMS
)

def set_up_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=API_RETRY_COUNT, backoff_factor=API_BACKOFF_FACTOR)
    return openmeteo_requests.Client(session=retry_session)

def extract_weather_data(start_date = None, end_date = None, **context):
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = "2020-01-01"
    print(f"Extracting weather data from {start_date} to {end_date}")
    
    openmeteo = set_up_client()
    
    latitudes = [city['latitude'] for city in CITIES]
    longitudes = [city['longitude'] for city in CITIES]
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_PARAMS,
        "hourly": HOURLY_PARAMS
    }   
    
    print(f"Calling API for {len(CITIES)} cities...")
    responses = openmeteo.weather_api(WEATHER_API_URL, params=params)
    print(f"Successfully received {len(CITIES)} responses")
    
    return responses

if __name__ == "__main__":
    responses = extract_weather_data()
    print(f"Extracted data for {len(CITIES)} cities") 
    
    all_data = []
    for idx, response in enumerate(responses):
        Latitude = response.Latitude()
        Longitude = response.Longitude()
        Elevation = response.Elevation()
        
        data = {
            "City": CITIES[idx]["name"],
            "Latitude": Latitude,
            "Longitude": Longitude,
            "Elevation": Elevation
        }
        all_data.append(data)
        
    df = pd.DataFrame(all_data)
    print(df)
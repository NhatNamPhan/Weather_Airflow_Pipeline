import json
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
from pathlib import Path
from scripts.config import (
    CITIES,
    WEATHER_API_URL,
    API_RETRY_COUNT,
    API_BACKOFF_FACTOR,
    RAW_DATA_DIR, 
    DAILY_PARAMS,
    HOURLY_PARAMS
)

def set_up_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=API_RETRY_COUNT, backoff_factor=API_BACKOFF_FACTOR)
    return openmeteo_requests.Client(session=retry_session)

def extract_weather_data(start_date = None, end_date = None, **context):
    if end_date == None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date == None:
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
    
    save_raw_data(responses, end_date)
    
    return responses

def save_raw_data(responses, date_str):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_data = []
    for idx, response in enumerate(responses):
        city_data = {
            "city": CITIES[idx]['name'],
            "latitude": response.Latitude(),
            'longitude': response.Longitude(),
            'elevation': response.Elevation(),
            'timezone': response.Timezone(),
            'timezone_abbreviation': response.TimezoneAbbreviation(),
        }
        raw_data.append(city_data)
        
    filename = RAW_DATA_DIR / f"weather_raw_{date_str}.json"
    with open(filename, 'w') as f:
        json.dump(raw_data, f, indent=2)
        
    print(f"Raw data saved to {filename}")
    
if __name__ == "__main__":
    responses = extract_weather_data()
    print(f"Extracted data for {len(CITIES)} cities")    
        

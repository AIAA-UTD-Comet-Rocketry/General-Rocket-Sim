# Now Obsolete

from datetime import datetime

import pandas as pd
import FlightParams
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


url = "https://api.open-meteo.com/v1/forecast"

now = datetime.now()
current_date = now.date()  
current_date = str(current_date)

params = {
	"latitude": FlightParams.latitude,
	"longitude": FlightParams.longitude,
	"hourly": ["wind_speed_10m", "wind_speed_100m", "wind_speed_925hPa", "wind_speed_850hPa", "wind_speed_700hPa", "wind_direction_10m",  "wind_direction_100m", "wind_direction_925hPa", "wind_direction_850hPa", "wind_direction_700hPa"],
	"models": "ecmwf_ifs025",
    "timezone": "America/Chicago",
	"start_date": "2025-05-32",
	"end_date": "2025-05-32"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_wind_speed_10m = hourly.Variables(0).ValuesAsNumpy() / 3600 * 1000
hourly_wind_speed_100m = hourly.Variables(1).ValuesAsNumpy() / 3600 * 1000
hourly_wind_speed_925hPa = hourly.Variables(2).ValuesAsNumpy() / 3600 * 1000
hourly_wind_speed_850hPa = hourly.Variables(3).ValuesAsNumpy() / 3600 * 1000
hourly_wind_speed_700hPa = hourly.Variables(4).ValuesAsNumpy() / 3600 * 1000
hourly_wind_direction_10m = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_direction_100m = hourly.Variables(6).ValuesAsNumpy()
hourly_wind_direction_925hPa = hourly.Variables(7).ValuesAsNumpy()
hourly_wind_direction_850hPa = hourly.Variables(8).ValuesAsNumpy()
hourly_wind_direction_700hPa = hourly.Variables(9).ValuesAsNumpy()

print(hourly.Time())
print(hourly.TimeEnd())

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit="s").tz_localize("UTC").tz_convert("America/Chicago"),
	end = pd.to_datetime(hourly.TimeEnd(), unit="s").tz_localize("UTC").tz_convert("America/Chicago"),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
hourly_data["wind_speed_925hPa"] = hourly_wind_speed_925hPa
hourly_data["wind_speed_850hPa"] = hourly_wind_speed_850hPa
hourly_data["wind_speed_700hPa"] = hourly_wind_speed_700hPa
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
hourly_data["wind_direction_100m"] = hourly_wind_direction_100m
hourly_data["wind_direction_925hPa"] = hourly_wind_direction_925hPa
hourly_data["wind_direction_850hPa"] = hourly_wind_direction_850hPa
hourly_data["wind_direction_700hPa"] = hourly_wind_direction_700hPa

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

hourly_dataframe.to_csv("WallahiThisBetterWork.csv", index=False)
import openmeteo_requests
import requests_cache
from retry_requests import retry
import math

def convertDictToArr(dict):
    finalArr = []
    for hPa in dict.keys():
        alt = dict[hPa]
        finalArr.append((alt, hPa * 100))
    return finalArr

def processWeatherDataToArr(hourlyData, meterValues, hpaVals, hpaToMeter, counter, hour):
    finalArr = []
    for meterVal in meterValues:
        finalArr.append((meterVal, hourlyData.Variables(counter).ValuesAsNumpy()[hour]))
        counter += 1
    
    for hpaVal in hpaVals:
        meterVal = hpaToMeter[hpaVal]
        finalArr.append((meterVal, hourlyData.Variables(counter).ValuesAsNumpy()[hour]))
        counter += 1

    return finalArr, counter

def processWindVectors(speed, direction):
    finalArrU = []
    finalArrV = []
    for i in range(0, len(speed), 1):
        passedAlt = speed[i][0]
        newUVal = speed[i][1] * math.cos(math.radians(direction[i][1]))
        newVVal = speed[i][1] * math.sin(math.radians(direction[i][1]))
        finalArrU.append((passedAlt, newUVal))
        finalArrV.append((passedAlt, newVVal))
    
    return finalArrU, finalArrV

def fetchAllData(date, lat, lon):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    meterValuesWind = [10, 80]
    meterValuesTemp = [2, 80, 120]
    
    hpaVals = [975, 950, 925, 900, 850, 800, 700, 600]

    variableGetting = "geopotential_height"

    heightPoints = [
        f"{variableGetting}_975hPa",  f"{variableGetting}_950hPa",   f"{variableGetting}_925hPa",
        f"{variableGetting}_900hPa",  f"{variableGetting}_850hPa",   f"{variableGetting}_800hPa",
        f"{variableGetting}_700hPa",  f"{variableGetting}_600hPa",
    ]

    variableGetting = "wind_speed"

    windSpeedPoints = [
        f"{variableGetting}_10m",     f"{variableGetting}_80m",
        f"{variableGetting}_975hPa",  f"{variableGetting}_950hPa",   f"{variableGetting}_925hPa",
        f"{variableGetting}_900hPa",  f"{variableGetting}_850hPa",   f"{variableGetting}_800hPa",
        f"{variableGetting}_700hPa",  f"{variableGetting}_600hPa",
    ]

    variableGetting = "wind_direction"

    windDirectionPoints = [
        f"{variableGetting}_10m",     f"{variableGetting}_80m",
        f"{variableGetting}_975hPa",  f"{variableGetting}_950hPa",   f"{variableGetting}_925hPa",
        f"{variableGetting}_900hPa",  f"{variableGetting}_850hPa",   f"{variableGetting}_800hPa",
        f"{variableGetting}_700hPa",  f"{variableGetting}_600hPa",
    ]

    variableGetting = "temperature"

    temperaturePoints = [
        f"{variableGetting}_2m",      f"{variableGetting}_80m",      f"{variableGetting}_120m",
        f"{variableGetting}_975hPa",  f"{variableGetting}_950hPa",   f"{variableGetting}_925hPa",
        f"{variableGetting}_900hPa",  f"{variableGetting}_850hPa",   f"{variableGetting}_800hPa",
        f"{variableGetting}_700hPa",  f"{variableGetting}_600hPa",
    ]


    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": heightPoints + windSpeedPoints + windDirectionPoints + temperaturePoints,
        "timezone": "America/Chicago",
        "start_date": f"2026-{date[1]:02d}-{date[2]:02d}",
        "end_date": f"2026-{date[1]:02d}-{date[2]:02d}",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "ms",
    }

    url = "https://api.open-meteo.com/v1/forecast"
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourlyData = response.Hourly()

    pascalToMeters = {}

    totalCounter = 0

    for pascal in hpaVals:
        pascalToMeters[pascal] = hourlyData.Variables(totalCounter).ValuesAsNumpy()[date[3]]
        totalCounter += 1


    pressureArray = convertDictToArr(pascalToMeters)

    windSpeedArray, totalCounter = processWeatherDataToArr(hourlyData, meterValuesWind, hpaVals, pascalToMeters, totalCounter, date[3])
    windDirectionArray, totalCounter = processWeatherDataToArr(hourlyData, meterValuesWind, hpaVals, pascalToMeters, totalCounter, date[3])
    tempArray, totalCounter = processWeatherDataToArr(hourlyData, meterValuesTemp, hpaVals, pascalToMeters, totalCounter, date[3])

    return (pressureArray, tempArray, windSpeedArray, windDirectionArray)

def GetWeatherData(date, lat, lon):
    pressure, temperature, windSpeed, windDirection = fetchAllData(date, lat, lon)
    wind_u, wind_v = processWindVectors(windSpeed, windDirection)

    print(pressure)

    return pressure, temperature, wind_u, wind_v
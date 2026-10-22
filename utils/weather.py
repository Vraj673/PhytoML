"""
utils/weather.py
-----------------
Weather integration using the Open-Meteo API (https://open-meteo.com/).

Open-Meteo is used because it is completely free and requires NO API key
or account signup — ideal for a student project. Two of its endpoints
are used:
    1. Geocoding API  — turns a typed city name into latitude/longitude.
    2. Forecast API    — returns the current weather for that location.

On top of the raw weather data, this module adds a simple, explainable
heuristic that estimates plant-disease risk from humidity and
temperature — tying the weather feature back into the project's actual
subject (fungal/bacterial plant diseases spread faster in warm, humid
conditions).
"""

import requests
from flask import current_app

# Open-Meteo "weather code" -> human-readable condition.
# Reference: https://open-meteo.com/en/docs (WMO Weather interpretation codes)
WEATHER_CODE_MAP = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def geocode_city(city_name):
    """Turn a typed city name into {lat, lon, name, country}, or None if not found."""
    try:
        resp = requests.get(
            current_app.config["WEATHER_GEOCODE_URL"],
            params={"name": city_name, "count": 1},
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return None

    results = resp.json().get("results")
    if not results:
        return None

    r = results[0]
    return {
        "lat": r["latitude"],
        "lon": r["longitude"],
        "name": r["name"],
        "country": r.get("country", ""),
    }


def get_current_weather(lat, lon):
    """Fetch the current weather for a latitude/longitude. Returns None on failure."""
    try:
        resp = requests.get(
            current_app.config["WEATHER_FORECAST_URL"],
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return None

    current = resp.json().get("current", {})
    if not current:
        return None

    return {
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "wind_kmh": current.get("wind_speed_10m"),
        "condition": WEATHER_CODE_MAP.get(current.get("weather_code"), "Unknown"),
    }


def assess_disease_risk(humidity_pct, temperature_c):
    """
    Simple, explainable heuristic (not a model): fungal and bacterial plant
    diseases spread fastest in warm + humid conditions. This gives the
    user a quick, practical takeaway alongside the raw weather numbers.
    """
    humidity_pct = humidity_pct or 0
    temperature_c = temperature_c if temperature_c is not None else 0

    if humidity_pct >= 80 and 15 <= temperature_c <= 32:
        return {
            "level": "High",
            "color": "danger",
            "message": "Warm, humid conditions — favorable for fungal and bacterial "
                       "disease spread (e.g. blight). Inspect your plants closely.",
        }
    if humidity_pct >= 60:
        return {
            "level": "Moderate",
            "color": "warning",
            "message": "Moderate humidity — keep an eye out for early disease symptoms.",
        }
    return {
        "level": "Low",
        "color": "success",
        "message": "Low humidity — lower risk of fungal disease spread right now.",
    }


def get_weather_for_city(city_name):
    """
    Full pipeline: city name -> coordinates -> current weather -> disease
    risk hint. Returns None if the city can't be found or the API call fails
    (e.g. no internet access), so callers can show a friendly message instead
    of crashing.
    """
    location = geocode_city(city_name)
    if not location:
        return None

    weather = get_current_weather(location["lat"], location["lon"])
    if not weather:
        return None

    weather["location_name"] = location["name"]
    weather["country"] = location["country"]
    weather["risk"] = assess_disease_risk(weather["humidity_pct"], weather["temperature_c"])
    return weather

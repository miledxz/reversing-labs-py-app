import httpx
from typing import Dict
from datetime import datetime


GEOCODING_BASE = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_BASE = "https://api.open-meteo.com/v1/forecast"


async def get_city_coordinates(session: httpx.AsyncClient, city: str) -> tuple[float, float]:
    """Get latitude and longitude for a city name using OpenMeteo Geocoding API"""
    params = {"name": city, "count": 1, "format": "json"}
    r = await session.get(GEOCODING_BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    
    if not data.get("results"):
        raise ValueError(f"City '{city}' not found")
    
    result = data["results"][0]
    return result["latitude"], result["longitude"]


async def fetch_city(session: httpx.AsyncClient, city: str, units: str) -> Dict:
    lat, lon = await get_city_coordinates(session, city)
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,pressure_msl,visibility,cloud_cover",
        "daily": "sunrise,sunset",
        "timezone": "auto"
    }
    
    r = await session.get(WEATHER_BASE, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def parse_datetime_to_timestamp(datetime_str: str) -> int:
    """Convert ISO datetime string to Unix timestamp"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except (ValueError, TypeError):
        return 0


def normalize(city: str, payload: Dict) -> Dict:
    current = payload.get("current", {})
    daily = payload.get("daily", {})
    
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
        53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
        63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall",
        73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    
    weather_code = current.get("weather_code", 0)
    description = weather_codes.get(weather_code, "Unknown")
    
    sunrise_str = daily.get("sunrise", [""])[0] if daily.get("sunrise") else ""
    sunset_str = daily.get("sunset", [""])[0] if daily.get("sunset") else ""
    
    return {
        "city": city,
        "temperature": float(current.get("temperature_2m", 0)),
        "humidity": int(current.get("relative_humidity_2m", 0)),
        "wind_speed": float(current.get("wind_speed_10m", 0.0)),
        "description": description,
        "clouds": int(current.get("cloud_cover", 0)),
        "pressure": int(current.get("pressure_msl", 0)),
        "visibility": int(current.get("visibility", 0)),
        "sunrise": parse_datetime_to_timestamp(sunrise_str),
        "sunset": parse_datetime_to_timestamp(sunset_str),
    }
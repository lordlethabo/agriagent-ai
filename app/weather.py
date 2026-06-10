import os
import requests


def get_weather_context(location: str) -> dict:
    """
    Fetches real-time weather data from WeatherAPI.
    Falls back safely if the API key or request fails.
    """

    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return {
            "available": False,
            "summary": "Weather data unavailable because WEATHER_API_KEY is missing.",
            "source": "WeatherAPI",
            "error": "Missing WEATHER_API_KEY"
        }

    try:
        url = "https://api.weatherapi.com/v1/forecast.json"

        params = {
            "key": api_key,
            "q": location,
            "days": 3,
            "aqi": "no",
            "alerts": "no"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        location_data = data.get("location", {})
        forecast_days = data.get("forecast", {}).get("forecastday", [])

        forecast_summary = []

        for day in forecast_days:
            date = day.get("date")
            day_data = day.get("day", {})

            forecast_summary.append({
                "date": date,
                "max_temp_c": day_data.get("maxtemp_c"),
                "min_temp_c": day_data.get("mintemp_c"),
                "avg_temp_c": day_data.get("avgtemp_c"),
                "total_precip_mm": day_data.get("totalprecip_mm"),
                "avg_humidity": day_data.get("avghumidity"),
                "condition": day_data.get("condition", {}).get("text")
            })

        summary = (
            f"Weather for {location_data.get('name', location)}, "
            f"{location_data.get('country', '')}: "
            f"Current temperature {current.get('temp_c')}°C, "
            f"humidity {current.get('humidity')}%, "
            f"wind {current.get('wind_kph')} kph, "
            f"condition {current.get('condition', {}).get('text')}. "
            f"3-day forecast includes rainfall and temperature outlook."
        )

        return {
            "available": True,
            "source": "WeatherAPI",
            "location_name": location_data.get("name"),
            "region": location_data.get("region"),
            "country": location_data.get("country"),
            "current": {
                "temperature_c": current.get("temp_c"),
                "humidity": current.get("humidity"),
                "wind_kph": current.get("wind_kph"),
                "precip_mm": current.get("precip_mm"),
                "condition": current.get("condition", {}).get("text")
            },
            "forecast": forecast_summary,
            "summary": summary
        }

    except Exception as e:
        return {
            "available": False,
            "summary": "Weather data could not be retrieved. AgriAgent is using general advisory mode.",
            "source": "WeatherAPI",
            "error": str(e)
        }

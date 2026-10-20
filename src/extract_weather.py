import json
from pathlib import Path
from datetime import datetime, timezone
import requests


def fetch_weather(latitude: float, longitude: float) -> dict:
    """Fetch current weather data from the Open-Meteo API."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "America/Sao_Paulo",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def validate_weather(data: dict) -> None:
    """Validate the structure of the weather API response."""

    if not isinstance(data, dict):
        raise ValueError("Weather response must be a dictionary.")

    if "current" not in data or not isinstance(data["current"], dict):
        raise ValueError("Missing or invalid 'current' section.")

    required_fields = [
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]

    current = data["current"]

    missing_fields = [
        field
        for field in required_fields
        if field not in current or current[field] is None
    ]

    if missing_fields:
        raise ValueError(
            f"Missing or null weather fields: {missing_fields}"
        )


def save_weather(data: dict, output_dir: str = "data/raw") -> str:
    """Save weather data to a timestamped JSON file."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    path = Path(output_dir) / f"weather_{timestamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return str(path)
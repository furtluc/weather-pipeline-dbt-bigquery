from unittest.mock import Mock, patch

import requests

import json

import pytest

from src.extract_weather import fetch_weather, save_weather, validate_weather


@pytest.fixture
def valid_weather_data():
    return {
        "latitude": -27.5954,
        "longitude": -48.5480,
        "current": {
            "time": "2026-10-19T15:00",
            "temperature_2m": 18.5,
            "relative_humidity_2m": 64,
            "precipitation": 0.0,
            "wind_speed_10m": 16.7,
        },
    }


def test_validate_weather_accepts_valid_data(valid_weather_data):
    validate_weather(valid_weather_data)


def test_validate_weather_rejects_missing_current():
    with pytest.raises(ValueError, match="current"):
        validate_weather({"latitude": -27.5954})


def test_validate_weather_rejects_missing_field(valid_weather_data):
    del valid_weather_data["current"]["temperature_2m"]

    with pytest.raises(ValueError, match="temperature_2m"):
        validate_weather(valid_weather_data)


def test_validate_weather_rejects_null_field(valid_weather_data):
    valid_weather_data["current"]["temperature_2m"] = None

    with pytest.raises(ValueError, match="temperature_2m"):
        validate_weather(valid_weather_data)


def test_save_weather_creates_json_file(tmp_path, valid_weather_data):
    output_path = save_weather(
        valid_weather_data,
        output_dir=str(tmp_path),
    )

    with open(output_path, encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == valid_weather_data
    assert output_path.endswith(".json")


@patch("src.extract_weather.requests.get")
def test_fetch_weather_returns_json(mock_get):
    expected_data = {
        "latitude": -27.5954,
        "longitude": -48.5480,
        "current": {
            "time": "2026-10-19T15:00",
            "temperature_2m": 18.5,
            "relative_humidity_2m": 64,
            "precipitation": 0.0,
            "wind_speed_10m": 16.7,
        },
    }

    mock_response = Mock()
    mock_response.json.return_value = expected_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_weather(-27.5954, -48.5480)

    assert result == expected_data
    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args
    assert kwargs["params"]["latitude"] == -27.5954
    assert kwargs["params"]["longitude"] == -48.5480
    assert kwargs["timeout"] == 30


@patch("src.extract_weather.requests.get")
def test_fetch_weather_raises_http_error(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        "Internal Server Error"
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        fetch_weather(-27.5954, -48.5480)

import json
from pathlib import Path

from src.load_weather import prepare_weather_record

from unittest.mock import Mock, patch

from google.cloud import bigquery

from src.load_weather import load_weather


def test_prepare_weather_record_converts_timezone(tmp_path: Path):
    weather_data = {
        "latitude": -27.5954,
        "longitude": -48.5480,
        "timezone": "America/Sao_Paulo",
        "current": {
            "time": "2026-10-19T17:30",
            "temperature_2m": 16.6,
            "relative_humidity_2m": 74,
            "precipitation": 0.0,
            "wind_speed_10m": 15.8,
        },
    }

    json_path = tmp_path / "weather.json"
    json_path.write_text(
        json.dumps(weather_data),
        encoding="utf-8",
    )

    record = prepare_weather_record(str(json_path))

    assert record["observed_at"] == "2026-10-19T20:30:00+00:00"
    assert record["latitude"] == -27.5954
    assert record["longitude"] == -48.5480
    assert record["temperature_c"] == 16.6
    assert record["relative_humidity_pct"] == 74
    assert record["precipitation_mm"] == 0.0
    assert record["wind_speed_kmh"] == 15.8
    assert "ingested_at" in record
    

@patch("src.load_weather.bigquery.Client")
@patch("src.load_weather.prepare_weather_record")
def test_load_weather_appends_record(mock_prepare, mock_client_class):
    mock_prepare.return_value = {
        "observed_at": "2026-10-19T20:30:00+00:00",
        "latitude": -27.5954,
        "longitude": -48.5480,
        "temperature_c": 16.6,
        "relative_humidity_pct": 74,
        "precipitation_mm": 0.0,
        "wind_speed_kmh": 15.8,
        "ingested_at": "2026-10-23T18:00:00+00:00",
    }

    mock_client = Mock()
    mock_load_job = Mock()
    mock_client.load_table_from_json.return_value = mock_load_job
    mock_client_class.return_value = mock_client

    load_weather("fake_weather.json")

    mock_prepare.assert_called_once_with("fake_weather.json")
    mock_client_class.assert_called_once_with(
        project="weather-data-pipeline-512220"
    )
    mock_client.load_table_from_json.assert_called_once()

    args, kwargs = mock_client.load_table_from_json.call_args

    assert args[0] == [mock_prepare.return_value]
    assert args[1] == (
        "weather-data-pipeline-512220.weather_raw.weather_observations"
    )
    assert kwargs["job_config"].write_disposition == (
        bigquery.WriteDisposition.WRITE_APPEND
    )

    mock_load_job.result.assert_called_once()
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from google.cloud import bigquery


def prepare_weather_record(json_path: str) -> dict:
    """Read a weather JSON file and prepare a record for BigQuery."""

    path = Path(json_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    current = data["current"]

    observed_at = datetime.fromisoformat(
        current["time"]
    ).replace(
        tzinfo=ZoneInfo(data["timezone"])
    ).astimezone(timezone.utc)

    return {
        "observed_at": observed_at.isoformat(),
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "temperature_c": current["temperature_2m"],
        "relative_humidity_pct": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


def load_weather(
    json_path: str,
    project_id: str = "weather-data-pipeline-512220",
) -> None:
    """Append a weather record to the BigQuery raw table."""

    record = prepare_weather_record(json_path)

    client = bigquery.Client(project=project_id)

    table_id = f"{project_id}.weather_raw.weather_observations"
    
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("observed_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("temperature_c", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("relative_humidity_pct", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("precipitation_mm", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("wind_speed_kmh", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ],
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_json(
        [record],
        table_id,
        job_config=job_config,
    )
    load_job.result()

    print(f"Weather record loaded into {table_id}")
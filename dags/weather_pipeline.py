from datetime import datetime
import subprocess

from airflow.sdk import dag, task

from src.extract_weather import (
    fetch_weather,
    save_weather,
    validate_weather,
)
from src.load_weather import load_weather


@dag(
    dag_id="weather_pipeline",
    description="Extract, load and transform weather data",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["weather", "etl", "bigquery", "dbt"],
)
def weather_pipeline():

    @task
    def extract():
        weather_data = fetch_weather(
            latitude=-27.5954,
            longitude=-48.5480,
        )

        validate_weather(weather_data)

        output_path = save_weather(
            weather_data,
            output_dir="/opt/airflow/data/raw",
        )

        print(f"Weather data saved to {output_path}")
        return output_path

    @task
    def load(json_path: str):
        load_weather(json_path)

    @task
    def transform():
        subprocess.run(
            [
                "dbt",
                "build",
                "--project-dir",
                "/opt/airflow/dbt_project",
                "--profiles-dir",
                "/home/airflow/.dbt",
            ],
            check=True,
        )

    json_path = extract()
    load_task = load(json_path)
    transform_task = transform()

    load_task >> transform_task


weather_pipeline()
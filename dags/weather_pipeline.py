from datetime import datetime

from airflow.sdk import dag, task

from src.extract_weather import (
    fetch_weather,
    save_weather,
    validate_weather,
)


@dag(
    dag_id="weather_pipeline",
    description="Extract current weather data from Open-Meteo",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["weather", "etl"],
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

    extract()


weather_pipeline()
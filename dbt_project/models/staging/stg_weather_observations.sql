SELECT
    observed_at,
    latitude,
    longitude,
    temperature_c,
    relative_humidity_pct,
    precipitation_mm,
    wind_speed_kmh,
    ingested_at
FROM `weather-data-pipeline-512220.weather_raw.weather_observations`

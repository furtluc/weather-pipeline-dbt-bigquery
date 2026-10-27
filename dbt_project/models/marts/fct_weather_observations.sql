SELECT
    observed_at,
    DATE(observed_at, "America/Sao_Paulo") AS observed_date,
    latitude,
    longitude,
    temperature_c,
    relative_humidity_pct,
    precipitation_mm,
    wind_speed_kmh,
    ingested_at
FROM {{ ref('stg_weather_observations') }}

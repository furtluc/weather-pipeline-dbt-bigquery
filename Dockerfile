FROM apache/airflow:3.1.7

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow==3.1.7" \
    -r /requirements.txt

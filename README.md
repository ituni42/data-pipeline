# Motor Insurance Pipeline

A metadata-driven motor insurance data pipeline built with PySpark, Apache Airflow, and Docker.

## Requirements

- Docker Desktop
- Git

## Setup & Installation

1. Clone the repository:

```
git clone https://github.com/ituni42/data-pipeline.git
cd data-pipeline
```

2. Start all services:

```
docker compose up --build
```

3. Open Airflow at [http://localhost:8080](http://localhost:8080) and log in with `admin` / `admin`

4. Enable the `motor_ingestion` DAG and trigger it manually

## Services

| Service | URL |
|---------|-----|
| Airflow UI | http://localhost:8080 |
| Spark Master UI | http://localhost:8081 |

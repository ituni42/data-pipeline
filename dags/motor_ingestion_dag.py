from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

SPARK_SUBMIT = (
    "docker exec motor_insurance_pipeline-spark-master-1 "
    "/opt/spark/bin/spark-submit "
    "--master spark://spark-master:7077 "
    "/opt/pipeline/src/pipeline_runner.py "
    "--metadata /opt/pipeline/config/motor_policy_metadata.json "
    "--dataflow motor-ingestion"
)

with DAG(
    dag_id="motor_ingestion",
    description="Metadata-driven motor insurance policy ingestion pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["motor", "ingestion", "insurance"],
) as dag:

    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command=SPARK_SUBMIT,
    )

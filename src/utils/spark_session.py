import os

from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "motor-insurance-pipeline") -> SparkSession:
    master_url: str = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")

    spark: SparkSession = (
        SparkSession.builder
        .master(master_url)
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark

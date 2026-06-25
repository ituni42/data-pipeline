from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from utils.logger import get_logger

logger = get_logger(__name__)

#reads data into a spark dataframe based on source config from metadata
def read_source(spark: SparkSession, source_config: dict) -> DataFrame:
    name = source_config["name"]
    path = source_config["path"]
    fmt = source_config["format"].lower()

    logger.info(f"Reading source '{name}' from '{path}' as {fmt.upper()}")

    if fmt == "json":
        df = spark.read.option("multiline", "false").json(path)
    elif fmt == "csv":
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(path)
    else:
        raise ValueError(f"Unsupported source format: '{fmt}'. Supported: json, csv")

    logger.info(f"Source '{name}' loaded with {df.count()} rows and {len(df.columns)} columns")
    return df
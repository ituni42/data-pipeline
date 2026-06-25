from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from utils.logger import get_logger

logger = get_logger(__name__)

#maps function names from metadata to Spark functions
FIELD_FUNCTIONS = {
    "current_timestamp": F.current_timestamp,
    "current_date": F.current_date,
}


def apply_transformations(df: DataFrame, transformation_config: dict) -> DataFrame:
    return _add_fields(df, transformation_config["params"]["addFields"])


def _add_fields(df: DataFrame, fields_config: List[dict]) -> DataFrame:
    for field in fields_config:
        name: str = field["name"]
        function_name: str = field["function"]

        if function_name not in FIELD_FUNCTIONS:
            raise ValueError(
                f"Unknown field function: '{function_name}'. "
                f"Supported: {list(FIELD_FUNCTIONS.keys())}"
            )

        df = df.withColumn(name, FIELD_FUNCTIONS[function_name]())
        logger.info(f"Added field '{name}' using function '{function_name}'")

    return df

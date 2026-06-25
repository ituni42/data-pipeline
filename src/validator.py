from typing import List, Tuple

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

from utils.logger import get_logger

logger = get_logger(__name__)

# each rule returns a Spark column expression that is True when the row is invalid
VALIDATION_RULES = {
    "notNull": lambda field: F.col(field).isNull(),
    "notEmpty": lambda field: (F.col(field).isNull() | (F.trim(F.col(field)) == "")),
    "validAge": lambda field: (
        F.col(field).isNotNull() & ((F.col(field) < 18) | (F.col(field) > 100))
    ),
}


def validate(df: DataFrame, validation_config: dict) -> Tuple[DataFrame, DataFrame]:
    validations: list = validation_config["params"]["validations"]
    error_columns: List[Tuple] = []

    #build one error entry per field+rule combo
    for field_config in validations:
        field: str = field_config["field"]
        rules: list = field_config["validations"]

        for rule_name in rules:
            if rule_name not in VALIDATION_RULES:
                raise ValueError(
                    f"Unknown validation rule: '{rule_name}'. "
                    f"Supported rules: {list(VALIDATION_RULES.keys())}"
                )

            is_invalid = VALIDATION_RULES[rule_name](field)
            error_message: str = f"Field '{field}' failed rule '{rule_name}'"
            error_key: str = f"{field}__{rule_name}"

            error_col = F.when(is_invalid, F.lit(error_message)).otherwise(
                F.lit(None).cast(StringType())
            )
            error_columns.append((error_key, error_col))

    map_entries: list = []
    for key, col_expr in error_columns:
        map_entries.extend([F.lit(key), col_expr])

# build a map of {error_key: error_message} per row, then strip null entries
    df_with_error_column: DataFrame = df.withColumn(
        "_all_errors",
        F.map_filter(
            F.create_map(*map_entries),
            lambda _, v: v.isNotNull()
        )
    )

# _all_errors column is empty which means it's validation_ok
    validation_ok: DataFrame = (
        df_with_error_column
        .filter(F.size(F.col("_all_errors")) == 0)
        .drop("_all_errors")
    )

    validation_ko: DataFrame = (
        df_with_error_column
        .filter(F.size(F.col("_all_errors")) > 0)
        .withColumnRenamed("_all_errors", "validation_errors")
    )

    ok_count: int = validation_ok.count()
    ko_count: int = validation_ko.count()
    logger.info(f"Validation complete - OK: {ok_count} rows, KO: {ko_count} rows")

    return validation_ok, validation_ko

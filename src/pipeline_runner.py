import argparse
import sys
from typing import Dict

from pyspark.sql import DataFrame, SparkSession

from utils.spark_session import get_spark_session
from utils.metadata_loader import load_metadata, get_dataflow
from utils.logger import get_logger
from source_reader import read_source
from validator import validate
from transformer import apply_transformations
from sink_writer import write_sink

logger = get_logger(__name__)


def run_pipeline(metadata_path: str, dataflow_name: str) -> None:
    logger.info(f"Running pipeline '{dataflow_name}'")

    metadata: dict = load_metadata(metadata_path)
    dataflow: dict = get_dataflow(metadata, dataflow_name)
    spark: SparkSession = get_spark_session(app_name=dataflow_name)
    logger.info(f"Spark session started - master: {spark.sparkContext.master}")

    dataframes: Dict[str, DataFrame] = {}

    # ingest
    for source_config in dataflow["sources"]: #read all sources into a dataframe
        dataframes[source_config["name"]] = read_source(spark, source_config)

    # transform
    for transformation in dataflow["transformations"]:
        transformation_type: str = transformation["type"]
        input_name: str = transformation["params"]["input"]

        if transformation_type == "validate_fields":
            logger.info(f"[validate] Applying '{transformation['name']}' on '{input_name}'")
            ok_df, ko_df = validate(dataframes[input_name], transformation)
            dataframes["validation_ok"] = ok_df
            dataframes["validation_ko"] = ko_df

        elif transformation_type == "add_fields":
            logger.info(f"[transform] Applying '{transformation['name']}' on '{input_name}'")
            dataframes[transformation["name"]] = apply_transformations(dataframes[input_name], transformation)
    # write
    for sink_config in dataflow["sinks"]:
        sink_input: str = sink_config["input"]
        if sink_input not in dataframes:
            raise KeyError(
                f"Sink '{sink_config['name']}' references input '{sink_input}' "
                f"which does not exist. Available: {list(dataframes.keys())}"
            )
        write_sink(dataframes[sink_input], sink_config)

    logger.info(f"Pipeline '{dataflow_name}' completed successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motor insurance pipeline runner")
    parser.add_argument("--metadata", required=True, help="Path to the pipeline metadata JSON file")
    parser.add_argument("--dataflow", default="motor-ingestion", help="Name of the dataflow to run")
    args = parser.parse_args()

    try:
        run_pipeline(metadata_path=args.metadata, dataflow_name=args.dataflow)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        get_spark_session().stop()

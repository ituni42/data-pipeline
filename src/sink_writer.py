from typing import List

from pyspark.sql import DataFrame

from utils.logger import get_logger

logger = get_logger(__name__)


def write_sink(df: DataFrame, sink_config: dict) -> None:
    name: str = sink_config["name"]
    paths: List[str] = sink_config["paths"]
    fmt: str = sink_config["format"].lower()
    save_mode: str = sink_config["saveMode"].lower()

    if save_mode not in ("overwrite", "append"):
        raise ValueError(f"Unsupported saveMode: '{save_mode}'. Supported: overwrite, append")

    for path in paths:
        logger.info(f"Writing sink '{name}' to '{path}' as {fmt.upper()} (mode: {save_mode})")

        writer = df.write.mode(save_mode)

        if fmt == "json":
            writer.json(path)
        elif fmt == "csv":
            writer.option("header", "true").csv(path) # include column names in CSV output
        else:
            raise ValueError(f"Unsupported sink format: '{fmt}'. Supported: json, csv")

        logger.info(f"Sink '{name}' written successfully to '{path}'")

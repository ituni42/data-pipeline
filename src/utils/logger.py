import logging
import os


def get_logger(name: str) -> logging.Logger:
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    logger: logging.Logger = logging.getLogger(name)

    if not logger.handlers:  # avoid duplicate handlers on repeated calls
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger

import logging
import sys


def configure_logging() -> None:
    """
    Configure the global SPARKS logging system.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for a SPARKS component.
    """

    return logging.getLogger(name)
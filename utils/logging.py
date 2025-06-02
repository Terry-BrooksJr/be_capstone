import os
import sys

from loguru import logger


def setup_loguru(log_dir="logs"):
    """Configures the Loguru logger for both console and file output.

    This function sets up logging to display messages in the console and to write logs to a file in the specified directory.

    Args:
        log_dir (str): The directory where log files will be stored. Defaults to "logs".

    Returns:
        None
    """
    logger.remove()
    # Console
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    # File
    os.makedirs(log_dir, exist_ok=True)
    logger.add(
        os.path.join(log_dir, "info.log"),
        format="{time} {level} {message}",
        level="DEBUG",
        enqueue=True,
    )

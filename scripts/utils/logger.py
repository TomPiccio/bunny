from logging.handlers import RotatingFileHandler
import coloredlogs
import logging
import os

def setup_logger(log_directory="logs"):
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger("BunnyLog")
    if logger.handlers:  # prevent re-adding handlers
        return logger

    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(
        os.path.join(log_directory, "app.log"), maxBytes=1_000_000, backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    coloredlogs.install(level='DEBUG', logger=logger)
    logger.propagate = False

    return logger

import logging


def createLogger(className: str) -> logging.Logger:
    logger = logging.getLogger(className)
    return logger

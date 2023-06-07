import logging


def create_logger(class_name: str) -> logging.Logger:
    logger = logging.getLogger(class_name)
    return logger


def set_logging_config(
    log_level: str = "INFO",
    filename: str | None = None,
    filemode: str = "w",
) -> None:
    """Set logging configuration

    Parameters
    ----------
    log_level : str
        Log level, defaults to INFO
    filename : str, optional
        Log filename, defaults to None

    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        filename=filename,
        filemode=filemode,
        encoding="utf-8",
    )

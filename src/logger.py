import logging


def get_logger(name: str, log_file: str = 'app.log', level: int = logging.DEBUG) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name (str): Name of the logger.
        log_file (str): File to log messages to.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove all existing handlers (don't want to print to console)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger

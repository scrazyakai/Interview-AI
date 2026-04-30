import logging

ACCESS_LOGGER_NAME = "app.access"
EXCEPTION_LOGGER_NAME = "app.exception"


def _get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


def get_logger(module_name: str | None = None) -> logging.Logger:
    return _get_logger(module_name or "app")


def get_access_logger(module_name: str | None = None) -> logging.Logger:
    return _get_logger(module_name or ACCESS_LOGGER_NAME)


def get_exception_logger(module_name: str | None = None) -> logging.Logger:
    return _get_logger(module_name or EXCEPTION_LOGGER_NAME)

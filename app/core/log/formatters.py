import logging


DEFAULT_TEXT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
EXCEPTION_TEXT_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s | "
    "%(pathname)s:%(lineno)d"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def build_text_formatter() -> logging.Formatter:
    return logging.Formatter(DEFAULT_TEXT_FORMAT, datefmt=DATE_FORMAT)


def build_exception_formatter() -> logging.Formatter:
    return logging.Formatter(EXCEPTION_TEXT_FORMAT, datefmt=DATE_FORMAT)

import logging
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.log.formatters import build_exception_formatter, build_text_formatter

_LOGGING_CONFIGURED = False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_log_dir(log_dir: Path | None = None) -> Path:
    preferred = log_dir or (_repo_root() / "logs")
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        return preferred
    except PermissionError:
        fallback = Path(tempfile.gettempdir()) / "interview-ai-logs"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _build_console_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(build_text_formatter())
    return handler


def _build_error_file_handler(log_dir: Path) -> logging.Handler:
    handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
        delay=True,
    )
    handler.setLevel(logging.ERROR)
    handler.setFormatter(build_exception_formatter())
    return handler


def _reset_logger(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def _configure_named_logger(
    name: str,
    *,
    level: int,
    handlers: list[logging.Handler],
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    _reset_logger(logger)
    for handler in handlers:
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def configure_logging(log_dir: Path | None = None) -> None:
    global _LOGGING_CONFIGURED

    target_log_dir = _resolve_log_dir(log_dir)
    console_handler = _build_console_handler()
    error_file_handler = _build_error_file_handler(target_log_dir)
    shared_handlers = [console_handler, error_file_handler]

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    _reset_logger(root_logger)
    for handler in shared_handlers:
        root_logger.addHandler(handler)

    _configure_named_logger("app", level=logging.INFO, handlers=shared_handlers)
    _configure_named_logger("sqlalchemy.engine", level=logging.INFO, handlers=shared_handlers)
    _configure_named_logger("sqlalchemy.engine.Engine", level=logging.INFO, handlers=shared_handlers)
    _configure_named_logger("sqlalchemy.pool", level=logging.WARNING, handlers=shared_handlers)

    _LOGGING_CONFIGURED = True


def is_logging_configured() -> bool:
    return _LOGGING_CONFIGURED

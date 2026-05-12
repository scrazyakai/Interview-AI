import logging
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


class LogSystemTests(unittest.TestCase):
    def test_configure_logging_writes_exception_log_file(self) -> None:
        from app.core.log import configure_logging, get_exception_logger

        log_dir = Path(tempfile.mkdtemp(dir=Path.cwd()))
        try:
            configure_logging(log_dir=log_dir)
            logger = get_exception_logger()
            logger.error("exception-log-test")

            for handler in logger.handlers:
                handler.flush()

            error_log = log_dir / "error.log"
            self.assertTrue(error_log.exists())
            self.assertIn("exception-log-test", error_log.read_text(encoding="utf-8"))
        finally:
            logging.shutdown()
            shutil.rmtree(log_dir, ignore_errors=True)

    def test_access_log_middleware_records_request_summary(self) -> None:
        from app.core.log import AccessLogMiddleware, get_access_logger

        app = FastAPI()
        app.add_middleware(AccessLogMiddleware)

        @app.get("/ping")
        async def ping() -> dict[str, str]:
            return {"ok": "true"}

        logger = get_access_logger()
        records: list[logging.LogRecord] = []

        class ListHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record)

        handler = ListHandler()
        original_handlers = logger.handlers[:]
        original_propagate = logger.propagate
        logger.handlers = [handler]
        logger.propagate = False

        try:
            client = TestClient(app)
            response = client.get("/ping")
        finally:
            logger.handlers = original_handlers
            logger.propagate = original_propagate

        self.assertEqual(response.status_code, 200)
        self.assertTrue(records)
        self.assertIn("GET", records[0].getMessage())
        self.assertIn("/ping", records[0].getMessage())
        self.assertIn("200", records[0].getMessage())

    def test_app_and_sqlalchemy_loggers_use_stdout_handlers_only(self) -> None:
        from app.core.log import configure_logging, get_logger

        log_dir = Path(tempfile.mkdtemp(dir=Path.cwd()))
        try:
            configure_logging(log_dir=log_dir)

            app_logger = get_logger("app.services.auth_service")
            sqlalchemy_logger = logging.getLogger("sqlalchemy.engine.Engine")

            for logger in (app_logger, sqlalchemy_logger):
                self.assertFalse(logger.propagate)
                stream_handlers = [
                    handler
                    for handler in logger.handlers
                    if isinstance(handler, logging.StreamHandler)
                ]
                self.assertTrue(stream_handlers)
                self.assertTrue(any(handler.stream is sys.stdout for handler in stream_handlers))
                self.assertFalse(any(handler.stream is sys.stderr for handler in stream_handlers))
        finally:
            logging.shutdown()
            shutil.rmtree(log_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

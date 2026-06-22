"""Structured JSON logging for the SupportBot backend.

Configures a named logger 'supportbot' that emits JSON-formatted log
records to stdout. This makes logs parseable by cloud log aggregators
(Render, Datadog, CloudWatch, etc.).

Usage in any module:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("event_name", extra={"key": "value"})
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON for cloud log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        """Convert a LogRecord to a JSON string."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        # Merge extra fields from record.__dict__
        reserved = set(logging.LogRecord(
            "", 0, "", 0, "", None, None
        ).__dict__.keys()) | {"message", "asctime"}
        for key, value in record.__dict__.items():
            if key not in reserved and not key.startswith("_"):
                log_data[key] = value
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, default=str)


def get_logger(name: str = "supportbot") -> logging.Logger:
    """Return a configured logger with JSON output to stdout.

    Args:
        name: Logger name (use __name__ in modules).

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger

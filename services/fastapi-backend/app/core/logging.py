"""
Datadog Logging Configuration with APM Trace Correlation.

This module configures structured JSON logging with automatic trace correlation
for Datadog APM. When DD_LOGS_INJECTION=true, ddtrace automatically injects
trace_id and span_id into log records.

Reference:
- https://docs.datadoghq.com/logs/log_collection/python/
- https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/
"""

import logging
import sys
from typing import Any

try:
    from pythonjsonlogger import jsonlogger

    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False


class DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes Datadog trace correlation fields.

    Datadog trace fields (automatically injected by ddtrace when DD_LOGS_INJECTION=true):
    - dd.trace_id: Trace ID for correlation
    - dd.span_id: Span ID for correlation
    - dd.env: Environment (e.g., dev, prod)
    - dd.service: Service name
    - dd.version: Service version
    """

    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        """
        Add custom fields to the log record.

        Args:
            log_record: The dictionary to be logged
            record: The LogRecord instance
            message_dict: Dictionary of message components
        """
        super().add_fields(log_record, record, message_dict)

        # Ensure standard fields are present
        if not log_record.get("timestamp"):
            log_record["timestamp"] = self.formatTime(record, self.datefmt)

        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add source location
        log_record["filename"] = record.filename
        log_record["lineno"] = record.lineno

        # Datadog trace correlation fields are automatically added by ddtrace
        # when DD_LOGS_INJECTION=true, no manual extraction needed


def configure_logging(
    level: str = "INFO",
    json_logs: bool = True,
    service_name: str = "vote-extractor",
) -> None:
    """
    Configure application logging with Datadog trace correlation.

    This function sets up structured JSON logging (if available) with automatic
    trace correlation via ddtrace. When DD_LOGS_INJECTION=true, trace_id and
    span_id are automatically injected into log records.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to use JSON formatting (recommended for Datadog)
        service_name: Service name for logging context

    Example:
        >>> from app.core.logging import configure_logging
        >>> configure_logging(level="INFO", json_logs=True)
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Test log with trace correlation")

    Environment Variables:
        DD_LOGS_INJECTION: Set to "true" to enable automatic trace injection
        DD_SERVICE: Service name (used by ddtrace)
        DD_ENV: Environment name (used by ddtrace)
        DD_VERSION: Service version (used by ddtrace)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Configure formatter
    if json_logs and JSON_LOGGER_AVAILABLE:
        # JSON formatter with Datadog trace correlation fields
        # Format string includes placeholders for ddtrace-injected fields
        formatter = DatadogJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s "
            "%(dd.env)s %(dd.service)s %(dd.version)s "
            "%(dd.trace_id)s %(dd.span_id)s",
            rename_fields={
                "levelname": "level",
                "name": "logger",
                "asctime": "timestamp",
            },
        )
        console_handler.setFormatter(formatter)
        root_logger.info(
            f"✅ Datadog JSON logging configured for service: {service_name} "
            "(trace correlation enabled via DD_LOGS_INJECTION)"
        )
    else:
        # Fallback to standard formatter with trace fields
        # This format is parseable by Datadog but not as clean as JSON
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] "
            "[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s "
            "dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] - %(message)s"
        )
        console_handler.setFormatter(formatter)
        if not JSON_LOGGER_AVAILABLE:
            root_logger.warning(
                "⚠️ python-json-logger not available, using standard formatter. "
                "Install with: pip install python-json-logger"
            )
        else:
            root_logger.info(f"✅ Datadog logging configured for service: {service_name}")

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Set log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google.auth").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    This is a convenience function that returns a standard Python logger.
    Trace correlation fields are automatically injected by ddtrace when
    DD_LOGS_INJECTION=true.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> from app.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Test log")
    """
    return logging.getLogger(name)


def setup_logging(log_level: str = "info") -> None:
    """
    Setup application logging (backward compatibility wrapper).

    This function wraps configure_logging() for backward compatibility
    with existing code that calls setup_logging().

    Args:
        log_level: Logging level as string (info, debug, warning, error)
    """
    configure_logging(level=log_level.upper(), json_logs=True)

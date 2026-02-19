"""Structlog configuration helpers."""

from __future__ import annotations

import logging
import sys
from typing import Final, cast

import structlog

_LOGGING_CONFIGURED: bool = False
_ALLOWED_LOG_FORMATS: Final[set[str]] = {"pretty", "json"}


def configure_logging(*, log_format: str = "pretty", log_level: str = "INFO") -> None:
    """Configure logging once for the process.

    `log_format` accepts `pretty` (colored console) and `json`.
    """

    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    if log_format not in _ALLOWED_LOG_FORMATS:
        raise ValueError(f"Unsupported log format: {log_format}")

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        stream=sys.stdout,
        format="%(message)s",
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.typing.Processor
    if log_format == "json":
        renderer = structlog.processors.JSONRenderer(sort_keys=True)
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=cast(list[structlog.typing.Processor], [*processors, renderer]),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a typed structlog logger."""

    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))

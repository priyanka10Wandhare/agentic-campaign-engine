import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog


def _rename_event_key(_, __, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Normalize log payload key from `event` to `message`."""

    event_dict["message"] = event_dict.pop("event")
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Set up structured logging for the application."""

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            *shared_processors,
            _rename_event_key,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True,
    )

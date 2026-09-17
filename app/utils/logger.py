"""
Application-wide logging setup.

Every agent and service should call `get_logger(__name__)` rather than
`logging.getLogger` directly, so formatting/handlers stay consistent and
can be changed in one place (e.g. to add a file handler or ship logs to a
monitoring service later).
"""
import logging
import sys

from app.config import settings

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.DEBUG if settings.environment == "development" else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, e.g. get_logger(__name__)."""
    _configure_root_logger()
    return logging.getLogger(name)
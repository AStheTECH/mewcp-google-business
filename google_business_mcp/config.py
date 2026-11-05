"""Configuration for MewCP Google Business MCP Server."""

import logging
import os

SERVER_VERSION = "v1.2.0"
BREAKING_CHANGES: list[dict] = []

SCOPES = [
    "https://www.googleapis.com/auth/business.manage",
]


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        handler.setFormatter(
            jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

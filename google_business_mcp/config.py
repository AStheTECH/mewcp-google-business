"""Configuration for MewCP Google Business MCP Server."""

import logging
import os

SERVER_VERSION = "v1.4.0"
BREAKING_CHANGES: list[dict] = [
    {
        "tool": "update_location_attributes",
        "change": "parameter removed: 'attributes_name' (duplicated 'name')",
        "migration": "Drop 'attributes_name' and pass locations/{locationId}/attributes once as 'name'",
    },
]

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

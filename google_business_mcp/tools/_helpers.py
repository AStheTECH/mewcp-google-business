"""Shared error helpers for all tool modules."""

import json

import pydantic
from fastmcp_credentials import CredentialError
from googleapiclient.errors import HttpError

from ..logging_utils import ToolLogger
from ..schemas import ToolError


def _err(result_class, tlog, code, message, status, retriable=False, retry_after=None):
    tlog.failure(code, message)
    return result_class(
        success=False, statusCode=status, retriable=retriable,
        retry_after_seconds=retry_after,
        error=ToolError(code=code, message=message),
    )


def _handle_request_exc(result_class, tlog, exc):
    if isinstance(exc, HttpError):
        status = exc.resp.status if exc.resp is not None else 500
        message = exc.reason or f"HTTP {status}"
        details = None
        try:
            content = json.loads(exc.content)
            message = content.get("error", {}).get("message", message)
            details = content.get("error", {}).get("details") or None
        except Exception:
            pass
        retriable = status in (429, 500, 502, 503)
        tlog.failure("UPSTREAM_ERROR", f"HTTP {status}")
        return result_class(success=False, statusCode=status, retriable=retriable,
            error=ToolError(code="UPSTREAM_ERROR", message=str(message), details=details))
    # Must precede ValueError — ValidationError subclasses it.
    if isinstance(exc, pydantic.ValidationError):
        tlog.failure("UPSTREAM_ERROR", str(exc))  # detail stays in the log
        return result_class(success=False, statusCode=502, retriable=False,
            error=ToolError(code="UPSTREAM_ERROR",
                            message="Upstream response did not match the expected schema"))
    # googleapiclient raises TypeError for bad params (resource-name pattern, unknown kwarg).
    if isinstance(exc, TypeError):
        tlog.failure("VALIDATION_ERROR", str(exc))
        return result_class(success=False, statusCode=400, retriable=False,
            error=ToolError(code="VALIDATION_ERROR", message=str(exc)))
    # CredentialError subclasses Exception, not ValueError.
    if isinstance(exc, (CredentialError, ValueError)):
        tlog.failure("AUTH_ERROR", str(exc))
        return result_class(success=False, statusCode=401, retriable=False,
            error=ToolError(code="AUTH_ERROR", message=str(exc)))
    tlog.failure("SERVER_ERROR", str(exc))  # log full detail internally
    return result_class(success=False, statusCode=500, retriable=False,
        error=ToolError(code="SERVER_ERROR", message="Unexpected server error"))


def _upstream_err(result_class, tlog, status, data, retry_after=None):
    retriable = status in (429, 500, 502, 503)
    tlog.failure("UPSTREAM_ERROR", f"HTTP {status}")
    msg = data.get("error") or data.get("message") or f"HTTP {status}"
    return result_class(
        success=False, statusCode=status, retriable=retriable,
        retry_after_seconds=retry_after,
        error=ToolError(code="UPSTREAM_ERROR", message=str(msg)),
    )

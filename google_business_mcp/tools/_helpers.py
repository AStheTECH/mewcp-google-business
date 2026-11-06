"""Shared error helpers for all tool modules."""

import json
import re

import httpx
import pydantic
from fastmcp_credentials import CredentialError
from googleapiclient.errors import HttpError

from ..logging_utils import ToolLogger
from ..schemas import ToolError
from ..service import V4HttpError

_SEG = r"[A-Za-z0-9_-]+"
_V4_NAME_FORMS = {
    "account": ("accounts/{accountId}", rf"accounts/{_SEG}"),
    "location": ("accounts/{accountId}/locations/{locationId}", rf"accounts/{_SEG}/locations/{_SEG}"),
    "local_post": (
        "accounts/{accountId}/locations/{locationId}/localPosts/{localPostId}",
        rf"accounts/{_SEG}/locations/{_SEG}/localPosts/{_SEG}",
    ),
    "review": (
        "accounts/{accountId}/locations/{locationId}/reviews/{reviewId}",
        rf"accounts/{_SEG}/locations/{_SEG}/reviews/{_SEG}",
    ),
}


def _err(result_class, tlog, code, message, status, retriable=False, retry_after=None):
    tlog.failure(code, message)
    return result_class(
        success=False, statusCode=status, retriable=retriable,
        retry_after_seconds=retry_after,
        error=ToolError(code=code, message=message),
    )


def _v4_name_error(param: str, value: str, kind: str) -> str | None:
    """Message if `value` is not a v4 resource name of `kind`, else None."""
    form, pattern = _V4_NAME_FORMS[kind]
    if re.fullmatch(pattern, value or ""):
        return None
    hint = " Get accountId from list_accounts." if "/locations/" in form else ""
    return f"{param} must be {form}; got {value!r}.{hint}"


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
    if isinstance(exc, V4HttpError):
        tlog.failure("UPSTREAM_ERROR", f"HTTP {exc.status}")
        return result_class(success=False, statusCode=exc.status,
            retriable=exc.status in (429, 500, 502, 503), retry_after_seconds=exc.retry_after,
            error=ToolError(code="UPSTREAM_ERROR", message=str(exc.message), details=exc.details))
    # TimeoutException subclasses RequestError.
    if isinstance(exc, httpx.TimeoutException):
        tlog.failure("UPSTREAM_ERROR", "upstream timeout")
        return result_class(success=False, statusCode=504, retriable=True,
            error=ToolError(code="UPSTREAM_ERROR", message="Upstream request timed out"))
    if isinstance(exc, httpx.RequestError):
        tlog.failure("UPSTREAM_ERROR", f"transport error: {type(exc).__name__}")
        return result_class(success=False, statusCode=502, retriable=True,
            error=ToolError(code="UPSTREAM_ERROR", message="Could not reach the upstream API"))
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

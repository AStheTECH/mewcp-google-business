"""Upstream API client for MewCP Google Business MCP Server."""

import logging

import httpx
from fastmcp_credentials import get_credentials
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest

logger = logging.getLogger("google-business-mcp.service")


class _DetailedErrorRequest(HttpRequest):
    """Asks Google for detailed error responses (e.g. which required field is missing)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["X-GOOG-API-FORMAT-VERSION"] = "2"


def get_business_information_service():
    """Build and return an authenticated My Business Business Information v1 client."""
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")

    creds = Credentials(token=cred.access_token, scopes=cred.scopes)
    return build("mybusinessbusinessinformation", "v1", credentials=creds, requestBuilder=_DetailedErrorRequest)


def get_performance_service():
    """Build and return an authenticated My Business Business Performance v1 client."""
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")

    creds = Credentials(token=cred.access_token, scopes=cred.scopes)
    return build("businessprofileperformance", "v1", credentials=creds, requestBuilder=_DetailedErrorRequest)


def get_account_management_service():
    """Build and return an authenticated My Business Account Management v1 client."""
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")

    creds = Credentials(token=cred.access_token, scopes=cred.scopes)
    return build("mybusinessaccountmanagement", "v1", credentials=creds, requestBuilder=_DetailedErrorRequest)


# Google My Business API v4 (local posts, reviews): no discovery doc, so plain httpx.
V4_BASE_URL = "https://mybusiness.googleapis.com/v4/"
_v4_client = httpx.Client(base_url=V4_BASE_URL, timeout=30.0)


class V4HttpError(Exception):
    """Non-2xx response from the v4 API."""

    def __init__(self, status: int, message: str, details=None, retry_after: int | None = None):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.message = message
        self.details = details
        self.retry_after = retry_after


def v4_request(method: str, path: str, *, params: dict | None = None, json: dict | None = None) -> dict:
    """Call a v4 endpoint; `path` is relative to V4_BASE_URL. Raises V4HttpError on non-2xx."""
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")

    resp = _v4_client.request(
        method, path,
        params={k: v for k, v in (params or {}).items() if v is not None} or None,
        json=json,
        headers={"Authorization": f"Bearer {cred.access_token}", "X-GOOG-API-FORMAT-VERSION": "2"},
    )
    if resp.is_success:
        if not resp.content:
            return {}
        try:
            return resp.json()
        except ValueError:
            raise V4HttpError(502, "Upstream returned a non-JSON response") from None

    message, details = resp.reason_phrase or f"HTTP {resp.status_code}", None
    try:
        err = resp.json().get("error", {})
        if isinstance(err, dict):
            message = err.get("message") or message
            details = err.get("details") or None
    except (ValueError, AttributeError):
        pass  # non-JSON error page
    retry_after = resp.headers.get("Retry-After")
    raise V4HttpError(
        resp.status_code, message, details,
        int(retry_after) if retry_after and retry_after.isdigit() else None,
    )

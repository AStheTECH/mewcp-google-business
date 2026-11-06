"""Upstream API client for MewCP Google Business MCP Server."""

import logging

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

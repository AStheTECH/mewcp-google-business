import logging
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .schemas import OAuthTokenData

logger = logging.getLogger("google-business-mcp-server")


def get_token_data(oauth_token: OAuthTokenData) -> dict[str, Any]:
    return {
        "token": oauth_token.get("token"),
        "refresh_token": oauth_token.get("refresh_token"),
        "token_uri": oauth_token.get("token_uri") or "https://oauth2.googleapis.com/token",
        "client_id": oauth_token.get("client_id"),
        "client_secret": oauth_token.get("client_secret"),
        "scopes": oauth_token.get("scopes"),
    }


def get_service(oauth_token: OAuthTokenData):
    """Build and return an authenticated My Business API client."""
    auth_data = get_token_data(oauth_token)
    logger.info("Creating Google Business API service with provided OAuth token")
    creds = Credentials(**auth_data)

    # My Business Account Management (accounts, locations)
    mybusiness = build(
        "mybusinessaccountmanagement", "v1", credentials=creds
    )
    logger.info("Google Business API service created successfully")
    return mybusiness


def get_business_info_service(oauth_token: OAuthTokenData):
    """Build and return an authenticated My Business Business Information client."""
    auth_data = get_token_data(oauth_token)
    creds = Credentials(**auth_data)
    return build("mybusinessbusinessinformation", "v1", credentials=creds)


def get_mybusiness_service(oauth_token: OAuthTokenData):
    """Build and return the legacy My Business v4 client (reviews, posts, insights)."""
    auth_data = get_token_data(oauth_token)
    creds = Credentials(**auth_data)
    return build("mybusiness", "v4", credentials=creds)

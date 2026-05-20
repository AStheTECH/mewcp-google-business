import logging

from fastmcp_credentials import get_credentials
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("google-business-mcp-server")


def get_mybusiness_service():
    """Build and return an authenticated My Business v4 client (reviews, posts, insights)."""
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("No OAuth access token available in credentials")
    logger.info("Creating Google Business API service with provided access token")
    creds = Credentials(token=cred.access_token, scopes=cred.scopes)
    service = build("mybusiness", "v4", credentials=creds)
    logger.info("Google Business API service created successfully")
    return service

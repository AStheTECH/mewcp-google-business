"""MewCP Google Business tool registration."""

from fastmcp import FastMCP

from .locations_tools import register_locations_tools
from .chains_tools import register_chains_tools
from .categories_tools import register_categories_tools
from .attributes_tools import register_attributes_tools
from .google_locations_tools import register_google_locations_tools
from .performance_tools import register_performance_tools
from .accounts_tools import register_accounts_tools
from .local_posts_tools import register_local_posts_tools
from .reviews_tools import register_reviews_tools


def register_tools(mcp: FastMCP) -> None:
    register_locations_tools(mcp)
    register_chains_tools(mcp)
    register_categories_tools(mcp)
    register_attributes_tools(mcp)
    register_google_locations_tools(mcp)
    register_performance_tools(mcp)
    register_accounts_tools(mcp)
    register_local_posts_tools(mcp)
    register_reviews_tools(mcp)

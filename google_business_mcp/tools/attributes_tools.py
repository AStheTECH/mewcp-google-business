"""Attributes group: list_available_attributes"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.attributes import AvailableAttributesData, AvailableAttributesResult
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("google-business-mcp.tools.attributes")


def register_attributes_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_available_attributes",
        description=(
            "Returns the list of attributes that would be available for a location with the "
            "given primary category and country. Provide exactly one of: `parent` (the resource "
            "name of an existing location), OR `category_name` together with `region_code` and "
            "`language_code`. Set `show_all` to true to get metadata for all available attributes "
            "regardless of `parent`/`category_name` — in that case `region_code` and `language_code` "
            "are required. Use `page_token` from a previous response to page through results."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_available_attributes(
        parent: str | None = Field(
            default=None,
            description=(
                "Resource name of the location to look up available attributes for. If set, "
                "category_name, region_code, language_code and show_all are not required and "
                "must not be set. Format: locations/{location_id}."
            ),
        ),
        category_name: str | None = Field(
            default=None,
            description=(
                "The primary category stable ID to find available attributes. Must be of the "
                "format categories/{category_id}. Omit when parent is set."
            ),
        ),
        region_code: str | None = Field(
            default=None,
            description="The ISO 3166-1 alpha-2 country code to find available attributes. "
            "Omit when parent is set.",
        ),
        language_code: str | None = Field(
            default=None,
            description=(
                "The BCP 47 code of language to get attribute display names in. Falls back to "
                "English if unavailable. Omit when parent is set."
            ),
        ),
        show_all: bool | None = Field(
            default=None,
            description=(
                "If true, metadata for all available attributes is returned, disregarding parent "
                "and category_name. region_code and language_code are required when this is true."
            ),
        ),
        page_size: int | None = Field(
            default=None,
            description="How many attributes to include per page. Default is 200, minimum is 1.",
        ),
        page_token: str | None = Field(
            default=None,
            description="If specified, the next page of attribute metadata is retrieved.",
        ),
    ) -> AvailableAttributesResult:
        tlog = ToolLogger(logger, "list_available_attributes")

        if not parent and not category_name:
            return _err(
                AvailableAttributesResult, tlog, "VALIDATION_ERROR",
                "Exactly one of `parent` or `category_name` (with `region_code` and "
                "`language_code`) must be provided.",
                400,
            )

        try:
            svc = service.get_business_information_service()
            resp = svc.attributes().list(
                parent=parent,
                categoryName=category_name,
                regionCode=region_code,
                languageCode=language_code,
                showAll=show_all,
                pageSize=page_size,
                pageToken=page_token,
            ).execute()
            tlog.success()
            return AvailableAttributesResult(success=True, statusCode=200, data=AvailableAttributesData(**resp))
        except Exception as exc:
            return _handle_request_exc(AvailableAttributesResult, tlog, exc)

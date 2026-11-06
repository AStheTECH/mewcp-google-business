"""Categories group: list_categories, batch_get_categories."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.categories import (
    CategoriesData,
    CategoriesResult,
    CategoryListData,
    CategoryListResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("google-business-mcp.tools.categories")


def register_categories_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_categories",
        description=(
            "Returns a list of business categories matched by the front of the category "
            "name (e.g. 'food' matches 'Food Court' but not 'Fast Food Restaurant')."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_categories(
        region_code: str = Field(description="The ISO 3166-1 alpha-2 country code."),
        language_code: str = Field(description="The BCP 47 code of the language."),
        view: str = Field(
            description=(
                "Specifies which parts of the Category resource to return. Values: "
                "`CATEGORY_VIEW_UNSPECIFIED` (equivalent to `BASIC`), `BASIC` (only "
                "`displayName`, `category_id`, `languageCode`), `FULL` (all fields)."
            )
        ),
        filter_: str | None = Field(
            default=None,
            description=(
                "Filter string from the user; the only supported field is `displayName`, "
                "e.g. `filter=displayName=foo`. Quote values that contain spaces: "
                "`displayName=\"software company\"` (an unquoted multi-word value is rejected "
                "with 400). Omit to return all categories."
            ),
        ),
        page_size: int | None = Field(
            default=None,
            description="How many categories to fetch per page. Default is 100, minimum is 1, maximum is 100.",
        ),
        page_token: str | None = Field(
            default=None, description="If specified, fetches the next page of categories."
        ),
    ) -> CategoriesResult:
        tlog = ToolLogger(logger, "list_categories")

        if page_size is not None and (page_size < 1 or page_size > 100):
            return _err(CategoriesResult, tlog, "VALIDATION_ERROR", "page_size must be 1-100", 400)

        try:
            svc = service.get_business_information_service()
            resp = svc.categories().list(
                regionCode=region_code,
                languageCode=language_code,
                filter=filter_,
                pageSize=page_size,
                pageToken=page_token,
                view=view,
            ).execute()
            tlog.success()
            return CategoriesResult(success=True, statusCode=200, data=CategoriesData(**resp))
        except Exception as exc:
            return _handle_request_exc(CategoriesResult, tlog, exc)

    @mcp.tool(
        name="batch_get_categories",
        description=(
            "Returns a list of business categories for the provided language and category "
            "(GConcept) IDs."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def batch_get_categories(
        names: list[str] = Field(
            description=(
                "The GConcept ids the localized category names should be returned for. "
                "Repeat this parameter to request more than one category; at least one "
                "name must be set."
            )
        ),
        language_code: str = Field(
            description="The BCP 47 code of the language that the category names should be returned in."
        ),
        view: str = Field(
            description=(
                "Specifies which parts of the Category resource to return. Values: "
                "`CATEGORY_VIEW_UNSPECIFIED` (equivalent to `BASIC`), `BASIC` (only "
                "`displayName`, `category_id`, `languageCode`), `FULL` (all fields)."
            )
        ),
        region_code: str | None = Field(
            default=None,
            description="The ISO 3166-1 alpha-2 country code used to infer non-standard language. "
            "Omit if not needed.",
        ),
    ) -> CategoryListResult:
        tlog = ToolLogger(logger, "batch_get_categories")

        if not names:
            return _err(CategoryListResult, tlog, "VALIDATION_ERROR", "At least one name must be set", 400)

        try:
            svc = service.get_business_information_service()
            resp = svc.categories().batchGet(
                names=names,
                languageCode=language_code,
                regionCode=region_code,
                view=view,
            ).execute()
            tlog.success()
            return CategoryListResult(success=True, statusCode=200, data=CategoryListData(**resp))
        except Exception as exc:
            return _handle_request_exc(CategoryListResult, tlog, exc)

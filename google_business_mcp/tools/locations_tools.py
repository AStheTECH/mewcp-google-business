"""Locations group: list_locations, create_location, get_location, update_location,
delete_location, get_google_updated_location, get_location_attributes,
update_location_attributes, get_google_updated_location_attributes."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.locations import (
    GoogleUpdatedLocationAttributesGetData,
    GoogleUpdatedLocationAttributesGetResult,
    GoogleUpdatedLocationGetData,
    GoogleUpdatedLocationGetResult,
    LocationAttributesData,
    LocationAttributesGetData,
    LocationAttributesGetResult,
    LocationAttributesUpdateData,
    LocationAttributesUpdateResult,
    LocationCreateData,
    LocationCreateResult,
    LocationData,
    LocationDeleteData,
    LocationDeleteResult,
    LocationGetData,
    LocationGetResult,
    LocationListData,
    LocationListResult,
    LocationUpdateData,
    LocationUpdateResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("google-business-mcp.tools.locations")


def register_locations_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_locations",
        description=(
            "Lists the locations for the specified account, optionally filtered and sorted, "
            "and returns the matching Location objects with pagination info."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_locations(
        parent: str = Field(
            description="The name of the account to fetch locations from, in the form "
            "accounts/{accountId}. Get valid account names from list_accounts. "
            "Use the - wildcard (accounts/-) to include indirectly owned listings "
            "(owned or managed via a group). "
            "If the parent Account is of type PERSONAL, only "
            "directly-owned Locations are returned; "
            "otherwise all accessible locations (direct or indirect) are returned."
        ),
        read_mask: str = Field(
            description="Comma-separated list of fully qualified field names to return. "
            'Example: "user.displayName,photo".'
        ),
        page_size: int | None = Field(
            default=None,
            description="How many locations to fetch per page. Default 10, minimum 1, maximum 100.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Fetches the next page; returned by a previous call when more "
            "locations exist than fit the page size. Omit for the first page.",
        ),
        filter_: str | None = Field(
            default=None,
            description="Filter constraining which locations to return. Empty means no "
            "constraints (all locations, paginated). Syntax: <field><operator><value> with "
            "operator = (token match) or : (substring match); quote string values; combine "
            "restrictions with AND, and use OR only between restrictions on the same field. "
            "Fields: title, categories (category ID without gcid:), phone_numbers.primary_phone "
            "(E.164), storefront_address.region_code, storefront_address.administrative_area, "
            "storefront_address.locality, storefront_address.postal_code, metadata.place_id, "
            "openInfo.status (OPEN, CLOSED_PERMANENTLY), labels (exact, case-sensitive match), "
            "storeCode, and the function distance(latlng, geopoint(<lat>, <lng>))<<distance>. "
            'Example: title:"Bajis".',
        ),
        order_by: str | None = Field(
            default=None,
            description="Comma-separated sort fields (SQL syntax). Default ascending; append "
            '" desc" for descending. Valid fields: title, storeCode. E.g. "title, storeCode desc". '
            "Omit to use Google's default order.",
        ),
    ) -> LocationListResult:
        tlog = ToolLogger(logger, "list_locations")

        if page_size is not None and not (1 <= page_size <= 100):
            return _err(LocationListResult, tlog, "VALIDATION_ERROR",
                "page_size must be between 1 and 100", 400)

        try:
            svc = service.get_business_information_service()
            resp = svc.accounts().locations().list(
                parent=parent, readMask=read_mask, pageSize=page_size,
                pageToken=page_token, filter=filter_, orderBy=order_by,
            ).execute()
            tlog.success()
            return LocationListResult(success=True, statusCode=200, data=LocationListData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocationListResult, tlog, exc)

    @mcp.tool(
        name="create_location",
        description=(
            "Creates a new Location that will be owned by the logged-in user, and returns "
            "the newly created Location. A newly created location is unverified and not "
            "publicly visible on Google Search or Maps until it is verified."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_location(
        parent: str = Field(
            description="The name of the account in which to create this location, in the "
            "form accounts/{accountId}. Get valid account names from list_accounts."
        ),
        location: dict = Field(
            description="Location object to create. Full schema: see get_location. Required "
            "sub-fields: title (and primaryCategory within categories if categories are set). "
            "Google validates storefrontAddress against Business Profile postal-address "
            "requirements, which are stricter than community-sourced Maps data. "
            "regularHours.periods[].openTime / closeTime are TimeOfDay objects, e.g. "
            '{"hours": 9}; "09:00" strings are rejected. categories.primaryCategory.name '
            "accepts both gcid:software_company and categories/gcid:software_company (as "
            "returned by list_categories)."
        ),
        validate_only: bool | None = Field(
            default=None,
            description="If true, validates the request without actually creating the location. "
            "Google recommends calling with validate_only=true first to confirm required fields "
            "are present and the address is properly formatted.",
        ),
        request_id: str | None = Field(
            default=None,
            description="A unique request ID for the server to detect duplicate requests. "
            "UUIDs recommended. Max 50 characters. Omit to skip duplicate detection.",
        ),
    ) -> LocationCreateResult:
        tlog = ToolLogger(logger, "create_location")

        if request_id is not None and len(request_id) > 50:
            return _err(LocationCreateResult, tlog, "VALIDATION_ERROR",
                "request_id must be at most 50 characters", 400)

        try:
            svc = service.get_business_information_service()
            resp = svc.accounts().locations().create(
                parent=parent, requestId=request_id, validateOnly=validate_only, body=location,
            ).execute()
            tlog.success()
            return LocationCreateResult(success=True, statusCode=200, data=LocationCreateData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocationCreateResult, tlog, exc)

    @mcp.tool(
        name="get_location",
        description=(
            "Returns the specified location as last set by the merchant; may not reflect "
            "updates from Google or user-generated content live on Google Maps."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_location(
        name: str = Field(
            description="The name of the location to fetch, in the form locations/{locationId}."
        ),
        read_mask: str = Field(
            description="Read mask specifying which fields to return in the response. "
            'Comma-separated list of fully qualified field names. Example: "title,websiteUri".'
        ),
    ) -> LocationGetResult:
        tlog = ToolLogger(logger, "get_location")
        try:
            svc = service.get_business_information_service()
            resp = svc.locations().get(name=name, readMask=read_mask).execute()
            tlog.success()
            return LocationGetResult(success=True, statusCode=200, data=LocationGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocationGetResult, tlog, exc)

    @mcp.tool(
        name="update_location",
        description=(
            "Updates the specified location's fields per the given update mask, and returns "
            "the updated Location. Only the fields you provide are changed — others keep "
            "their current value. NOTE: this overwrites the current field values — the "
            "original state is not stored after the call. The response includes both the "
            "before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_location(
        location_name: str = Field(
            description="Google identifier for this location, in the form locations/{locationId}."
        ),
        update_mask: str = Field(
            description="The specific fields to update. Comma-separated list of fully "
            "qualified field names."
        ),
        location: dict = Field(description="Location object carrying the updated field values."),
        validate_only: bool | None = Field(
            default=None,
            description="If true, validates the request without actually updating anything; "
            "the returned after is then empty rather than the updated location.",
        ),
    ) -> LocationUpdateResult:
        tlog = ToolLogger(logger, "update_location")
        try:
            svc = service.get_business_information_service()
            before = svc.locations().get(name=location_name, readMask=update_mask).execute()
            after = svc.locations().patch(
                name=location_name, updateMask=update_mask, validateOnly=validate_only, body=location,
            ).execute()
            tlog.success()
            return LocationUpdateResult(
                success=True, statusCode=200,
                data=LocationUpdateData(before=LocationData(**before), after=LocationData(**after)),
            )
        except Exception as exc:
            return _handle_request_exc(LocationUpdateResult, tlog, exc)

    @mcp.tool(
        name="delete_location",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes the location. This action is irreversible — the location "
            "and its data cannot be recovered via this API (the Google Business Profile "
            "website may offer other recovery paths). NEVER call this tool autonomously or "
            "as part of an automated flow. You MUST stop, tell the user exactly what will "
            "be deleted and that it is permanent, and wait for their explicit written "
            "confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_location(
        name: str = Field(
            description="The name of the location to delete, in the form locations/{locationId}."
        ),
    ) -> LocationDeleteResult:
        tlog = ToolLogger(logger, "delete_location")
        try:
            svc = service.get_business_information_service()
            svc.locations().delete(name=name).execute()
            tlog.success()
            return LocationDeleteResult(success=True, statusCode=200, data=LocationDeleteData())
        except Exception as exc:
            return _handle_request_exc(LocationDeleteResult, tlog, exc)

    @mcp.tool(
        name="get_google_updated_location",
        description=(
            "Returns the specified location as it appears live on Google Maps and Search, "
            "which may differ from the merchant's version, along with masks of what Google "
            "changed and what's still pending."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_google_updated_location(
        name: str = Field(
            description="The name of the location to fetch, in the form locations/{locationId}."
        ),
        read_mask: str = Field(
            description="Comma-separated list of fully qualified field names to return."
        ),
    ) -> GoogleUpdatedLocationGetResult:
        tlog = ToolLogger(logger, "get_google_updated_location")
        try:
            svc = service.get_business_information_service()
            resp = svc.locations().getGoogleUpdated(name=name, readMask=read_mask).execute()
            tlog.success()
            return GoogleUpdatedLocationGetResult(
                success=True, statusCode=200, data=GoogleUpdatedLocationGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(GoogleUpdatedLocationGetResult, tlog, exc)

    @mcp.tool(
        name="get_location_attributes",
        description="Retrieves attributes for a location as last set by the merchant.",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_location_attributes(
        name: str = Field(
            description="Google identifier for this location, in the form "
            "locations/{locationId}/attributes."
        ),
    ) -> LocationAttributesGetResult:
        tlog = ToolLogger(logger, "get_location_attributes")
        try:
            svc = service.get_business_information_service()
            resp = svc.locations().getAttributes(name=name).execute()
            tlog.success()
            return LocationAttributesGetResult(
                success=True, statusCode=200, data=LocationAttributesGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocationAttributesGetResult, tlog, exc)

    @mcp.tool(
        name="update_location_attributes",
        description=(
            "Updates attributes for a given location per the given attribute mask, and "
            "returns the updated Attributes. Only the fields you provide are changed — "
            "others keep their current value. NOTE: this overwrites the current field "
            "values — the original state is not stored after the call. The response "
            "includes both the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_location_attributes(
        name: str = Field(
            description="Google identifier for this location, in the form "
            "locations/{locationId}/attributes. Used for both the request path and the "
            "request body's name, which carry the same value, so it is supplied only once."
        ),
        attribute_mask: str = Field(
            description="Comma-separated attribute names (as attributes/{attribute}) to update. "
            "Updates: every attribute you want updated must be in both attributes and "
            "attribute_mask; attributes not in attribute_mask are ignored. Deletes: to delete "
            "an attribute, put it in attribute_mask with no matching entry in attributes; to "
            "delete all attributes, add all applicable attributes to attribute_mask with an "
            "empty attributes list."
        ),
        attributes: list[dict] | None = Field(
            default=None,
            description="The attributes to set (each with name, valueType, values, "
            "repeatedEnumValue, uriValues). May be empty when deleting all attributes via "
            "attributeMask.",
        ),
    ) -> LocationAttributesUpdateResult:
        tlog = ToolLogger(logger, "update_location_attributes")
        try:
            svc = service.get_business_information_service()
            before = svc.locations().getAttributes(name=name).execute()
            after = svc.locations().updateAttributes(
                name=name, attributeMask=attribute_mask,
                body={"name": name, "attributes": attributes or []},
            ).execute()
            tlog.success()
            return LocationAttributesUpdateResult(
                success=True, statusCode=200,
                data=LocationAttributesUpdateData(
                    before=LocationAttributesData(**before),
                    after=LocationAttributesData(**after),
                ),
            )
        except Exception as exc:
            return _handle_request_exc(LocationAttributesUpdateResult, tlog, exc)

    @mcp.tool(
        name="get_google_updated_location_attributes",
        description=(
            "Retrieves attributes for a location as they appear live on Google Maps and "
            "Search, which may differ from the merchant's version."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_google_updated_location_attributes(
        name: str = Field(
            description="Google identifier for this location, in the form "
            "locations/{locationId}/attributes."
        ),
    ) -> GoogleUpdatedLocationAttributesGetResult:
        tlog = ToolLogger(logger, "get_google_updated_location_attributes")
        try:
            svc = service.get_business_information_service()
            resp = svc.locations().attributes().getGoogleUpdated(name=name).execute()
            tlog.success()
            return GoogleUpdatedLocationAttributesGetResult(
                success=True, statusCode=200, data=GoogleUpdatedLocationAttributesGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(GoogleUpdatedLocationAttributesGetResult, tlog, exc)

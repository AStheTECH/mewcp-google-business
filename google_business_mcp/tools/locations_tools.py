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
            "accounts/{accountId}. If the parent Account is of type PERSONAL, only "
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
            "locations exist than fit the page size.",
        ),
        filter_: str | None = Field(
            default=None,
            description="Filter constraining which locations to return. Empty means no "
            'constraints (all locations, paginated). See Google\'s "Work with Location Data" '
            "guide for valid fields.",
        ),
        order_by: str | None = Field(
            default=None,
            description="Comma-separated sort fields (SQL syntax). Default ascending; append "
            '" desc" for descending. Valid fields: title, storeCode. E.g. "title, storeCode desc".',
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
            "the newly created Location."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_location(
        parent: str = Field(
            description="The name of the account in which to create this location, in the "
            "form accounts/{accountId}."
        ),
        location: dict = Field(
            description="Location object to create. Required sub-fields: title (and "
            "primaryCategory within categories if categories are set)."
        ),
        validate_only: bool | None = Field(
            default=None,
            description="If true, validates the request without actually creating the location.",
        ),
        request_id: str | None = Field(
            default=None,
            description="A unique request ID for the server to detect duplicate requests. "
            "UUIDs recommended. Max 50 characters.",
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
            description="If true, validates the request without actually updating; response "
            "is empty unless there are validation errors.",
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
        attributes_name: str = Field(
            description="Google identifier for this location, in the form "
            "locations/{locationId}/attributes."
        ),
        attribute_mask: str = Field(
            description="Attribute names (as attributes/{attribute}) to update. Every "
            "attribute you want updated must be in both attributes and attributeMask. To "
            "delete an attribute, put it in attributeMask with no matching entry in attributes."
        ),
        name: str = Field(
            description="Google identifier for this location, in the form "
            "locations/{locationId}/attributes (body field, same value as attributes.name)."
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
            before = svc.locations().getAttributes(name=attributes_name).execute()
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

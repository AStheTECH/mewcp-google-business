"""Schemas for the locations tool group: list_locations, create_location, get_location,
update_location, delete_location, get_google_updated_location, get_location_attributes,
update_location_attributes, get_google_updated_location_attributes."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class LocationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    languageCode: str | None = None
    storeCode: str | None = None
    title: str | None = None
    phoneNumbers: dict | None = None
    categories: dict | None = None
    storefrontAddress: dict | None = None
    websiteUri: str | None = None
    regularHours: dict | None = None
    specialHours: dict | None = None
    serviceArea: dict | None = None
    labels: list | None = None
    adWordsLocationExtensions: dict | None = None
    latlng: dict | None = None
    openInfo: dict | None = None
    metadata: dict | None = None
    profile: dict | None = None
    relationshipData: dict | None = None
    moreHours: list | None = None
    serviceItems: list | None = None


class LocationListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    locations: list[LocationData] = Field(default_factory=list)
    nextPageToken: str | None = None
    totalSize: int | None = None


class LocationListResult(ToolResult):
    data: LocationListData | None = None


class LocationCreateData(LocationData):
    """Newly created Location — same shape as LocationData."""


class LocationCreateResult(ToolResult):
    data: LocationCreateData | None = None


class LocationGetData(LocationData):
    """Fetched Location — same shape as LocationData."""


class LocationGetResult(ToolResult):
    data: LocationGetData | None = None


class LocationUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: LocationData
    after: LocationData


class LocationUpdateResult(ToolResult):
    data: LocationUpdateData | None = None


class LocationDeleteData(BaseModel):
    model_config = ConfigDict(extra="allow")


class LocationDeleteResult(ToolResult):
    data: LocationDeleteData | None = None


class GoogleUpdatedLocationGetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    location: dict
    diffMask: str | None = None
    pendingMask: str | None = None


class GoogleUpdatedLocationGetResult(ToolResult):
    data: GoogleUpdatedLocationGetData | None = None


class AttributeData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    valueType: str | None = None
    values: list | None = None
    repeatedEnumValue: dict | None = None
    uriValues: list | None = None


class LocationAttributesData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    attributes: list[AttributeData] = Field(default_factory=list)


class LocationAttributesGetData(LocationAttributesData):
    """Fetched location attributes — same shape as LocationAttributesData."""


class LocationAttributesGetResult(ToolResult):
    data: LocationAttributesGetData | None = None


class LocationAttributesUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: LocationAttributesData
    after: LocationAttributesData


class LocationAttributesUpdateResult(ToolResult):
    data: LocationAttributesUpdateData | None = None


class GoogleUpdatedLocationAttributesGetData(LocationAttributesData):
    """Live Google-side location attributes — same shape as LocationAttributesData."""


class GoogleUpdatedLocationAttributesGetResult(ToolResult):
    data: GoogleUpdatedLocationAttributesGetData | None = None

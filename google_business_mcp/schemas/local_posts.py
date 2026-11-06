"""Schemas for the local_posts tool group: list_local_posts, get_local_post, create_local_post,
update_local_post, delete_local_post, report_local_post_insights."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class LocalPostData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(
        default=None,
        description="accounts/{accountId}/locations/{locationId}/localPosts/{localPostId}.",
    )
    languageCode: str | None = None
    summary: str | None = None
    callToAction: dict | None = Field(default=None, description="{actionType, url}.")
    createTime: str | None = None
    updateTime: str | None = None
    event: dict | None = Field(default=None, description="{title, schedule: TimeInterval}.")
    state: str | None = Field(
        default=None,
        description="LOCAL_POST_STATE_UNSPECIFIED, REJECTED, LIVE, or PROCESSING.",
    )
    media: list[dict] | None = None
    searchUrl: str | None = None
    topicType: str | None = Field(default=None, description="STANDARD, EVENT, OFFER, or ALERT.")
    alertType: str | None = None
    offer: dict | None = Field(default=None, description="{couponCode, redeemOnlineUrl, termsConditions}.")


class LocalPostListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    localPosts: list[LocalPostData] = Field(default_factory=list)
    nextPageToken: str | None = None


class LocalPostListResult(ToolResult):
    data: LocalPostListData | None = None


class LocalPostGetData(LocalPostData):
    """Fetched LocalPost — same shape as LocalPostData."""


class LocalPostGetResult(ToolResult):
    data: LocalPostGetData | None = None


class LocalPostCreateData(LocalPostData):
    """Newly created LocalPost — same shape as LocalPostData."""


class LocalPostCreateResult(ToolResult):
    data: LocalPostCreateData | None = None


class LocalPostUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: LocalPostData
    after: LocalPostData


class LocalPostUpdateResult(ToolResult):
    data: LocalPostUpdateData | None = None


class LocalPostDeleteData(BaseModel):
    model_config = ConfigDict(extra="allow")


class LocalPostDeleteResult(ToolResult):
    data: LocalPostDeleteData | None = None


class LocalPostMetricsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    localPostName: str | None = None
    metricValues: list[dict] = Field(
        default_factory=list,
        description="MetricValue objects: {metric, totalValue, dimensionalValues}.",
    )


class LocalPostInsightsData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    localPostMetrics: list[LocalPostMetricsData] = Field(default_factory=list)
    timeZone: str | None = Field(default=None, description="IANA time zone ID of the location.")


class LocalPostInsightsResult(ToolResult):
    data: LocalPostInsightsData | None = None

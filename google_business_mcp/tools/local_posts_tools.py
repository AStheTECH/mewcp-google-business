"""Local posts group (Google My Business API v4): list_local_posts, get_local_post,
create_local_post, update_local_post, delete_local_post, report_local_post_insights."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.local_posts import (
    LocalPostCreateData,
    LocalPostCreateResult,
    LocalPostData,
    LocalPostDeleteData,
    LocalPostDeleteResult,
    LocalPostGetData,
    LocalPostGetResult,
    LocalPostInsightsData,
    LocalPostInsightsResult,
    LocalPostListData,
    LocalPostListResult,
    LocalPostUpdateData,
    LocalPostUpdateResult,
)
from ._helpers import _err, _handle_request_exc, _v4_name_error

logger = logging.getLogger("google-business-mcp.tools.local_posts")


def register_local_posts_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_local_posts",
        description=(
            "Lists the local posts (updates, events, offers) of a location and returns the "
            "LocalPost objects with a next-page token. Takes the v4 location name "
            "accounts/{accountId}/locations/{locationId}, not the locations/{locationId} form "
            "the other location tools use."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_local_posts(
        parent: str = Field(
            description="The location whose local posts to list, in the form "
            "accounts/{accountId}/locations/{locationId}."
        ),
        page_size: int | None = Field(
            default=None,
            description="How many local posts to return per page, 1 to 100. Omit to use the default of 20.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Token from a previous call's nextPageToken to fetch the next page. "
            "Omit for the first page.",
        ),
    ) -> LocalPostListResult:
        tlog = ToolLogger(logger, "list_local_posts")

        if msg := _v4_name_error("parent", parent, "location"):
            return _err(LocalPostListResult, tlog, "VALIDATION_ERROR", msg, 400)
        if page_size is not None and not (1 <= page_size <= 100):
            return _err(LocalPostListResult, tlog, "VALIDATION_ERROR",
                "page_size must be between 1 and 100", 400)

        try:
            resp = service.v4_request(
                "GET", f"{parent}/localPosts",
                params={"pageSize": page_size, "pageToken": page_token},
            )
            tlog.success()
            return LocalPostListResult(success=True, statusCode=200, data=LocalPostListData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocalPostListResult, tlog, exc)

    @mcp.tool(
        name="get_local_post",
        description=(
            "Returns the specified local post, including its summary, topic type, call to "
            "action, event and offer details, media, state (LIVE, PROCESSING, REJECTED) and "
            "Google Search link. Fails with statusCode 404 if the post does not exist."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_local_post(
        name: str = Field(
            description="The local post to fetch, in the form "
            "accounts/{accountId}/locations/{locationId}/localPosts/{localPostId}."
        ),
    ) -> LocalPostGetResult:
        tlog = ToolLogger(logger, "get_local_post")

        if msg := _v4_name_error("name", name, "local_post"):
            return _err(LocalPostGetResult, tlog, "VALIDATION_ERROR", msg, 400)

        try:
            resp = service.v4_request("GET", name)
            tlog.success()
            return LocalPostGetResult(success=True, statusCode=200, data=LocalPostGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocalPostGetResult, tlog, exc)

    @mcp.tool(
        name="create_local_post",
        description=(
            "Creates a local post on the specified location and returns the new LocalPost. "
            "EVENT and OFFER posts require event (title and a full schedule), offer should "
            "only be set on OFFER posts, call_to_action is ignored on OFFER posts, and ALERT "
            "posts are not always available for authoring."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_local_post(
        parent: str = Field(
            description="The location to post on, in the form "
            "accounts/{accountId}/locations/{locationId}."
        ),
        topic_type: str = Field(
            description="Post type: STANDARD (summary and images), EVENT (adds an event), "
            "OFFER (adds an event and offer details such as a coupon code), or ALERT "
            "(high-priority announcement; not always available)."
        ),
        summary: str | None = Field(
            default=None,
            description="Description/body of the post. Omit for a post without body text.",
        ),
        language_code: str | None = Field(
            default=None,
            description="Language of the post, e.g. en. Omit to leave unset.",
        ),
        call_to_action: dict | None = Field(
            default=None,
            description="Button shown on the post: {\"actionType\": BOOK | ORDER | SHOP | "
            "LEARN_MORE | SIGN_UP | CALL, \"url\": \"https://...\"}. Leave url out for CALL. "
            "GET_OFFER is deprecated — use topic_type OFFER. Ignored for OFFER posts. "
            "Omit for no button.",
        ),
        event: dict | None = Field(
            default=None,
            description="Event details, needed for EVENT and OFFER posts: {\"title\": str, "
            "\"schedule\": {\"startDate\": {\"year\", \"month\", \"day\"}, \"startTime\": "
            "{\"hours\", \"minutes\"}, \"endDate\": {...}, \"endTime\": {...}}}. All four "
            "schedule fields must be set. Omit for STANDARD and ALERT posts.",
        ),
        media: list[dict] | None = Field(
            default=None,
            description="Media items, each {\"mediaFormat\": \"PHOTO\" | \"VIDEO\", "
            "\"sourceUrl\": \"<public URL>\"}; sourceUrl is the only supported data field. "
            "Photos must be at least 250px on the short edge and 10240 bytes. Omit for a "
            "post without media.",
        ),
        alert_type: str | None = Field(
            default=None,
            description="Alert sub-type for ALERT posts, e.g. COVID_19 (supports only summary "
            "and call_to_action). Omit for other topic types.",
        ),
        offer: dict | None = Field(
            default=None,
            description="Offer details for OFFER posts: {\"couponCode\", \"redeemOnlineUrl\", "
            "\"termsConditions\"}, all optional. Omit for other topic types.",
        ),
    ) -> LocalPostCreateResult:
        tlog = ToolLogger(logger, "create_local_post")

        if msg := _v4_name_error("parent", parent, "location"):
            return _err(LocalPostCreateResult, tlog, "VALIDATION_ERROR", msg, 400)

        body = {
            "topicType": topic_type, "summary": summary, "languageCode": language_code,
            "callToAction": call_to_action, "event": event, "media": media,
            "alertType": alert_type, "offer": offer,
        }
        try:
            resp = service.v4_request(
                "POST", f"{parent}/localPosts",
                json={k: v for k, v in body.items() if v is not None},
            )
            tlog.success()
            return LocalPostCreateResult(success=True, statusCode=200, data=LocalPostCreateData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocalPostCreateResult, tlog, exc)

    @mcp.tool(
        name="update_local_post",
        description=(
            "Updates the fields of the specified local post named in the update mask, and "
            "returns the updated LocalPost. Only the fields you provide are changed — others "
            "keep their current value. NOTE: this overwrites the current field values — the "
            "original state is not stored after the call. The response includes both the "
            "before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_local_post(
        name: str = Field(
            description="The local post to update, in the form "
            "accounts/{accountId}/locations/{locationId}/localPosts/{localPostId}."
        ),
        update_mask: str = Field(
            description="Comma-separated list of the fields being updated, e.g. "
            "summary,callToAction. Every field you change must be listed."
        ),
        local_post: dict = Field(
            description="LocalPost object carrying the new values for the fields in "
            "update_mask, e.g. {\"summary\": \"New text\"}. Same field shapes as create_local_post."
        ),
    ) -> LocalPostUpdateResult:
        tlog = ToolLogger(logger, "update_local_post")

        if msg := _v4_name_error("name", name, "local_post"):
            return _err(LocalPostUpdateResult, tlog, "VALIDATION_ERROR", msg, 400)

        try:
            before = service.v4_request("GET", name)
            after = service.v4_request(
                "PATCH", name, params={"updateMask": update_mask}, json=local_post,
            )
            tlog.success()
            return LocalPostUpdateResult(
                success=True, statusCode=200,
                data=LocalPostUpdateData(before=LocalPostData(**before), after=LocalPostData(**after)),
            )
        except Exception as exc:
            return _handle_request_exc(LocalPostUpdateResult, tlog, exc)

    @mcp.tool(
        name="delete_local_post",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes the local post from the location's Business Profile. This "
            "action is irreversible — the post cannot be recovered. NEVER call this tool "
            "autonomously or as part of an automated flow. You MUST stop, tell the user "
            "exactly what will be deleted and that it is permanent, and wait for their "
            "explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_local_post(
        name: str = Field(
            description="The local post to delete, in the form "
            "accounts/{accountId}/locations/{locationId}/localPosts/{localPostId}."
        ),
    ) -> LocalPostDeleteResult:
        tlog = ToolLogger(logger, "delete_local_post")

        if msg := _v4_name_error("name", name, "local_post"):
            return _err(LocalPostDeleteResult, tlog, "VALIDATION_ERROR", msg, 400)

        try:
            service.v4_request("DELETE", name)
            tlog.success()
            return LocalPostDeleteResult(success=True, statusCode=200, data=LocalPostDeleteData())
        except Exception as exc:
            return _handle_request_exc(LocalPostDeleteResult, tlog, exc)

    @mcp.tool(
        name="report_local_post_insights",
        description=(
            "Returns performance metrics (Search views, call-to-action clicks) for up to 100 "
            "local posts of one location, with per-post metric values and the location's time "
            "zone. Time ranges can reach back at most 18 months, and days close to the "
            "request date may still be missing data."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def report_local_post_insights(
        name: str = Field(
            description="The location the posts belong to, in the form "
            "accounts/{accountId}/locations/{locationId}."
        ),
        local_post_names: list[str] = Field(
            description="1 to 100 local post names, each "
            "accounts/{accountId}/locations/{locationId}/localPosts/{localPostId} and "
            "belonging to the location in name."
        ),
        metric_requests: list[dict] | None = Field(
            default=None,
            description="Metrics to return, each {\"metric\": LOCAL_POST_VIEWS_SEARCH | "
            "LOCAL_POST_ACTIONS_CALL_TO_ACTION | ALL, \"options\": [AGGREGATED_TOTAL | "
            "AGGREGATED_DAILY]}. Options default to AGGREGATED_TOTAL. Omit to request no "
            "basic metrics.",
        ),
        start_time: str | None = Field(
            default=None,
            description="Start of the range (inclusive), RFC3339 UTC, e.g. 2026-01-01T00:00:00Z. "
            "Omit to leave the range start unset.",
        ),
        end_time: str | None = Field(
            default=None,
            description="End of the range (exclusive), RFC3339 UTC, e.g. 2026-02-01T00:00:00Z. "
            "Omit to leave the range end unset.",
        ),
    ) -> LocalPostInsightsResult:
        tlog = ToolLogger(logger, "report_local_post_insights")

        if msg := _v4_name_error("name", name, "location"):
            return _err(LocalPostInsightsResult, tlog, "VALIDATION_ERROR", msg, 400)
        if not (1 <= len(local_post_names) <= 100):
            return _err(LocalPostInsightsResult, tlog, "VALIDATION_ERROR",
                "local_post_names must contain between 1 and 100 posts", 400)
        for post in local_post_names:
            if msg := _v4_name_error("local_post_names entry", post, "local_post"):
                return _err(LocalPostInsightsResult, tlog, "VALIDATION_ERROR", msg, 400)
            if not post.startswith(f"{name}/localPosts/"):
                return _err(LocalPostInsightsResult, tlog, "VALIDATION_ERROR",
                    f"local post {post!r} does not belong to location {name!r}", 400)

        body: dict = {"localPostNames": local_post_names}
        basic: dict = {}
        if metric_requests is not None:
            basic["metricRequests"] = metric_requests
        time_range = {k: v for k, v in {"startTime": start_time, "endTime": end_time}.items() if v}
        if time_range:
            basic["timeRange"] = time_range
        if basic:
            body["basicRequest"] = basic

        try:
            resp = service.v4_request("POST", f"{name}/localPosts:reportInsights", json=body)
            tlog.success()
            return LocalPostInsightsResult(
                success=True, statusCode=200, data=LocalPostInsightsData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocalPostInsightsResult, tlog, exc)

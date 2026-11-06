"""Reviews group (Google My Business API v4): list_reviews, get_review, batch_get_reviews,
update_review_reply, delete_review_reply."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.reviews import (
    ReviewBatchGetData,
    ReviewBatchGetResult,
    ReviewGetData,
    ReviewGetResult,
    ReviewListData,
    ReviewListResult,
    ReviewReplyData,
    ReviewReplyDeleteData,
    ReviewReplyDeleteResult,
    ReviewReplyUpdateData,
    ReviewReplyUpdateResult,
)
from ._helpers import _err, _handle_request_exc, _v4_name_error

logger = logging.getLogger("google-business-mcp.tools.reviews")

_ORDER_BY = ("rating", "rating desc", "updateTime desc")


def register_reviews_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_reviews",
        description=(
            "Lists the customer reviews of a verified location and returns the reviews "
            "(reviewer, star rating, comment, owner reply) together with the location's "
            "average rating, total review count and a next-page token. Takes the v4 location "
            "name accounts/{accountId}/locations/{locationId}, not the locations/{locationId} "
            "form the other location tools use; unverified locations fail upstream."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_reviews(
        parent: str = Field(
            description="The location to fetch reviews for, in the form "
            "accounts/{accountId}/locations/{locationId}."
        ),
        page_size: int | None = Field(
            default=None,
            description="How many reviews to fetch per page, 1 to 50. Omit to use the API default.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Token from a previous call's nextPageToken to fetch the next page. "
            "Omit for the first page.",
        ),
        order_by: str | None = Field(
            default=None,
            description="Sort order: rating (ascending), rating desc, or updateTime desc. "
            "Omit to sort by updateTime desc.",
        ),
    ) -> ReviewListResult:
        tlog = ToolLogger(logger, "list_reviews")

        if msg := _v4_name_error("parent", parent, "location"):
            return _err(ReviewListResult, tlog, "VALIDATION_ERROR", msg, 400)
        if page_size is not None and not (1 <= page_size <= 50):
            return _err(ReviewListResult, tlog, "VALIDATION_ERROR",
                "page_size must be between 1 and 50", 400)
        if order_by is not None and order_by not in _ORDER_BY:
            return _err(ReviewListResult, tlog, "VALIDATION_ERROR",
                f"order_by must be one of {', '.join(_ORDER_BY)}", 400)

        try:
            resp = service.v4_request(
                "GET", f"{parent}/reviews",
                params={"pageSize": page_size, "pageToken": page_token, "orderBy": order_by},
            )
            tlog.success()
            return ReviewListResult(success=True, statusCode=200, data=ReviewListData(**resp))
        except Exception as exc:
            return _handle_request_exc(ReviewListResult, tlog, exc)

    @mcp.tool(
        name="get_review",
        description=(
            "Returns the specified review of a verified location, including the reviewer, "
            "star rating, comment, media and the owner's reply text. Google does not return the "
            "reply's reviewReplyState or policyViolation from this endpoint (they come back null); "
            "use list_reviews or batch_get_reviews to see whether a reply is APPROVED, PENDING or "
            "REJECTED. Fails with statusCode 404 if the review does not exist or has been deleted."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_review(
        name: str = Field(
            description="The review to fetch, in the form "
            "accounts/{accountId}/locations/{locationId}/reviews/{reviewId}."
        ),
    ) -> ReviewGetResult:
        tlog = ToolLogger(logger, "get_review")

        if msg := _v4_name_error("name", name, "review"):
            return _err(ReviewGetResult, tlog, "VALIDATION_ERROR", msg, 400)

        try:
            resp = service.v4_request("GET", name)
            tlog.success()
            return ReviewGetResult(success=True, statusCode=200, data=ReviewGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(ReviewGetResult, tlog, exc)

    @mcp.tool(
        name="batch_get_reviews",
        description=(
            "Returns one paginated list of reviews across up to 50 verified locations of an "
            "account, each review paired with its location name, plus a next-page token."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def batch_get_reviews(
        name: str = Field(
            description="The account the locations belong to, in the form accounts/{accountId}."
        ),
        location_names: list[str] = Field(
            description="1 to 50 location names, each accounts/{accountId}/locations/{locationId}."
        ),
        page_size: int | None = Field(
            default=None,
            description="How many reviews to fetch per page. Omit to use the default of 50.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Token from a previous call's nextPageToken to fetch the next page. "
            "Omit for the first page.",
        ),
        order_by: str | None = Field(
            default=None,
            description="Sort order: rating (ascending), rating desc, or updateTime desc; "
            "ascending updateTime is not supported. Omit to sort by updateTime desc.",
        ),
    ) -> ReviewBatchGetResult:
        tlog = ToolLogger(logger, "batch_get_reviews")

        if msg := _v4_name_error("name", name, "account"):
            return _err(ReviewBatchGetResult, tlog, "VALIDATION_ERROR", msg, 400)
        if not (1 <= len(location_names) <= 50):
            return _err(ReviewBatchGetResult, tlog, "VALIDATION_ERROR",
                "location_names must contain between 1 and 50 locations", 400)
        for loc in location_names:
            if msg := _v4_name_error("location_names entry", loc, "location"):
                return _err(ReviewBatchGetResult, tlog, "VALIDATION_ERROR", msg, 400)
        if page_size is not None and page_size < 1:
            return _err(ReviewBatchGetResult, tlog, "VALIDATION_ERROR",
                "page_size must be at least 1", 400)
        if order_by is not None and order_by not in _ORDER_BY:
            return _err(ReviewBatchGetResult, tlog, "VALIDATION_ERROR",
                f"order_by must be one of {', '.join(_ORDER_BY)}", 400)

        body = {
            "locationNames": location_names, "pageSize": page_size,
            "pageToken": page_token, "orderBy": order_by,
        }
        try:
            resp = service.v4_request(
                "POST", f"{name}/locations:batchGetReviews",
                json={k: v for k, v in body.items() if v is not None},
            )
            tlog.success()
            return ReviewBatchGetResult(success=True, statusCode=200, data=ReviewBatchGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(ReviewBatchGetResult, tlog, exc)

    @mcp.tool(
        name="update_review_reply",
        description=(
            "Sets the owner's public reply to the specified review of a verified location, "
            "creating the reply if none exists, and returns the saved reply text and time. The "
            "returned reviewReplyState is null because Google does not report moderation state "
            "here; call list_reviews or batch_get_reviews afterwards to see whether the reply is "
            "APPROVED, PENDING or REJECTED with a policy violation. Google's Business Profile "
            "API policies prohibit automating or triggering review replies without the business "
            "owner's prior specific and express consent, and replies must follow Google's "
            "prohibited and restricted content policies. Read the review first, write a reply "
            "specific to what the reviewer said, show the draft to the user and post it only "
            "once they approve it. Generic or copy-pasted replies across many reviews can be "
            "rejected (e.g. REPETITIVE or GENERIC_QUALITY). NOTE: this overwrites the current "
            "reply — the original state is not stored after the call. The response includes "
            "both the before and after state so you have a full record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_review_reply(
        name: str = Field(
            description="The review to reply to, in the form "
            "accounts/{accountId}/locations/{locationId}/reviews/{reviewId} (without /reply)."
        ),
        comment: str = Field(
            description="The reply text the user approved, plain text with markups, at most "
            "4096 bytes. It appears publicly under the review, so address the points the "
            "reviewer raised rather than a stock thank-you."
        ),
    ) -> ReviewReplyUpdateResult:
        tlog = ToolLogger(logger, "update_review_reply")

        if msg := _v4_name_error("name", name, "review"):
            return _err(ReviewReplyUpdateResult, tlog, "VALIDATION_ERROR", msg, 400)
        if not comment or len(comment.encode("utf-8")) > 4096:
            return _err(ReviewReplyUpdateResult, tlog, "VALIDATION_ERROR",
                "comment must be non-empty and at most 4096 bytes", 400)

        try:
            review = service.v4_request("GET", name)
            after = service.v4_request("PUT", f"{name}/reply", json={"comment": comment})
            before = review.get("reviewReply")
            tlog.success()
            return ReviewReplyUpdateResult(
                success=True, statusCode=200,
                data=ReviewReplyUpdateData(
                    before=ReviewReplyData(**before) if before else None,
                    after=ReviewReplyData(**after),
                ),
            )
        except Exception as exc:
            return _handle_request_exc(ReviewReplyUpdateResult, tlog, exc)

    @mcp.tool(
        name="delete_review_reply",
        description=(
            "DESTRUCTIVE — REQUIRES EXPLICIT USER CONFIRMATION BEFORE CALLING. "
            "Permanently deletes the owner's reply to the specified review of a verified "
            "location; the review itself stays. This action is irreversible — the reply text "
            "cannot be recovered. NEVER call this tool autonomously or as part of an automated "
            "flow. You MUST stop, tell the user exactly what will be deleted and that it is "
            "permanent, and wait for their explicit written confirmation before proceeding."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True),
    )
    def delete_review_reply(
        name: str = Field(
            description="The review whose reply to delete, in the form "
            "accounts/{accountId}/locations/{locationId}/reviews/{reviewId} (without /reply)."
        ),
    ) -> ReviewReplyDeleteResult:
        tlog = ToolLogger(logger, "delete_review_reply")

        if msg := _v4_name_error("name", name, "review"):
            return _err(ReviewReplyDeleteResult, tlog, "VALIDATION_ERROR", msg, 400)

        try:
            service.v4_request("DELETE", f"{name}/reply")
            tlog.success()
            return ReviewReplyDeleteResult(success=True, statusCode=200, data=ReviewReplyDeleteData())
        except Exception as exc:
            return _handle_request_exc(ReviewReplyDeleteResult, tlog, exc)

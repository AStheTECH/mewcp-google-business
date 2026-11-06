"""Schemas for the reviews tool group: list_reviews, get_review, batch_get_reviews,
update_review_reply, delete_review_reply."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class ReviewerData(BaseModel):
    model_config = ConfigDict(extra="allow")

    profilePhotoUrl: str | None = None
    displayName: str | None = None
    isAnonymous: bool | None = None


class ReviewReplyData(BaseModel):
    model_config = ConfigDict(extra="allow")

    comment: str | None = None
    updateTime: str | None = None
    reviewReplyState: str | None = Field(
        default=None,
        description="REVIEW_REPLY_STATE_UNSPECIFIED, PENDING, REJECTED, or APPROVED.",
    )
    policyViolation: str | None = Field(
        default=None, description="Only set when reviewReplyState is REJECTED."
    )


class ReviewData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(
        default=None,
        description="accounts/{accountId}/locations/{locationId}/reviews/{reviewId}.",
    )
    reviewId: str | None = None
    reviewer: ReviewerData | None = None
    starRating: str | None = Field(
        default=None, description="STAR_RATING_UNSPECIFIED, ONE, TWO, THREE, FOUR, or FIVE."
    )
    comment: str | None = None
    createTime: str | None = None
    updateTime: str | None = None
    reviewReply: ReviewReplyData | None = None
    reviewMediaItems: list[dict] | None = Field(
        default=None, description="{thumbnailUrl, thumbnailLabel, videoUrl}."
    )


class ReviewListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    reviews: list[ReviewData] = Field(default_factory=list)
    averageRating: float | None = None
    totalReviewCount: int | None = None
    nextPageToken: str | None = None


class ReviewListResult(ToolResult):
    data: ReviewListData | None = None


class ReviewGetData(ReviewData):
    """Fetched Review — same shape as ReviewData."""


class ReviewGetResult(ToolResult):
    data: ReviewGetData | None = None


class LocationReviewData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(default=None, description="Location resource name.")
    review: ReviewData | None = None


class ReviewBatchGetData(BaseModel):
    model_config = ConfigDict(extra="allow")

    locationReviews: list[LocationReviewData] = Field(default_factory=list)
    nextPageToken: str | None = None


class ReviewBatchGetResult(ToolResult):
    data: ReviewBatchGetData | None = None


class ReviewReplyUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: ReviewReplyData | None = Field(
        default=None, description="Previous reply; null if the review had none."
    )
    after: ReviewReplyData


class ReviewReplyUpdateResult(ToolResult):
    data: ReviewReplyUpdateData | None = None


class ReviewReplyDeleteData(BaseModel):
    model_config = ConfigDict(extra="allow")


class ReviewReplyDeleteResult(ToolResult):
    data: ReviewReplyDeleteData | None = None

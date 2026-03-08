import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .schemas import OAuthTokenData
from .service import get_mybusiness_service
from .config import RATING_MAP

logger = logging.getLogger("google-business-mcp-server")


def register_tools(mcp: FastMCP) -> None:

    # ═══════════════════════════════════════════════════════════
    # 📋 PROFILE TOOLS
    # ═══════════════════════════════════════════════════════════

    @mcp.tool(
        name="list_accounts",
        description="List all Google Business Profile accounts accessible by the authenticated user.",
    )
    def list_accounts(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = service.accounts().list().execute()
            accounts = response.get("accounts", [])
            return json.dumps(accounts if accounts else {"message": "No accounts found."})
        except Exception as e:
            logger.error(f"Failed to list accounts: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="list_locations",
        description="List all business locations under a given account.",
    )
    def list_locations(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        account_name: str = Field(..., description="Account name, e.g. 'accounts/12345678'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = service.accounts().locations().list(parent=account_name).execute()
            locations = response.get("locations", [])
            return json.dumps(locations if locations else {"message": "No locations found."})
        except Exception as e:
            logger.error(f"Failed to list locations for '{account_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="get_location",
        description="Get detailed info about a specific business location.",
    )
    def get_location(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = service.accounts().locations().get(name=location_name).execute()
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to get location '{location_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="update_location",
        description="Update business profile fields such as description, phone, website, or hours.",
    )
    def update_location(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
        update_mask: str = Field(..., description="Comma-separated fields to update, e.g. 'profile.description,phoneNumbers'"),
        location_data: str = Field(..., description="JSON string of location fields to update"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            parsed = json.loads(location_data)
            response = (
                service.accounts()
                .locations()
                .patch(name=location_name, updateMask=update_mask, body=parsed)
                .execute()
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to update location '{location_name}': {e}")
            return json.dumps({"error": str(e)})

    # ═══════════════════════════════════════════════════════════
    # ⭐ REVIEW TOOLS
    # ═══════════════════════════════════════════════════════════

    @mcp.tool(
        name="list_reviews",
        description="Fetch reviews for a business location.",
    )
    def list_reviews(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
        page_size: int | None = Field(default=20, description="Number of reviews to return (max 50)"),
        order_by: str | None = Field(default="updateTime desc", description="Order by: 'updateTime desc', 'rating desc', or 'rating asc'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = (
                service.accounts()
                .locations()
                .reviews()
                .list(parent=location_name, pageSize=page_size, orderBy=order_by)
                .execute()
            )
            reviews = response.get("reviews", [])
            summary = [
                {
                    "name": r.get("name"),
                    "author": r.get("reviewer", {}).get("displayName"),
                    "rating": r.get("starRating"),
                    "comment": r.get("comment"),
                    "createTime": r.get("createTime"),
                    "reply": r.get("reviewReply", {}).get("comment") if r.get("reviewReply") else None,
                }
                for r in reviews
            ]
            return json.dumps(summary if summary else {"message": "No reviews found."})
        except Exception as e:
            logger.error(f"Failed to list reviews for '{location_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="reply_to_review",
        description="Post or update a reply to a customer review.",
    )
    def reply_to_review(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        review_name: str = Field(..., description="Review name, e.g. 'accounts/123/locations/456/reviews/789'"),
        reply_text: str = Field(..., description="The reply text to post (max 4096 chars)"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = (
                service.accounts()
                .locations()
                .reviews()
                .updateReply(name=review_name, body={"comment": reply_text})
                .execute()
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to reply to review '{review_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="delete_review_reply",
        description="Delete an existing reply to a customer review.",
    )
    def delete_review_reply(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        review_name: str = Field(..., description="Review name, e.g. 'accounts/123/locations/456/reviews/789'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            service.accounts().locations().reviews().deleteReply(name=review_name).execute()
            return json.dumps({"success": True, "message": f"Reply deleted for review: {review_name}"})
        except Exception as e:
            logger.error(f"Failed to delete reply for review '{review_name}': {e}")
            return json.dumps({"error": str(e)})

    # ═══════════════════════════════════════════════════════════
    # 📢 POSTS / UPDATES TOOLS
    # ═══════════════════════════════════════════════════════════

    @mcp.tool(
        name="list_posts",
        description="List recent posts/updates for a business location.",
    )
    def list_posts(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
        page_size: int | None = Field(default=10, description="Number of posts to return (max 100)"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = (
                service.accounts()
                .locations()
                .localPosts()
                .list(parent=location_name, pageSize=page_size)
                .execute()
            )
            posts = response.get("localPosts", [])
            return json.dumps(posts if posts else {"message": "No posts found."})
        except Exception as e:
            logger.error(f"Failed to list posts for '{location_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="create_post",
        description=(
            "Create a new post/update on a business location. "
            "Supports STANDARD, EVENT, OFFER, and PRODUCT topic types."
        ),
    )
    def create_post(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
        summary: str = Field(..., description="Main post text (max 1500 chars)"),
        topic_type: str = Field(default="STANDARD", description="Post type: STANDARD | EVENT | OFFER | PRODUCT"),
        call_to_action_type: str | None = Field(default=None, description="CTA type: BOOK | ORDER | SHOP | LEARN_MORE | SIGN_UP | CALL"),
        call_to_action_url: str | None = Field(default=None, description="URL for the CTA button"),
        event_title: str | None = Field(default=None, description="Title for EVENT posts"),
        event_start: str | None = Field(default=None, description="ISO 8601 event start datetime"),
        event_end: str | None = Field(default=None, description="ISO 8601 event end datetime"),
        offer_coupon: str | None = Field(default=None, description="Coupon code for OFFER posts"),
        offer_terms: str | None = Field(default=None, description="Terms & conditions for OFFER posts"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            body: dict = {"topicType": topic_type, "summary": summary}

            if call_to_action_type:
                body["callToAction"] = {
                    "actionType": call_to_action_type,
                    "url": call_to_action_url,
                }
            if topic_type == "EVENT" and event_title:
                body["event"] = {
                    "title": event_title,
                    "schedule": {
                        "startDateTime": event_start,
                        "endDateTime": event_end,
                    },
                }
            if topic_type == "OFFER":
                body["offer"] = {
                    "couponCode": offer_coupon,
                    "termsConditions": offer_terms,
                }

            response = (
                service.accounts()
                .locations()
                .localPosts()
                .create(parent=location_name, body=body)
                .execute()
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to create post for '{location_name}': {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="delete_post",
        description="Delete an existing post/update from a business location.",
    )
    def delete_post(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        post_name: str = Field(..., description="Post name, e.g. 'accounts/123/locations/456/localPosts/789'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            service.accounts().locations().localPosts().delete(name=post_name).execute()
            return json.dumps({"success": True, "message": f"Post deleted: {post_name}"})
        except Exception as e:
            logger.error(f"Failed to delete post '{post_name}': {e}")
            return json.dumps({"error": str(e)})

    # ═══════════════════════════════════════════════════════════
    # 📊 INSIGHTS / ANALYTICS TOOLS
    # ═══════════════════════════════════════════════════════════

    @mcp.tool(
        name="get_insights",
        description="Fetch performance insights (views, searches, actions) for one or more locations.",
    )
    def get_insights(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_names: str = Field(..., description="Comma-separated location names"),
        start_date: str = Field(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Field(..., description="End date in YYYY-MM-DD format"),
        metric_requests: str = Field(
            default="ALL",
            description=(
                "Metrics to fetch. Use 'ALL' or comma-separated subset: "
                "QUERIES_DIRECT, QUERIES_INDIRECT, VIEWS_MAPS, VIEWS_SEARCH, "
                "ACTIONS_WEBSITE, ACTIONS_PHONE, ACTIONS_DRIVING_DIRECTIONS"
            ),
        ),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            locations = [l.strip() for l in location_names.split(",")]
            all_metrics = [
                "QUERIES_DIRECT", "QUERIES_INDIRECT",
                "VIEWS_MAPS", "VIEWS_SEARCH",
                "ACTIONS_WEBSITE", "ACTIONS_PHONE", "ACTIONS_DRIVING_DIRECTIONS",
            ]
            metrics = all_metrics if metric_requests == "ALL" else [m.strip() for m in metric_requests.split(",")]

            sy, sm, sd = start_date.split("-")
            ey, em, ed = end_date.split("-")

            account_name = locations[0].rsplit("/locations/", 1)[0]
            response = (
                service.accounts()
                .locations()
                .reportInsights(
                    name=account_name,
                    body={
                        "locationNames": locations,
                        "basicRequest": {
                            "metricRequests": [{"metric": m} for m in metrics],
                            "timeRange": {
                                "startTime": f"{sy}-{sm}-{sd}T00:00:00Z",
                                "endTime":   f"{ey}-{em}-{ed}T23:59:59Z",
                            },
                        },
                    },
                )
                .execute()
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="get_review_summary",
        description="Get a quick summary of review stats (count, average rating, reply rate) for a location.",
    )
    def get_review_summary(
        oauth_token: OAuthTokenData = Field(..., description="OAuth token"),
        location_name: str = Field(..., description="Location name, e.g. 'accounts/123/locations/456'"),
    ) -> str:
        try:
            service = get_mybusiness_service(oauth_token)
            response = (
                service.accounts()
                .locations()
                .reviews()
                .list(parent=location_name, pageSize=50)
                .execute()
            )
            reviews = response.get("reviews", [])
            total = len(reviews)
            avg = (
                sum(RATING_MAP.get(r.get("starRating", ""), 0) for r in reviews) / total
                if total else 0
            )
            dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for r in reviews:
                dist[RATING_MAP.get(r.get("starRating", ""), 0)] += 1
            replied = sum(1 for r in reviews if r.get("reviewReply"))

            return json.dumps({
                "total_reviews": total,
                "average_rating": round(avg, 2),
                "replied_to": replied,
                "unreplied": total - replied,
                "rating_distribution": dist,
            })
        except Exception as e:
            logger.error(f"Failed to get review summary for '{location_name}': {e}")
            return json.dumps({"error": str(e)})
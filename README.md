**Manage your Google Business Profile - reviews, posts, locations, and insights - with Agents.**

A Model Context Protocol (MCP) server that exposes Google Business Profile's API for managing business locations, customer reviews, posts, and performance analytics.


## Overview

The Google Business MCP Server provides full management of your Google Business Profile presence:

- Manage business locations and profile information
- Read, reply to, and track customer reviews
- Create and delete business posts and updates
- Fetch performance insights and review analytics

Perfect for:

- Business owners automating review responses and post publishing
- Marketing teams monitoring performance metrics across locations
- Developers building Google Business Profile integrations


## Tools

### Profile & Locations

<details>
<summary><code>list_accounts</code> — List all Business Profile accounts</summary>

Returns all Google Business Profile accounts accessible by the authenticated user.

**Inputs:**
```
None
```

**Output:**

```json
[
  {
    "name": "accounts/123456789",
    "accountName": "Acme Corp",
    "type": "PERSONAL",
    "verificationState": "VERIFIED",
    "vettedState": "NOT_VETTED"
  }
]
```

</details>

<details>
<summary><code>list_locations</code> — List locations under an account</summary>

Returns all business locations under a given account.

**Inputs:**
```
- `account_name` (string, required) — Account resource name, e.g. `accounts/123456789`
```

**Output:**

```json
[
  {
    "name": "accounts/123456789/locations/987654321",
    "locationName": "Acme Corp - Downtown",
    "primaryPhone": "+1-555-555-0100",
    "websiteUrl": "https://acme.example.com",
    "primaryCategory": {
      "displayName": "Coffee Shop"
    }
  }
]
```

</details>

<details>
<summary><code>get_location</code> — Get a specific business location</summary>

Returns detailed information about a specific business location.

**Inputs:**
```
- `location_name` (string, required) — Location resource name, e.g. `accounts/123456789/locations/987654321`
```

**Output:**

```json
{
  "name": "accounts/123456789/locations/987654321",
  "locationName": "Acme Corp - Downtown",
  "primaryPhone": "+1-555-555-0100",
  "websiteUrl": "https://acme.example.com",
  "address": {
    "addressLines": ["123 Main St"],
    "locality": "San Francisco",
    "administrativeArea": "CA",
    "postalCode": "94105",
    "regionCode": "US"
  },
  "primaryCategory": {
    "displayName": "Coffee Shop",
    "categoryId": "gcid:coffee_shop"
  }
}
```

</details>

<details>
<summary><code>update_location</code> — Update business profile fields</summary>

Updates business profile fields such as description, phone number, website, or hours. Only fields specified in `update_mask` are changed.

**Inputs:**
```
- `location_name`  (string, required) — Location resource name, e.g. `accounts/123456789/locations/987654321`
- `update_mask`    (string, required) — Comma-separated fields to update, e.g. `profile.description,phoneNumbers`
- `location_data`  (string, required) — JSON string of the location fields to update
```

**Output:**

```json
{
  "name": "accounts/123456789/locations/987654321",
  "locationName": "Acme Corp - Downtown",
  "primaryPhone": "+1-555-555-0199",
  "websiteUrl": "https://acme.example.com/new",
  "profile": {
    "description": "Updated description for our downtown location."
  }
}
```

</details>


### Reviews

<details>
<summary><code>list_reviews</code> — Fetch reviews for a location</summary>

Returns customer reviews for a business location, ordered by update time or rating.

**Inputs:**
```
- `location_name`  (string, required)  — Location resource name, e.g. `accounts/123456789/locations/987654321`
- `page_size`      (integer, optional) — Number of reviews to return, max 50. Default: `20`
- `order_by`       (string, optional)  — Sort order: `updateTime desc`, `rating desc`, or `rating asc`. Default: `updateTime desc`
```

**Output:**

```json
[
  {
    "name": "accounts/123456789/locations/987654321/reviews/rev111",
    "author": "Jane Smith",
    "rating": "FIVE",
    "comment": "Amazing coffee and friendly staff!",
    "createTime": "2025-01-10T14:00:00Z",
    "reply": null
  },
  {
    "name": "accounts/123456789/locations/987654321/reviews/rev222",
    "author": "Bob Jones",
    "rating": "THREE",
    "comment": "Good place but can get crowded.",
    "createTime": "2025-01-08T09:30:00Z",
    "reply": "Thanks for the feedback, Bob!"
  }
]
```

</details>

<details>
<summary><code>reply_to_review</code> — Post or update a reply to a review</summary>

Posts a new reply or updates an existing reply to a customer review.

**Inputs:**
```
- `review_name`  (string, required) — Review resource name, e.g. `accounts/123456789/locations/987654321/reviews/rev111`
- `reply_text`   (string, required) — The reply text to post (max 4096 characters)
```

**Output:**

```json
{
  "comment": "Thank you so much for the kind words, Jane! We look forward to seeing you again.",
  "updateTime": "2025-01-11T10:00:00Z"
}
```

</details>

<details>
<summary><code>delete_review_reply</code> — Delete a reply to a review</summary>

Deletes an existing reply to a customer review.

**Inputs:**
```
- `review_name` (string, required) — Review resource name, e.g. `accounts/123456789/locations/987654321/reviews/rev111`
```

**Output:**

```json
{
  "success": true,
  "message": "Reply deleted for review: accounts/123456789/locations/987654321/reviews/rev111"
}
```

</details>


### Posts & Updates

<details>
<summary><code>list_posts</code> — List posts for a location</summary>

Returns recent posts and updates published to a business location.

**Inputs:**
```
- `location_name`  (string, required)  — Location resource name, e.g. `accounts/123456789/locations/987654321`
- `page_size`      (integer, optional) — Number of posts to return, max 100. Default: `10`
```

**Output:**

```json
[
  {
    "name": "accounts/123456789/locations/987654321/localPosts/post111",
    "topicType": "STANDARD",
    "summary": "We are now open on Sundays from 9am to 5pm!",
    "state": "LIVE",
    "createTime": "2025-01-12T08:00:00Z",
    "updateTime": "2025-01-12T08:00:00Z"
  }
]
```

</details>

<details>
<summary><code>create_post</code> — Create a post or update</summary>

Creates a new post on a business location. Supports STANDARD, EVENT, OFFER, and PRODUCT post types.

**Inputs:**
```
- `location_name`        (string, required)  — Location resource name, e.g. `accounts/123456789/locations/987654321`
- `summary`              (string, required)  — Main post text (max 1500 characters)
- `topic_type`           (string, optional)  — Post type: `STANDARD` | `EVENT` | `OFFER` | `PRODUCT`. Default: `STANDARD`
- `call_to_action_type`  (string, optional)  — CTA button: `BOOK` | `ORDER` | `SHOP` | `LEARN_MORE` | `SIGN_UP` | `CALL`
- `call_to_action_url`   (string, optional)  — URL for the CTA button
- `event_title`          (string, optional)  — Title for EVENT posts
- `event_start`          (string, optional)  — ISO 8601 event start datetime
- `event_end`            (string, optional)  — ISO 8601 event end datetime
- `offer_coupon`         (string, optional)  — Coupon code for OFFER posts
- `offer_terms`          (string, optional)  — Terms and conditions for OFFER posts
```

**Output:**

```json
{
  "name": "accounts/123456789/locations/987654321/localPosts/post222",
  "topicType": "EVENT",
  "summary": "Join us for our grand re-opening celebration!",
  "event": {
    "title": "Grand Re-Opening",
    "schedule": {
      "startDateTime": "2025-02-01T10:00:00Z",
      "endDateTime": "2025-02-01T18:00:00Z"
    }
  },
  "callToAction": {
    "actionType": "LEARN_MORE",
    "url": "https://acme.example.com/event"
  },
  "state": "LIVE",
  "createTime": "2025-01-15T09:00:00Z"
}
```

</details>

<details>
<summary><code>delete_post</code> — Delete a post</summary>

Deletes an existing post or update from a business location.

**Inputs:**
```
- `post_name` (string, required) — Post resource name, e.g. `accounts/123456789/locations/987654321/localPosts/post111`
```

**Output:**

```json
{
  "success": true,
  "message": "Post deleted: accounts/123456789/locations/987654321/localPosts/post111"
}
```

</details>


### Insights & Analytics

<details>
<summary><code>get_insights</code> — Fetch performance insights for locations</summary>

Returns performance metrics (views, searches, customer actions) for one or more locations over a date range.

**Inputs:**
```
- `location_names`   (string, required)  — Comma-separated location resource names
- `start_date`       (string, required)  — Start date in `YYYY-MM-DD` format
- `end_date`         (string, required)  — End date in `YYYY-MM-DD` format
- `metric_requests`  (string, optional)  — Metrics to fetch. Use `ALL` or a comma-separated subset: `QUERIES_DIRECT`, `QUERIES_INDIRECT`, `VIEWS_MAPS`, `VIEWS_SEARCH`, `ACTIONS_WEBSITE`, `ACTIONS_PHONE`, `ACTIONS_DRIVING_DIRECTIONS`. Default: `ALL`
```

**Output:**

```json
{
  "locationMetrics": [
    {
      "locationName": "accounts/123456789/locations/987654321",
      "timeZone": "America/Los_Angeles",
      "metricValues": [
        {
          "metric": "QUERIES_DIRECT",
          "totalValue": { "metricOption": "AGGREGATED_TOTAL", "value": "320" }
        },
        {
          "metric": "VIEWS_SEARCH",
          "totalValue": { "metricOption": "AGGREGATED_TOTAL", "value": "1540" }
        },
        {
          "metric": "ACTIONS_WEBSITE",
          "totalValue": { "metricOption": "AGGREGATED_TOTAL", "value": "87" }
        }
      ]
    }
  ]
}
```

</details>

<details>
<summary><code>get_review_summary</code> — Get review stats for a location</summary>

Returns a computed summary of review statistics including total count, average rating, reply rate, and rating distribution.

**Inputs:**
```
- `location_name` (string, required) — Location resource name, e.g. `accounts/123456789/locations/987654321`
```

**Output:**

```json
{
  "total_reviews": 48,
  "average_rating": 4.35,
  "replied_to": 31,
  "unreplied": 17,
  "rating_distribution": {
    "1": 2,
    "2": 3,
    "3": 5,
    "4": 14,
    "5": 24
  }
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Resource Name Formats</strong></summary>

All Google Business Profile resources use hierarchical resource names:

**Account:**
```
accounts/{account_id}
Example: accounts/123456789
```

**Location:**
```
accounts/{account_id}/locations/{location_id}
Example: accounts/123456789/locations/987654321
```

**Review:**
```
accounts/{account_id}/locations/{location_id}/reviews/{review_id}
Example: accounts/123456789/locations/987654321/reviews/rev111
```

**Post:**
```
accounts/{account_id}/locations/{location_id}/localPosts/{post_id}
Example: accounts/123456789/locations/987654321/localPosts/post111
```

</details>

<details>
<summary><strong>Post Topic Types</strong></summary>

- `STANDARD` — General update or announcement
- `EVENT` — Time-bound event with title, start, and end datetime
- `OFFER` — Promotional offer with optional coupon code and terms
- `PRODUCT` — Product highlight with name and description

</details>

<details>
<summary><strong>Review Star Ratings</strong></summary>

Google returns star ratings as strings: `ONE`, `TWO`, `THREE`, `FOUR`, `FIVE`.

The `get_review_summary` tool maps these to numeric values (1–5) for the rating distribution output.

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** OAuth token not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_TOKEN` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check that your Google credential is active in your MewCP account

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No Google Business Profile credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Connect your Google account via OAuth
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload in `location_data` is invalid or `update_mask` fields do not match the payload keys
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure `update_mask` field names exactly match keys in your `location_data` JSON
  3. Check parameter types match expected values

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>Google Business Profile API Error</strong></summary>

- **Cause:** Upstream Google Business Profile API returned an error (e.g. 403 Forbidden, 404 Not Found)
- **Solution:**
  1. Check the [Google Workspace Status Dashboard](https://workspace.google.com/status) for outages
  2. Verify your Google account is an owner or manager of the business location
  3. Ensure the `business.manage` scope is granted in your OAuth credential

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Google Business Profile API Documentation](https://developers.google.com/my-business/content/overview)** — Official API overview
- **[Google Business Profile API Reference](https://developers.google.com/my-business/reference/rest)** — Complete endpoint reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — Credential handling package

</details>

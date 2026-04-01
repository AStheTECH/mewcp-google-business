# Google Business Profile MCP Server

A Model Context Protocol (MCP) server that provides access to Google Business Profile APIs for accounts, locations, reviews, posts, and insights.

## Authentication

Authentication is handled by passing a valid `oauth_token` with each tool call.

- The server does not generate OAuth tokens.
- The token must include Google Business Profile scope access.
- A commonly used scope is `https://www.googleapis.com/auth/business.manage`.

## Features

This server includes tools for:

- Account and location management.
- Review listing and reply management.
- Post listing, creation, and deletion.
- Performance insights and review summaries.

## Available Tools

- `list_accounts`
- `list_locations`
- `get_location`
- `update_location`
- `list_reviews`
- `reply_to_review`
- `delete_review_reply`
- `list_posts`
- `create_post`
- `delete_post`
- `get_insights`
- `get_review_summary`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server from `server.py`:

- For `stdio` transport:

```bash
python server.py
```

- For `sse` transport:

```bash
python server.py --transport sse --host 127.0.0.1 --port 8001
```

- For `streamable-http` transport:

```bash
python server.py --transport streamable-http --host 127.0.0.1 --port 8001
```

## Usage Notes

- All tools require `oauth_token`.
- Resource identifiers should use Google formats, for example:
	- Account: `accounts/123456789`
	- Location: `accounts/123456789/locations/987654321`
	- Review: `accounts/123456789/locations/987654321/reviews/555`

## Example Tool Call Payload

```json
{
	"tool": "list_locations",
	"arguments": {
		"oauth_token": {
			"token": "ya29...",
			"refresh_token": "1//...",
			"token_uri": "https://oauth2.googleapis.com/token",
			"client_id": "...apps.googleusercontent.com",
			"client_secret": "...",
			"scopes": [
				"https://www.googleapis.com/auth/business.manage"
			]
		},
		"account_name": "accounts/123456789"
	}
}
```

## Project Entry Point

The runtime entrypoint for this MCP server is `server.py`, which:

- creates the FastMCP instance,
- registers all tools,
- and exposes the HTTP app at `/mcp` for streamable HTTP transport.

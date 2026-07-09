# Jira OAuth 2.0 Authentication

This document describes the Jira OAuth 2.0 (3-Legged OAuth) integration in the BrainTrust MCP Server. It covers the Atlassian app setup, environment configuration, the authentication flow, token management, and troubleshooting.

## Table of Contents

- [Overview](#overview)
- [Atlassian App Setup](#atlassian-app-setup)
- [Environment Variables](#environment-variables)
- [Authentication Flow](#authentication-flow)
- [Token Storage](#token-storage)
- [API Routing (Atlassian API Gateway)](#api-routing-atlassian-api-gateway)
- [MCP Tools](#mcp-tools)
- [MCP Prompts](#mcp-prompts)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)

---

## Overview

The MCP server uses **Atlassian OAuth 2.0 (3LO)** to authenticate users against Jira Cloud. Each user authenticates independently via their browser, and the server stores per-user tokens in a local SQLite database. Tokens are keyed by the user's **Atlassian email address**, which is resolved automatically during the OAuth flow.

Key characteristics:

- **Per-user tokens**: each user authenticates independently; tokens are not shared.
- **Automatic token refresh**: access tokens are refreshed transparently when they expire.
- **Browser-based consent**: the user grants permissions via Atlassian's consent screen.
- **Automatic callback handling**: the server hosts the OAuth callback endpoint on the same port as the MCP server.

---

## Atlassian App Setup

Before the server can authenticate users, you must create an OAuth 2.0 app in the Atlassian Developer Console.

### Step-by-step

1. Go to [https://developer.atlassian.com/console/myapps/](https://developer.atlassian.com/console/myapps/) and log in with an Atlassian account that has admin access to your Jira instance.

2. Click **Create** > **OAuth 2.0 integration**.

3. Give the app a name (e.g., `BrainTrust MCP`) and accept the terms.

4. In the app settings, go to **Authorization** > **OAuth 2.0 (3LO)** and set the **Callback URL** to:
   ```
   http://localhost:8000/callback
   ```
   If you deploy the server on a custom host/port or behind a reverse proxy, use the appropriate public URL (e.g., `https://mcp.example.com/callback`). This must match the `MCP_SERVER_BASE_URL` + `/callback`.

5. Go to **Permissions** and add the following scopes:
   | Scope | Purpose |
   |---|---|
   | `read:me` | Resolve the user's Atlassian email after consent |
   | `read:jira-work` | Read issues, projects, boards, sprints |
   | `read:jira-user` | Read user profiles (assignee, reporter) |
   | `offline_access` | Obtain a refresh token for long-lived sessions |

6. Go to **Settings** and copy the **Client ID** and **Client Secret**.

### Finding your Cloud ID

The Cloud ID uniquely identifies your Jira Cloud instance. OAuth 2.0 API calls **must** be routed through the Atlassian API Gateway using this ID (see [API Routing](#api-routing-atlassian-api-gateway)).

To find it, open this URL in your browser (replace `your-domain` with your actual Jira subdomain):

```
https://your-domain.atlassian.net/_edge/tenant_info
```

The response is a JSON object:

```json
{
  "cloudId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  ...
}
```

Copy the `cloudId` value.

---

## Environment Variables

All configuration is done via environment variables prefixed with `MCP_SERVER_`. The server reads these from a `.env` file at the project root (powered by `pydantic-settings`).

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

### Jira-specific variables

| Variable | Required | Description |
|---|---|---|
| `MCP_SERVER_JIRA_CLIENT_ID` | Yes | OAuth 2.0 Client ID from the Atlassian app settings |
| `MCP_SERVER_JIRA_CLIENT_SECRET` | Yes | OAuth 2.0 Client Secret from the Atlassian app settings |
| `MCP_SERVER_JIRA_CLOUD_ID` | Yes | Cloud ID of your Jira instance (see [Finding your Cloud ID](#finding-your-cloud-id)) |
| `MCP_SERVER_JIRA_SERVER_URL` | No | Direct Jira instance URL (e.g., `https://your-domain.atlassian.net`). Not used for API calls but kept for reference |
| `MCP_SERVER_BASE_URL` | No | Externally accessible URL of the server. Defaults to `http://localhost:{port}`. The OAuth callback URI is derived as `{base_url}/callback` |
| `MCP_SERVER_TOKEN_DB_PATH` | No | Path to the SQLite token database. Defaults to `data/tokens.db` |

### Example `.env`

```env
MCP_SERVER_JIRA_CLIENT_ID=your-client-id-here
MCP_SERVER_JIRA_CLIENT_SECRET=your-client-secret-here
MCP_SERVER_JIRA_CLOUD_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
MCP_SERVER_JIRA_SERVER_URL=https://your-domain.atlassian.net
MCP_SERVER_BASE_URL=http://localhost:8000
MCP_SERVER_TOKEN_DB_PATH=data/tokens.db
```

### Derived values

The following values are computed automatically from the settings above:

- **`jira_redirect_uri`**: Derived as `{base_url}/callback`. For example, if `MCP_SERVER_BASE_URL=http://localhost:8000`, the redirect URI is `http://localhost:8000/callback`. This must match the Callback URL configured in the Atlassian app.

---

## Authentication Flow

The authentication flow follows the standard OAuth 2.0 Authorization Code Grant.

### Sequence

```
User/Agent              MCP Server              Atlassian
    |                       |                       |
    |-- generate_jira_auth_url -->                  |
    |<-- auth URL ----------|                       |
    |                       |                       |
    |-------------- open URL in browser ----------->|
    |                       |                       |
    |                       |    (user logs in,     |
    |                       |     grants consent)   |
    |                       |                       |
    |                       |<-- GET /callback?code=ABC
    |                       |                       |
    |                       |-- POST token exchange |
    |                       |<-- access + refresh --|
    |                       |                       |
    |                       |-- GET /me             |
    |                       |<-- { email: "..." } --|
    |                       |                       |
    |                       |-- store tokens (keyed by email)
    |                       |                       |
    |<-- success HTML page -|                       |
    |   (shows email)       |                       |
```

### Detailed steps

1. **Generate authorization URL**: The MCP tool `generate_jira_auth_url` builds a URL pointing to `https://auth.atlassian.com/authorize` with the configured client ID, scopes, redirect URI, and a `state` parameter.

2. **User consent**: The user opens the URL in their browser, logs into Atlassian (if not already), and grants the requested permissions.

3. **Callback redirect**: Atlassian redirects the browser to `{base_url}/callback?code=AUTH_CODE&state=oauth`. The MCP server has a route handler (`OAuthCallbackController`) listening at `/callback` on the same port as the MCP server.

4. **Token exchange**: The callback handler sends a POST request to `https://auth.atlassian.com/oauth/token` with the authorization code, client ID, client secret, and redirect URI. Atlassian returns an access token, refresh token, and expiration time.

5. **Email resolution**: The server immediately calls `https://api.atlassian.com/me` with the new access token to retrieve the user's Atlassian email address. This email becomes the **unique key** for the user's tokens.

6. **Token storage**: The access token, refresh token, and expiration timestamp are stored in the SQLite database, keyed by the email.

7. **Success page**: The browser displays a styled HTML success page showing the user's email. This email must be used as the `user_id` parameter in all subsequent Jira tool calls.

### Fallback: manual code exchange

If the automatic callback cannot be reached (e.g., the user is on a different network, or the server is behind a firewall without ingress), the user can:

1. Copy the `code` parameter from the redirect URL in their browser's address bar.
2. Call the `complete_jira_auth` MCP tool with that code.
3. The tool performs the same token exchange and returns the resolved email.

---

## Token Storage

Tokens are persisted in a local **SQLite database** at the path specified by `MCP_SERVER_TOKEN_DB_PATH` (default: `data/tokens.db`).

### Database schema

```sql
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id TEXT PRIMARY KEY,       -- Atlassian email address
    access_token TEXT NOT NULL,     -- OAuth 2.0 access token
    refresh_token TEXT NOT NULL,    -- OAuth 2.0 refresh token
    expires_at INTEGER NOT NULL     -- Unix timestamp (seconds) when access_token expires
);
```

### Key points

- The `user_id` column stores the user's **Atlassian email address**, resolved during the OAuth flow.
- Tokens are upserted: re-authenticating with the same email overwrites the previous tokens.
- The `data/` directory is included in `.gitignore` to prevent accidental commits of token data.
- The database file and its parent directory are created automatically on first use.

### Token refresh

Access tokens expire (typically after 1 hour). The server handles refresh **automatically and transparently**:

1. Before each Jira API call, the server checks if the access token expires within the next 60 seconds.
2. If expired or about to expire, it sends a POST request to `https://auth.atlassian.com/oauth/token` with `grant_type=refresh_token`.
3. The new tokens (access token, refresh token, expiration) replace the old ones in the database.
4. The API call proceeds with the fresh access token.

If the refresh token itself has been revoked (e.g., user revoked app access in Atlassian settings), the server raises a `JiraAuthenticationException` and the user must re-authenticate.

---

## API Routing (Atlassian API Gateway)

This is a critical detail for DevOps and infrastructure setup.

**OAuth 2.0 access tokens issued by Atlassian Cloud are ONLY valid when used against the Atlassian API Gateway.** They do NOT work when sent directly to the Jira instance URL.

| Method | Base URL | Works with OAuth? |
|---|---|---|
| API Gateway | `https://api.atlassian.com/ex/jira/{cloud_id}` | Yes |
| Direct instance | `https://your-domain.atlassian.net` | No (returns 401) |

The server constructs the gateway URL as:

```
https://api.atlassian.com/ex/jira/{cloud_id}
```

where `{cloud_id}` is the value of `MCP_SERVER_JIRA_CLOUD_ID`.

All Jira REST API calls (fetching issues, searching, etc.) are routed through this gateway. The `jira` Python library is configured with `token_auth=access_token`, which sets the `Authorization: Bearer {token}` header automatically.

### Why this matters

If you see `401 Unauthorized` errors after a successful authentication, the most likely cause is an incorrect `MCP_SERVER_JIRA_CLOUD_ID` or the server mistakenly using the direct instance URL. Always verify:

1. The Cloud ID matches your Jira instance (`https://your-domain.atlassian.net/_edge/tenant_info`).
2. The server logs show requests going to `api.atlassian.com`, not to `your-domain.atlassian.net`.

---

## MCP Tools

The server exposes the following MCP tools related to Jira authentication and usage:

### `generate_jira_auth_url`

- **Parameters**: none
- **Returns**: `{ auth_url: string }` — the Atlassian authorization URL
- **Purpose**: Generates the OAuth consent URL. The user must open this in a browser.

### `complete_jira_auth`

- **Parameters**: `code` (string) — the authorization code from the redirect URL
- **Returns**: `{ success: boolean, email: string, message: string }`
- **Purpose**: Manually exchanges an authorization code for tokens. Only needed if the automatic callback is not reachable.

### `get_jira_issue`

- **Parameters**:
  - `issue_id` (string) — Jira issue key (e.g., `PROJ-123`)
  - `user_id` (string) — the Atlassian email from the auth flow
- **Returns**: a `JiraTask` object with issue details (title, status, priority, assignee, etc.)

### `get_pending_jira_issues`

- **Parameters**:
  - `user_id` (string) — the Atlassian email from the auth flow
  - `assignee` (string) — the display name or email of the assignee to filter by
- **Returns**: a tuple of `JiraTask` objects matching `status IN ("To Do", "In Progress")`

### Important: `user_id` is the Atlassian email

In all Jira tools, the `user_id` parameter is the **Atlassian email address** shown on the success page after authentication. It is NOT a Jira account ID, display name, or any other identifier. Using the wrong value results in `UserTokensNotFoundException`.

---

## MCP Prompts

### `jira_login`

An MCP prompt that guides an AI agent through the complete Jira OAuth flow. When invoked:

1. Calls `generate_jira_auth_url` and presents the URL to the user.
2. Instructs the user to open it in their browser and grant consent.
3. Explains that the callback handles token exchange automatically.
4. Tells the user that the email shown on the success page is their `user_id` for future Jira tool calls.
5. Provides fallback instructions for manual code exchange if the callback is unreachable.

---

## Error Handling

All Jira-related errors are caught and surfaced to MCP clients via `ToolError` with descriptive messages.

| Exception | User-facing message | Cause |
|---|---|---|
| `UserTokensNotFoundException` | "User not authenticated. Please complete the OAuth flow first." | No tokens found for the given `user_id` (email) |
| `JiraAuthenticationException` | "Jira authentication failed. Token may be revoked — please re-authenticate." | 401 from Jira API — token invalid/revoked, or wrong Cloud ID |
| `TokenRefreshException` | "Failed to refresh access token. Please re-authenticate." | Refresh token rejected by Atlassian |
| `IssueNotFoundException` | "The requested Jira issue was not found." | Issue key does not exist (404) |
| `JiraUserNotFoundException` | "The specified Jira user/assignee was not found." | Assignee not found in Jira (400) |
| `JiraApiException` | "Jira API error occurred." | Any other Jira REST API error |
| `AuthCodeExchangeException` | "Failed to exchange authorization code. The code may be invalid or expired." | Token exchange failed (bad code, expired code, HTTP error) |

---

## Troubleshooting

### "User not authenticated" after completing the OAuth flow

**Cause**: The `user_id` passed to Jira tools does not match the email stored during authentication.

**Fix**: Use the exact email shown on the success page. It is case-sensitive and must match exactly.

### 401 Unauthorized after successful authentication

**Cause**: API calls are being routed to the wrong base URL. OAuth tokens only work against the Atlassian API Gateway (`api.atlassian.com`), not the direct Jira instance URL.

**Fix**:
1. Verify `MCP_SERVER_JIRA_CLOUD_ID` is correct — visit `https://your-domain.atlassian.net/_edge/tenant_info`.
2. Ensure the Cloud ID in your `.env` matches the `cloudId` in the JSON response.

### "Token refresh failed" or "Token may be revoked"

**Cause**: The user revoked app access from their Atlassian account settings, or the refresh token expired (rare with `offline_access` scope).

**Fix**: The user must re-authenticate: call `generate_jira_auth_url` and complete the flow again.

### Callback page shows an error

**Cause**: The authorization code exchange failed. Common reasons:
- The code was already used (codes are single-use).
- The code expired (codes are short-lived, typically 10 minutes).
- The `redirect_uri` in the token exchange request does not match the one configured in the Atlassian app.

**Fix**:
1. Verify the callback URL in the Atlassian app matches `{MCP_SERVER_BASE_URL}/callback`.
2. Retry the flow from the beginning (generate a new auth URL).

### Callback not reachable (network/firewall issues)

**Cause**: The browser cannot reach the MCP server's `/callback` endpoint (e.g., the server runs on a remote machine, or a firewall blocks the port).

**Fix**:
1. Use the manual code exchange: after granting consent, copy the `code` parameter from the browser's address bar and call `complete_jira_auth(code=...)`.
2. Alternatively, set `MCP_SERVER_BASE_URL` to a publicly accessible URL and configure a reverse proxy to forward `/callback` to the server.

### Database locked or permission errors

**Cause**: The SQLite database file or its parent directory cannot be written to.

**Fix**:
1. Ensure the `data/` directory is writable by the user running the server.
2. Check that no other process has an exclusive lock on the database file.
3. If the database is corrupted, delete `data/tokens.db` and re-authenticate all users.

### OAuth scopes insufficient

**Cause**: The Atlassian app does not have the required scopes, causing API calls to fail with 403.

**Fix**: Go to the Atlassian app settings > **Permissions** and ensure these scopes are granted:
- `read:me`
- `read:jira-work`
- `read:jira-user`
- `offline_access`

After adding scopes, existing users must re-authenticate to obtain new tokens with the updated scope set.

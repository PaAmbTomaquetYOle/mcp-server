import logging
from collections.abc import Callable
from functools import wraps

from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.domain.exceptions import (
    AuthCodeExchangeException,
    CollaborationToolException,
    IssueNotFoundException,
    JiraApiException,
    JiraAuthenticationException,
    JiraUserNotFoundException,
    TokenRefreshException,
    TrelloApiException,
    TrelloAuthenticationException,
    TrelloCardNotFoundException,
    TrelloMemberNotFoundException,
    TrelloTokenStorageException,
    UserTokensNotFoundException,
)

logger = logging.getLogger(__name__)

ERROR_MESSAGES: dict[type[CollaborationToolException], str] = {
    UserTokensNotFoundException: "User not authenticated. Please complete the OAuth flow first.",
    JiraAuthenticationException: "Jira authentication failed. Token may be revoked — please re-authenticate.",
    TokenRefreshException: "Failed to refresh access token. Please re-authenticate.",
    IssueNotFoundException: "The requested Jira issue was not found.",
    JiraUserNotFoundException: "The specified Jira user/assignee was not found.",
    JiraApiException: "Jira API error occurred.",
    TrelloAuthenticationException: "Trello authentication failed. Token may be revoked — please re-authenticate.",
    TrelloCardNotFoundException: "The requested Trello card was not found.",
    TrelloMemberNotFoundException: "The specified Trello member was not found.",
    TrelloApiException: "Trello API error occurred.",
    TrelloTokenStorageException: "Failed to store Trello token. Please verify the token is valid.",
    AuthCodeExchangeException: "Failed to exchange authorization code. The code may be invalid or expired.",
}


def tool_error_handler(fn: Callable) -> Callable:
    """Decorator that catches exceptions in MCP tool handlers and raises
    ToolError so FastMCP surfaces them correctly to the client."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except CollaborationToolException as exc:
            user_message = ERROR_MESSAGES.get(type(exc), str(exc))
            logger.warning("Tool '%s' failed: %s", fn.__name__, exc)
            raise ToolError(f"{user_message} ({exc})") from exc
        except ToolError:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in tool '%s'", fn.__name__)
            raise ToolError(f"An unexpected error occurred: {exc}") from exc

    return wrapper

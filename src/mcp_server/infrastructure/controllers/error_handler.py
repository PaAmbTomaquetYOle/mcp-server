import logging
from collections.abc import Callable
from functools import wraps

from mcp_server.domain.exceptions import (
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
}


def tool_error_handler(fn: Callable) -> Callable:
    """Decorator that catches exceptions in MCP tool handlers and returns
    structured error dicts instead of letting the server crash."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except CollaborationToolException as exc:
            user_message = ERROR_MESSAGES.get(type(exc), str(exc))
            logger.warning("Tool '%s' failed: %s", fn.__name__, exc)
            return {
                "error": True,
                "error_type": type(exc).__name__,
                "message": user_message,
                "detail": str(exc),
            }
        except Exception as exc:
            logger.exception("Unexpected error in tool '%s'", fn.__name__)
            return {
                "error": True,
                "error_type": "InternalError",
                "message": "An unexpected error occurred. The server is still running.",
                "detail": str(exc),
            }

    return wrapper

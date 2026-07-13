import logging
from collections.abc import Callable
from functools import wraps

from mcp.server.fastmcp.exceptions import ResourceError, ToolError

from mcp_server.domain.exceptions import (
    AuthCodeExchangeException,
    BackendApiException,
    DomainException,
    EventPublishException,
    IssueNotFoundException,
    JiraApiException,
    JiraAuthenticationException,
    JiraUserNotFoundException,
    KnowledgeGraphApiException,
    PersonNotFoundException,
    SlackApiException,
    SopCacheException,
    TokenRefreshException,
    TrelloApiException,
    TrelloAuthenticationException,
    TrelloCardNotFoundException,
    TrelloMemberNotFoundException,
    TrelloTokenStorageException,
    UserTokensNotFoundException,
)

logger = logging.getLogger(__name__)

ERROR_MESSAGES: dict[type[DomainException], str] = {
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
    BackendApiException: "Failed to reach the backend API or it returned an error.",
    SlackApiException: "Failed to reach the Slack API or it returned an error.",
    SopCacheException: "Failed to refresh the SOP search cache.",
    PersonNotFoundException: "The requested person was not found in the knowledge graph.",
    KnowledgeGraphApiException: "Knowledge Graph API error occurred.",
    EventPublishException: "Failed to publish the interaction event.",
}


def tool_error_handler(fn: Callable) -> Callable:
    """Decorator that catches exceptions in MCP tool handlers and raises
    ToolError so FastMCP surfaces them correctly to the client."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except DomainException as exc:
            user_message = ERROR_MESSAGES.get(type(exc), str(exc))
            logger.warning("Tool '%s' failed: %s", fn.__name__, exc)
            raise ToolError(f"{user_message} ({exc})") from exc
        except ToolError:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in tool '%s'", fn.__name__)
            raise ToolError(f"An unexpected error occurred: {exc}") from exc

    return wrapper


def resource_error_handler(fn: Callable) -> Callable:
    """Decorator that catches exceptions in MCP resource handlers and raises
    ResourceError so FastMCP surfaces them correctly to the client.

    Mirrors ``tool_error_handler`` but targets the SDK's resource error model
    (``ResourceError`` instead of ``ToolError``), since resources are read via
    a different code path (``FastMCP.read_resource``) than tools.
    """

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except DomainException as exc:
            user_message = ERROR_MESSAGES.get(type(exc), str(exc))
            logger.warning("Resource '%s' failed: %s", fn.__name__, exc)
            raise ResourceError(f"{user_message} ({exc})") from exc
        except ResourceError:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in resource '%s'", fn.__name__)
            raise ResourceError(f"An unexpected error occurred: {exc}") from exc

    return wrapper

"""Domain layer: the enterprise business rules.

This is the innermost layer of the hexagonal architecture. It models the core
concepts and invariants of the problem space, independently of any technology,
framework, or transport.

What to put here:
    - Entities and aggregates (objects with identity and lifecycle).
    - Value objects (immutable, equality by value).
    - Domain services (logic that doesn't naturally belong to a single entity).
    - Domain events and domain-specific exceptions.

What NOT to put here:
    - Imports from ``application`` or ``infrastructure`` (the domain depends on
      nothing else in the project).
    - Any IO, persistence, networking, configuration, or third-party SDK code
      (no MCP, Slack, HTTP, database or filesystem access).
    - Framework decorators, serialization concerns, or transport models.

This layer must stay pure Python so it can be reasoned about and tested in
isolation.
"""

from .enums import *  # noqa: I001 (must precede collaboration_tasks, which depends on it)
from .collaboration_tasks import *
from .exceptions import *
from .search import SearchDocument, SearchQuery, SlackWorkspaceSearchResult

__all__ = [
    "CollaborationToolEnum",
    "CollaborationTask",
    "JiraTask",
    "JiraUser",
    "TrelloTask",
    "TrelloMember",
    "CollaborationToolException",
    "BackendApiException",
    "IssueNotFoundException",
    "JiraApiException",
    "JiraAuthenticationException",
    "JiraUserNotFoundException",
    "TokenRefreshException",
    "UserTokensNotFoundException",
    "AuthCodeExchangeException",
    "KnowledgeGraphException",
    "PersonNotFoundException",
    "KnowledgeGraphApiException",
    "EventPublishException",
    "SlackSearchException",
    "SlackApiException",
    "SopCacheException",
    "SearchTimeoutException",
    "SearchDocument",
    "SearchQuery",
    "SlackWorkspaceSearchResult",
]
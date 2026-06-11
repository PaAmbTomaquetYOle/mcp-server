"""Driven adapters: concrete implementations of the application's outbound ports.

These classes fulfil the contracts defined in ``application.ports`` using real
technology, e.g. a Slack API client, an HTTP client, or a database/repository
implementation.

What to put here:
    - Concrete classes implementing ``application.ports`` interfaces.
    - The translation between domain types and the external system's models
      (mapping, serialization, error translation).

What NOT to put here:
    - Business logic or use-case orchestration (keep adapters thin; they only
      adapt). Domain decisions belong in ``domain``/``application``.
"""

from .sqlite_token_storage import SqliteTokenStorage
from .jira import JiraAdapter

__all__ = [
    "SqliteTokenStorage",
    "JiraAdapter",
]
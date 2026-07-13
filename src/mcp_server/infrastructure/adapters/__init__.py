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

from .backend_api import BackendApiAdapter
from .backend_token_client import BackendTokenClient
from .jira import JiraAdapter
from .jira_auth import JiraAuthAdapter
from .kafka_event_publisher import KafkaEventPublisherAdapter
from .kafka_sop_cache_consumer import KafkaSopCacheConsumerAdapter
from .knowledge_graph_api import KnowledgeGraphApiAdapter
from .slack_api import SlackApiAdapter
from .slack_auth import SlackAuthAdapter
from .slack_workspace_search import SlackWorkspaceSearchAdapter
from .sop_cache import InMemorySopCacheAdapter
from .sqlite_token_storage import SqliteTokenStorage
from .token_encryptor import TokenEncryptor
from .trello import TrelloAdapter
from .trello_auth import TrelloAuthAdapter

__all__ = [
    "BackendApiAdapter",
    "BackendTokenClient",
    "InMemorySopCacheAdapter",
    "KafkaEventPublisherAdapter",
    "KafkaSopCacheConsumerAdapter",
    "KnowledgeGraphApiAdapter",
    "SqliteTokenStorage",
    "TokenEncryptor",
    "JiraAdapter",
    "JiraAuthAdapter",
    "SlackApiAdapter",
    "SlackAuthAdapter",
    "SlackWorkspaceSearchAdapter",
    "TrelloAdapter",
    "TrelloAuthAdapter",
]

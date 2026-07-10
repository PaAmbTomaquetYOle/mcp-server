"""Search domain: entities representing content indexed by the Slack search connector."""

from .search_document import SearchDocument, SearchQuery
from .slack_workspace_search_result import SlackWorkspaceSearchResult

__all__ = [
    "SearchDocument",
    "SearchQuery",
    "SlackWorkspaceSearchResult",
]

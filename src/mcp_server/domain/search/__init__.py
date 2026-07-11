"""Search domain: entities representing content indexed by the Slack search connector."""

from .relevance_scorer import RelevanceScorer
from .search_document import SearchDocument, SearchQuery
from .slack_workspace_search_result import SlackWorkspaceSearchResult
from .synonym_expander import SynonymExpander
from .token_normalizer import TokenNormalizer

__all__ = [
    "RelevanceScorer",
    "SearchDocument",
    "SearchQuery",
    "SlackWorkspaceSearchResult",
    "SynonymExpander",
    "TokenNormalizer",
]

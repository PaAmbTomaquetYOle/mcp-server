"""Schemas for MCP tool controllers."""

from .dossier_schemas import (
    DossierContact,
    DossierKnowledgeArea,
    DossierPendingTask,
    DossierSearchResult,
    DossierSection,
    GenerateDossierResponse,
    GetDossierResponse,
)
from .jira_auth_schemas import CompleteJiraAuthResponse, GenerateJiraAuthResponse
from .ping_schemas import PingResult
from .search_connector_schemas import (
    ConnectorStatusResponse,
    RefreshResponse,
    SearchAnalyticsResponse,
    SearchQueryTestResponse,
    SearchResultItem,
)
from .slack_auth_schemas import CompleteSlackAuthResponse, GenerateSlackAuthResponse
from .slack_workspace_search_schemas import SlackWorkspaceSearchResponse, SlackWorkspaceSearchResultItem
from .trello_auth_schemas import CompleteTrelloAuthResponse, GenerateTrelloAuthResponse

__all__ = [
    "PingResult",
    "CompleteJiraAuthResponse",
    "CompleteSlackAuthResponse",
    "CompleteTrelloAuthResponse",
    "ConnectorStatusResponse",
    "DossierContact",
    "DossierKnowledgeArea",
    "DossierPendingTask",
    "DossierSearchResult",
    "DossierSection",
    "GenerateDossierResponse",
    "GetDossierResponse",
    "GenerateJiraAuthResponse",
    "GenerateSlackAuthResponse",
    "GenerateTrelloAuthResponse",
    "RefreshResponse",
    "SearchAnalyticsResponse",
    "SearchResultItem",
    "SearchQueryTestResponse",
    "SlackWorkspaceSearchResponse",
    "SlackWorkspaceSearchResultItem",
]

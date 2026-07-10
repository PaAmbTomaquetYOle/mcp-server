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
from .knowledge_graph_schemas import (
    AddInteractionResponse,
    DocumentInfo,
    ExpertResult,
    KnowledgeMapResponse,
    PersonInfo,
    QueryExpertsResponse,
    TopicInfo,
)
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
    "AddInteractionResponse",
    "CompleteJiraAuthResponse",
    "CompleteSlackAuthResponse",
    "CompleteTrelloAuthResponse",
    "ConnectorStatusResponse",
    "DocumentInfo",
    "DossierContact",
    "DossierKnowledgeArea",
    "DossierPendingTask",
    "DossierSearchResult",
    "DossierSection",
    "ExpertResult",
    "GenerateDossierResponse",
    "GetDossierResponse",
    "GenerateJiraAuthResponse",
    "GenerateSlackAuthResponse",
    "GenerateTrelloAuthResponse",
    "KnowledgeMapResponse",
    "PersonInfo",
    "QueryExpertsResponse",
    "RefreshResponse",
    "SearchAnalyticsResponse",
    "SearchResultItem",
    "SearchQueryTestResponse",
    "SlackWorkspaceSearchResponse",
    "SlackWorkspaceSearchResultItem",
    "TopicInfo",
]

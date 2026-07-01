"""Schemas for MCP tool controllers."""

from .dossier_schemas import DossierSearchResult, GetDossierResponse
from .jira_auth_schemas import CompleteJiraAuthResponse, GenerateJiraAuthResponse
from .ping_schemas import PingResult
from .trello_auth_schemas import CompleteTrelloAuthResponse, GenerateTrelloAuthResponse

__all__ = [
    "PingResult",
    "CompleteJiraAuthResponse",
    "CompleteTrelloAuthResponse",
    "DossierSearchResult",
    "GetDossierResponse",
    "GenerateJiraAuthResponse",
    "GenerateTrelloAuthResponse",
]

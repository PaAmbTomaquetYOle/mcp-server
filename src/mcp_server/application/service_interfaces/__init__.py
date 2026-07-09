"""Inbound service interfaces: the use cases the application exposes.

These are the *driving* side of the hexagon: abstract contracts that describe
what the application can do, consumed by driving adapters (the MCP
``controllers``). They let entry points depend on a use-case abstraction rather
than on a concrete service.

What to put here:
    - Abstract interfaces only (``Protocol`` / ``ABC``) for the application's
      use cases, plus their request/response data shapes if needed.

What NOT to put here:
    - Implementations of these interfaces (those live in ``services``).
    - Any transport, framework, or IO code.
"""

from .collaboration_tool_integration_service_interface import ICollaborationToolIntegrationService
from .dossier_generation_service_interface import IDossierGenerationService
from .jira_auth_service_interface import IJiraAuthService
from .search_connector_service_interface import ConnectorStatus, ISearchConnectorService
from .slack_auth_service_interface import ISlackAuthService
from .slack_workspace_search_service_interface import ISlackWorkspaceSearchService
from .trello_auth_service_interface import ITrelloAuthService

__all__ = [
    "ConnectorStatus",
    "ICollaborationToolIntegrationService",
    "IDossierGenerationService",
    "IJiraAuthService",
    "ISearchConnectorService",
    "ISlackAuthService",
    "ISlackWorkspaceSearchService",
    "ITrelloAuthService",
]
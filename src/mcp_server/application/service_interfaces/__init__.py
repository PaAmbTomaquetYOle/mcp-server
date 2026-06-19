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
from .jira_auth_service_interface import IJiraAuthService

__all__ = [
    "ICollaborationToolIntegrationService",
    "IJiraAuthService",
]
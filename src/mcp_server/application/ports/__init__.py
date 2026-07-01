"""Outbound ports: interfaces the application requires from the outside world.

These are the *driven* side of the hexagon: abstract contracts (typing
``Protocol`` or ``abc.ABC``) describing capabilities the application needs but
does not implement, such as repositories, message senders, or external service
clients.

What to put here:
    - Abstract interfaces only (``Protocol`` / ``ABC``), expressed in terms of
      domain types and plain Python.

What NOT to put here:
    - Concrete implementations. Those are infrastructure ``adapters`` that
      implement these ports (dependency inversion: infrastructure depends on
      these abstractions, not the other way around).
    - Any framework, SDK, or IO code.
"""

from .backend_api import IBackendApiPort
from .collaboration_tool import ICollaborationToolPort
from .jira_auth import IJiraAuthPort
from .token_storage import AuthResult, ITokenStoragePort, TokenData
from .trello_auth import ITrelloAuthPort

__all__ = [
    "AuthResult",
    "IBackendApiPort",
    "ICollaborationToolPort",
    "IJiraAuthPort",
    "ITokenStoragePort",
    "ITrelloAuthPort",
    "TokenData",
]
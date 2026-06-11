"""Application layer: use-case orchestration.

Coordinates the domain to fulfil the application's use cases. It defines the
abstractions (ports and service interfaces) through which it talks to the
outside world, but never the concrete implementations.

Sub-packages:
    - ``ports``              : outbound interfaces the application *requires*.
    - ``service_interfaces`` : inbound interfaces the application *exposes*.
    - ``services``           : concrete use-case implementations.

What to put here:
    - Application services that orchestrate domain objects via ports.
    - The abstract contracts that decouple use cases from infrastructure.

What NOT to put here:
    - Imports from ``infrastructure`` (this layer depends on ``domain`` only,
      plus its own abstractions).
    - Concrete IO, transport, framework, or third-party SDK code (those live in
      ``infrastructure`` as adapters).
"""

from .service_interfaces import ICollaborationToolIntegrationService
from .services import CollaborationToolIntegrationService
from .ports import ICollaborationToolPort

__all__ = [
    "ICollaborationToolIntegrationService",
    "CollaborationToolIntegrationService",
    "ICollaborationToolPort",
]
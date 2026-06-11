"""Application services: concrete use-case implementations.

These classes implement the ``service_interfaces`` and orchestrate the work:
they coordinate domain entities and delegate all external interactions to
``ports``, receiving the concrete adapters via dependency injection.

What to put here:
    - Concrete services implementing the inbound ``service_interfaces``.
    - Use-case orchestration logic (validation flow, transaction boundaries,
      coordination between domain objects and ports).

What NOT to put here:
    - Direct IO, transport, framework, or SDK code: always go through a port so
      the service stays testable with fakes/mocks.
    - Core business invariants that belong in the ``domain`` layer.
"""

from .collaboration_tool_integration_service import CollaborationToolIntegrationService

__all__ = [
    "CollaborationToolIntegrationService",
]
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

from .collaboration_tool import ICollaborationToolPort

__all__ = [
    "ICollaborationToolPort"
]
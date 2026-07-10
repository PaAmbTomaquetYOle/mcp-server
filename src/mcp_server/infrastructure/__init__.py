"""Infrastructure layer: adapters to the outside world.

The outermost layer of the hexagonal architecture. It contains everything
technology- and framework-specific: the MCP server wiring, third-party SDKs
(e.g. Slack), persistence, networking, and configuration.

Sub-packages:
    - ``adapters``    : driven adapters implementing ``application.ports``.
    - ``config``      : settings, environment loading, and DI/composition.
    - ``controllers`` : driving adapters (the MCP entry points).
    - ``dto``         : Pydantic schemas for MCP operation contracts.

Dependency rule:
    Infrastructure may import from ``application`` and ``domain``; those inner
    layers must never import from here.

What NOT to put here:
    - Business rules or use-case orchestration (those belong to ``domain`` and
      ``application`` respectively). Keep this layer about wiring and IO only.
"""

from .adapters import JiraAdapter, SqliteTokenStorage, TrelloAdapter

__all__ = [
    "SqliteTokenStorage",
    "JiraAdapter",
    "TrelloAdapter",
]

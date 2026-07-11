"""Configuration and composition root.

Holds the application's configuration and the wiring that assembles it: reading
settings from the environment, constructing concrete adapters, and injecting
them into application services to build the runnable MCP server.

What to put here:
    - Settings objects (e.g. pydantic-settings) and environment loading.
    - Dependency-injection / composition wiring (build the object graph here).
    - Server bootstrap configuration.

What NOT to put here:
    - Business rules or use-case logic.
    - Secrets or credentials in source: load them from the environment / a
      secrets manager.
"""

from mcp_server.infrastructure.config.server_factory import ServerFactory
from mcp_server.infrastructure.config.settings import McpServerSettings, get_settings

__all__ = ["McpServerSettings", "ServerFactory", "get_settings"]

"""MCP tool controllers.

Defines and registers the server's MCP *tools* (callable actions the client can
invoke, with typed arguments and results).

What to put here:
    - Tool declarations, their argument schemas, and handlers that validate
      input and delegate execution to an application ``service_interface``.

What NOT to put here:
    - Business logic or use-case orchestration: the handler parses/validates the
      request and calls an application service; the real work happens there.
"""

from mcp_server.infrastructure.controllers.tools.ping_controller import (
    PingToolController,
)

__all__ = ["PingToolController"]

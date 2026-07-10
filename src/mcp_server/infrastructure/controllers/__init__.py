"""Driving adapters: the MCP server entry points.

This package exposes the application's capabilities to MCP clients. It is the
*driving* side of the hexagon and maps directly onto the three MCP primitives,
each in its own sub-package:

    - ``prompts``   : MCP prompt definitions.
    - ``resources`` : MCP resource definitions.
    - ``tools``     : MCP tool definitions.

What to put here:
    - Registration and handlers that translate an incoming MCP request into a
      call on an application ``service_interface``, and the result back into an
      MCP response.

What NOT to put here:
    - Business logic or orchestration: controllers stay thin and delegate to
      application services. Domain decisions never live in the transport layer.
"""

from .base_controller import BaseController
from .error_handler import resource_error_handler, tool_error_handler
from .prompts import *
from .resources import *
from .routes import *
from .tools import *

__all__ = [
    "BaseController",
    "OAuthCallbackController",
    "PingToolController",
    "ExtractJiraTasksToolController",
    "ExtractTrelloTasksToolController",
    "ExtractTasksPromptController",
    "JiraLoginPromptController",
    "DossierResourceController",
    "KnowledgeGraphResourceController",
    "SopResourceController",
    "resource_error_handler",
    "tool_error_handler",
]
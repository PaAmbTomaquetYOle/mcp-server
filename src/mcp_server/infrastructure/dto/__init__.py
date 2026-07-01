"""Pydantic schemas for MCP tool inputs and outputs.

Each tool exposes a typed contract through a pair of models (input + output).
FastMCP introspects these to auto-generate the JSON Schema that clients receive
via ``tools/list``, making these models the single source of truth for the
tool's API contract.

Sub-packages mirror the controller structure:
    - ``tools``     : schemas for MCP tool controllers.
    - ``prompts``   : schemas for MCP prompt controllers (future).
    - ``resources`` : schemas for MCP resource controllers (future).

What to put here:
    - Request/response models for each MCP operation, with
      ``Field(description=...)`` on every attribute so the schema is
      self-documenting.

What NOT to put here:
    - Domain entities or application-layer DTOs: those live in their own layers.
"""

from .tools import *

__all__ = [
    "CompleteJiraAuthResponse",
    "CompleteTrelloAuthResponse",
    "GenerateJiraAuthResponse",
    "GenerateTrelloAuthResponse",
    "PingResult",
    "DossierSearchResult",
    "GetDossierResponse",
]
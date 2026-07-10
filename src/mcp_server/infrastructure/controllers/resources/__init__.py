"""MCP resource controllers.

Defines and registers the server's MCP *resources* (addressable, readable data
the client can fetch by URI).

What to put here:
    - Resource declarations and their read handlers, delegating to application
      services to obtain the underlying data.

What NOT to put here:
    - Business logic or data-access details: fetch through an application
      service / port, not directly. Keep these handlers thin.
"""

from .dossier_resource_controller import DossierResourceController
from .knowledge_graph_resource_controller import KnowledgeGraphResourceController
from .sop_resource_controller import SopResourceController

__all__ = [
    "DossierResourceController",
    "KnowledgeGraphResourceController",
    "SopResourceController",
]

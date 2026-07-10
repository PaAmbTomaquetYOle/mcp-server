"""Pydantic schemas for MCP resource outputs.

Only SOP resources need dedicated schemas here (a lightweight list-item shape
and a full-detail shape). Dossier and Knowledge Graph resources reuse the
existing tool DTOs (``DossierSearchResult``, ``QueryExpertsResponse``,
``KnowledgeMapResponse``, ...) since those already match resource semantics.
"""

from .sop_resource_schemas import SopDetail, SopListItem, SopListResponse

__all__ = [
    "SopDetail",
    "SopListItem",
    "SopListResponse",
]

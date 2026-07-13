from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

_TITLE_MAX_LENGTH = 80
_DESCRIPTION_MAX_LENGTH = 200


class SearchDocument(BaseModel):
    """A SOP transformed into a document searchable from Slack's search bar."""

    external_id: str
    title: str
    description: str
    content: str
    link: str
    author: str
    tags: list[str] = Field(default_factory=list)
    origin_channel: str
    date_updated: str

    @classmethod
    def from_sop(cls, sop: dict[str, Any], base_url: str) -> SearchDocument:
        content: str = sop["content"]
        # The backend's /sops response now always includes a title (BE-18).
        # Fall back to the derived first-line title only for stale cached
        # entries fetched before that rollout.
        explicit_title = sop.get("title")
        if explicit_title:
            title = explicit_title[:_TITLE_MAX_LENGTH]
        else:
            first_line = content.splitlines()[0] if content else ""
            title = first_line[:_TITLE_MAX_LENGTH]

        return cls(
            external_id=sop["id"],
            title=title,
            description=content[:_DESCRIPTION_MAX_LENGTH],
            content=content,
            link=f"{base_url.rstrip('/')}/{sop['id']}",
            author=sop["author"],
            tags=list(sop.get("tags", [])),
            origin_channel=sop["origin_channel"],
            date_updated=str(sop["updated_at"])[:10],
        )


class SearchQuery(BaseModel):
    """An incoming search request from Slack's Real-Time Search API."""

    query: str
    filters: dict[str, Any] = Field(default_factory=dict)

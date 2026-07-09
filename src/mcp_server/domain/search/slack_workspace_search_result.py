from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SlackWorkspaceSearchResult(BaseModel):
    """A single result from Slack's internal workspace search (assistant.search.context)."""

    content_type: str
    text: str
    permalink: str | None = None
    timestamp: str | None = None

    @classmethod
    def from_api_item(cls, content_type: str, item: dict[str, Any]) -> SlackWorkspaceSearchResult:
        text = ""
        if content_type == "messages":
            text = item.get("text", "")
        elif content_type == "files":
            text = item.get("title", "")
        elif content_type == "channels":
            text = item.get("name", "")
        elif content_type == "users":
            text = item.get("real_name") or item.get("name", "")

        return cls(
            content_type=content_type,
            text=text,
            permalink=item.get("permalink"),
            timestamp=item.get("ts"),
        )

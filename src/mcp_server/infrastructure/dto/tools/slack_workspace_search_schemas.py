from pydantic import BaseModel, Field


class SlackWorkspaceSearchResultItem(BaseModel):
    content_type: str = Field(title="Content Type")
    text: str = Field(title="Text")
    permalink: str | None = Field(default=None, title="Permalink")
    timestamp: str | None = Field(default=None, title="Timestamp")


class SlackWorkspaceSearchResponse(BaseModel):
    query: str = Field(title="Query")
    results: list[SlackWorkspaceSearchResultItem] = Field(default_factory=list, title="Matching Results")
    count: int = Field(title="Result Count")

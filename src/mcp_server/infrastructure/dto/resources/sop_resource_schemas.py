from pydantic import BaseModel, Field


class SopListItem(BaseModel):
    """A single SOP's identity, as shown in the browsable SOP list resource."""

    id: str = Field(title="SOP ID")
    title: str = Field(title="Title")
    tags: list[str] = Field(default_factory=list, title="Tags")


class SopListResponse(BaseModel):
    """All SOPs currently cached for Slack search."""

    sops: list[SopListItem] = Field(default_factory=list, title="SOPs")
    count: int = Field(title="Result Count")


class SopDetail(BaseModel):
    """Full content of a single SOP."""

    id: str = Field(title="SOP ID")
    title: str = Field(title="Title")
    content: str = Field(title="Content")
    author: str = Field(title="Author")
    tags: list[str] = Field(default_factory=list, title="Tags")
    origin_channel: str = Field(title="Origin Channel")
    version: int = Field(title="Version")
    created_at: str = Field(title="Created At")
    updated_at: str = Field(title="Updated At")

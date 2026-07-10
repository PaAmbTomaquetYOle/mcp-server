from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    external_id: str = Field(title="SOP ID")
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    link: str = Field(title="Link")
    author: str = Field(title="Author")
    tags: list[str] = Field(default_factory=list, title="Tags")
    date_updated: str = Field(title="Date Updated")


class ConnectorStatusResponse(BaseModel):
    backend_reachable: bool = Field(title="Backend Reachable")
    cache_size: int = Field(title="Cached Documents")
    last_refresh: str | None = Field(default=None, title="Last Refresh Timestamp")
    is_stale: bool = Field(title="Cache Is Stale")


class SearchQueryTestResponse(BaseModel):
    query: str = Field(title="Query")
    results: list[SearchResultItem] = Field(default_factory=list, title="Matching Documents")
    count: int = Field(title="Result Count")


class RefreshResponse(BaseModel):
    total_indexed: int = Field(title="Total Documents Indexed")
    status: str = Field(title="Refresh Status")


class SearchAnalyticsResponse(BaseModel):
    total_searches: int = Field(title="Total Searches")
    cache_hits: int = Field(title="Cache Hits")
    cache_misses: int = Field(title="Cache Misses")

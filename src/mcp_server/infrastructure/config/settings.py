"""Application settings for the MCP server."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings sourced from environment variables and optional `.env` files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000
    app_name: str = "BrainTrust MCP Server"
    log_level: str = "INFO"
    jira_auth_base_url: str = "https://auth.atlassian.com/authorize"
    jira_client_id: str = "braintrust-jira-client"
    jira_redirect_uri: str = "https://braintrust.local/oauth/jira/callback"
    trello_auth_base_url: str = "https://trello.com/1/authorize"
    trello_client_id: str = "braintrust-trello-client"
    trello_redirect_uri: str = "https://braintrust.local/oauth/trello/callback"
    search_results_base_url: str = "https://braintrust.local/knowledge"
    search_max_results: int = Field(default=5, ge=1, le=10)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()

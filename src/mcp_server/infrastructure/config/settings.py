from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_SERVER_",
        env_file=".env",
        extra="ignore",
    )

    name: str = "OffBoardMe-mcp"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    debug: bool = False

    base_url: str = ""

    jira_server_url: str = ""
    jira_client_id: str = ""
    jira_client_secret: str = ""
    jira_redirect_uri: str = ""
    jira_cloud_id: str = ""
    trello_api_key: str = ""
    trello_api_secret: str = ""
    trello_app_name: str = "OffBoardMe"
    token_db_path: str = "data/tokens.db"

    backend_api_url: str = "http://localhost:8001/api/v1"
    backend_client_id: str = ""
    backend_client_secret: str = ""

    kafka_bootstrap_servers: str = "localhost:9092"

    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_client_id: str = ""
    slack_client_secret: str = ""
    slack_redirect_uri: str = ""
    sop_cache_ttl_seconds: int = 60
    sop_base_url: str = ""

    # generate_dossier tool (DossierGenerationService)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    dossier_generation_max_tool_iterations: int = 4

    @model_validator(mode="after")
    def _derive_urls(self) -> Self:
        if not self.base_url:
            self.base_url = f"http://localhost:{self.port}"
        if not self.jira_redirect_uri:
            self.jira_redirect_uri = f"{self.base_url}/callback"
        if not self.sop_base_url:
            self.sop_base_url = f"{self.base_url}/sops"
        if not self.slack_redirect_uri:
            self.slack_redirect_uri = f"{self.base_url}/slack/oauth/callback"
        return self


# Backwards-compatible alias used by older modules and tests.
Settings = McpServerSettings


def get_settings() -> McpServerSettings:
    """Build the MCP server settings from the current environment."""

    return McpServerSettings()

from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_SERVER_",
        env_file=".env",
        extra="ignore",
    )

    name: str = "BrainTrust-mcp"
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
    trello_app_name: str = "BrainTrust"
    token_db_path: str = "data/tokens.db"

    @model_validator(mode="after")
    def _derive_urls(self) -> Self:
        if not self.base_url:
            self.base_url = f"http://localhost:{self.port}"
        if not self.jira_redirect_uri:
            self.jira_redirect_uri = f"{self.base_url}/callback"
        return self

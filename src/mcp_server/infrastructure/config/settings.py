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

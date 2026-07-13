import ssl
from typing import Self

from cryptography.fernet import Fernet
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_TOKEN_ENCRYPTION_KEY_HELP = (
    "MCP_SERVER_TOKEN_ENCRYPTION_KEY is missing or invalid.\n"
    "This key is required to encrypt OAuth tokens at rest.\n"
    "Generate one with:\n"
    '  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"\n'
    "Then set MCP_SERVER_TOKEN_ENCRYPTION_KEY=<generated-key> in your .env file."
)


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
    jira_auth_base_url: str = "https://auth.atlassian.com/authorize"
    trello_api_key: str = ""
    trello_api_secret: str = ""
    trello_app_name: str = "OffBoardMe"
    trello_client_id: str = ""
    trello_redirect_uri: str = ""
    trello_auth_base_url: str = "https://trello.com/1/authorize"
    token_db_path: str = "data/tokens.db"
    token_encryption_key: str

    backend_api_url: str = "http://localhost:8888/api/v1"
    backend_client_id: str = ""
    backend_client_secret: str = ""

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "offboardme-mcp-server"
    kafka_topic_prefix: str = "offboarding"
    kafka_consumer_group_id: str = "mcp-server-consumer"
    # Transport security — mirrors backend/src/app/main.py's Kafka settings.
    # Defaults to PLAINTEXT so local dev without a broker (or a plaintext
    # broker) is unaffected; the shared docker-compose broker requires
    # SASL_SSL + SCRAM-SHA-512, matching backend and slack-agent.
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = "SCRAM-SHA-512"
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    kafka_ssl_cafile: str = ""

    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_client_id: str = ""
    slack_client_secret: str = ""
    slack_redirect_uri: str = ""
    sop_cache_ttl_seconds: int = 60
    sop_base_url: str = ""
    search_results_base_url: str = "https://braintrust.local/knowledge"
    search_max_results: int = 3

    # generate_dossier tool (DossierGenerationService)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    dossier_generation_max_tool_iterations: int = 4
    dossier_generation_max_tokens: int = 4096
    # MCP-15: the annual review scope is exhaustive (all accumulated knowledge,
    # not just recent activity) and routinely needs more headroom than the
    # offboarding/monthly-review default above.
    dossier_generation_max_tokens_annual: int = 8192

    @field_validator("token_encryption_key")
    @classmethod
    def _validate_token_encryption_key(cls, value: str) -> str:
        try:
            Fernet(value.encode())
        except Exception as exc:
            raise ValueError(_TOKEN_ENCRYPTION_KEY_HELP) from exc
        return value

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
        if not self.trello_client_id:
            self.trello_client_id = self.trello_api_key
        if not self.trello_redirect_uri:
            self.trello_redirect_uri = self.base_url
        return self

    @property
    def app_name(self) -> str:
        """Backward-compatible alias for older code paths."""

        return self.name


# Backwards-compatible alias used by older modules and tests.
Settings = McpServerSettings


def get_settings() -> McpServerSettings:
    """Build the MCP server settings from the current environment."""

    return McpServerSettings()


def kafka_connection_kwargs(settings: McpServerSettings) -> dict:
    """Build the security-related kwargs shared by the Kafka producer and consumer.

    Mirrors backend's ``_kafka_connection_kwargs`` (src/app/main.py) so all
    three services agree on how PLAINTEXT/SASL_SSL are configured. Defaults
    to PLAINTEXT (no extra kwargs) so local dev/tests are unaffected.

    Args:
        settings: Application settings holding the Kafka security configuration.

    Returns:
        dict: Keyword arguments to merge into the producer/consumer constructor.
    """
    kwargs: dict = {"security_protocol": settings.kafka_security_protocol}
    protocol = settings.kafka_security_protocol.upper()
    if protocol.startswith("SASL"):
        kwargs["sasl_mechanism"] = settings.kafka_sasl_mechanism
        kwargs["sasl_plain_username"] = settings.kafka_sasl_username
        kwargs["sasl_plain_password"] = settings.kafka_sasl_password
    if protocol.endswith("SSL"):
        kwargs["ssl_context"] = ssl.create_default_context(
            cafile=settings.kafka_ssl_cafile or None
        )
    return kwargs

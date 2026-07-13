import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from mcp_server.infrastructure.config.settings import McpServerSettings

_VALID_KEY = Fernet.generate_key().decode()


class TestMcpServerSettings:
    def test_defaults(self):
        settings = McpServerSettings(
            token_encryption_key=_VALID_KEY,
            _env_file=None,
        )

        assert settings.name == "OffBoardMe-mcp"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.log_level == "INFO"
        assert settings.debug is False

    def test_override_via_constructor(self):
        settings = McpServerSettings(
            name="custom",
            host="127.0.0.1",
            port=9000,
            log_level="DEBUG",
            debug=True,
            token_encryption_key=_VALID_KEY,
            _env_file=None,
        )

        assert settings.name == "custom"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"
        assert settings.debug is True

    def test_base_url_defaults_to_localhost_with_port(self):
        settings = McpServerSettings(token_encryption_key=_VALID_KEY, _env_file=None)

        assert settings.base_url == "http://localhost:8000"

    def test_base_url_uses_custom_port(self):
        settings = McpServerSettings(port=9000, token_encryption_key=_VALID_KEY, _env_file=None)

        assert settings.base_url == "http://localhost:9000"

    def test_redirect_uri_derived_from_base_url(self):
        settings = McpServerSettings(token_encryption_key=_VALID_KEY, _env_file=None)

        assert settings.jira_redirect_uri == "http://localhost:8000/callback"

    def test_redirect_uri_derived_from_custom_base_url(self):
        settings = McpServerSettings(
            base_url="https://mcp.example.com",
            token_encryption_key=_VALID_KEY,
            _env_file=None,
        )

        assert settings.jira_redirect_uri == "https://mcp.example.com/callback"

    def test_dossier_generation_max_tokens_default(self):
        settings = McpServerSettings(token_encryption_key=_VALID_KEY, _env_file=None)

        assert settings.dossier_generation_max_tokens == 4096

    def test_dossier_generation_max_tokens_override(self):
        settings = McpServerSettings(
            dossier_generation_max_tokens=8192,
            token_encryption_key=_VALID_KEY,
            _env_file=None,
        )

        assert settings.dossier_generation_max_tokens == 8192

    def test_explicit_redirect_uri_not_overridden(self):
        settings = McpServerSettings(
            base_url="https://mcp.example.com",
            jira_redirect_uri="https://custom.example.com/oauth/callback",
            token_encryption_key=_VALID_KEY,
            _env_file=None,
        )

        assert settings.jira_redirect_uri == "https://custom.example.com/oauth/callback"

    def test_missing_token_encryption_key_raises(self):
        with pytest.raises(ValidationError, match="token_encryption_key"):
            McpServerSettings(_env_file=None)

    def test_invalid_token_encryption_key_raises(self):
        with pytest.raises(ValidationError, match="MCP_SERVER_TOKEN_ENCRYPTION_KEY"):
            McpServerSettings(token_encryption_key="not-a-valid-fernet-key", _env_file=None)

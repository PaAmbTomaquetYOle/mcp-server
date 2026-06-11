from mcp_server.infrastructure.config.settings import McpServerSettings


class TestMcpServerSettings:
    def test_defaults(self):
        settings = McpServerSettings(
            _env_file=None,
        )

        assert settings.name == "BrainTrust-mcp"
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
            _env_file=None,
        )

        assert settings.name == "custom"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"
        assert settings.debug is True

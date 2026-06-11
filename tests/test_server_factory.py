import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.config.server_factory import ServerFactory
from tests.conftest import get_tool_names


class TestServerFactory:
    def test_create_returns_fastmcp_instance(self, make_settings):
        factory = ServerFactory.get_instance(make_settings())

        server = factory.create()

        assert isinstance(server, FastMCP)
        assert server.name == "test-server"

    def test_create_registers_ping_tool(self, server):
        assert "ping" in get_tool_names(server)

    def test_singleton_returns_same_instance(self, make_settings):
        settings = make_settings()

        first = ServerFactory.get_instance(settings)
        second = ServerFactory.get_instance(settings)

        assert first is second

    def test_direct_init_raises(self, make_settings):
        with pytest.raises(TypeError, match="singleton"):
            ServerFactory(make_settings())

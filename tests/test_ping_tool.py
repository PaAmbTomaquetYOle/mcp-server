import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.controllers.tools import PingToolController
from tests.conftest import get_tool_names


class TestPingToolController:
    def test_register_adds_ping_tool(self):
        server = FastMCP("test")
        controller = PingToolController(server)

        controller.register()

        assert "ping" in get_tool_names(server)

    @pytest.mark.anyio
    async def test_ping_returns_pong(self):
        controller = PingToolController(FastMCP("test"))

        result = await controller.ping()

        assert result == "pong"

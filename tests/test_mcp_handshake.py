import pytest
from mcp.server import FastMCP
from starlette.testclient import TestClient

from mcp_server.infrastructure.config import ServerFactory
from tests.conftest import parse_sse_data


class TestMcpHandshake:
    @pytest.fixture
    def server(self, make_settings) -> FastMCP:
        settings = make_settings(name="test-handshake")
        factory = ServerFactory.get_instance(settings)
        return factory.create()

    @pytest.fixture
    def client(self, server: FastMCP):
        app = server.streamable_http_app()
        with TestClient(app) as tc:
            yield tc

    def _initialize_payload(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0",
                },
            },
        }

    def test_initialize_returns_200(self, client: TestClient):
        response = client.post(
            "/mcp",
            json=self._initialize_payload(),
            headers={"Accept": "application/json, text/event-stream"},
        )

        assert response.status_code == 200
        data = parse_sse_data(response.text)
        assert "result" in data
        assert "serverInfo" in data["result"]

    def test_initialize_returns_server_name(self, client: TestClient):
        response = client.post(
            "/mcp",
            json=self._initialize_payload(),
            headers={"Accept": "application/json, text/event-stream"},
        )

        data = parse_sse_data(response.text)
        assert data["result"]["serverInfo"]["name"] == "test-handshake"

    def test_ping_tool_via_mcp(self, client: TestClient):
        init_response = client.post(
            "/mcp",
            json=self._initialize_payload(),
            headers={"Accept": "application/json, text/event-stream"},
        )
        session_id = init_response.headers.get("mcp-session-id")

        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        client.post(
            "/mcp",
            json=initialized_notification,
            headers={
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

        call_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "ping",
                "arguments": {},
            },
        }
        call_response = client.post(
            "/mcp",
            json=call_payload,
            headers={
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id,
            },
        )

        assert call_response.status_code == 200
        data = parse_sse_data(call_response.text)
        content_items = data["result"]["content"]
        assert any("pong" in item["text"] for item in content_items)

"""HTTP smoke tests for the MCP server app."""

from __future__ import annotations

from starlette.testclient import TestClient

from mcp_server.app import create_app

from .conftest import TEST_TOKEN_ENCRYPTION_KEY


def test_health_returns_ok(monkeypatch) -> None:
    monkeypatch.setenv("MCP_SERVER_TOKEN_ENCRYPTION_KEY", TEST_TOKEN_ENCRYPTION_KEY)

    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "mcp-server"
    assert response.json()["mode"] == "mcp-http"

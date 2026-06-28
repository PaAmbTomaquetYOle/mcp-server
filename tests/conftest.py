from __future__ import annotations

import json

import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.config import McpServerSettings, ServerFactory


@pytest.fixture(autouse=True)
def _reset_server_factory():
    ServerFactory.reset()
    yield
    ServerFactory.reset()


@pytest.fixture
def make_settings():
    def _factory(**overrides) -> McpServerSettings:
        defaults: dict = {"name": "test-server", "_env_file": None}
        defaults.update(overrides)
        return McpServerSettings(**defaults)

    return _factory


@pytest.fixture
def server(make_settings) -> FastMCP:
    settings = make_settings()
    factory = ServerFactory.get_instance(settings)
    return factory.create()


def get_tool_names(server: FastMCP) -> list[str]:
    return [t.name for t in server._tool_manager.list_tools()]


def parse_sse_data(response_text: str) -> dict:
    for line in response_text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: "):])
    raise ValueError(f"No SSE data found in response: {response_text}")


# === Mock fixtures para APIs externas ===

from unittest.mock import AsyncMock

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def mock_token_storage():
    """Reusable mock for ITokenStoragePort (driven port)."""
    storage = AsyncMock()
    storage.save_tokens = AsyncMock()
    storage.get_tokens = AsyncMock(return_value=None)
    storage.delete_tokens = AsyncMock()
    return storage

@pytest.fixture
def mock_jira_port():
    """Reusable mock for IJiraCollaborationToolPort."""
    port = AsyncMock()
    port.get_pending_tasks = AsyncMock(return_value=[])
    return port

@pytest.fixture
def mock_trello_port():
    """Reusable mock for ITrelloCollaborationToolPort."""
    port = AsyncMock()
    port.get_pending_tasks = AsyncMock(return_value=[])
    return port

@pytest.fixture
def mock_jira_auth_port():
    """Reusable mock for IJiraAuthPort."""
    port = AsyncMock()
    port.generate_auth_url = AsyncMock(
        return_value="https://auth.atlassian.com/authorize?..."
    )
    port.exchange_auth_code = AsyncMock(return_value={
        "email": "test@example.com",
        "access_token": "mock-access-token",
        "refresh_token": "mock-refresh-token",
        "expires_at": 9999999999,
    })
    return port

@pytest.fixture
def mock_trello_auth_port():
    """Reusable mock for ITrelloAuthPort."""
    port = AsyncMock()
    port.generate_auth_url = AsyncMock(
        return_value="https://trello.com/1/authorize?key=mock"
    )
    port.store_token = AsyncMock(return_value="mock-user")
    return port

@pytest.fixture
def mock_backend_http_client():
    """Reusable mock for HTTP calls to the backend API."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client

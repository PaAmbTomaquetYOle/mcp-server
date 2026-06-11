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

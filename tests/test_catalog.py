"""Tests for MCP prompt and tool behavior."""

from __future__ import annotations

import json

from mcp_server.application.services.catalog import (
    OAuthMemoryStore,
    build_search_link,
    create_mcp_server,
)
from mcp_server.infrastructure.config.settings import Settings

from .conftest import TEST_TOKEN_ENCRYPTION_KEY


def _settings() -> Settings:
    return Settings(_env_file=None, token_encryption_key=TEST_TOKEN_ENCRYPTION_KEY)


def test_oauth_store_tracks_pending_and_completed_sessions() -> None:
    settings = _settings()
    store = OAuthMemoryStore()

    pending = store.generate_authorization("jira", "U123", settings)
    assert store.auth_status("jira", "U123") == "pending"
    assert "state=" in pending.authorization_url

    completed = store.complete_authorization("jira", "U123", "code-123", pending.state)
    assert store.auth_status("jira", "U123") == "authenticated"
    assert completed.authorization_code == "code-123"


def test_search_tool_returns_matching_fixture_results() -> None:
    server = create_mcp_server(_settings())
    tool = server._tool_manager.get_tool("test_search_query")

    result = tool.fn(query="How do I handle a rollback incident?")  # pyright: ignore[reportFunctionMemberAccess]
    payload = json.loads(result)

    assert payload["results"]
    assert payload["results"][0]["external_id"] == "kb-incident-rollback"
    assert payload["results"][0]["link"] == "https://braintrust.local/knowledge/incident-rollback"


def test_build_search_link_avoids_duplicate_path_segments() -> None:
    assert (
        build_search_link(
            "https://braintrust.local/knowledge",
            "https://braintrust.local/knowledge/incident-rollback",
        )
        == "https://braintrust.local/knowledge/incident-rollback"
    )

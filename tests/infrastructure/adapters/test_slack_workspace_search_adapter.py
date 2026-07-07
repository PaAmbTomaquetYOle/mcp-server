from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.domain import SlackApiException
from mcp_server.infrastructure.adapters.slack_workspace_search import SlackWorkspaceSearchAdapter


@pytest.fixture
def adapter():
    return SlackWorkspaceSearchAdapter()


def _mock_response(json_data, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: json_data
    response.raise_for_status = lambda: None
    return response


def _patched_client(response):
    patcher = patch("mcp_server.infrastructure.adapters.slack_workspace_search.AsyncClient")
    mock_client_cls = patcher.start()
    client = AsyncMock()
    client.post = AsyncMock(return_value=response)
    mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
    mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
    return patcher, client


class TestSearchWorkspace:
    @pytest.mark.anyio
    async def test_sends_query_and_token(self, adapter):
        response_data = {"ok": True, "results": {"messages": {"items": []}}}
        patcher, client = _patched_client(_mock_response(response_data))
        try:
            await adapter.search_workspace("xoxp-token", "deploy", {})
        finally:
            patcher.stop()

        client.post.assert_awaited_once()
        url, kwargs = client.post.await_args.args[0], client.post.await_args.kwargs
        assert url.endswith("assistant.search.context")
        assert kwargs["headers"]["Authorization"] == "Bearer xoxp-token"
        assert kwargs["json"]["query"] == "deploy"

    @pytest.mark.anyio
    async def test_no_action_token_included(self, adapter):
        response_data = {"ok": True, "results": {}}
        patcher, client = _patched_client(_mock_response(response_data))
        try:
            await adapter.search_workspace("xoxp-token", "deploy", {})
        finally:
            patcher.stop()

        assert "action_token" not in client.post.await_args.kwargs["json"]

    @pytest.mark.anyio
    async def test_maps_results_across_content_types(self, adapter):
        response_data = {
            "ok": True,
            "results": {
                "messages": {"items": [{"text": "deploy failed"}]},
                "files": {"items": [{"title": "runbook.pdf"}]},
            },
        }
        patcher, client = _patched_client(_mock_response(response_data))
        try:
            results = await adapter.search_workspace("xoxp-token", "deploy", {})
        finally:
            patcher.stop()

        assert len(results) == 2
        content_types = {r.content_type for r in results}
        assert content_types == {"messages", "files"}

    @pytest.mark.anyio
    async def test_passes_filters_as_params(self, adapter):
        response_data = {"ok": True, "results": {}}
        patcher, client = _patched_client(_mock_response(response_data))
        try:
            await adapter.search_workspace("xoxp-token", "deploy", {"content_types": ["messages"]})
        finally:
            patcher.stop()

        assert client.post.await_args.kwargs["json"]["content_types"] == ["messages"]

    @pytest.mark.anyio
    async def test_raises_on_slack_not_ok(self, adapter):
        patcher, _ = _patched_client(_mock_response({"ok": False, "error": "missing_query"}))
        try:
            with pytest.raises(SlackApiException, match="missing_query"):
                await adapter.search_workspace("xoxp-token", "", {})
        finally:
            patcher.stop()

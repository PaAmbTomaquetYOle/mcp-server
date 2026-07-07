from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.domain import SlackApiException
from mcp_server.infrastructure.adapters.slack_api import SlackApiAdapter


@pytest.fixture
def adapter():
    return SlackApiAdapter(bot_token="xoxb-test-token")


def _mock_response(json_data, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: json_data
    response.raise_for_status = lambda: None
    return response


def _patched_client(response):
    patcher = patch("mcp_server.infrastructure.adapters.slack_api.AsyncClient")
    mock_client_cls = patcher.start()
    client = AsyncMock()
    client.post = AsyncMock(return_value=response)
    mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
    mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
    return patcher, client


class TestCompleteSearchSuccess:
    @pytest.mark.anyio
    async def test_posts_results_to_slack(self, adapter):
        patcher, client = _patched_client(_mock_response({"ok": True}))
        try:
            await adapter.complete_search_success("fx1", [{"title": "SOP"}])
        finally:
            patcher.stop()

        client.post.assert_awaited_once()
        url, kwargs = client.post.await_args.args[0], client.post.await_args.kwargs
        assert url.endswith("functions.completeSuccess")
        assert kwargs["json"]["function_execution_id"] == "fx1"
        assert kwargs["headers"]["Authorization"] == "Bearer xoxb-test-token"

    @pytest.mark.anyio
    async def test_raises_on_slack_not_ok(self, adapter):
        patcher, _ = _patched_client(_mock_response({"ok": False, "error": "invalid_arguments"}))
        try:
            with pytest.raises(SlackApiException, match="invalid_arguments"):
                await adapter.complete_search_success("fx1", [])
        finally:
            patcher.stop()


class TestCompleteSearchError:
    @pytest.mark.anyio
    async def test_posts_error_to_slack(self, adapter):
        patcher, client = _patched_client(_mock_response({"ok": True}))
        try:
            await adapter.complete_search_error("fx1", "backend unreachable")
        finally:
            patcher.stop()

        kwargs = client.post.await_args.kwargs
        assert kwargs["json"]["error"] == "backend unreachable"


class TestUpdateUserConnection:
    @pytest.mark.anyio
    async def test_posts_connection_status(self, adapter):
        patcher, client = _patched_client(_mock_response({"ok": True}))
        try:
            await adapter.update_user_connection("U1", "connected")
        finally:
            patcher.stop()

        kwargs = client.post.await_args.kwargs
        assert kwargs["json"]["user_id"] == "U1"
        assert kwargs["json"]["status"] == "connected"


class TestPresentEntityDetails:
    @pytest.mark.anyio
    async def test_posts_entity_metadata(self, adapter):
        patcher, client = _patched_client(_mock_response({"ok": True}))
        try:
            await adapter.present_entity_details("trigger1", {"foo": "bar"})
        finally:
            patcher.stop()

        kwargs = client.post.await_args.kwargs
        assert kwargs["json"]["trigger_id"] == "trigger1"
        assert kwargs["json"]["metadata"] == {"foo": "bar"}

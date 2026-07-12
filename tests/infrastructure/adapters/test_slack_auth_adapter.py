from unittest.mock import AsyncMock, Mock
from urllib.parse import parse_qs, urlparse

import pytest
from httpx2 import HTTPStatusError, Request, Response

from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.adapters.slack_auth import SlackAuthAdapter


@pytest.fixture
def token_storage():
    storage = AsyncMock()
    storage.save_tokens = AsyncMock()
    return storage


@pytest.fixture
def http_client():
    return AsyncMock()


@pytest.fixture
def adapter(token_storage, http_client):
    return SlackAuthAdapter(
        token_storage_port=token_storage,
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:8000/slack/oauth/callback",
        client=http_client,
    )


def _configure_http_client(mock_client, oauth_response):
    resp = Mock()
    resp.json.return_value = oauth_response
    resp.raise_for_status = Mock()
    mock_client.post.return_value = resp


class TestGenerateAuthUrl:
    @pytest.mark.anyio
    async def test_returns_valid_slack_url(self, adapter):
        url = await adapter.generate_auth_url("some-state")

        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "slack.com"
        assert parsed.path == "/oauth/v2/authorize"

    @pytest.mark.anyio
    async def test_includes_required_params(self, adapter):
        url = await adapter.generate_auth_url("some-state")

        params = parse_qs(urlparse(url).query)
        assert params["client_id"] == ["test-client-id"]
        assert params["redirect_uri"] == ["http://localhost:8000/slack/oauth/callback"]
        assert params["state"] == ["some-state"]

    @pytest.mark.anyio
    async def test_includes_required_user_scopes(self, adapter):
        url = await adapter.generate_auth_url("some-state")

        params = parse_qs(urlparse(url).query)
        scopes = params["user_scope"][0].split(",")
        assert "search:read.public" in scopes
        assert "search:read.private" in scopes
        assert "search:read.im" in scopes
        assert "search:read.mpim" in scopes
        assert "search:read.files" in scopes
        assert "search:read.users" in scopes


class TestExchangeAuthCode:
    @pytest.mark.anyio
    async def test_success_stores_token_under_slack_user_id(self, adapter, token_storage, http_client):
        oauth_response = {
            "ok": True,
            "team": {"id": "T1"},
            "authed_user": {"id": "U1", "access_token": "xoxp-new-token"},
        }
        _configure_http_client(http_client, oauth_response)

        result = await adapter.exchange_auth_code("auth-code-123")

        assert result["slack_user_id"] == "U1"
        assert result["team_id"] == "T1"
        assert result["access_token"] == "xoxp-new-token"
        token_storage.save_tokens.assert_awaited_once_with("U1", "xoxp-new-token", "", 0)

    @pytest.mark.anyio
    async def test_sends_correct_payload(self, adapter, token_storage, http_client):
        oauth_response = {"ok": True, "team": {"id": "T1"}, "authed_user": {"id": "U1", "access_token": "xoxp-t"}}
        _configure_http_client(http_client, oauth_response)

        await adapter.exchange_auth_code("the-code")

        http_client.post.assert_awaited_once()
        call_kwargs = http_client.post.call_args
        assert call_kwargs[1]["data"]["code"] == "the-code"
        assert call_kwargs[1]["data"]["client_id"] == "test-client-id"
        assert call_kwargs[1]["data"]["client_secret"] == "test-client-secret"
        assert call_kwargs[1]["data"]["redirect_uri"] == "http://localhost:8000/slack/oauth/callback"

    @pytest.mark.anyio
    async def test_slack_not_ok_raises_auth_code_exchange_exception(self, adapter, http_client):
        oauth_response = {"ok": False, "error": "invalid_code"}
        _configure_http_client(http_client, oauth_response)

        with pytest.raises(AuthCodeExchangeException, match="invalid_code"):
            await adapter.exchange_auth_code("bad-code")

    @pytest.mark.anyio
    async def test_http_error_raises_auth_code_exchange_exception(self, adapter, http_client):
        mock_response_obj = Mock()
        mock_response_obj.raise_for_status.side_effect = HTTPStatusError(
            "Bad Request",
            request=Request("POST", "https://slack.com/api/oauth.v2.access"),
            response=Response(400, text="invalid_grant"),
        )
        http_client.post.return_value = mock_response_obj

        with pytest.raises(AuthCodeExchangeException):
            await adapter.exchange_auth_code("bad-code")

    @pytest.mark.anyio
    async def test_network_error_raises_auth_code_exchange_exception(self, adapter, http_client):
        http_client.post.side_effect = ConnectionError("network down")

        with pytest.raises(AuthCodeExchangeException):
            await adapter.exchange_auth_code("some-code")

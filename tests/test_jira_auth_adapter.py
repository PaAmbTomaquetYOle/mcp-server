from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from httpx2 import HTTPStatusError, Request, Response

from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.adapters.jira_auth import JiraAuthAdapter


@pytest.fixture
def token_storage():
    storage = AsyncMock()
    storage.save_tokens = AsyncMock()
    return storage


@pytest.fixture
def adapter(token_storage):
    return JiraAuthAdapter(
        token_storage_port=token_storage,
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:8080/callback",
    )


class TestGenerateAuthUrl:
    @pytest.mark.anyio
    async def test_returns_valid_atlassian_url(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "auth.atlassian.com"
        assert parsed.path == "/authorize"

    @pytest.mark.anyio
    async def test_includes_required_params(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        params = parse_qs(urlparse(url).query)
        assert params["client_id"] == ["test-client-id"]
        assert params["redirect_uri"] == ["http://localhost:8080/callback"]
        assert params["state"] == ["user-1"]
        assert params["response_type"] == ["code"]
        assert params["audience"] == ["api.atlassian.com"]
        assert params["prompt"] == ["consent"]

    @pytest.mark.anyio
    async def test_includes_required_scopes(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        params = parse_qs(urlparse(url).query)
        scopes = params["scope"][0].split()
        assert "read:jira-work" in scopes
        assert "read:jira-user" in scopes
        assert "offline_access" in scopes


class TestExchangeAuthCode:
    @pytest.mark.anyio
    async def test_success_stores_tokens(self, adapter, token_storage):
        api_response = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 3600,
        }
        with patch("mcp_server.infrastructure.adapters.jira_auth.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = api_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.post.return_value = mock_response_obj

            result = await adapter.exchange_auth_code("user-1", "auth-code-123")

        assert result["access_token"] == "new-access-token"
        assert result["refresh_token"] == "new-refresh-token"
        assert result["expires_at"] > 0
        token_storage.save_tokens.assert_awaited_once_with(
            "user-1",
            "new-access-token",
            "new-refresh-token",
            result["expires_at"],
        )

    @pytest.mark.anyio
    async def test_sends_correct_payload(self, adapter, token_storage):
        with patch("mcp_server.infrastructure.adapters.jira_auth.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = {
                "access_token": "at",
                "refresh_token": "rt",
                "expires_in": 3600,
            }
            mock_response_obj.raise_for_status = Mock()
            mock_client.post.return_value = mock_response_obj

            await adapter.exchange_auth_code("user-1", "the-code")

        mock_client.post.assert_awaited_once()
        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["json"]["grant_type"] == "authorization_code"
        assert call_kwargs[1]["json"]["code"] == "the-code"
        assert call_kwargs[1]["json"]["client_id"] == "test-client-id"
        assert call_kwargs[1]["json"]["client_secret"] == "test-client-secret"
        assert call_kwargs[1]["json"]["redirect_uri"] == "http://localhost:8080/callback"

    @pytest.mark.anyio
    async def test_http_error_raises_auth_code_exchange_exception(self, adapter):
        with patch("mcp_server.infrastructure.adapters.jira_auth.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_response_obj = Mock()
            mock_response_obj.raise_for_status.side_effect = HTTPStatusError(
                "Bad Request",
                request=Request("POST", "https://auth.atlassian.com/oauth/token"),
                response=Response(400, text="invalid_grant"),
            )
            mock_client.post.return_value = mock_response_obj

            with pytest.raises(AuthCodeExchangeException) as exc_info:
                await adapter.exchange_auth_code("user-1", "bad-code")

        assert "user-1" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_network_error_raises_auth_code_exchange_exception(self, adapter):
        with patch("mcp_server.infrastructure.adapters.jira_auth.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.post.side_effect = ConnectionError("network down")

            with pytest.raises(AuthCodeExchangeException) as exc_info:
                await adapter.exchange_auth_code("user-1", "some-code")

        assert "user-1" in str(exc_info.value)

from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlparse

import pytest

from mcp_server.domain.exceptions import TrelloTokenStorageException
from mcp_server.infrastructure.adapters.trello_auth import TrelloAuthAdapter


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
    return TrelloAuthAdapter(
        token_storage_port=token_storage,
        api_key="test-api-key",
        app_name="TestApp",
        client=http_client,
    )


class TestGenerateAuthUrl:
    @pytest.mark.anyio
    async def test_returns_valid_trello_url(self, adapter):
        url = await adapter.generate_auth_url()

        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "trello.com"
        assert parsed.path == "/1/authorize"

    @pytest.mark.anyio
    async def test_includes_api_key(self, adapter):
        url = await adapter.generate_auth_url()

        params = parse_qs(urlparse(url).query)
        assert params["key"] == ["test-api-key"]

    @pytest.mark.anyio
    async def test_includes_app_name(self, adapter):
        url = await adapter.generate_auth_url()

        params = parse_qs(urlparse(url).query)
        assert params["name"] == ["TestApp"]

    @pytest.mark.anyio
    async def test_includes_required_params(self, adapter):
        url = await adapter.generate_auth_url()

        params = parse_qs(urlparse(url).query)
        assert params["scope"] == ["read,write"]
        assert params["response_type"] == ["token"]
        assert params["expiration"] == ["never"]


class TestStoreToken:
    @pytest.mark.anyio
    async def test_resolves_username_and_stores_token(self, adapter, token_storage, http_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"username": "johndoe"}
        mock_response.raise_for_status = MagicMock()
        http_client.get = AsyncMock(return_value=mock_response)

        username = await adapter.store_token("my-token")

        assert username == "johndoe"
        token_storage.save_tokens.assert_awaited_once_with(
            user_id="johndoe",
            access_token="my-token",
            refresh_token="",
            expires_at=0,
        )

    @pytest.mark.anyio
    async def test_empty_token_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token must not be empty"):
            await adapter.store_token("")

    @pytest.mark.anyio
    async def test_whitespace_token_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token must not be empty"):
            await adapter.store_token("   ")

    @pytest.mark.anyio
    async def test_api_failure_raises_exception(self, adapter, http_client):
        http_client.get.side_effect = Exception("connection refused")

        with pytest.raises(TrelloTokenStorageException, match="Failed to resolve Trello username"):
            await adapter.store_token("my-token")

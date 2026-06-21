from unittest.mock import AsyncMock
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
def adapter(token_storage):
    return TrelloAuthAdapter(
        token_storage_port=token_storage,
        api_key="test-api-key",
        app_name="TestApp",
    )


class TestGenerateAuthUrl:
    @pytest.mark.anyio
    async def test_returns_valid_trello_url(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.hostname == "trello.com"
        assert parsed.path == "/1/authorize"

    @pytest.mark.anyio
    async def test_includes_api_key(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        params = parse_qs(urlparse(url).query)
        assert params["key"] == ["test-api-key"]

    @pytest.mark.anyio
    async def test_includes_app_name(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        params = parse_qs(urlparse(url).query)
        assert params["name"] == ["TestApp"]

    @pytest.mark.anyio
    async def test_includes_required_params(self, adapter):
        url = await adapter.generate_auth_url("user-1")

        params = parse_qs(urlparse(url).query)
        assert params["scope"] == ["read,write"]
        assert params["response_type"] == ["token"]
        assert params["expiration"] == ["never"]


class TestStoreTokens:
    @pytest.mark.anyio
    async def test_stores_tokens_with_correct_mapping(self, adapter, token_storage):
        await adapter.store_tokens("user-1", "my-token", "my-secret")

        token_storage.save_tokens.assert_awaited_once_with(
            user_id="user-1",
            access_token="my-token",
            refresh_token="my-secret",
            expires_at=0,
        )

    @pytest.mark.anyio
    async def test_empty_token_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token must not be empty"):
            await adapter.store_tokens("user-1", "", "my-secret")

    @pytest.mark.anyio
    async def test_whitespace_token_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token must not be empty"):
            await adapter.store_tokens("user-1", "   ", "my-secret")

    @pytest.mark.anyio
    async def test_empty_token_secret_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token_secret must not be empty"):
            await adapter.store_tokens("user-1", "my-token", "")

    @pytest.mark.anyio
    async def test_whitespace_token_secret_raises_exception(self, adapter):
        with pytest.raises(TrelloTokenStorageException, match="token_secret must not be empty"):
            await adapter.store_tokens("user-1", "my-token", "   ")

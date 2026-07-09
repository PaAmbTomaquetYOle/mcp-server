import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.domain import BackendApiException
from mcp_server.infrastructure.adapters.backend_token_client import BackendTokenClient


def _mock_token_response(access_token="tok-1", expires_in=300, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }
    response.raise_for_status = lambda: None
    return response


@pytest.fixture
def client():
    return AsyncMock()


@pytest.fixture
def token_client(client):
    return BackendTokenClient(
        base_url="http://backend/api/v1",
        client_id="mcp-server",
        client_secret="s3cret",
        client=client,
    )


class TestGetAccessToken:
    @pytest.mark.anyio
    async def test_fetches_and_caches_token(self, token_client, client):
        client.post = AsyncMock(return_value=_mock_token_response())

        token_a = await token_client.get_access_token()
        token_b = await token_client.get_access_token()

        assert token_a == "tok-1"
        assert token_b == "tok-1"
        client.post.assert_awaited_once()
        called_url = client.post.await_args.args[0]
        called_body = client.post.await_args.kwargs["json"]
        assert called_url == "http://backend/api/v1/auth/token"
        assert called_body == {
            "grant_type": "client_credentials",
            "client_id": "mcp-server",
            "client_secret": "s3cret",
        }

    @pytest.mark.anyio
    async def test_refreshes_token_within_skew_of_expiry(self, token_client, client):
        client.post = AsyncMock(
            side_effect=[
                _mock_token_response(access_token="tok-1", expires_in=300),
                _mock_token_response(access_token="tok-2", expires_in=300),
            ]
        )
        now = 0.0

        with patch(
            "mcp_server.infrastructure.adapters.backend_token_client.time.monotonic",
            side_effect=lambda: now,
        ):
            first = await token_client.get_access_token()
            now = 241.0  # within 60s of the 300s expiry -> must refresh
            second = await token_client.get_access_token()

        assert first == "tok-1"
        assert second == "tok-2"
        assert client.post.await_count == 2

    @pytest.mark.anyio
    async def test_concurrent_calls_fetch_token_once(self, token_client, client):
        client.post = AsyncMock(return_value=_mock_token_response())

        tokens = await asyncio.gather(*[token_client.get_access_token() for _ in range(5)])

        assert tokens == ["tok-1"] * 5
        client.post.assert_awaited_once()

    @pytest.mark.anyio
    async def test_wraps_http_errors(self, token_client, client):
        from httpx2 import HTTPStatusError

        error_response = _mock_token_response(status_code=401)

        def _raise():
            raise HTTPStatusError("error", request=None, response=error_response)

        error_response.raise_for_status = _raise
        client.post = AsyncMock(return_value=error_response)

        with pytest.raises(BackendApiException):
            await token_client.get_access_token()

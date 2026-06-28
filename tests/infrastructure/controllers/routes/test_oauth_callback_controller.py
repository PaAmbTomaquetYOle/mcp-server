from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from starlette.testclient import TestClient

from mcp_server.application.ports.token_storage import AuthResult
from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.controllers.routes.oauth_callback_controller import (
    OAuthCallbackController,
)


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.exchange_auth_code = AsyncMock(
        return_value=AuthResult(email="user@example.com", access_token="at", refresh_token="rt", expires_at=9999)
    )
    return service


@pytest.fixture
def app(mock_auth_service):
    server = FastMCP(name="test-callback")
    OAuthCallbackController(server, mock_auth_service).register()
    return server.streamable_http_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class TestOAuthCallbackSuccess:
    def test_exchanges_code_and_returns_success_html(self, client, mock_auth_service):
        response = client.get("/callback?code=auth-code-123&state=oauth")

        assert response.status_code == 200
        assert "Jira Connected Successfully" in response.text
        assert "user@example.com" in response.text
        mock_auth_service.exchange_auth_code.assert_awaited_once_with("auth-code-123")


class TestOAuthCallbackMissingParams:
    def test_missing_code_returns_400(self, client):
        response = client.get("/callback?state=oauth")

        assert response.status_code == 400
        assert "Missing required parameter" in response.text

    def test_no_params_returns_400(self, client):
        response = client.get("/callback")

        assert response.status_code == 400


class TestOAuthCallbackExchangeFailure:
    def test_exchange_error_returns_500(self, client, mock_auth_service):
        mock_auth_service.exchange_auth_code.side_effect = AuthCodeExchangeException(
            "unknown", "invalid_grant"
        )

        response = client.get("/callback?code=bad-code&state=oauth")

        assert response.status_code == 500
        assert "Authorization Failed" in response.text
        assert "invalid_grant" in response.text

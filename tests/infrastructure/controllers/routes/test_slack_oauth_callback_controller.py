from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from starlette.testclient import TestClient

from mcp_server.application.ports.slack_auth import SlackAuthResult
from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.controllers.routes.slack_oauth_callback_controller import (
    SlackOAuthCallbackController,
)


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.exchange_auth_code = AsyncMock(
        return_value=SlackAuthResult(slack_user_id="U1", team_id="T1", access_token="xoxp-at")
    )
    return service


@pytest.fixture
def app(mock_auth_service):
    server = FastMCP(name="test-slack-callback")
    SlackOAuthCallbackController(server, mock_auth_service).register()
    return server.streamable_http_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class TestSlackOAuthCallbackSuccess:
    def test_exchanges_code_and_returns_success_html(self, client, mock_auth_service):
        response = client.get("/slack/oauth/callback?code=auth-code-123&state=oauth")

        assert response.status_code == 200
        assert "U1" in response.text
        mock_auth_service.exchange_auth_code.assert_awaited_once_with("auth-code-123")


class TestSlackOAuthCallbackMissingParams:
    def test_missing_code_returns_400(self, client):
        response = client.get("/slack/oauth/callback?state=oauth")

        assert response.status_code == 400
        assert "Missing required parameter" in response.text


class TestSlackOAuthCallbackExchangeFailure:
    def test_exchange_error_returns_500(self, client, mock_auth_service):
        mock_auth_service.exchange_auth_code.side_effect = AuthCodeExchangeException("unknown", "invalid_code")

        response = client.get("/slack/oauth/callback?code=bad-code&state=oauth")

        assert response.status_code == 500
        assert "invalid_code" in response.text

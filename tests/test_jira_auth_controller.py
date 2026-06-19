from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP

from mcp_server.application.ports.token_storage import AuthResult
from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.controllers.tools.jira_auth_controller import JiraAuthToolController
from mcp_server.infrastructure.dto import CompleteJiraAuthResponse, GenerateJiraAuthResponse
from tests.conftest import get_tool_names


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.generate_auth_url = AsyncMock(return_value="https://auth.atlassian.com/authorize?test=1")
    service.exchange_auth_code = AsyncMock(
        return_value=AuthResult(email="user@example.com", access_token="at", refresh_token="rt", expires_at=9999)
    )
    return service


@pytest.fixture
def auth_server(mock_auth_service):
    server = FastMCP(name="test-auth")
    JiraAuthToolController(server, mock_auth_service).register()
    return server


class TestJiraAuthToolRegistration:
    def test_registers_generate_auth_url_tool(self, auth_server):
        assert "generate_jira_auth_url" in get_tool_names(auth_server)

    def test_registers_complete_auth_tool(self, auth_server):
        assert "complete_jira_auth" in get_tool_names(auth_server)


class TestGenerateJiraAuthUrl:
    @pytest.mark.anyio
    async def test_returns_generate_auth_response(self, mock_auth_service):
        controller = JiraAuthToolController.__new__(JiraAuthToolController)
        controller._JiraAuthToolController__jira_auth_service = mock_auth_service

        result = await controller.generate_jira_auth_url()

        assert isinstance(result, GenerateJiraAuthResponse)
        assert result.auth_url == "https://auth.atlassian.com/authorize?test=1"
        mock_auth_service.generate_auth_url.assert_awaited_once_with(state="oauth")


class TestCompleteJiraAuth:
    @pytest.mark.anyio
    async def test_returns_complete_auth_response_with_email(self, mock_auth_service):
        controller = JiraAuthToolController.__new__(JiraAuthToolController)
        controller._JiraAuthToolController__jira_auth_service = mock_auth_service

        result = await controller.complete_jira_auth(code="auth-code")

        assert isinstance(result, CompleteJiraAuthResponse)
        assert result.success is True
        assert result.email == "user@example.com"
        mock_auth_service.exchange_auth_code.assert_awaited_once_with("auth-code")

    @pytest.mark.anyio
    async def test_error_raises_tool_error(self, mock_auth_service):
        from mcp.server.fastmcp.exceptions import ToolError

        mock_auth_service.exchange_auth_code.side_effect = AuthCodeExchangeException(
            "unknown", "invalid_grant"
        )
        controller = JiraAuthToolController.__new__(JiraAuthToolController)
        controller._JiraAuthToolController__jira_auth_service = mock_auth_service

        with pytest.raises(ToolError, match="invalid_grant"):
            await controller.complete_jira_auth(code="bad-code")

from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP

from mcp_server.application.ports.slack_auth import SlackAuthResult
from mcp_server.domain import AuthCodeExchangeException
from mcp_server.infrastructure.controllers.tools.slack_auth_controller import SlackAuthToolController
from mcp_server.infrastructure.dto import CompleteSlackAuthResponse, GenerateSlackAuthResponse
from tests.conftest import get_tool_names


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.generate_auth_url = AsyncMock(return_value="https://slack.com/oauth/v2/authorize?test=1")
    service.exchange_auth_code = AsyncMock(
        return_value=SlackAuthResult(slack_user_id="U1", team_id="T1", access_token="xoxp-at")
    )
    return service


@pytest.fixture
def auth_server(mock_auth_service):
    server = FastMCP(name="test-slack-auth")
    SlackAuthToolController(server, mock_auth_service).register()
    return server


class TestSlackAuthToolRegistration:
    def test_registers_generate_auth_url_tool(self, auth_server):
        assert "generate_slack_auth_url" in get_tool_names(auth_server)

    def test_registers_complete_auth_tool(self, auth_server):
        assert "complete_slack_auth" in get_tool_names(auth_server)


class TestGenerateSlackAuthUrl:
    @pytest.mark.anyio
    async def test_returns_generate_auth_response(self, mock_auth_service):
        controller = SlackAuthToolController.__new__(SlackAuthToolController)
        controller._SlackAuthToolController__slack_auth_service = mock_auth_service

        result = await controller.generate_slack_auth_url()

        assert isinstance(result, GenerateSlackAuthResponse)
        assert result.auth_url == "https://slack.com/oauth/v2/authorize?test=1"
        mock_auth_service.generate_auth_url.assert_awaited_once_with(state="oauth")


class TestCompleteSlackAuth:
    @pytest.mark.anyio
    async def test_returns_complete_auth_response(self, mock_auth_service):
        controller = SlackAuthToolController.__new__(SlackAuthToolController)
        controller._SlackAuthToolController__slack_auth_service = mock_auth_service

        result = await controller.complete_slack_auth(code="auth-code")

        assert isinstance(result, CompleteSlackAuthResponse)
        assert result.success is True
        assert result.slack_user_id == "U1"
        assert result.team_id == "T1"
        mock_auth_service.exchange_auth_code.assert_awaited_once_with("auth-code")

    @pytest.mark.anyio
    async def test_error_raises_tool_error(self, mock_auth_service):
        from mcp.server.fastmcp.exceptions import ToolError

        mock_auth_service.exchange_auth_code.side_effect = AuthCodeExchangeException("unknown", "invalid_code")
        controller = SlackAuthToolController.__new__(SlackAuthToolController)
        controller._SlackAuthToolController__slack_auth_service = mock_auth_service

        with pytest.raises(ToolError, match="invalid_code"):
            await controller.complete_slack_auth(code="bad-code")

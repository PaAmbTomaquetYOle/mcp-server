from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.domain.exceptions import TrelloTokenStorageException
from mcp_server.infrastructure.controllers.tools.trello_auth_controller import TrelloAuthToolController
from mcp_server.infrastructure.dto import CompleteTrelloAuthResponse, GenerateTrelloAuthResponse
from tests.conftest import get_tool_names


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.generate_auth_url = AsyncMock(
        return_value="https://trello.com/1/authorize?key=test-key&name=TestApp"
    )
    service.store_tokens = AsyncMock(return_value="johndoe")
    return service


@pytest.fixture
def auth_server(mock_auth_service):
    server = FastMCP(name="test-trello-auth")
    TrelloAuthToolController(server, mock_auth_service).register()
    return server


class TestTrelloAuthToolRegistration:
    def test_registers_generate_auth_url_tool(self, auth_server):
        assert "generate_trello_auth_url" in get_tool_names(auth_server)

    def test_registers_complete_auth_tool(self, auth_server):
        assert "complete_trello_auth" in get_tool_names(auth_server)


class TestGenerateTrelloAuthUrl:
    @pytest.mark.anyio
    async def test_returns_generate_auth_response(self, mock_auth_service):
        controller = TrelloAuthToolController.__new__(TrelloAuthToolController)
        controller._TrelloAuthToolController__trello_auth_service = mock_auth_service

        result = await controller.generate_trello_auth_url()

        assert isinstance(result, GenerateTrelloAuthResponse)
        assert result.auth_url == "https://trello.com/1/authorize?key=test-key&name=TestApp"
        mock_auth_service.generate_auth_url.assert_awaited_once_with()


class TestCompleteTrelloAuth:
    @pytest.mark.anyio
    async def test_returns_complete_auth_response_with_resolved_username(self, mock_auth_service):
        controller = TrelloAuthToolController.__new__(TrelloAuthToolController)
        controller._TrelloAuthToolController__trello_auth_service = mock_auth_service

        result = await controller.complete_trello_auth(
            token="my-token", token_secret="my-secret"
        )

        assert isinstance(result, CompleteTrelloAuthResponse)
        assert result.success is True
        assert result.user_id == "johndoe"
        mock_auth_service.store_tokens.assert_awaited_once_with("my-token", "my-secret")

    @pytest.mark.anyio
    async def test_error_raises_tool_error(self, mock_auth_service):
        mock_auth_service.store_tokens.side_effect = TrelloTokenStorageException(
            "unknown", "token must not be empty"
        )
        controller = TrelloAuthToolController.__new__(TrelloAuthToolController)
        controller._TrelloAuthToolController__trello_auth_service = mock_auth_service

        with pytest.raises(ToolError, match="token must not be empty"):
            await controller.complete_trello_auth(
                token="", token_secret="my-secret"
            )

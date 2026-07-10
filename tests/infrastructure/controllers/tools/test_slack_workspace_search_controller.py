from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.domain import UserTokensNotFoundException
from mcp_server.domain.search import SlackWorkspaceSearchResult
from mcp_server.infrastructure.controllers.tools.slack_workspace_search_controller import (
    SlackWorkspaceSearchToolController,
)
from mcp_server.infrastructure.dto import SlackWorkspaceSearchResponse
from tests.conftest import get_tool_names

_RESULT = SlackWorkspaceSearchResult(
    content_type="messages", text="deploy failed", permalink="https://x", timestamp="1"
)


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.search = AsyncMock(return_value=[_RESULT])
    return service


@pytest.fixture
def search_server(mock_service):
    server = FastMCP(name="test-slack-workspace-search")
    SlackWorkspaceSearchToolController(server, mock_service).register()
    return server


class TestRegistration:
    def test_registers_tool(self, search_server):
        assert "search_slack_workspace" in get_tool_names(search_server)


class TestSearchSlackWorkspace:
    @pytest.mark.anyio
    async def test_returns_results(self, mock_service):
        controller = SlackWorkspaceSearchToolController.__new__(SlackWorkspaceSearchToolController)
        controller._SlackWorkspaceSearchToolController__service = mock_service

        result = await controller.search_slack_workspace(user_id="U1", query="deploy")

        assert isinstance(result, SlackWorkspaceSearchResponse)
        assert result.count == 1
        assert result.results[0].text == "deploy failed"
        mock_service.search.assert_awaited_once_with("U1", "deploy", filters={})

    @pytest.mark.anyio
    async def test_not_authenticated_raises_tool_error(self, mock_service):
        mock_service.search.side_effect = UserTokensNotFoundException("U1")
        controller = SlackWorkspaceSearchToolController.__new__(SlackWorkspaceSearchToolController)
        controller._SlackWorkspaceSearchToolController__service = mock_service

        with pytest.raises(ToolError):
            await controller.search_slack_workspace(user_id="U1", query="deploy")

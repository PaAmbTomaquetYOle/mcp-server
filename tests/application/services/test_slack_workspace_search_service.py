from unittest.mock import AsyncMock

import pytest

from mcp_server.application.ports.token_storage import TokenData
from mcp_server.application.services.slack_workspace_search_service import SlackWorkspaceSearchService
from mcp_server.domain import UserTokensNotFoundException
from mcp_server.domain.search import SlackWorkspaceSearchResult

_RESULT = SlackWorkspaceSearchResult(content_type="messages", text="deploy failed", permalink=None, timestamp=None)


@pytest.fixture
def mock_token_storage():
    storage = AsyncMock()
    storage.get_tokens = AsyncMock(
        return_value=TokenData(access_token="xoxp-test", refresh_token="", expires_at=0)
    )
    return storage


@pytest.fixture
def mock_workspace_search_port():
    port = AsyncMock()
    port.search_workspace = AsyncMock(return_value=[_RESULT])
    return port


@pytest.fixture
def service(mock_token_storage, mock_workspace_search_port):
    return SlackWorkspaceSearchService(
        token_storage=mock_token_storage, workspace_search_port=mock_workspace_search_port
    )


class TestSearch:
    @pytest.mark.anyio
    async def test_uses_stored_token_for_user(self, service, mock_token_storage, mock_workspace_search_port):
        results = await service.search("U1", "deploy", filters={})

        assert results == [_RESULT]
        mock_token_storage.get_tokens.assert_awaited_once_with("U1")
        mock_workspace_search_port.search_workspace.assert_awaited_once_with("xoxp-test", "deploy", {})

    @pytest.mark.anyio
    async def test_raises_when_user_not_authenticated(self, service, mock_token_storage):
        mock_token_storage.get_tokens.return_value = None

        with pytest.raises(UserTokensNotFoundException):
            await service.search("U1", "deploy", filters={})

    @pytest.mark.anyio
    async def test_defaults_filters_to_empty_dict(self, service, mock_workspace_search_port):
        await service.search("U1", "deploy")

        mock_workspace_search_port.search_workspace.assert_awaited_once_with("xoxp-test", "deploy", {})

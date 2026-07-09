from typing import Any

from mcp_server.application.ports import ISlackWorkspaceSearchPort, ITokenStoragePort
from mcp_server.application.service_interfaces import ISlackWorkspaceSearchService
from mcp_server.domain import UserTokensNotFoundException
from mcp_server.domain.search import SlackWorkspaceSearchResult


class SlackWorkspaceSearchService(ISlackWorkspaceSearchService):
    """Orchestrates authenticated searches over a Slack workspace's internal content."""

    __token_storage: ITokenStoragePort
    __workspace_search_port: ISlackWorkspaceSearchPort

    def __init__(self, token_storage: ITokenStoragePort, workspace_search_port: ISlackWorkspaceSearchPort) -> None:
        self.__token_storage = token_storage
        self.__workspace_search_port = workspace_search_port

    async def search(
        self, slack_user_id: str, query: str, filters: dict[str, Any] | None = None
    ) -> list[SlackWorkspaceSearchResult]:
        tokens = await self.__token_storage.get_tokens(slack_user_id)
        if tokens is None:
            raise UserTokensNotFoundException(slack_user_id)

        return await self.__workspace_search_port.search_workspace(
            tokens["access_token"], query, filters or {}
        )

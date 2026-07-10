from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ISlackWorkspaceSearchService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import SlackWorkspaceSearchResponse, SlackWorkspaceSearchResultItem


class SlackWorkspaceSearchToolController(BaseController):
    """Controller for the tool that searches Slack's internal workspace content (Real-Time Search API)."""

    __service: ISlackWorkspaceSearchService

    def __init__(self, server: FastMCP, service: ISlackWorkspaceSearchService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.add_tool(
            self.search_slack_workspace,
            name="search_slack_workspace",
            title="Search Slack workspace",
            description=(
                "Search Slack's own internal messages, files, channels, and users on behalf of an "
                "authenticated user, using the Real-Time Search API (assistant.search.context). "
                "Requires the user to have completed the Slack OAuth flow first "
                "(generate_slack_auth_url / complete_slack_auth)."
            ),
        )

    @tool_error_handler
    async def search_slack_workspace(self, user_id: str, query: str) -> SlackWorkspaceSearchResponse:
        """Search Slack's internal workspace content on behalf of an authenticated user.

        Args:
            user_id (str): The Slack user ID whose stored OAuth token authorizes the search.
            query (str): Free-text search query.
        """
        documents = await self.__service.search(user_id, query, filters={})
        results = [
            SlackWorkspaceSearchResultItem(
                content_type=doc.content_type,
                text=doc.text,
                permalink=doc.permalink,
                timestamp=doc.timestamp,
            )
            for doc in documents
        ]
        return SlackWorkspaceSearchResponse(query=query, results=results, count=len(results))

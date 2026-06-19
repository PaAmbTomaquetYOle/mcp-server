from mcp.server import FastMCP

from mcp_server.application.service_interfaces import IJiraAuthService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import CompleteJiraAuthResponse, GenerateJiraAuthResponse


class JiraAuthToolController(BaseController):
    """Controller for Jira OAuth 2.0 authentication tools."""

    __jira_auth_service: IJiraAuthService

    def __init__(self, server: FastMCP, jira_auth_service: IJiraAuthService) -> None:
        super().__init__(server)
        self.__jira_auth_service = jira_auth_service

    def register(self) -> None:
        self._server.add_tool(
            self.generate_jira_auth_url,
            name="generate_jira_auth_url",
            title="Generate Jira authorization URL",
            description=(
                "Generate an Atlassian OAuth 2.0 authorization URL for a user. "
                "The user must visit this URL to grant consent. "
                "After granting consent, the browser redirects to the callback endpoint "
                "which automatically exchanges the code for tokens."
            ),
        )
        self._server.add_tool(
            self.complete_jira_auth,
            name="complete_jira_auth",
            title="Complete Jira authentication",
            description=(
                "Exchange an OAuth authorization code for access and refresh tokens. "
                "Usually not needed — the /callback endpoint handles this automatically. "
                "Use this tool only for programmatic flows where the callback is not available."
            ),
        )

    @tool_error_handler
    async def generate_jira_auth_url(self, user_id: str) -> GenerateJiraAuthResponse:
        """Generate the Atlassian OAuth 2.0 authorization URL.

        Args:
            user_id (str): Arbitrary identifier used as the key for token storage
                (e.g. Slack user ID, email). Not a Jira account ID. Must be the
                same value used in subsequent Jira API tool calls.
        Returns:
            The GenerateJiraAuthResponse object.
        """
        auth_url = await self.__jira_auth_service.generate_auth_url(user_id)
        return GenerateJiraAuthResponse(
            auth_url=auth_url,
            user_id=user_id,
        )

    @tool_error_handler
    async def complete_jira_auth(self, user_id: str, code: str) -> CompleteJiraAuthResponse:
        """Exchange an authorization code for tokens and store them.

        Args:
            user_id (str): Arbitrary identifier used as the key for token storage.
                Must match the value used in generate_jira_auth_url.
            code (str): The authorization code received after user consent.
        Returns:
            A dict confirming the authentication was completed successfully.
        """
        await self.__jira_auth_service.exchange_auth_code(user_id, code)
        return CompleteJiraAuthResponse(
            success=True,
            user_id=user_id,
            message="Jira authentication completed. Tokens stored successfully.",
        )

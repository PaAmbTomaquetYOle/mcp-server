from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ISlackAuthService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import CompleteSlackAuthResponse, GenerateSlackAuthResponse


class SlackAuthToolController(BaseController):
    """Controller for Slack OAuth 2.0 user authentication tools."""

    __slack_auth_service: ISlackAuthService

    def __init__(self, server: FastMCP, slack_auth_service: ISlackAuthService) -> None:
        super().__init__(server)
        self.__slack_auth_service = slack_auth_service

    def register(self) -> None:
        self._server.add_tool(
            self.generate_slack_auth_url,
            name="generate_slack_auth_url",
            title="Generate Slack authorization URL",
            description=(
                "Generate a Slack OAuth 2.0 authorization URL requesting search scopes. "
                "The user must visit this URL to grant consent. After granting consent, the "
                "browser redirects to the callback endpoint which automatically exchanges the "
                "code for a user token."
            ),
        )
        self._server.add_tool(
            self.complete_slack_auth,
            name="complete_slack_auth",
            title="Complete Slack authentication",
            description=(
                "Exchange an OAuth authorization code for a Slack user token. "
                "Usually not needed — the /slack/oauth/callback endpoint handles this automatically. "
                "Use this tool only for programmatic flows where the callback is not available. "
                "Returns the Slack user ID, which must be used as user_id in search_slack_workspace."
            ),
        )

    @tool_error_handler
    async def generate_slack_auth_url(self) -> GenerateSlackAuthResponse:
        """Generate the Slack OAuth 2.0 authorization URL."""
        auth_url = await self.__slack_auth_service.generate_auth_url(state="oauth")
        return GenerateSlackAuthResponse(auth_url=auth_url)

    @tool_error_handler
    async def complete_slack_auth(self, code: str) -> CompleteSlackAuthResponse:
        """Exchange an authorization code for a Slack user token and store it.

        Args:
            code (str): The authorization code received after user consent.
        Returns:
            CompleteSlackAuthResponse with the resolved Slack user ID.
        """
        result = await self.__slack_auth_service.exchange_auth_code(code)
        return CompleteSlackAuthResponse(
            success=True,
            slack_user_id=result["slack_user_id"],
            team_id=result["team_id"],
            message=f"Slack authentication completed for user {result['slack_user_id']}.",
        )

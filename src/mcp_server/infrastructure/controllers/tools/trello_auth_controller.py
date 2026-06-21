from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ITrelloAuthService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import CompleteTrelloAuthResponse, GenerateTrelloAuthResponse


class TrelloAuthToolController(BaseController):
    """Controller for Trello OAuth 1.0a authentication tools."""

    __trello_auth_service: ITrelloAuthService

    def __init__(self, server: FastMCP, trello_auth_service: ITrelloAuthService) -> None:
        super().__init__(server)
        self.__trello_auth_service = trello_auth_service

    def register(self) -> None:
        self._server.add_tool(
            self.generate_trello_auth_url,
            name="generate_trello_auth_url",
            title="Generate Trello authorization URL",
            description=(
                "Generate a Trello OAuth authorization URL. "
                "The user must visit this URL to grant consent and obtain "
                "the OAuth token and token secret required for Trello access."
            ),
        )
        self._server.add_tool(
            self.complete_trello_auth,
            name="complete_trello_auth",
            title="Complete Trello authentication",
            description=(
                "Store Trello OAuth credentials (token and token_secret). "
                "Resolves the Trello username automatically from the token "
                "and uses it as the user_id for all subsequent Trello operations. "
                "Call this after the user has completed the Trello authorization flow "
                "and obtained their token pair."
            ),
        )

    @tool_error_handler
    async def generate_trello_auth_url(self) -> GenerateTrelloAuthResponse:
        """Generate the Trello OAuth authorization URL.

        Returns:
            GenerateTrelloAuthResponse with the authorization URL.
        """
        auth_url = await self.__trello_auth_service.generate_auth_url()
        return GenerateTrelloAuthResponse(auth_url=auth_url)

    @tool_error_handler
    async def complete_trello_auth(
        self, token: str, token_secret: str
    ) -> CompleteTrelloAuthResponse:
        """Store Trello OAuth tokens, resolving the username from the token.

        Args:
            token (str): The OAuth access token from Trello.
            token_secret (str): The OAuth token secret from Trello.
        Returns:
            CompleteTrelloAuthResponse with the resolved username.
        """
        username = await self.__trello_auth_service.store_tokens(token, token_secret)
        return CompleteTrelloAuthResponse(
            success=True,
            user_id=username,
            message=f"Trello authentication completed. Tokens stored for {username}.",
        )

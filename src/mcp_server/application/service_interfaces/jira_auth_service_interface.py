from abc import ABC, abstractmethod

from mcp_server.application.ports.token_storage import TokenData


class IJiraAuthService(ABC):
    """Interface for the Jira authentication use case."""

    @abstractmethod
    async def generate_auth_url(self, user_id: str) -> str:
        """Generate the Atlassian OAuth 2.0 authorization URL.

        Args:
            user_id: Identifier for the user initiating the OAuth flow.
        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def exchange_auth_code(self, user_id: str, code: str) -> TokenData:
        """Exchange an authorization code for access and refresh tokens.

        Args:
            user_id: Identifier for the user completing the OAuth flow.
            code: The authorization code received after user consent.
        Returns:
            The stored token data.
        """

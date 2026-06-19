from abc import ABC, abstractmethod

from mcp_server.application.ports.token_storage import AuthResult


class IJiraAuthService(ABC):
    """Interface for the Jira authentication use case."""

    @abstractmethod
    async def generate_auth_url(self, state: str) -> str:
        """Generate the Atlassian OAuth 2.0 authorization URL.

        Args:
            state: Opaque value for CSRF protection in the OAuth state parameter.
        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def exchange_auth_code(self, code: str) -> AuthResult:
        """Exchange an authorization code for tokens and resolve the user email.

        Args:
            code: The authorization code received after user consent.
        Returns:
            AuthResult with the user's email and token data.
        """

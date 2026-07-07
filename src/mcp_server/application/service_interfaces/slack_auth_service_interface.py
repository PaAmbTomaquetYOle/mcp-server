from abc import ABC, abstractmethod

from mcp_server.application.ports.slack_auth import SlackAuthResult


class ISlackAuthService(ABC):
    """Interface for the Slack OAuth 2.0 user authentication use case."""

    @abstractmethod
    async def generate_auth_url(self, state: str) -> str:
        """Generate the Slack OAuth 2.0 authorization URL.

        Args:
            state: Opaque value for CSRF protection in the OAuth state parameter.
        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def exchange_auth_code(self, code: str) -> SlackAuthResult:
        """Exchange an authorization code for a Slack user token and store it.

        Args:
            code: The authorization code received after user consent.
        Returns:
            SlackAuthResult with the Slack user ID, team ID, and access token.
        """

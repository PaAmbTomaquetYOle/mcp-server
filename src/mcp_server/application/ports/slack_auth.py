from abc import ABC, abstractmethod
from typing import TypedDict


class SlackAuthResult(TypedDict):
    """Result of a successful Slack OAuth v2 user-token exchange."""

    slack_user_id: str
    team_id: str
    access_token: str


class ISlackAuthPort(ABC):
    """Interface for Slack OAuth 2.0 user-token authentication operations."""

    @abstractmethod
    async def generate_auth_url(self, state: str) -> str:
        """Generate the Slack OAuth 2.0 authorization URL requesting user search scopes.

        Args:
            state: Opaque value included in the OAuth state parameter.
        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def exchange_auth_code(self, code: str) -> SlackAuthResult:
        """Exchange an authorization code for a Slack user token.

        Args:
            code: The authorization code received after user consent.
        Returns:
            SlackAuthResult with the Slack user ID, team ID, and user access token.
        """

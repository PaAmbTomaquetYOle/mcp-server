from abc import ABC, abstractmethod


class ITrelloAuthPort(ABC):
    """Interface for Trello OAuth 1.0a authentication operations."""

    @abstractmethod
    async def generate_auth_url(self) -> str:
        """Generate the Trello OAuth authorization URL.

        Returns:
            The authorization URL the user must visit to grant consent.
        """

    @abstractmethod
    async def store_token(self, token: str) -> str:
        """Resolve the Trello username from the token and persist OAuth credentials.

        Args:
            token: The OAuth access token from Trello.
        Returns:
            The resolved Trello username, used as user_id for subsequent calls.
        """
